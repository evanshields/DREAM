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


# =============================================================================
# WAVE-1 HARD GATES (Envy 3-way forensic — process-discipline floor)
# =============================================================================
# These are deterministic validators, not analytical models. They move the
# mechanical, error-prone checks (fee bounds, unit-count reconcile, named
# formula-bug sweep) out of "the human notices" and into "the engine asserts."
# The forensic proved each one prevents a defect that actually shipped:
#   - assert_fee_bounds      -> Fahd's unread 5% Esplanade acq fee (~$3M basis)
#   - UnitCountReconciler    -> Fahd's 244-unit parse (no status/use filter)
#   - formula_integrity_check-> reactive-only bug handling (S40, row-78 by luck)
# They are the autonomy floor: HOTL must not run unattended without them.


# ------------------------------------------------------------------------- #
# BL-03 — Fee/cost-cell bounds assertion (B45 acquisition fee)
# ------------------------------------------------------------------------- #

SENTINEL_ACQ_FEE = D("0.05")              # the EFB/Esplanade 5% template default
ACQ_FEE_BOUNDS = (D("0.005"), D("0.01"))  # ACQ rule: 0.5%-1.0% per size band


@dataclass
class FeeBoundsResult:
    ok: bool
    value: Decimal
    is_sentinel: bool
    reason: str


def assert_fee_bounds(
    acq_fee: Decimal,
    routing: str = "ACQ",
    override: bool = False,
) -> FeeBoundsResult:
    """Assert the acquisition fee is in-bounds for the deal routing.

    Fahd's B45 stayed at 0.05 (the EFB/Esplanade default) across 183 messages —
    never read, never overwritten — overstating acquisition basis by ~$3M on a
    $74M deal. On the ACQ route the rule is 0.5-1.0%; a 0.05 sentinel is the
    smoking gun of an unexamined template carryover.

    Rules (ACQ route, no override):
      - FAIL if acq_fee == 0.05 (the sentinel) — this is the carryover signal.
      - FAIL if acq_fee outside [0.005, 0.01].
    EFB route, or override=True, always passes (5% IS the EFB default).
    """
    fee = D(str(acq_fee))
    is_sentinel = fee == SENTINEL_ACQ_FEE
    if routing.upper() != "ACQ" or override:
        why = "override flag present" if override else f"{routing} route (no ACQ fee bound)"
        return FeeBoundsResult(ok=True, value=fee, is_sentinel=is_sentinel, reason=why)
    lo, hi = ACQ_FEE_BOUNDS
    if is_sentinel:
        return FeeBoundsResult(
            ok=False, value=fee, is_sentinel=True,
            reason=f"acq fee {fee} == 0.05 EFB/Esplanade template sentinel — unexamined "
                   f"carryover; ACQ must be {lo}-{hi}. Set an explicit override note to keep 5%.")
    if not (lo <= fee <= hi):
        return FeeBoundsResult(
            ok=False, value=fee, is_sentinel=False,
            reason=f"acq fee {fee} outside ACQ bounds [{lo}, {hi}] (0.5%-1.0% per size band)")
    return FeeBoundsResult(ok=True, value=fee, is_sentinel=False,
                           reason=f"acq fee {fee} within ACQ bounds [{lo}, {hi}]")


# ------------------------------------------------------------------------- #
# BL-01 + BL-09 — Rent-roll unit-count reconcile gate
# ------------------------------------------------------------------------- #

# Status values that still count as a unit (a unit exists whether or not it is
# leased). Non-residential / excluded segments are the ones that inflate counts.
NON_RESIDENTIAL_TOKENS = (
    "condo", "marina", "slip", "boat", "storage", "office", "retail",
    "commercial", "garage", "parking",
)


@dataclass
class UnitCountResult:
    counted: int                       # status+use-classified residential count
    summary_tab: Optional[int]         # the roll's own summary-tab total
    second_source: Optional[int]       # CoStar/ISG if available at parse time
    excluded_segments: List[str]       # non-residential / user-excluded segments detected
    reconciled: bool                   # count agrees with the best available source
    blocked: bool                      # HARD gate: refuse to populate the unit-mix S-cells
    single_source_warning: bool        # passed on the roll's own summary tab only (no 2nd source)
    reasons: List[str]


class UnitCountReconciler:
    """Classify-then-reconcile the rent-roll unit count before it lands in S22.

    Fahd's pandas read (header=5, all SQFT>0) counted 244 — including the condo +
    marina-slip rows the user explicitly said to exclude ("Just focus on EB5
    Multifamily part"). No status filter, no use filter, no second source. Evan
    and Dream independently got 214 (Dream validated vs the roll's own summary tab
    214u/188 occ/87.85%). The 30 phantom units (14%) inflated GPR, EGI, and every
    per-unit denominator.

    Locked behavior (Evan 2026-06-05 — "pass-with-flag on summary-tab match"):
      - second source present -> BLOCK if |counted - 2nd| / 2nd > tol.
      - else summary tab present -> pass within tol but set single_source_warning;
        BLOCK if it disagrees > tol.
      - BLOCK if a non-residential segment is detected but not excluded, or an
        explicit user exclusion is violated.
    B6 is the formula =S22, so the populator guards the S3:S21 unit-mix inputs that
    feed S22 — never B6 directly.
    """

    def reconcile(
        self,
        classified_units: List[Dict],          # [{"bedroom","status","use_type"|"segment", ...}]
        summary_tab_count: Optional[int] = None,
        second_source_count: Optional[int] = None,
        user_exclusions: Optional[List[str]] = None,
        tol: Decimal = D("0.02"),
    ) -> UnitCountResult:
        user_exclusions = [e.lower() for e in (user_exclusions or [])]
        reasons: List[str] = []
        excluded_segments: List[str] = []
        blocked = False

        def _segment(u: Dict) -> str:
            return str(u.get("use_type") or u.get("segment") or u.get("building") or "").lower()

        counted = 0
        for u in classified_units:
            seg = _segment(u)
            is_non_res = any(tok in seg for tok in NON_RESIDENTIAL_TOKENS)
            violates_user = any(ex in seg for ex in user_exclusions) if user_exclusions else False
            if is_non_res or violates_user:
                label = seg or "(unlabeled)"
                if label not in excluded_segments:
                    excluded_segments.append(label)
                # A detected-but-present non-residential/excluded segment is a hard block:
                # the roll mixes use types and the parse must not silently include them.
                blocked = True
                if violates_user:
                    reasons.append(f"segment '{label}' violates explicit user exclusion")
                else:
                    reasons.append(f"non-residential segment '{label}' present in roll — must be excluded")
                continue
            counted += 1

        def _off(a: int, b: int) -> Decimal:
            return abs(D(a) - D(b)) / D(b) if b else (D("0") if a == 0 else D("1"))

        reconciled = False
        single_source_warning = False
        if second_source_count is not None:
            off = _off(counted, second_source_count)
            if off > tol:
                blocked = True
                reasons.append(f"counted {counted} vs 2nd source {second_source_count} "
                               f"({float(off)*100:.1f}% > {float(tol)*100:.0f}% tol)")
            else:
                reconciled = True
                reasons.append(f"reconciled to 2nd source {second_source_count} "
                               f"({float(off)*100:.1f}% within tol)")
        elif summary_tab_count is not None:
            off = _off(counted, summary_tab_count)
            if off > tol:
                blocked = True
                reasons.append(f"counted {counted} vs roll summary tab {summary_tab_count} "
                               f"({float(off)*100:.1f}% > {float(tol)*100:.0f}% tol)")
            else:
                reconciled = True
                single_source_warning = True
                reasons.append(f"single-source WARNING: reconciled to roll's own summary tab "
                               f"{summary_tab_count} only (no independent 2nd source at parse time)")
        else:
            # No reconciliation source at all -> cannot validate -> block & escalate.
            blocked = True
            reasons.append("no reconciliation source (neither 2nd source nor summary tab) — "
                           "cannot validate unit count")

        return UnitCountResult(
            counted=counted,
            summary_tab=summary_tab_count,
            second_source=second_source_count,
            excluded_segments=excluded_segments,
            reconciled=reconciled,
            blocked=blocked,
            single_source_warning=single_source_warning,
            reasons=reasons,
        )


# ------------------------------------------------------------------------- #
# BL-07 — Named formula-integrity sweep (S40, B66, B67, rows 31-32, row 78)
# ------------------------------------------------------------------------- #

# The canonical 5 fragile cells from the Rayzor-derived templates. S40 and row-78
# are AUTO-PATCH (detect -> patch string -> printed -> human-confirm -> applied=true);
# the rest are verdict-only (flag for human, no mutation). Per Evan 2026-06-05.
AUTO_PATCH_CELLS = ("S40", "row78")


@dataclass
class FormulaVerdict:
    cell: str
    status: str            # "ok" | "bug"
    expected: str          # expected/canonical formula (or "" if none asserted)
    actual: str
    patch: str             # the patch to apply if status=="bug" and auto (else "")
    auto: bool             # True if in the auto-patch set


@dataclass
class FormulaAuditResult:
    verdicts: List[FormulaVerdict]
    patch_log: List[str]   # one printed line per cell verdict (PASS/PATCH ...)

    @property
    def any_bug(self) -> bool:
        return any(v.status == "bug" for v in self.verdicts)

    @property
    def auto_patches(self) -> List[FormulaVerdict]:
        return [v for v in self.verdicts if v.status == "bug" and v.auto and v.patch]


def _norm_formula(f: Optional[str]) -> str:
    return ("" if f is None else str(f)).replace(" ", "").upper()


def formula_integrity_check(formulas: Dict[str, str]) -> FormulaAuditResult:
    """Emit a NAMED PASS/PATCH verdict for each of the 5 fragile template cells,
    EVERY run — regardless of whether they surface downstream.

    Both humans fixed these reactively (Evan diagnosed row-78 only as a one-off
    #NUM! IRR symptom; Fahd fixed row78=D48 only as a comps-grid ref repair).
    Neither ran the canonical sweep, so success was by luck, not protocol.

    `formulas` is {cell -> actual formula string} read from the template by the
    orchestrator (the engine is pure — it does not open the workbook). Keys this
    function recognizes: "S40", "B66", "B67", "row31", "row32", "row78". Missing
    keys yield a verdict noting the cell was not read (status "ok", actual "").

    Auto-patch set (S40, row78): returns a `patch` string. The populator applies it
    ONLY when the spec marks it applied=true (printed-patch + human-confirm gate).
    The other three are verdict-only (flag for human; no patch).
    """
    verdicts: List[FormulaVerdict] = []
    patch_log: List[str] = []

    def _add(cell: str, status: str, expected: str, actual: str, patch: str, auto: bool):
        verdicts.append(FormulaVerdict(cell, status, expected, actual, patch, auto))
        tag = "PASS" if status == "ok" else ("PATCH(auto)" if auto and patch else "PATCH(flag)")
        detail = f" -> {patch}" if patch else (f" (expected {expected})" if expected and status == "bug" else "")
        patch_log.append(f"{cell}: {tag}{detail}")

    # --- S40 (auto): Other Income annualization. ships =U36, should be =U36*12 ---
    s40 = formulas.get("S40")
    s40n = _norm_formula(s40)
    if s40 is None:
        _add("S40", "ok", "=U36*12", "", "", auto=True)
    elif s40n == "=U36":
        _add("S40", "bug", "=U36*12", str(s40), "=U36*12", auto=True)
    elif "U36" in s40n and "*12" not in s40n and "U36*12" not in s40n:
        # any non-annualized reference to U36 (e.g. =U36+0) is the same defect class
        _add("S40", "bug", "=U36*12", str(s40), "=U36*12", auto=True)
    else:
        _add("S40", "ok", "=U36*12", str(s40), "", auto=True)

    # --- row78 (auto): Senior DSCR bridge->refi pointer ---
    # Buggy form points the DSCR denominator at the BRIDGE balance/DS past the refi
    # switch (zeroing / mis-stating Senior DSCR Y3+). The repointed form references
    # the refi debt service. We can't know the exact column layout per template, so
    # the patch is supplied by the orchestrator if it read one; otherwise we emit the
    # canonical repoint and let the populator's applied=true gate hold it.
    r78 = formulas.get("row78")
    r78n = _norm_formula(r78)
    if r78 is None:
        _add("row78", "ok", "<refi-DSCR pointer>", "", "", auto=True)
    elif "D48" in r78n or "BRIDGE" in r78n or r78n in ("=0", "0"):
        # bridge-pointer / comps-ref-repair / zeroed forms are all the known defect
        patch = formulas.get("row78_patch", "")  # orchestrator-supplied repoint, if read
        _add("row78", "bug", "<refi-DSCR pointer>", str(r78), patch, auto=True)
    else:
        _add("row78", "ok", "<refi-DSCR pointer>", str(r78), "", auto=True)

    # --- B66 (flag-only): combined LTV ---
    b66 = formulas.get("B66")
    expected_b66 = '=IFERROR(SUM(B52,B67)/B10,"N/A")'
    if b66 is None:
        _add("B66", "ok", expected_b66, "", "", auto=False)
    elif _norm_formula(b66) == _norm_formula(expected_b66):
        _add("B66", "ok", expected_b66, str(b66), "", auto=False)
    else:
        _add("B66", "bug", expected_b66, str(b66), "", auto=False)

    # --- B67 (flag-only): refi loan amount (INPUT in current templates) ---
    b67 = formulas.get("B67")
    if b67 is None:
        _add("B67", "ok", "<refi loan input>", "", "", auto=False)
    elif str(b67).startswith("="):
        # B67 should be an INPUT, not a formula; a formula here is suspicious -> flag
        _add("B67", "bug", "<refi loan input (not a formula)>", str(b67), "", auto=False)
    else:
        _add("B67", "ok", "<refi loan input>", str(b67), "", auto=False)

    # --- rows 31-32 (flag-only): refi P+I thresholds ---
    for key in ("row31", "row32"):
        r = formulas.get(key)
        if r is None:
            _add(key, "ok", "<refi P+I threshold>", "", "", auto=False)
        elif "B70" in _norm_formula(r) and "+B69" not in _norm_formula(r) and "B69" not in _norm_formula(r):
            # B70 (IO period) treated as an absolute year instead of relative to B69 (orig year)
            _add(key, "bug", "<refi P+I threshold relative to B69 orig year>", str(r), "", auto=False)
        else:
            _add(key, "ok", "<refi P+I threshold>", str(r), "", auto=False)

    return FormulaAuditResult(verdicts=verdicts, patch_log=patch_log)
