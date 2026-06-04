"""
Dream Underwrite — ACQ (Conventional Value-Add) Calc Engine
Version 1.0  |  2026-06-03

The ACQ layer the LIHTC/EFB engine (`lihtc_engine.py`) does not cover. Computes a
conventional value-add multifamily deal end-to-end so the math can be sanity-checked before
the ACQ Mini Model is populated, and reconciled against the Excel formulas (the human gate).

Covers:
- Per-period senior debt: bridge IO -> agency-refi IO -> agency-refi P+I, with an optional
  servicing/guaranty spread on top of the note rate (Fannie/Freddie add a few bps; this is
  why the Mini Model's debt service runs ~1.16% above the bare note-rate constant).
- 10-year levered cash flow with a year-by-year vacancy curve.
- DSCR series across the bridge->refi transition.
- 3-method exit-cap triangulation (Treasury spread / comp validation / entry+strategy),
  TAKE HIGHEST per Manual v2 §Exit Cap Triangulation.
- Exit value, levered project IRR, equity multiple, stabilized cash-on-cash.
- Agency takeout sizing: MIN across DSCR / LTV / Debt-Yield constraints (binding constraint
  reported) per Manual v2 §90/90 + HUD 223(f) LTV caps.
- State-specific property-tax reassessment (FL/TX/GA + default).
- Return-hurdle check (market tier base + risk premiums) per Manual v2 §Return Hurdles.

Methodology source: references/13-manual-standards.md (distilled from
SHIELDSTONE_TECHNICAL_MANUAL_V2_FINAL.md). All money math uses Decimal; IRR uses
numpy_financial.irr (same library the LIHTC engine uses).

Design note: debt service is modeled PER PERIOD and can be either derived (note rate +
servicing spread, monthly-amortizing) or passed explicitly. This lets the engine match
whatever convention a given Mini Model uses; any residual delta is surfaced by the
reconciliation gate rather than silently absorbed.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List, Dict, Optional
import numpy_financial as npf

D = Decimal


# =============================================================================
# ENUMS / DATACLASSES
# =============================================================================

class LoanPhase(Enum):
    BRIDGE_IO = "bridge_io"
    REFI_IO = "refi_io"
    REFI_PI = "refi_pi"


class MarketTier(Enum):
    GATEWAY = "Gateway"      # base IRR 14-16%
    SECONDARY = "Secondary"  # base IRR 16-19%
    TERTIARY = "Tertiary"    # base IRR 18-22%


@dataclass
class LoanTerms:
    """Senior debt terms for the bridge->agency-refi structure.

    servicing_spread is added to the note rate when DERIVING debt service (decimal, e.g.
    0.0116 for ~1.16% of the bare constant -> see Esplanade reconciliation). Set to 0 to
    use the bare note rate. Ignored if explicit per-year debt service is supplied to the
    cash-flow projector.
    """
    bridge_loan: Decimal
    bridge_rate: Decimal
    bridge_io_years: int            # years of bridge before refi takes out
    refi_loan: Decimal
    refi_rate: Decimal
    refi_io_years: int              # years of IO AFTER refi origination
    refi_amort_years: int = 30
    refi_year: int = 2              # model year the refi originates / takes out the bridge
    servicing_spread: Decimal = D("0")


@dataclass
class DebtServiceYear:
    year: int
    phase: LoanPhase
    loan_balance: Decimal
    debt_service: Decimal


@dataclass
class ExitCapResult:
    method_treasury: Decimal
    method_comp: Optional[Decimal]
    method_entry_strategy: Decimal
    exit_cap: Decimal               # the HIGHEST (most conservative)
    binding_method: str


@dataclass
class AgencySizingResult:
    by_dscr: Decimal
    by_ltv: Decimal
    by_debt_yield: Decimal
    max_loan: Decimal               # MIN of the three
    binding_constraint: str


@dataclass
class ACQCashFlowYear:
    year: int
    gpr: Decimal
    vacancy_rate: Decimal
    egi: Decimal
    opex: Decimal
    noi: Decimal
    debt_service: Decimal
    phase: str
    cfbt: Decimal                   # cash flow before tax (after debt service)
    dscr: Decimal


@dataclass
class ACQReturnResult:
    irr: Decimal
    equity_multiple: Decimal
    coc_year1: Decimal
    coc_stabilized: Decimal
    exit_value: Decimal
    net_sale_proceeds: Decimal
    total_equity: Decimal
    cash_flows: List[Decimal]       # the levered equity cash-flow stream fed to IRR
    dscr_series: List[Decimal]


@dataclass
class HurdleResult:
    base_irr: Decimal
    total_premium_bps: int
    adjusted_hurdle: Decimal
    recommendation: str             # PROCEED / PROCEED WITH CAUTION / REQUEST REPRICING / PASS
    components: Dict[str, int]


# =============================================================================
# SENIOR DEBT (per-period: bridge IO -> refi IO -> refi P+I)
# =============================================================================

class SeniorDebtCalculator:
    """Builds the per-year senior debt service stream across the bridge->refi transition.

    Year mapping (matches the ACQ Mini Model convention validated on Esplanade):
      - Years 1 .. bridge_io_years            -> BRIDGE_IO   (bridge_loan * bridge_rate)
      - Next refi_io_years                     -> REFI_IO    (refi_loan  * refi_rate)
      - Remaining to `years`                   -> REFI_PI    (amortizing P+I on refi_loan)
    servicing_spread scales the derived debt service uniformly (1 + spread).
    """

    def annual_pi(self, principal: Decimal, rate: Decimal, amort_years: int) -> Decimal:
        """Annualized monthly-amortizing P+I payment."""
        mr = float(rate) / 12.0
        n = amort_years * 12
        p = float(principal)
        if mr <= 0:
            return D(str(p / amort_years))
        pmt = p * mr / (1 - (1 + mr) ** -n)
        return D(str(pmt * 12))

    def build(self, terms: LoanTerms, years: int = 10) -> List[DebtServiceYear]:
        spread = D("1") + terms.servicing_spread
        bridge_ds = terms.bridge_loan * terms.bridge_rate * spread
        refi_io_ds = terms.refi_loan * terms.refi_rate * spread
        refi_pi_ds = self.annual_pi(terms.refi_loan, terms.refi_rate, terms.refi_amort_years) * spread

        io_end = terms.bridge_io_years + terms.refi_io_years
        out: List[DebtServiceYear] = []
        for y in range(1, years + 1):
            if y <= terms.bridge_io_years:
                out.append(DebtServiceYear(y, LoanPhase.BRIDGE_IO, terms.bridge_loan, bridge_ds))
            elif y <= io_end:
                out.append(DebtServiceYear(y, LoanPhase.REFI_IO, terms.refi_loan, refi_io_ds))
            else:
                out.append(DebtServiceYear(y, LoanPhase.REFI_PI, terms.refi_loan, refi_pi_ds))
        return out


# =============================================================================
# INTEREST RESERVE SIZING (lease-up / Year-1 DSCR shortfall)
# =============================================================================

@dataclass
class InterestReserveResult:
    shortfall_years: List[int]
    gross_shortfall: Decimal        # sum of (debt service - NOI) across shortfall years
    buffer: Decimal                 # multiplier applied (1.25-1.35)
    reserve_sized: Decimal          # rounded up to nearest round_to
    covered_dscr_floor: Decimal     # DSCR floor the reserve lets the deal clear


class InterestReserveSizer:
    """Sizes an interest reserve to cover the debt-service shortfall in lease-up / ramp years.

    Per references/08-efb-financing.md Step 4 and references/09-acq-financing.md. A lease-up
    acquisition (or Texas EFB Year-1-at-full-tax) has NOI below debt service early on; rather
    than failing the deal on a Year-1 DSCR that ignores the reserve every real deal carries,
    size the reserve = sum of shortfalls across the covered years x buffer, rounded up.

    Use the result to (a) add to total project cost / equity, and (b) treat reserve-covered
    years as DSCR-passing in the cash-flow projector (the reserve, not operations, pays debt
    service in those years).
    """

    def size(
        self,
        noi_series: List[Decimal],
        debt_service: List[DebtServiceYear],
        dscr_floor: Decimal = D("1.15"),
        buffer: Decimal = D("1.30"),
        round_to: Decimal = D("50000"),
        max_cover_years: int = 3,
    ) -> InterestReserveResult:
        shortfall_years: List[int] = []
        gross = D("0")
        for i in range(min(len(noi_series), len(debt_service), max_cover_years)):
            ds = debt_service[i].debt_service
            need = ds * dscr_floor  # NOI needed to hit the floor
            if noi_series[i] < need:
                # shortfall is what the reserve must top up to reach the floor coverage,
                # capped at the actual debt service (reserve never pays more than DS).
                top_up = min(need - noi_series[i], ds - max(noi_series[i], D("0")))
                if top_up > 0:
                    shortfall_years.append(i + 1)
                    gross += top_up
        reserve = gross * buffer
        # round up to nearest round_to
        if round_to > 0 and reserve > 0:
            import math
            reserve = D(str(math.ceil(float(reserve) / float(round_to)))) * round_to
        return InterestReserveResult(
            shortfall_years=shortfall_years,
            gross_shortfall=gross,
            buffer=buffer,
            reserve_sized=reserve,
            covered_dscr_floor=dscr_floor,
        )


# =============================================================================
# LEASE-UP NOI RAMP (derive from forensic vacancy curve + concession burn-off)
# =============================================================================

class LeaseUpRamp:
    """Derives the Year-1..N NOI ramp from a vacancy curve + concession burn-off instead of a
    flat manual assumption. Stabilized NOI is the input; the ramp scales it down in early years
    by the extra economic loss (elevated vacancy + concessions) relative to stabilized.
    """

    def noi_series(
        self,
        stabilized_noi: Decimal,
        stabilized_egi: Decimal,
        vacancy_curve: List[Decimal],      # per-year economic vacancy (decimal), e.g. [0.15,0.10,0.08,...]
        concession_curve: List[Decimal],   # per-year concessions as % of GPR, e.g. [0.06,0.03,0.01,...]
        stabilized_vacancy: Decimal = D("0.08"),
        stabilized_concession: Decimal = D("0.01"),
        growth: Decimal = D("0.025"),
        years: int = 10,
    ) -> List[Decimal]:
        out: List[Decimal] = []
        for y in range(years):
            vac = vacancy_curve[y] if y < len(vacancy_curve) else stabilized_vacancy
            conc = concession_curve[y] if y < len(concession_curve) else stabilized_concession
            # extra loss vs stabilized, as a fraction of EGI
            extra_loss = (vac - stabilized_vacancy) + (conc - stabilized_concession)
            extra_loss = max(extra_loss, D("0"))
            base = stabilized_noi - (stabilized_egi * extra_loss)
            # apply growth once stabilized (after the ramp settles to stabilized vacancy)
            stab_year = next((i for i, v in enumerate(vacancy_curve) if v <= stabilized_vacancy), len(vacancy_curve))
            if y > stab_year:
                base = stabilized_noi * ((D("1") + growth) ** (y - stab_year))
            out.append(base)
        return out


# =============================================================================
# FOUR-TIER GPR-MAX OPTIMIZER (mixed-income tier x bedroom allocation)
# =============================================================================

@dataclass
class TierAllocation:
    tier: str           # "Market" | "100AMI" | "HAP" | "80AMI"
    bedroom: str
    units: int
    rent: Decimal       # per-unit/month net-to-owner rent for this tier+bedroom
    inplace: Decimal


class FourTierOptimizer:
    """Allocates units across tiers (Market / 100% AMI / HAP / 80% AMI) to MAXIMIZE GPR under a
    fixed tier-share constraint (e.g. 49% market / 15% HAP / 18% 100AMI / 18% 80AMI).

    Principle (per Evan's Envy methodology): market tier takes the highest signed-rent units;
    affordable tiers take the units with the SMALLEST give-up to their ceiling (least GPR lost).
    100% AMI is often accretive on bedrooms where the ceiling >= in-place. Returns the allocation
    and the GPR delta vs pure-market.
    """

    def allocate(
        self,
        units: List[Dict],          # [{"bedroom","sf","inplace","market_rent"}], one per physical unit
        tier_shares: Dict[str, Decimal],   # {"Market":0.49,"HAP":0.15,"100AMI":0.18,"80AMI":0.18}
        tier_ceilings: Dict[str, Dict[str, Decimal]],  # {"100AMI":{"1BR":..},"80AMI":{..},"HAP_FMR":{..}}
    ) -> Dict:
        n = len(units)
        targets = {t: round(float(share) * n) for t, share in tier_shares.items()}
        # fix rounding so targets sum to n
        diff = n - sum(targets.values())
        if diff != 0:
            biggest = max(targets, key=targets.get)
            targets[biggest] += diff

        # net-to-owner rent for a unit in a given tier
        def tier_rent(u, tier):
            br = u["bedroom"]
            if tier == "Market":
                return D(str(u["market_rent"]))
            if tier == "HAP":
                return tier_ceilings.get("HAP_FMR", {}).get(br, D("0"))
            if tier == "100AMI":
                return min(D(str(u["market_rent"])), tier_ceilings.get("100AMI", {}).get(br, D("0")))
            if tier == "80AMI":
                return min(D(str(u["market_rent"])), tier_ceilings.get("80AMI", {}).get(br, D("0")))
            return D("0")

        remaining = list(range(n))
        assigned: Dict[int, str] = {}
        # 1) Market: take the highest market_rent units
        order = sorted(remaining, key=lambda i: float(units[i]["market_rent"]), reverse=True)
        for i in order[:targets.get("Market", 0)]:
            assigned[i] = "Market"
        remaining = [i for i in remaining if i not in assigned]
        # 2) For each affordable tier, take units with the SMALLEST give-up (market - tier rent)
        for tier in ["100AMI", "80AMI", "HAP"]:
            k = targets.get(tier, 0)
            ranked = sorted(remaining, key=lambda i: float(D(str(units[i]["market_rent"])) - tier_rent(units[i], tier)))
            for i in ranked[:k]:
                assigned[i] = tier
            remaining = [i for i in remaining if i not in assigned]
        # any leftover -> Market
        for i in remaining:
            assigned[i] = "Market"

        # build allocation + GPR
        gpr = D("0")
        pure_market_gpr = D("0")
        allocs: List[TierAllocation] = []
        agg: Dict = {}
        for i, u in enumerate(units):
            t = assigned[i]
            r = tier_rent(u, t)
            gpr += r * 12
            pure_market_gpr += D(str(u["market_rent"])) * 12
            key = (t, u["bedroom"])
            if key not in agg:
                agg[key] = {"units": 0, "rent_sum": D("0"), "inplace_sum": D("0")}
            agg[key]["units"] += 1
            agg[key]["rent_sum"] += r
            agg[key]["inplace_sum"] += D(str(u["inplace"]))
        for (t, br), a in sorted(agg.items()):
            allocs.append(TierAllocation(tier=t, bedroom=br, units=a["units"],
                                         rent=(a["rent_sum"] / a["units"]),
                                         inplace=(a["inplace_sum"] / a["units"])))
        return {
            "allocations": allocs,
            "gpr": gpr,
            "pure_market_gpr": pure_market_gpr,
            "gpr_delta": gpr - pure_market_gpr,
            "gpr_delta_pct": (gpr / pure_market_gpr - D("1")) if pure_market_gpr else D("0"),
            "tier_targets": targets,
        }


# =============================================================================
# AGENCY TAKEOUT SIZING (MIN of DSCR / LTV / Debt-Yield)
# =============================================================================

class AgencyTakeoutSizer:
    """Sizes the agency refi loan as the MIN across three binding constraints.

    - DSCR:       max_loan_by_dscr = (NOI / target_dscr) capitalized at the loan constant
    - LTV:        max_loan_by_ltv  = stabilized_value * max_ltv
    - Debt Yield: max_loan_by_dy   = NOI / min_debt_yield
    Returns the binding (lowest) constraint per Manual v2 §90/90 and HUD 223(f) LTV caps.
    """

    def size(
        self,
        stabilized_noi: Decimal,
        stabilized_value: Decimal,
        refi_rate: Decimal,
        amort_years: int = 30,
        target_dscr: Decimal = D("1.25"),
        max_ltv: Decimal = D("0.75"),
        min_debt_yield: Decimal = D("0.085"),
    ) -> AgencySizingResult:
        # Loan constant (monthly-amortizing) -> annual factor per $1 of loan
        mr = float(refi_rate) / 12.0
        n = amort_years * 12
        constant = D(str((mr / (1 - (1 + mr) ** -n)) * 12)) if mr > 0 else D(str(1.0 / amort_years))

        max_annual_ds = stabilized_noi / target_dscr
        by_dscr = max_annual_ds / constant
        by_ltv = stabilized_value * max_ltv
        by_dy = stabilized_noi / min_debt_yield

        max_loan = min(by_dscr, by_ltv, by_dy)
        binding = {by_dscr: "DSCR", by_ltv: "LTV", by_dy: "Debt Yield"}[max_loan]
        return AgencySizingResult(by_dscr, by_ltv, by_dy, max_loan, binding)


# =============================================================================
# EXIT CAP TRIANGULATION (3-method, take HIGHEST)
# =============================================================================

class ExitCapTriangulator:
    """Manual v2 §Exit Cap Triangulation. Final exit cap = HIGHEST of three methods."""

    STRATEGY_SPREAD = {
        "core": D("0.0035"),        # +25-45 bps -> midpoint 35
        "core_plus": D("0.00625"),  # +50-75 bps -> midpoint 62.5
        "value_add": D("0.0100"),   # +100 bps
        "opportunistic": D("0.0150"),  # +100-200 bps -> midpoint 150
    }

    def triangulate(
        self,
        going_in_cap: Decimal,
        strategy: str = "value_add",
        forward_treasury: Optional[Decimal] = None,
        agency_spread: Decimal = D("0.0150"),
        neg_leverage_buffer: Decimal = D("0.0075"),
        comp_implied_cap: Optional[Decimal] = None,
    ) -> ExitCapResult:
        # Method 1: Treasury spread (only if a forward treasury is supplied)
        m1 = (forward_treasury + agency_spread + neg_leverage_buffer) if forward_treasury is not None else None
        # Method 3: entry cap + strategy spread
        m3 = going_in_cap + self.STRATEGY_SPREAD.get(strategy, D("0.0100"))
        # Method 2: comp-implied (optional external)
        m2 = comp_implied_cap

        candidates = {"entry+strategy": m3}
        if m1 is not None:
            candidates["treasury_spread"] = m1
        if m2 is not None:
            candidates["comp_validation"] = m2

        exit_cap = max(candidates.values())
        binding = [k for k, v in candidates.items() if v == exit_cap][0]
        return ExitCapResult(
            method_treasury=m1 if m1 is not None else D("0"),
            method_comp=m2,
            method_entry_strategy=m3,
            exit_cap=exit_cap,
            binding_method=binding,
        )


# =============================================================================
# STATE PROPERTY TAX (reassessment ratios)
# =============================================================================

class PropertyTaxCalculator:
    """ACQ state-specific reassessment. Year 1 = current assessed x millage; Year 2+ =
    ratio x purchase price x millage, growing at a default rate. Per references/06-property-tax.md.
    """
    # midpoint reassessment ratios (Manual / 06-property-tax)
    STATE_RATIO = {"FL": D("0.725"), "TX": D("0.65"), "GA": D("0.40")}

    def project(
        self,
        purchase_price: Decimal,
        millage: Decimal,
        state: str,
        years: int = 10,
        year1_tax: Optional[Decimal] = None,
        growth: Decimal = D("0.025"),
        ratio_override: Optional[Decimal] = None,
    ) -> List[Decimal]:
        ratio = ratio_override if ratio_override is not None else self.STATE_RATIO.get(state.upper(), D("0.675"))
        reassessed_base = purchase_price * ratio * millage
        out: List[Decimal] = []
        for y in range(1, years + 1):
            if y == 1 and year1_tax is not None:
                out.append(year1_tax)
            else:
                start = y if year1_tax is None else 2
                grown = reassessed_base * ((D("1") + growth) ** (y - start))
                out.append(grown)
        return out


# =============================================================================
# ACQ CASH FLOW + RETURNS (levered IRR / EM / CoC)
# =============================================================================

class ACQCashFlowProjector:
    """Assembles the 10-year levered cash flow and the equity return stream.

    Accepts NOI series + debt-service series (from SeniorDebtCalculator or explicit), the
    equity invested, and the exit (cap on exit-year NOI). Produces DSCR series, exit value,
    net sale proceeds, levered IRR, equity multiple, and cash-on-cash.
    """

    def project(
        self,
        noi_series: List[Decimal],
        debt_service: List[DebtServiceYear],
        total_equity: Decimal,
        exit_cap: Decimal,
        sale_year: int,
        costs_of_sale: Decimal = D("0.02"),
        gpr_series: Optional[List[Decimal]] = None,
        egi_series: Optional[List[Decimal]] = None,
        opex_series: Optional[List[Decimal]] = None,
        vacancy_series: Optional[List[Decimal]] = None,
        refi_loan: Optional[Decimal] = None,
        bridge_loan: Optional[Decimal] = None,
        refi_year: Optional[int] = None,
        refi_cost_pct: Decimal = D("0.0"),
        exit_on_forward_noi: bool = True,
    ) -> ACQReturnResult:
        """Build the levered cash flow and returns.

        Two conventions matched to the ACQ Mini Model (validated on Esplanade):
        - exit_on_forward_noi: exit value = (sale_year+1) NOI / exit_cap (buyers price off
          forward NOI). Falls back to sale-year NOI if the forward year isn't projected.
        - refi cash-out: when refi_loan > bridge_loan, the excess (net of refi_cost_pct on the
          refi loan) is distributed to equity in refi_year. This is what lifts levered IRR/EM.
        """
        n = len(noi_series)
        rows: List[ACQCashFlowYear] = []
        dscr_series: List[Decimal] = []
        for i in range(n):
            y = i + 1
            ds = debt_service[i].debt_service
            noi = noi_series[i]
            cfbt = noi - ds
            dscr = (noi / ds) if ds > 0 else D("0")
            rows.append(ACQCashFlowYear(
                year=y,
                gpr=(gpr_series[i] if gpr_series else D("0")),
                vacancy_rate=(D(str(vacancy_series[i])) / 100 if vacancy_series else D("0")),
                egi=(egi_series[i] if egi_series else D("0")),
                opex=(opex_series[i] if opex_series else D("0")),
                noi=noi,
                debt_service=ds,
                phase=debt_service[i].phase.value,
                cfbt=cfbt,
                dscr=dscr,
            ))
            if y <= sale_year:
                dscr_series.append(dscr)

        # Exit value: buyers price off FORWARD NOI (sale_year + 1) when available.
        fwd_idx = sale_year if (exit_on_forward_noi and sale_year < n) else sale_year - 1
        exit_noi = noi_series[fwd_idx]
        exit_value = exit_noi / exit_cap
        net_sale = exit_value * (D("1") - costs_of_sale)
        loan_payoff = refi_loan if refi_loan is not None else D("0")
        net_sale_proceeds = net_sale - loan_payoff

        # Refi cash-out: when the agency refi loan exceeds the bridge payoff, the excess
        # (net of refi closing costs on the refi loan) is distributed to equity in refi_year.
        refi_cashout = D("0")
        if refi_loan is not None and bridge_loan is not None and refi_year is not None:
            gross = refi_loan - bridge_loan
            if gross > 0:
                refi_cashout = gross - (refi_loan * refi_cost_pct)

        # Levered equity cash-flow stream: -equity at t0, CFBT yrs 1..sale_year,
        # + refi cash-out in refi_year, + net sale proceeds in the sale year.
        flows: List[Decimal] = [-total_equity]
        for i in range(sale_year):
            cf = rows[i].cfbt
            if refi_year is not None and i + 1 == refi_year:
                cf = cf + refi_cashout
            if i + 1 == sale_year:
                cf = cf + net_sale_proceeds
            flows.append(cf)

        irr = D(str(npf.irr([float(f) for f in flows])))
        total_distributions = sum((f for f in flows[1:]), D("0"))
        equity_multiple = (total_distributions + total_equity) / total_equity if total_equity > 0 else D("0")
        # ^ distributions already net of equity outflow at t0; EM = total cash returned / equity in
        equity_multiple = sum((f for f in flows[1:]), D("0")) / total_equity if total_equity > 0 else D("0")

        coc_year1 = rows[0].cfbt / total_equity if total_equity > 0 else D("0")
        # stabilized CoC: average of post-renovation stabilized years up to sale (yrs 3..sale_year)
        stab_years = [r.cfbt for r in rows[2:sale_year]] or [rows[min(2, n - 1)].cfbt]
        coc_stab = (sum(stab_years, D("0")) / D(str(len(stab_years)))) / total_equity if total_equity > 0 else D("0")

        return ACQReturnResult(
            irr=irr,
            equity_multiple=equity_multiple,
            coc_year1=coc_year1,
            coc_stabilized=coc_stab,
            exit_value=exit_value,
            net_sale_proceeds=net_sale_proceeds,
            total_equity=total_equity,
            cash_flows=flows,
            dscr_series=dscr_series,
        )


# =============================================================================
# RETURN HURDLE (market tier base + risk premiums)
# =============================================================================

class HurdleCalculator:
    """Manual v2 §Return Hurdles + Risk Adjustments. Computes the adjusted IRR hurdle and
    the recommendation band from total premium bps."""

    BASE_MIDPOINT = {MarketTier.GATEWAY: D("0.15"), MarketTier.SECONDARY: D("0.175"), MarketTier.TERTIARY: D("0.20")}

    def reno_premium_bps(self, vintage_year: int, heavy: bool) -> int:
        if not heavy:
            return 0
        if vintage_year >= 2000:
            return 150
        if vintage_year >= 1980:
            return 188  # 175-200 midpoint
        return 250

    def occupancy_premium_bps(self, occ: Decimal) -> int:
        if occ >= D("0.85"):
            return 0
        if occ >= D("0.75"):
            return 100
        return 150

    def age_premium_bps(self, age: int) -> int:
        if age <= 20:
            return 0
        if age <= 30:
            return 50
        if age <= 40:
            return 100
        return 150

    def financing_premium_bps(self, floating_bridge: bool) -> int:
        return 88 if floating_bridge else 0  # 75-100 midpoint

    def compute(
        self,
        tier: MarketTier,
        vintage_year: int,
        current_occ: Decimal,
        property_age: int,
        heavy_reno: bool = True,
        floating_bridge: bool = False,
        market_cycle_bps: int = 0,
    ) -> HurdleResult:
        comps = {
            "renovation": self.reno_premium_bps(vintage_year, heavy_reno),
            "occupancy": self.occupancy_premium_bps(current_occ),
            "age": self.age_premium_bps(property_age),
            "financing": self.financing_premium_bps(floating_bridge),
            "market_cycle": market_cycle_bps,
        }
        total = sum(comps.values())
        base = self.BASE_MIDPOINT[tier]
        adjusted = base + D(total) / D("10000")
        if total < 200:
            rec = "PROCEED"
        elif total < 400:
            rec = "PROCEED WITH CAUTION"
        elif total < 600:
            rec = "REQUEST REPRICING"
        else:
            rec = "PASS"
        return HurdleResult(base, total, adjusted, rec, comps)
