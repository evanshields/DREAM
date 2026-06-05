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

import math
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List, Dict, Optional, Callable
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


# =============================================================================
# PROPERTY TAX RANGE ESTIMATOR  (BL-13)
# Replaces the flat PP × ratio × millage point for ACQ deals with an
# assessor/CoStar-driven LOW / POINT / HIGH band.  The existing
# PropertyTaxCalculator (flat-ratio fallback) is NOT deleted.
#
# Forensic origin: references/06-property-tax.md §ACQ Property Tax +
#   §Florida Reassessment Specifics (Year-1 carry-over, 80% post-reassessment,
#   Save-Our-Homes cap resets at sale, millage pulled from CoStar).
# Manual v2: §State-Specific Reassessment — FL 65–80%, TX 60–70%, GA 40%.
# =============================================================================

@dataclass
class PropertyTaxRangeResult:
    """BL-13 output: LOW/HIGH/POINT tax range + audit trail.

    Field names are 1:1 with the property_tax_range schema node so the
    synthesis step serialises this dataclass directly — no remapping needed.

    low/point/high are Year-1 (or stabilized) ANNUAL tax figures in dollars.
    When used with PropertyTaxCalculator.project() the caller should substitute
    `point` as the Year-1 anchor; `low` and `high` are stress/sensitivity inputs
    for the IC narrative only.

    exemption_delta: annual tax saved if the deal converts to EFB (i.e. point - $0).
    Populated only when the caller passes efb_preview=True; else None.
    """
    low: Decimal
    high: Decimal
    point: Decimal
    basis: str                          # "county-method" | "flat-ratio"
    ratio_used: Decimal                 # assessment ratio at POINT
    assessed_value: Optional[Decimal]   # market-derived from agent-marketdata; None if flat-ratio
    millage: Decimal
    exemption_delta: Optional[Decimal]  # annual EFB savings preview; None unless efb_preview=True
    citation: str                       # source string per Universal Rule 7


class PropertyTaxRangeEstimator:
    """BL-13: ACQ property-tax range from an assessor/CoStar assessed-value input.

    Two paths:
    ─────────────────────────────────────────────────────────────────
    COUNTY-METHOD (primary): agent-marketdata supplies
      • assessed_value    — market-derived assessed value post-reassessment
      • millage           — pulled from CoStar (tax/assessed, NOT a state default)
      • fl_year1_tax      — for FL: the Year-1 carry-over bill (seller's last
                            assessment cycle; reassessment takes effect Year 2)
      The range comes from a ±ratio_band around the supplied assessed_value.
      For FL, Year-1 uses fl_year1_tax and Year-2+ uses assessed_value × millage,
      because the FL reassessment does NOT apply in the acquisition year
      (ref 06-property-tax.md §Florida Reassessment Specifics).

    FLAT-RATIO FALLBACK (default when assessed_value is None):
      Uses PropertyTaxCalculator.STATE_RATIO to derive point, and a ±band
      derived from the published range for that state (e.g. FL 65–80%).
      This is the documented fallback — caller should treat it as a stress band,
      not as a tight estimate.
    ─────────────────────────────────────────────────────────────────

    Florida specifics (hardcoded from the reference):
      • Year 1 : carry-over seller assessment × millage (NOT reassessed).
      • Year 2+: market-derived assessed value × millage.
      • Save Our Homes cap RESETS at sale — do NOT carry the seller's cap.
      • 80% is the county-appraiser midpoint for commercial multifamily
        (references/06-property-tax.md, example Orange County).

    The returned PropertyTaxRangeResult.point is the figure to feed
    PropertyTaxCalculator.project(year1_tax=point, ...) so it propagates
    to the S66-S71 projection cells.
    """

    # State ratio RANGES (low, midpoint/default, high) per 06-property-tax.md.
    # Used for both the flat-ratio fallback AND to build the ±band around a
    # county-method point.
    STATE_RATIO_RANGES: Dict[str, tuple] = {
        "FL": (D("0.65"), D("0.725"), D("0.80")),
        "TX": (D("0.60"), D("0.65"),  D("0.70")),
        "GA": (D("0.40"), D("0.40"),  D("0.40")),  # statutory flat in GA
    }
    # For states not in the table, use the "Default (uncertain)" cross-market range.
    DEFAULT_RATIO_RANGE = (D("0.65"), D("0.675"), D("0.70"))

    # Florida Year-2+ reassessment multiplier (commercial/multifamily)
    # per 06-property-tax.md §Florida Reassessment Specifics.
    FL_REASSESSMENT_FACTOR = D("0.80")

    def estimate(
        self,
        purchase_price: Decimal,
        state: str,
        millage: Decimal,
        assessed_value: Optional[Decimal] = None,
        fl_year1_tax: Optional[Decimal] = None,
        efb_preview: bool = False,
        ratio_override: Optional[Decimal] = None,
        citation: str = "references/06-property-tax.md (flat-ratio default)",
    ) -> PropertyTaxRangeResult:
        """Produce a LOW/POINT/HIGH annual tax range for a single projection year.

        Parameters
        ----------
        purchase_price:
            B10 acquisition price.
        state:
            Two-letter state code ("FL", "TX", "GA", etc.).
        millage:
            Tax rate pulled from CoStar (current_tax / current_assessed).
            Per 06-property-tax.md: NEVER use a state-default millage for FL.
        assessed_value:
            Market-derived post-reassessment assessed value supplied by
            agent-marketdata (county-method path).  None -> flat-ratio fallback.
        fl_year1_tax:
            For FL county-method: the Year-1 carry-over tax bill from the seller's
            last assessment cycle (from CoStar / tax bill).  If None and state=="FL"
            and assessed_value is supplied, the estimator derives Year-1 from the
            assessed_value × millage as a conservative proxy (may overstate Year 1).
        efb_preview:
            When True, populate exemption_delta = point (the annual tax saved if
            the deal converts to EFB at $0 ad valorem).  BL-04 companion.
        ratio_override:
            Caller-supplied assessment ratio override (e.g. from a direct assessor
            quote).  Overrides the STATE_RATIO_RANGES midpoint for POINT only;
            the LOW/HIGH band still uses the published state range endpoints.
        citation:
            Source string for the county assessed value / method (Universal Rule 7).
        """
        s = state.upper()
        lo_ratio, mid_ratio, hi_ratio = self.STATE_RATIO_RANGES.get(s, self.DEFAULT_RATIO_RANGE)

        if assessed_value is not None:
            # ── COUNTY-METHOD PATH ──────────────────────────────────────────
            basis = "county-method"
            ratio_used = ratio_override if ratio_override is not None else mid_ratio

            if s == "FL":
                # Year 1: carry-over seller bill (Save Our Homes does NOT protect buyer).
                # Year 2+: assessed_value × millage.
                # The POINT for the range uses Year-2 (the reassessed year), which is
                # what drives all holding-period projections.  Year-1 carry-over is the
                # supplied fl_year1_tax or estimated from assessed_value × millage as
                # a conservative fallback (the assessor's actual Y1 bill can be lower).
                point = assessed_value * millage
                if fl_year1_tax is not None:
                    # For the range: LOW = fl_year1_tax (Year-1 carry-over is often low),
                    # HIGH = full reassessment at the high state ratio.
                    # point stays at the county-method Year-2 figure.
                    low = fl_year1_tax
                    high = purchase_price * hi_ratio * millage
                else:
                    # No Year-1 carry-over supplied: conservative — use county assessed
                    # at the low ratio for LOW, high ratio for HIGH.
                    low = purchase_price * lo_ratio * millage
                    high = purchase_price * hi_ratio * millage
            else:
                # Non-FL county-method: band the supplied assessed_value using the
                # ratio range endpoints scaled to the same purchase_price.
                point = assessed_value * millage
                low = purchase_price * lo_ratio * millage
                high = purchase_price * hi_ratio * millage
        else:
            # ── FLAT-RATIO FALLBACK ─────────────────────────────────────────
            basis = "flat-ratio"
            ratio_used = ratio_override if ratio_override is not None else mid_ratio

            if s == "FL":
                # FL flat-ratio: use FL_REASSESSMENT_FACTOR (80%) as the midpoint per
                # the reference narrative (80% × PP is the Orange County typical),
                # but the state ratio range gives the band.
                ratio_used = ratio_override if ratio_override is not None else self.FL_REASSESSMENT_FACTOR
                point = purchase_price * ratio_used * millage
                low = purchase_price * lo_ratio * millage
                high = purchase_price * hi_ratio * millage
            else:
                point = purchase_price * ratio_used * millage
                low = purchase_price * lo_ratio * millage
                high = purchase_price * hi_ratio * millage

            assessed_value = None   # confirm null for schema serialisation

        # Defensive: ensure low <= point <= high.
        # For a genuinely flat state (GA statutory, lo==hi) keep low==point==high.
        # Otherwise guarantee a STRICT band around the point: a county assessed value can
        # coincide with PP x hi_ratio (collapsing high onto point), but real reassessment
        # carries upside/downside risk, so open a small headroom band (default +/-3%) when
        # the computed endpoints would otherwise touch the point.
        is_flat = (lo_ratio == hi_ratio)
        low = min(low, point)
        high = max(high, point)
        if not is_flat:
            band = D("0.03")
            if high <= point:
                high = point * (D("1") + band)
            if low >= point:
                low = point * (D("1") - band)

        exemption_delta = point if efb_preview else None

        return PropertyTaxRangeResult(
            low=low,
            high=high,
            point=point,
            basis=basis,
            ratio_used=ratio_used,
            assessed_value=assessed_value,
            millage=millage,
            exemption_delta=exemption_delta,
            citation=citation,
        )


# =============================================================================
# BL-19 — REPRICE SOLVER (goal-seek the purchase price that clears a return floor)
# =============================================================================
# Forensic origin: Envy Pompano Beach cleared the IRR/EM floor only around
# $56-57M vs the $74-75M ask. When a deal is BELOW hurdle, goal-seek the B10
# purchase price that makes the chosen return metric (IRR / equity multiple /
# min-DSCR / debt-yield) hit its floor, by RE-RUNNING the validated
# ACQCashFlowProjector at trial prices. The cash-flow / exit / IRR math is
# REUSED, never reimplemented — this class only searches over price.
#
# Surfacing is ADVISORY ONLY (CP-3 request-repricing ask). It NEVER auto-writes
# B10; the orchestrator stages reprice into headline_metrics for the memo/IC.
#
# Robustness contract (the task guard against non-monotone IRR curves):
#   - bracket [floor*ask, min(ask, ceiling*ask)] and verify the metric straddles
#     the target before searching;
#   - bisection (not secant) so a non-monotone region can't make the iterate
#     diverge — it always halves a valid bracket;
#   - a degenerate trial price (IRR = NaN from no sign change) is treated as
#     -1e18 (worst case), so the search is pushed away from it, never NaN-poisoned;
#   - max_iter hard cap; if the bracket never closes -> converged=False, no crash;
#   - if the metric clears even at the ceiling (current/marginal) -> clearing at
#     ceiling; if it can't clear even at the floor -> converged=False, clearing=None.


@dataclass
class RepriceResult:
    """BL-19 reprice signal. Mirrors the headline_metrics.reprice spec shape 1:1.

    clearing_price is the B10 purchase price that makes target_metric hit target_value
    (None if no clearing price within bounds). price_delta_pct = clearing/current - 1
    (the haircut the deal needs). converged=False flags 'no clearing price in range' —
    the deal cannot be repriced into the floor inside the searched band.
    """
    below_hurdle: bool
    target_metric: str
    target_value: Decimal
    current_value: Decimal
    current_price: Decimal
    clearing_price: Optional[Decimal]
    price_delta_pct: Optional[Decimal]
    iterations: int
    converged: bool
    reason: str = ""


def _reprice_metric_from_result(res: "ACQReturnResult", target_metric: str) -> Decimal:
    """Pull the goal-seek metric off an ACQReturnResult, NaN/Inf-safe.

    A NaN/Inf metric (degenerate cash flow — e.g. an absurd price with no sign change in the
    levered stream, which numpy_financial.irr returns as NaN) is mapped to -1e18 so the
    bisection treats that trial price as 'far below floor' and searches away from it, rather
    than propagating NaN into the bracket.
    """
    tm = target_metric.lower()
    if tm == "irr":
        v = res.irr
    elif tm in ("equity_multiple", "em"):
        v = res.equity_multiple
    elif tm == "dscr":
        v = min(res.dscr_series) if res.dscr_series else D("0")
    elif tm == "debt_yield":
        v = getattr(res, "debt_yield", None)
        if v is None:
            raise ValueError(
                "target_metric='debt_yield' needs a metric_extractor; ACQReturnResult "
                "has no debt_yield attribute")
    else:
        raise ValueError(f"unknown target_metric '{target_metric}'")
    try:
        fv = float(v)
        if v is None or math.isnan(fv) or math.isinf(fv):
            return D("-1e18")
    except (ValueError, TypeError, OverflowError):
        return D("-1e18")
    return D(str(v))


class RepriceSolver:
    """BL-19: goal-seek the purchase price that clears a return floor when a deal is below hurdle.

    Structure-agnostic: the caller supplies price_to_inputs(price) -> dict, a pure mapper from a
    trial purchase price to the FULL kwargs of ACQCashFlowProjector.project (re-sizing equity, the
    bridge/refi loans, etc. exactly as the synthesis flow does). The solver never touches the
    cash-flow math — it only re-runs the projector at trial prices and bisects on price.

    Reuses ACQCashFlowProjector / SeniorDebtCalculator via the callback; the validated Esplanade
    math is untouched (additive-only per the Wave-2 contract).
    """

    def solve(
        self,
        price_to_inputs: Callable[[Decimal], Dict],
        current_price: Decimal,
        target_metric: str = "irr",
        target_value: Decimal = D("0.15"),
        below_hurdle: Optional[bool] = None,
        hurdle_recommendation: Optional[str] = None,
        metric_extractor: Optional[Callable[["ACQReturnResult"], Decimal]] = None,
        price_floor_pct: Decimal = D("0.40"),
        price_ceiling_pct: Decimal = D("1.10"),
        tol: Decimal = D("0.0005"),
        max_iter: int = 60,
        bracket_expansions: int = 8,
        projector: Optional["ACQCashFlowProjector"] = None,
    ) -> RepriceResult:
        """Solve for the clearing price.

        below_hurdle resolution (first that applies):
          1) explicit below_hurdle argument;
          2) hurdle_recommendation in {'REQUEST REPRICING','PASS'} (from HurdleResult.recommendation);
          3) current metric < target_value.
        If not below hurdle, returns immediately (below_hurdle=False, clearing_price=None,
        converged=True) — there is nothing to reprice.

        price_floor_pct / price_ceiling_pct bound the search as fractions of current_price. The
        search bracket is [floor*price, min(price, ceiling*price)]; cheaper price -> higher return.
        bracket_expansions lets the floor drop further (x0.7 each time) if the floor price still
        doesn't clear, capped so a truly unreachable target terminates as converged=False.
        Pass metric_extractor to goal-seek on a metric not natively on ACQReturnResult (e.g.
        debt_yield), or to use a custom min-DSCR definition.
        """
        projector = projector or ACQCashFlowProjector()
        current_price = D(str(current_price))
        target_value = D(str(target_value))

        def metric_at(price: Decimal) -> Decimal:
            res = projector.project(**price_to_inputs(price))
            if metric_extractor is not None:
                v = metric_extractor(res)
                try:
                    fv = float(v)
                    if v is None or math.isnan(fv) or math.isinf(fv):
                        return D("-1e18")
                except (ValueError, TypeError, OverflowError):
                    return D("-1e18")
                return D(str(v))
            return _reprice_metric_from_result(res, target_metric)

        current_value = metric_at(current_price)

        # --- resolve below_hurdle ---
        if below_hurdle is None:
            if hurdle_recommendation is not None:
                below_hurdle = hurdle_recommendation.upper() in ("REQUEST REPRICING", "PASS")
            else:
                below_hurdle = current_value < target_value
        # Even with a non-repricing recommendation, fall through to the metric test so a
        # genuinely below-floor deal still gets a solve (advisory; never blocks).
        if below_hurdle is False and current_value < target_value and hurdle_recommendation is not None \
                and hurdle_recommendation.upper() not in ("REQUEST REPRICING", "PASS"):
            below_hurdle = True

        if not below_hurdle:
            return RepriceResult(
                below_hurdle=False, target_metric=target_metric, target_value=target_value,
                current_value=current_value, current_price=current_price,
                clearing_price=None, price_delta_pct=None, iterations=0, converged=True,
                reason="deal already clears the hurdle; no reprice needed",
            )

        # --- bracket the search: cheaper price => higher return ---
        lo = current_price * price_floor_pct
        hi = min(current_price, current_price * price_ceiling_pct)

        def cleared(price: Decimal) -> Decimal:
            return metric_at(price) - target_value

        iters = 0
        f_hi = cleared(hi); iters += 1
        f_lo = cleared(lo); iters += 1

        # expand the floor downward if even the floor price doesn't clear yet
        expansions = 0
        while f_lo < 0 and expansions < bracket_expansions and iters < max_iter:
            lo = lo * D("0.7")
            f_lo = cleared(lo); iters += 1
            expansions += 1

        # metric already clears at/above the ceiling price (current or marginal) -> clear there
        if f_hi >= 0:
            return RepriceResult(
                below_hurdle=True, target_metric=target_metric, target_value=target_value,
                current_value=current_value, current_price=current_price,
                clearing_price=hi, price_delta_pct=(hi / current_price - D("1")),
                iterations=iters, converged=True,
                reason="metric clears at/above the search ceiling (marginal/sensitivity-flat)",
            )

        # can't clear even at the floor price -> no solution in range
        if f_lo < 0:
            return RepriceResult(
                below_hurdle=True, target_metric=target_metric, target_value=target_value,
                current_value=current_value, current_price=current_price,
                clearing_price=None, price_delta_pct=None, iterations=iters, converged=False,
                reason=f"no clearing price within [{float(lo):,.0f}, {float(hi):,.0f}]; "
                       f"{target_metric} below {float(target_value)} even at the floor price",
            )

        # --- bisection on a valid bracket (f_lo >= 0 at the cheap end, f_hi < 0 at the dear end) ---
        clearing: Optional[Decimal] = None
        while iters < max_iter:
            mid = (lo + hi) / D("2")
            f_mid = cleared(mid); iters += 1
            if abs(f_mid) <= tol:
                clearing = mid
                break
            if f_mid >= 0:
                lo = mid
            else:
                hi = mid
            # price bracket collapsed tighter than 5 bps of the ask -> accept the cheap edge
            if (hi - lo) / current_price < D("0.0005"):
                clearing = lo
                break

        if clearing is None:
            return RepriceResult(
                below_hurdle=True, target_metric=target_metric, target_value=target_value,
                current_value=current_value, current_price=current_price,
                clearing_price=None, price_delta_pct=None, iterations=iters, converged=False,
                reason=f"bisection hit max_iter ({max_iter}) without converging within tol {float(tol)}",
            )

        return RepriceResult(
            below_hurdle=True, target_metric=target_metric, target_value=target_value,
            current_value=current_value, current_price=current_price,
            clearing_price=clearing, price_delta_pct=(clearing / current_price - D("1")),
            iterations=iters, converged=True,
            reason=f"cleared {target_metric} {float(target_value)} at {float(clearing):,.0f} "
                   f"({float(clearing / current_price - 1) * 100:.1f}% vs current price)",
        )


# =============================================================================
# WAVE-2 ADDITIONS (Epic C — wire built classes into synthesis + 3 small gates)
# =============================================================================
# Envy 3-way forensic, Wave 2. ADDITIVE ONLY — these do NOT touch the validated
# SeniorDebtCalculator / ACQCashFlowProjector / ExitCapTriangulator math. They:
#   - detect NOAH/EFB-structural and emit a routing RECOMMENDATION (BL-04, STOP at CP-1)
#   - net the interest reserve out of ramp-year DSCR so Y1 DSCR is realistic (BL-11)
#   - assert exit cap == HIGHEST method (BL-10), LTV formula integrity (BL-15),
#     and RUBS contra-sign + recovery-jump plausibility (BL-16)
# The Esplanade ground truth is protected: every helper is gated so a stabilized
# deal with no shortfall and a triangulation that already takes max() behaves
# EXACTLY as today (validated: reserve_adjusted_dscr is a no-op on Esplanade).


# ------------------------------------------------------------------------- #
# BL-04 — NOAH / EFB-structural detection + routing RECOMMENDATION
# ------------------------------------------------------------------------- #
# The Wave-2 synthesis already CALLS FourTierOptimizer.allocate() for the
# market-max GPR mix. This helper adds the missing detection step: per-bedroom,
# is the in-place rent so deep below the 80%-AMI ceiling that the asset is
# naturally-occurring affordable (NOAH) and an EFB four-tier (with $0 property
# tax) would likely be accretive? Per Evan's Envy methodology: in-place < 85% of
# the 80%-AMI ceiling on a bedroom means the affordable ceiling sits ABOVE
# in-place there, so converting that cohort gives up little/no rent while
# unlocking the tax exemption.
#
# LOCKED (Evan 2026-06-05, BL-04): the engine DETECTS and RECOMMENDS only. The
# fast path STOPS at CP-1 for a human glance (stop_at_cp1 is ALWAYS True); the
# engine NEVER auto-builds the EFB model. routing stays the Wave-0 value until a
# human flips it at CP-1.

NOAH_INPLACE_CEILING_RATIO = D("0.85")   # in-place < 85% of 80%-AMI ceiling => NOAH on that bedroom


@dataclass
class EFBRouteSignal:
    """BL-04 routing recommendation. Serializes 1:1 to meta.efb_route_signal."""
    noah_detected: bool
    efb_recommended: bool
    reason: str
    signals: List[str]
    stop_at_cp1: bool = True          # LOCKED: the fast path always halts here


def detect_noah(
    inplace_by_bedroom: Dict[str, Decimal],
    ami80_ceiling_by_bedroom: Dict[str, Decimal],
    ratio: Decimal = NOAH_INPLACE_CEILING_RATIO,
) -> Dict:
    """Per-bedroom NOAH test: in-place rent vs `ratio` x the 80%-AMI ceiling.

    A bedroom trips NOAH when its in-place rent is BELOW ratio x its 80%-AMI
    ceiling (default 85%) — i.e. the affordable ceiling sits comfortably above
    in-place, so an EFB conversion of that cohort gives up little or no rent.

    Forensic origin: the Envy run mentioned NOAH/HAP in prose but never quantified
    the in-place-to-AMI compression, so the EFB-accretion question never got an
    auditable answer. This makes it numeric and per-bedroom.

    Returns:
      {
        "noah": bool,                      # any bedroom tripped
        "by_bedroom": {br: {"inplace","ceiling","ratio","tripped"}},
        "tripped_bedrooms": [br, ...],
        "signals": [human-readable trigger per tripped bedroom],
      }
    Only bedrooms present in BOTH maps (and with a positive ceiling) are tested.
    """
    by_bedroom: Dict[str, Dict] = {}
    tripped: List[str] = []
    signals: List[str] = []
    for br, ceiling in ami80_ceiling_by_bedroom.items():
        if br not in inplace_by_bedroom:
            continue
        ceil = D(str(ceiling))
        if ceil <= 0:
            continue
        inplace = D(str(inplace_by_bedroom[br]))
        r = inplace / ceil
        is_trip = r < ratio
        by_bedroom[br] = {"inplace": inplace, "ceiling": ceil, "ratio": r, "tripped": is_trip}
        if is_trip:
            tripped.append(br)
            pct_below = (D("1") - r) * 100
            signals.append(
                f"{br}: in-place ${float(inplace):,.0f} is {float(pct_below):.0f}% below the "
                f"80%-AMI ceiling ${float(ceil):,.0f} (ratio {float(r):.2f} < {float(ratio):.2f}) "
                f"-> EFB four-tier likely accretive")
    return {
        "noah": bool(tripped),
        "by_bedroom": by_bedroom,
        "tripped_bedrooms": tripped,
        "signals": signals,
    }


def build_efb_route_signal(
    noah: Dict,
    hurdle: "HurdleResult",
    levered_irr: Optional[Decimal] = None,
    exemption_annual_tax: Optional[Decimal] = None,
    additional_signals: Optional[List[str]] = None,
) -> EFBRouteSignal:
    """Combine NOAH detection + the conventional-case hurdle result into a routing
    RECOMMENDATION (BL-04). EFB is recommended ONLY when the conventional case is
    weak AND the asset looks NOAH/exemption-bearing — never to short-circuit a
    deal that already clears as ACQ.

    Recommend EFB when ALL of:
      - NOAH detected (in-place deep below the 80%-AMI ceiling on >=1 bedroom), AND
      - the conventional case FAILS hurdles: HurdleResult.recommendation in
        {"REQUEST REPRICING","PASS"} OR (levered_irr is not None and
        levered_irr < hurdle.adjusted_hurdle), AND
      - there is a property-tax exemption to capture (exemption_annual_tax > 0)
        when that figure is supplied (if None, NOAH+hurdle alone suffice).

    stop_at_cp1 is ALWAYS True — the recommendation prompts the human glance; the
    engine never auto-builds the EFB four-tier (locked Evan 2026-06-05).
    """
    signals: List[str] = list(noah.get("signals", []))
    if additional_signals:
        signals.extend(additional_signals)

    conv_fails = hurdle.recommendation in ("REQUEST REPRICING", "PASS")
    if levered_irr is not None and D(str(levered_irr)) < hurdle.adjusted_hurdle:
        conv_fails = True
        signals.append(
            f"conventional levered IRR {float(levered_irr):.2%} < adjusted hurdle "
            f"{float(hurdle.adjusted_hurdle):.2%}")
    elif conv_fails:
        signals.append(f"conventional hurdle verdict: {hurdle.recommendation}")

    exemption_ok = True
    if exemption_annual_tax is not None:
        exemption_ok = D(str(exemption_annual_tax)) > 0
        if exemption_ok:
            signals.append(
                f"property-tax exemption capturable: ${float(exemption_annual_tax):,.0f}/yr "
                f"(~${float(D(str(exemption_annual_tax)) * 10):,.0f} over a 10-yr hold)")

    recommended = bool(noah.get("noah")) and conv_fails and exemption_ok

    if recommended:
        reason = (
            "conventional case fails hurdles AND in-place rents sit deep below the 80%-AMI "
            "ceiling with a capturable tax exemption -> EFB four-tier likely accretive. "
            "RECOMMENDATION ONLY: stop at CP-1 for a human glance; engine does not build EFB.")
    elif noah.get("noah") and not conv_fails:
        reason = (
            "NOAH signals present but the conventional case clears its hurdle -> stay ACQ; "
            "EFB not recommended (no need to give up market upside for the exemption).")
    elif conv_fails and not noah.get("noah"):
        reason = (
            "conventional case is weak but no NOAH/exemption signal -> reprice/pass as ACQ; "
            "EFB conversion would not be accretive here.")
    else:
        reason = "conventional case clears and no NOAH signal -> proceed as ACQ."

    return EFBRouteSignal(
        noah_detected=bool(noah.get("noah")),
        efb_recommended=recommended,
        reason=reason,
        signals=signals,
        stop_at_cp1=True,
    )


# ------------------------------------------------------------------------- #
# BL-11 — interest-reserve-aware DSCR (net of reserve draws in ramp years)
# ------------------------------------------------------------------------- #
# The validated ACQCashFlowProjector computes DSCR = NOI / DS straight. In a
# lease-up acquisition that produces a Year-1 DSCR of 0.41-0.77x that no IC would
# accept — because in reality the interest reserve (sized via InterestReserveSizer
# and funded from sources) pays the shortfall in those ramp years. This helper
# post-processes the engine's raw DSCR series, treating the reserve's shortfall
# years as reserve-covered: in a covered year the reserve tops NOI up to the
# floor, so the realistic DSCR is the floor, not the raw sub-1.0 figure. It NEVER
# mutates the projector and NEVER touches cash flows — exit value / IRR / EM are
# unchanged.
#
# GROUND-TRUTH GATE: if the reserve result has no shortfall years (a stabilized
# deal — Esplanade), this returns the raw DSCR series UNCHANGED (validated: on the
# Esplanade NOI series the reserve sizes to $0, shortfall_years == [], and the
# adjusted series is byte-identical to raw).


@dataclass
class ReserveAdjustedDSCR:
    raw_dscr: List[Decimal]            # the projector's straight NOI/DS series
    adjusted_dscr: List[Decimal]       # reserve-covered ramp years lifted to the floor
    covered_years: List[int]           # 1-indexed years the reserve paid into
    floor: Decimal                     # the DSCR floor the reserve underwrites


def reserve_adjusted_dscr(
    raw_dscr: List[Decimal],
    reserve: "InterestReserveResult",
) -> ReserveAdjustedDSCR:
    """Lift ramp-year DSCR to the reserve's covered floor (BL-11).

    For each shortfall year in `reserve.shortfall_years` (1-indexed), the modeled
    DSCR is max(raw, covered_dscr_floor): the funded reserve pays debt service in
    that year so operations are not asked to. Non-shortfall years pass through
    untouched (max() never lowers a year that already clears).

    GATE: if reserve.shortfall_years is empty (stabilized deal — e.g. Esplanade),
    adjusted_dscr IS raw_dscr (no lift), so the ground-truth result is unchanged.
    """
    floor = reserve.covered_dscr_floor
    covered = set(reserve.shortfall_years or [])
    adjusted: List[Decimal] = []
    for i, d in enumerate(raw_dscr):
        y = i + 1
        if y in covered:
            adjusted.append(max(D(str(d)), floor))
        else:
            adjusted.append(D(str(d)))
    return ReserveAdjustedDSCR(
        raw_dscr=list(raw_dscr),
        adjusted_dscr=adjusted,
        covered_years=sorted(covered),
        floor=floor,
    )


# ------------------------------------------------------------------------- #
# BL-10 — exit-cap gate: B79 must equal the HIGHEST of the 3 methods
# ------------------------------------------------------------------------- #
# ExitCapTriangulator.triangulate() already takes max(). This gate is the
# ASSERTION side: confirm the value STAGED for cell B79 (the INPUT cell) equals
# that max within tolerance, that the binding method resolves to the max, and
# that the entry+strategy method (always present) plus at least one other are
# documented. ok==False blocks the populator from writing a non-max exit cap —
# the defect this guards is silently writing a softer (lower) exit cap that
# embeds compression and inflates exit value.

EXIT_CAP_TOL = D("0.0001")             # 1 bp tolerance on the cap rate


@dataclass
class ExitCapGateResult:
    ok: bool
    methods: Dict[str, Optional[Decimal]]   # treasury_spread / comp_validation / entry_strategy
    selected: str
    max_cap: Decimal
    b79_value: Optional[Decimal]
    reason: str


def exit_cap_gate(
    result: "ExitCapResult",
    b79_value: Optional[Decimal],
    tol: Decimal = EXIT_CAP_TOL,
) -> ExitCapGateResult:
    """Assert the exit cap staged for B79 is the HIGHEST method (BL-10).

    FAILS (ok=False) when:
      - b79_value is None (nothing staged to cross-check), OR
      - |b79_value - result.exit_cap| > tol (a non-max cap is being written), OR
      - the binding_method does not resolve to the max among the run methods, OR
      - fewer than 2 methods are documented (entry+strategy alone is not a
        triangulation — at least Treasury-spread or a comp cap must accompany it).

    methods mirrors ExitCapResult: treasury_spread is None when no forward
    treasury was supplied (method_treasury comes back as D("0") in that case, so
    a 0 is treated as "not run"); comp_validation is None when no comp cap was
    given; entry_strategy is always present.
    """
    methods: Dict[str, Optional[Decimal]] = {
        "treasury_spread": (result.method_treasury
                            if result.method_treasury and result.method_treasury > 0 else None),
        "comp_validation": result.method_comp,
        "entry_strategy": result.method_entry_strategy,
    }
    run = {k: v for k, v in methods.items() if v is not None}
    documented = len(run)
    true_max = max(run.values())
    selected = result.binding_method
    # normalize binding_method ('entry+strategy' -> 'entry_strategy') for resolution
    sel_key = selected.replace("+", "_")
    selected_value = run.get(sel_key, result.exit_cap)

    reasons: List[str] = []
    ok = True
    if b79_value is None:
        ok = False
        reasons.append("no value staged for B79 to cross-check")
    elif abs(D(str(b79_value)) - result.exit_cap) > tol:
        ok = False
        reasons.append(
            f"B79 {float(b79_value):.4f} != max method {float(result.exit_cap):.4f} "
            f"(> {float(tol):.4f} tol) — writing a non-max exit cap")
    if abs(selected_value - true_max) > tol or abs(result.exit_cap - true_max) > tol:
        ok = False
        reasons.append(
            f"binding method '{selected}' ({float(selected_value):.4f}) does not resolve to the "
            f"highest method ({float(true_max):.4f})")
    if documented < 2:
        ok = False
        reasons.append(
            f"only {documented} method documented — exit cap needs >=2 of "
            f"(Treasury spread, comp validation, entry+strategy) to triangulate")
    if ok:
        reasons.append(
            f"B79 == highest of {documented} methods ({float(result.exit_cap):.4f}, "
            f"binding '{selected}')")
    return ExitCapGateResult(
        ok=ok,
        methods=methods,
        selected=selected,
        max_cap=result.exit_cap,
        b79_value=(D(str(b79_value)) if b79_value is not None else None),
        reason="; ".join(reasons),
    )


# ------------------------------------------------------------------------- #
# BL-15 — LTV gate: B52 must stay a FORMULA (=B51*B10), LTV ties to target
# ------------------------------------------------------------------------- #
# B51 is the INPUT LTV; B52 Loan Amount is a FORMULA (=B51*B10); B66 combined LTV
# is a FORMULA (=IFERROR(SUM(B52,B67)/B10,"N/A")). This gate asserts (a) the
# computed senior loan == target_ltv x price within tolerance, and (b) B52/B66
# read as formulas (not overwritten by a hardcoded loan amount). The populator
# already refuses to write formula cells; this is the assertion that FLAGS a
# literal where the formula belongs (a hardcoded B52 breaks combined LTV in B66).

LTV_TOL = D("0.005")                   # 0.5% tolerance on the implied LTV


@dataclass
class LTVGateResult:
    ok: bool
    target_ltv: Decimal
    computed_ltv: Decimal
    loan_amount: Optional[Decimal]
    b52_is_formula: bool
    b66_is_formula: bool
    reason: str


def ltv_gate(
    target_ltv: Decimal,
    purchase_price: Decimal,
    senior_loan: Decimal,
    b52_formula: Optional[str] = None,
    b66_formula: Optional[str] = None,
    tol: Decimal = LTV_TOL,
) -> LTVGateResult:
    """Assert LTV integrity (BL-15).

    computed_ltv = senior_loan / purchase_price (what B52's =B51*B10 should
    resolve to, divided back by price). FAILS (ok=False) when:
      - |computed_ltv - target_ltv| > tol (the senior loan does not tie to the
        input LTV — a hardcoded loan amount likely overwrote B52), OR
      - b52_formula is supplied and does NOT read as a formula (no leading '='),
        i.e. a literal sits where =B51*B10 belongs, OR
      - b66_formula is supplied and does NOT read as the combined-LTV formula.

    b52_formula / b66_formula are the actual cell-content strings the orchestrator
    read from the template (None = not read; the formula-content check is skipped
    but the LTV-tie check still runs). When a content string is not supplied the
    corresponding *_is_formula field defaults to True (assume intact, do not fail
    on missing read).
    """
    price = D(str(purchase_price))
    computed = (D(str(senior_loan)) / price) if price > 0 else D("0")
    target = D(str(target_ltv))

    def _is_formula(s: Optional[str]) -> Optional[bool]:
        if s is None:
            return None
        return str(s).strip().startswith("=")

    b52_is_formula = _is_formula(b52_formula)
    b66_is_formula = _is_formula(b66_formula)

    reasons: List[str] = []
    ok = True
    if abs(computed - target) > tol:
        ok = False
        reasons.append(
            f"computed LTV {float(computed):.4f} != target {float(target):.4f} "
            f"(> {float(tol):.4f} tol) — senior loan ${float(senior_loan):,.0f} does not tie to "
            f"B51*B10; a hardcoded loan amount may have overwritten B52")
    if b52_is_formula is False:
        ok = False
        reasons.append(
            f"B52 reads as a LITERAL ('{b52_formula}') where the =B51*B10 formula belongs — "
            f"hardcoded loan amount breaks combined LTV (B66)")
    if b66_is_formula is False:
        ok = False
        reasons.append(f"B66 reads as a LITERAL ('{b66_formula}') where the combined-LTV formula belongs")
    if ok:
        reasons.append(
            f"computed LTV {float(computed):.4f} ties to target {float(target):.4f}; "
            f"B52/B66 formula integrity intact")
    return LTVGateResult(
        ok=ok,
        target_ltv=target,
        computed_ltv=computed,
        loan_amount=(D(str(senior_loan)) if senior_loan is not None else None),
        b52_is_formula=bool(b52_is_formula) if b52_is_formula is not None else True,
        b66_is_formula=bool(b66_is_formula) if b66_is_formula is not None else True,
        reason="; ".join(reasons),
    )


# ------------------------------------------------------------------------- #
# BL-16 — RUBS sign + recovery-jump plausibility (S54 utility reimbursements)
# ------------------------------------------------------------------------- #
# S54 Utility Reimbursements is an INPUT entered NEGATIVE (contra-expense). A
# positive booking double-counts revenue. And the modeled RUBS recovery ratio
# (UW reimbursement / UW utility expense) must not jump implausibly vs the T-12
# actual recovery — an unjustified jump manufactures NOI. Default tolerance is a
# 15pp band (per the spec); pass a tighter value (e.g. 10) for stricter screening.
# Only an UPWARD jump beyond the band trips the gate — recovery falling vs T-12
# is always plausible.

RUBS_MAX_JUMP_PP = D("15")             # spec default; upward recovery jump above this trips unless justified


@dataclass
class RUBSSignResult:
    ok: bool
    reimbursement_value: Decimal
    is_negative: bool
    recovery_pct: Decimal
    t12_recovery_pct: Optional[Decimal]
    jump_pp: Decimal
    max_jump_pp: Decimal
    reason: str


def rubs_sign_gate(
    reimbursement_value: Decimal,       # value staged for S54 (must be <= 0)
    uw_utility_expense: Decimal,        # UW gross owner-paid utilities (positive)
    t12_reimbursement: Optional[Decimal] = None,   # T-12 actual reimbursement (signed; abs used)
    t12_utility_expense: Optional[Decimal] = None, # T-12 actual gross utilities (positive)
    max_jump_pp: Decimal = RUBS_MAX_JUMP_PP,
    justification: str = "",
) -> RUBSSignResult:
    """Assert S54 is a NEGATIVE contra-expense and the RUBS recovery jump vs T-12
    is plausible (BL-16).

    FAILS (ok=False) when:
      - reimbursement_value > 0 (positive RUBS double-counts — must be contra), OR
      - the modeled recovery ratio jumps more than max_jump_pp percentage points
        ABOVE the T-12 actual recovery and no justification note is supplied.

    recovery_pct = |reimbursement_value| / uw_utility_expense.
    t12_recovery_pct = |t12_reimbursement| / t12_utility_expense (None if either
    T-12 figure is missing — then only the sign check applies and jump_pp = 0).
    A negative jump (recovery falling vs T-12) is always plausible — only an
    UPWARD jump beyond the band trips the gate.
    """
    val = D(str(reimbursement_value))
    is_negative = val <= 0
    uw_util = D(str(uw_utility_expense))
    recovery = (abs(val) / uw_util) if uw_util > 0 else D("0")

    t12_recovery: Optional[Decimal] = None
    if t12_reimbursement is not None and t12_utility_expense is not None:
        t12_util = D(str(t12_utility_expense))
        if t12_util > 0:
            t12_recovery = abs(D(str(t12_reimbursement))) / t12_util

    if t12_recovery is not None:
        jump_pp = (recovery - t12_recovery) * 100
    else:
        jump_pp = D("0")

    reasons: List[str] = []
    ok = True
    if not is_negative:
        ok = False
        reasons.append(
            f"S54 {float(val):,.0f} is POSITIVE — utility reimbursements must be booked "
            f"NEGATIVE (contra-expense); a positive value double-counts revenue")
    # only an UPWARD jump beyond the band trips (recovery falling is always fine)
    if jump_pp > D(str(max_jump_pp)) and not justification:
        ok = False
        reasons.append(
            f"RUBS recovery jumps +{float(jump_pp):.0f}pp (UW {float(recovery)*100:.0f}% vs "
            f"T-12 {float(t12_recovery)*100:.0f}%) > {float(max_jump_pp):.0f}pp band with no "
            f"justification — manufactures NOI; requires a documented op plan (e.g. submetering)")
    if ok:
        if jump_pp > D(str(max_jump_pp)) and justification:
            reasons.append(
                f"recovery jump +{float(jump_pp):.0f}pp justified: {justification}")
        else:
            reasons.append(
                f"S54 negative contra; recovery {float(recovery)*100:.0f}% "
                + (f"({float(jump_pp):+.0f}pp vs T-12) within band" if t12_recovery is not None
                   else "(no T-12 baseline; sign check only)"))
    return RUBSSignResult(
        ok=ok,
        reimbursement_value=val,
        is_negative=is_negative,
        recovery_pct=recovery,
        t12_recovery_pct=t12_recovery,
        jump_pp=jump_pp,
        max_jump_pp=D(str(max_jump_pp)),
        reason="; ".join(reasons),
    )
