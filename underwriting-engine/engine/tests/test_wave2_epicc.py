"""
Wave-2 Epic C gates — pytest test suite.

Covers BL-04 (NOAH detection + EFB routing recommendation), BL-11 (reserve-adjusted
DSCR — lease-up ramp years and Esplanade ground-truth pass-through), BL-12 (lease-up
ramp is data-derived), BL-10 (exit-cap gate blocks non-max B79), BL-15 (LTV gate flags
literal B52 + asserts LTV ties to target), BL-16 (RUBS sign + recovery-jump plausibility).

Forensic origin: Envy 3-way forensic Wave-2 backlog (2026-06-05 locked decisions).
Style: matches engine/tests/ conventions (Decimal, rel(), sys.path shim, import as ax).
"""
import os
import sys
from decimal import Decimal as D

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import acq_engine as ax


def rel(a, b):
    """Relative error helper — mirrors test_acq_esplanade.py."""
    return abs(float(a) - float(b)) / abs(float(b)) if b else abs(float(a))


# =============================================================================
# BL-04 — NOAH detection + EFB routing recommendation
# =============================================================================

class TestDetectNoah:
    """detect_noah: per-bedroom NOAH test (in-place < 85% of 80%-AMI ceiling)."""

    def _ceilings(self):
        return {
            "1BR": D("1791"),
            "2BR": D("2140"),
            "3BR": D("2467"),
        }

    def test_tripped_when_inplace_below_85_pct_of_ceiling(self):
        # 1BR in-place $1350 / ceiling $1791 = 0.754 — well below 0.85 -> NOAH
        inplace = {"1BR": D("1350"), "2BR": D("2050")}
        result = ax.detect_noah(inplace, self._ceilings())
        assert result["noah"] is True
        assert "1BR" in result["tripped_bedrooms"]
        assert result["by_bedroom"]["1BR"]["tripped"] is True

    def test_not_tripped_when_inplace_above_85_pct(self):
        # 1BR in-place $1550 / ceiling $1791 = 0.866 — above 0.85 -> no trip
        inplace = {"1BR": D("1550"), "2BR": D("2000"), "3BR": D("2200")}
        result = ax.detect_noah(inplace, self._ceilings())
        assert result["noah"] is False
        assert result["tripped_bedrooms"] == []

    def test_boundary_at_exactly_85_pct_does_not_trip(self):
        # ratio == 0.85 exactly: the test is strict <, so 0.85 should NOT trip
        ceiling = D("2000")
        inplace = {"2BR": ceiling * D("0.85")}
        ceilings = {"2BR": ceiling}
        result = ax.detect_noah(inplace, ceilings)
        assert result["noah"] is False

    def test_just_below_85_pct_trips(self):
        ceiling = D("2000")
        inplace = {"2BR": ceiling * D("0.84")}
        ceilings = {"2BR": ceiling}
        result = ax.detect_noah(inplace, ceilings)
        assert result["noah"] is True

    def test_missing_bedroom_in_inplace_is_skipped(self):
        # 3BR has no in-place entry -> skipped, 1BR trips
        inplace = {"1BR": D("1200")}
        result = ax.detect_noah(inplace, self._ceilings())
        assert "1BR" in result["tripped_bedrooms"]
        assert "3BR" not in result["tripped_bedrooms"]

    def test_zero_ceiling_bedroom_is_skipped(self):
        inplace = {"1BR": D("1200"), "2BR": D("500")}
        ceilings = {"1BR": D("1791"), "2BR": D("0")}
        result = ax.detect_noah(inplace, ceilings)
        # 2BR has a zero ceiling -> skip; 1BR still trips
        assert "2BR" not in result["tripped_bedrooms"]

    def test_signals_contain_human_readable_text(self):
        inplace = {"1BR": D("1200")}
        ceilings = {"1BR": D("1791")}
        result = ax.detect_noah(inplace, ceilings)
        assert result["signals"], "expected at least one signal string"
        sig = result["signals"][0]
        assert "1BR" in sig
        assert "80%-AMI" in sig or "ceiling" in sig.lower()

    def test_multiple_bedrooms_can_trip_simultaneously(self):
        inplace = {"1BR": D("1200"), "2BR": D("1500"), "3BR": D("1800")}
        ceilings = {"1BR": D("1791"), "2BR": D("2140"), "3BR": D("2467")}
        result = ax.detect_noah(inplace, ceilings)
        assert len(result["tripped_bedrooms"]) == 3


class TestBuildEfbRouteSignal:
    """build_efb_route_signal: routing recommendation logic + BL-04 stop_at_cp1 lock."""

    def _weak_hurdle(self):
        """A HurdleResult that fails (REQUEST REPRICING) to trigger the recommendation."""
        return ax.HurdleCalculator().compute(
            tier=ax.MarketTier.TERTIARY, vintage_year=1975, current_occ=D("0.70"),
            property_age=50, heavy_reno=True, floating_bridge=True,
        )

    def _strong_hurdle(self):
        """A HurdleResult that passes (PROCEED) — conventional case clears."""
        return ax.HurdleCalculator().compute(
            tier=ax.MarketTier.SECONDARY, vintage_year=2007, current_occ=D("0.90"),
            property_age=19, heavy_reno=False, floating_bridge=False,
        )

    def _noah_result(self, trips=True):
        if trips:
            inplace = {"1BR": D("1200"), "2BR": D("1500")}
        else:
            inplace = {"1BR": D("1700"), "2BR": D("2050")}
        ceilings = {"1BR": D("1791"), "2BR": D("2140")}
        return ax.detect_noah(inplace, ceilings)

    def test_stop_at_cp1_is_always_true(self):
        """BL-04 LOCKED: stop_at_cp1 must be True regardless of recommendation."""
        hurdle = self._strong_hurdle()
        sig = ax.build_efb_route_signal(
            noah=self._noah_result(trips=False),
            hurdle=hurdle,
        )
        assert sig.stop_at_cp1 is True

    def test_stop_at_cp1_is_true_even_when_efb_recommended(self):
        hurdle = self._weak_hurdle()
        sig = ax.build_efb_route_signal(
            noah=self._noah_result(trips=True),
            hurdle=hurdle,
            exemption_annual_tax=D("400000"),
        )
        assert sig.efb_recommended is True
        assert sig.stop_at_cp1 is True  # LOCKED — never bypassed

    def test_efb_recommended_when_noah_plus_fails_hurdle_plus_exemption(self):
        hurdle = self._weak_hurdle()
        sig = ax.build_efb_route_signal(
            noah=self._noah_result(trips=True),
            hurdle=hurdle,
            exemption_annual_tax=D("350000"),
        )
        assert sig.noah_detected is True
        assert sig.efb_recommended is True
        assert sig.reason  # non-empty human-readable reason

    def test_efb_not_recommended_when_conventional_clears(self):
        """NOAH signals present but conventional ACQ clears -> stay ACQ."""
        hurdle = self._strong_hurdle()
        assert hurdle.recommendation == "PROCEED"
        sig = ax.build_efb_route_signal(
            noah=self._noah_result(trips=True),
            hurdle=hurdle,
            exemption_annual_tax=D("350000"),
        )
        assert sig.efb_recommended is False
        assert sig.noah_detected is True

    def test_efb_not_recommended_when_no_noah(self):
        """Conventional weak but no NOAH -> reprice/pass as ACQ, not EFB."""
        hurdle = self._weak_hurdle()
        sig = ax.build_efb_route_signal(
            noah=self._noah_result(trips=False),
            hurdle=hurdle,
            exemption_annual_tax=D("350000"),
        )
        assert sig.efb_recommended is False
        assert sig.noah_detected is False

    def test_efb_not_recommended_when_no_exemption(self):
        """NOAH + weak hurdle but zero exemption -> no recommendation."""
        hurdle = self._weak_hurdle()
        sig = ax.build_efb_route_signal(
            noah=self._noah_result(trips=True),
            hurdle=hurdle,
            exemption_annual_tax=D("0"),
        )
        assert sig.efb_recommended is False

    def test_levered_irr_below_hurdle_triggers_conv_fails(self):
        """levered_irr < adjusted_hurdle should count as conventional fail."""
        hurdle = self._strong_hurdle()  # hurdle says PROCEED
        # but pass an IRR that is explicitly below the adjusted hurdle
        low_irr = hurdle.adjusted_hurdle - D("0.05")
        sig = ax.build_efb_route_signal(
            noah=self._noah_result(trips=True),
            hurdle=hurdle,
            levered_irr=low_irr,
            exemption_annual_tax=D("350000"),
        )
        # conventional fails via the levered_irr path even though recommendation said PROCEED
        assert sig.efb_recommended is True
        assert any("IRR" in s or "irr" in s.lower() for s in sig.signals)

    def test_signal_not_empty_when_efb_recommended(self):
        hurdle = self._weak_hurdle()
        sig = ax.build_efb_route_signal(
            noah=self._noah_result(trips=True),
            hurdle=hurdle,
            exemption_annual_tax=D("400000"),
        )
        assert len(sig.signals) > 0

    def test_additional_signals_are_appended(self):
        hurdle = self._strong_hurdle()
        extra = ["bond takeout signal from OM page 3"]
        sig = ax.build_efb_route_signal(
            noah=self._noah_result(trips=False),
            hurdle=hurdle,
            additional_signals=extra,
        )
        assert any("bond" in s for s in sig.signals)


# =============================================================================
# BL-11 — reserve-adjusted DSCR
# =============================================================================

class TestReserveAdjustedDscr:
    """reserve_adjusted_dscr: ramp-year DSCR lifted to floor; stabilized pass-through."""

    def _make_reserve(self, shortfall_years, floor=D("1.15"), reserve_sized=D("500000")):
        return ax.InterestReserveResult(
            shortfall_years=shortfall_years,
            gross_shortfall=reserve_sized / D("1.30"),
            buffer=D("1.30"),
            reserve_sized=reserve_sized,
            covered_dscr_floor=floor,
        )

    def test_shortfall_years_lifted_to_floor(self):
        raw_dscr = [D("0.55"), D("0.82"), D("1.18"), D("1.25"), D("1.30")]
        reserve = self._make_reserve(shortfall_years=[1, 2], floor=D("1.15"))
        result = ax.reserve_adjusted_dscr(raw_dscr, reserve)
        # Year 1: 0.55 < floor -> lifted to 1.15
        assert result.adjusted_dscr[0] == D("1.15")
        # Year 2: 0.82 < floor -> lifted to 1.15
        assert result.adjusted_dscr[1] == D("1.15")
        # Year 3: 1.18 > floor -> unchanged
        assert result.adjusted_dscr[2] == D("1.18")
        assert result.covered_years == [1, 2]

    def test_year_above_floor_in_covered_set_is_not_lowered(self):
        """max() ensures a ramp year that already clears the floor is never lowered."""
        raw_dscr = [D("1.20"), D("1.10")]
        reserve = self._make_reserve(shortfall_years=[1, 2], floor=D("1.15"))
        result = ax.reserve_adjusted_dscr(raw_dscr, reserve)
        # Year 1: 1.20 > floor -> stays 1.20, NOT lowered to 1.15
        assert result.adjusted_dscr[0] == D("1.20")
        # Year 2: 1.10 < floor -> lifted to 1.15
        assert result.adjusted_dscr[1] == D("1.15")

    def test_stabilized_deal_no_shortfall_is_passthrough(self):
        """BL-11 ground-truth gate: empty shortfall_years -> adjusted == raw (Esplanade pattern)."""
        raw_dscr = [D("1.226"), D("1.329"), D("1.414"), D("1.487"), D("1.538"), D("1.348"), D("1.394")]
        reserve = ax.InterestReserveResult(
            shortfall_years=[],
            gross_shortfall=D("0"),
            buffer=D("1.30"),
            reserve_sized=D("0"),
            covered_dscr_floor=D("1.15"),
        )
        result = ax.reserve_adjusted_dscr(raw_dscr, reserve)
        assert result.covered_years == []
        assert result.adjusted_dscr == result.raw_dscr
        for adj, raw in zip(result.adjusted_dscr, raw_dscr):
            assert adj == raw, f"stabilized passthrough: {adj} != {raw}"

    def test_floor_field_matches_reserve_covered_dscr_floor(self):
        raw_dscr = [D("0.80"), D("1.20")]
        reserve = self._make_reserve(shortfall_years=[1], floor=D("1.20"))
        result = ax.reserve_adjusted_dscr(raw_dscr, reserve)
        assert result.floor == D("1.20")

    def test_esplanade_noi_series_zero_reserve_unchanged(self):
        """End-to-end: size() on the Esplanade stabilized NOI -> reserve_sized==0 ->
        adjusted DSCR series identical to raw (protects the 22.51% / 2.72 ground truth)."""
        from acq_engine import (
            LoanTerms, SeniorDebtCalculator, InterestReserveSizer,
        )
        NOI_SERIES = [D(str(v)) for v in
            [2387932, 2563041, 2742167, 2883487, 2983197, 3134540, 3241781, 3352240, 3466013, 3583198]]
        terms = LoanTerms(
            bridge_loan=D("23800000"), bridge_rate=D("0.08"), bridge_io_years=2,
            refi_loan=D("31944864"), refi_rate=D("0.06"), refi_io_years=3,
            refi_amort_years=30, refi_year=2, servicing_spread=D("0.0116"),
        )
        ds = SeniorDebtCalculator().build(terms, years=10)
        reserve = InterestReserveSizer().size(NOI_SERIES, ds, dscr_floor=D("1.15"))
        assert reserve.shortfall_years == [], "Esplanade is stabilized — no shortfall years"
        assert reserve.reserve_sized == D("0")
        # The adjusted series must be a no-op
        raw_dscr = [noi / dsy.debt_service for noi, dsy in zip(NOI_SERIES[:7], ds[:7])]
        result = ax.reserve_adjusted_dscr(raw_dscr, reserve)
        for adj, raw in zip(result.adjusted_dscr, raw_dscr):
            assert adj == raw, f"Esplanade passthrough: {adj} != {raw}"


# =============================================================================
# BL-12 — lease-up ramp is data-derived (changes with vacancy curve)
# =============================================================================

class TestLeaseUpRampDataDerived:
    """LeaseUpRamp.noi_series: the ramp is driven by the supplied vacancy/concession curves."""

    def test_ramp_is_monotone_increasing_through_stabilization(self):
        ramp = ax.LeaseUpRamp().noi_series(
            stabilized_noi=D("2627565"), stabilized_egi=D("6599826"),
            vacancy_curve=[D("0.18"), D("0.12"), D("0.08"), D("0.08")],
            concession_curve=[D("0.07"), D("0.03"), D("0.01"), D("0.01")],
            stabilized_vacancy=D("0.08"), stabilized_concession=D("0.01"), years=6,
        )
        assert ramp[0] < ramp[1] < ramp[2]  # ramps up through the lease-up period

    def test_ramp_changes_when_vacancy_curve_changes(self):
        """BL-12 core: output must differ when the forensic vacancy curve changes."""
        kwargs = dict(
            stabilized_noi=D("2627565"), stabilized_egi=D("6599826"),
            concession_curve=[D("0.03"), D("0.01"), D("0.01")],
            stabilized_vacancy=D("0.08"), stabilized_concession=D("0.01"), years=6,
        )
        ramp_tight = ax.LeaseUpRamp().noi_series(
            vacancy_curve=[D("0.12"), D("0.09"), D("0.08")], **kwargs,
        )
        ramp_deep = ax.LeaseUpRamp().noi_series(
            vacancy_curve=[D("0.25"), D("0.15"), D("0.08")], **kwargs,
        )
        # deeper vacancy in early years -> lower NOI in those years
        assert ramp_tight[0] > ramp_deep[0], "tight vacancy should yield higher Y1 NOI"
        assert ramp_tight[1] > ramp_deep[1], "tight vacancy should yield higher Y2 NOI"

    def test_ramp_changes_when_concession_curve_changes(self):
        kwargs = dict(
            stabilized_noi=D("2627565"), stabilized_egi=D("6599826"),
            vacancy_curve=[D("0.10"), D("0.08"), D("0.08")],
            stabilized_vacancy=D("0.08"), stabilized_concession=D("0.01"), years=4,
        )
        ramp_low_conc = ax.LeaseUpRamp().noi_series(
            concession_curve=[D("0.01"), D("0.01"), D("0.01")], **kwargs,
        )
        ramp_high_conc = ax.LeaseUpRamp().noi_series(
            concession_curve=[D("0.08"), D("0.04"), D("0.01")], **kwargs,
        )
        assert ramp_low_conc[0] > ramp_high_conc[0], "low concessions should yield higher Y1 NOI"

    def test_ramp_stabilizes_and_then_grows(self):
        """After the vacancy curve hits the stabilized level, NOI should grow with inflation."""
        ramp = ax.LeaseUpRamp().noi_series(
            stabilized_noi=D("2627565"), stabilized_egi=D("6599826"),
            vacancy_curve=[D("0.15"), D("0.10"), D("0.08"), D("0.08")],
            concession_curve=[D("0.06"), D("0.03"), D("0.01"), D("0.01")],
            stabilized_vacancy=D("0.08"), stabilized_concession=D("0.01"),
            growth=D("0.025"), years=8,
        )
        # Post-stabilization years should grow
        assert ramp[4] > ramp[3], "NOI should grow after stabilization"
        assert ramp[7] > ramp[4], "NOI continues to grow in later years"

    def test_ramp_length_matches_requested_years(self):
        ramp = ax.LeaseUpRamp().noi_series(
            stabilized_noi=D("2000000"), stabilized_egi=D("5000000"),
            vacancy_curve=[D("0.10"), D("0.08")],
            concession_curve=[D("0.02"), D("0.01")],
            years=10,
        )
        assert len(ramp) == 10


# =============================================================================
# BL-10 — exit-cap gate: B79 must equal the HIGHEST method
# =============================================================================

class TestExitCapGate:
    """exit_cap_gate: B79 must equal ExitCapTriangulator max; ok=False blocks populator."""

    def _triangulate(self, going_in=D("0.0702")):
        return ax.ExitCapTriangulator().triangulate(
            going_in_cap=going_in,
            strategy="value_add",
            forward_treasury=D("0.045"),
            agency_spread=D("0.0150"),
            neg_leverage_buffer=D("0.0075"),
        )

    def test_ok_when_b79_equals_max(self):
        result = self._triangulate()
        gate = ax.exit_cap_gate(result, b79_value=result.exit_cap)
        assert gate.ok is True
        assert gate.max_cap == result.exit_cap

    def test_fails_when_b79_is_none(self):
        result = self._triangulate()
        gate = ax.exit_cap_gate(result, b79_value=None)
        assert gate.ok is False
        assert "no value staged" in gate.reason.lower() or "b79" in gate.reason.lower()

    def test_fails_when_b79_is_softer_lower_cap(self):
        """Writing a lower (non-max) exit cap to B79 is the defect this guards."""
        result = self._triangulate()
        # Stage a value 30bp below the max — simulates a softened exit cap
        soft_cap = result.exit_cap - D("0.003")
        gate = ax.exit_cap_gate(result, b79_value=soft_cap)
        assert gate.ok is False
        assert "non-max" in gate.reason.lower() or "b79" in gate.reason.lower()

    def test_fails_when_b79_is_higher_than_max(self):
        """Even a higher cap than the triangulator's max should fail (wrong value)."""
        result = self._triangulate()
        gate = ax.exit_cap_gate(result, b79_value=result.exit_cap + D("0.005"))
        assert gate.ok is False

    def test_within_tolerance_passes(self):
        result = self._triangulate()
        # 0.5bp rounding noise (< 1bp default tol) should still pass
        gate = ax.exit_cap_gate(result, b79_value=result.exit_cap + D("0.00005"))
        assert gate.ok is True

    def test_fails_when_only_one_method_documented(self):
        """A triangulation with only entry+strategy (no treasury, no comp) is not a triangulation."""
        solo_result = ax.ExitCapTriangulator().triangulate(
            going_in_cap=D("0.07"),
            strategy="value_add",
            # no forward_treasury, no comp_implied_cap -> entry+strategy only
        )
        gate = ax.exit_cap_gate(solo_result, b79_value=solo_result.exit_cap)
        assert gate.ok is False
        assert "method" in gate.reason.lower()

    def test_methods_dict_has_entry_strategy_always(self):
        result = self._triangulate()
        gate = ax.exit_cap_gate(result, b79_value=result.exit_cap)
        assert gate.methods["entry_strategy"] is not None

    def test_methods_dict_treasury_none_when_not_supplied(self):
        solo_result = ax.ExitCapTriangulator().triangulate(going_in_cap=D("0.07"), strategy="value_add")
        gate = ax.exit_cap_gate(solo_result, b79_value=solo_result.exit_cap)
        assert gate.methods["treasury_spread"] is None

    def test_selected_field_is_the_binding_method(self):
        result = self._triangulate()
        gate = ax.exit_cap_gate(result, b79_value=result.exit_cap)
        assert gate.selected == result.binding_method

    def test_max_cap_field_matches_triangulator_exit_cap(self):
        result = self._triangulate()
        gate = ax.exit_cap_gate(result, b79_value=result.exit_cap)
        assert gate.max_cap == result.exit_cap

    def test_esplanade_exit_cap_passes_gate(self):
        """Esplanade EXIT_CAP = 0.06; triangulate first, then check B79 equals max."""
        result = ax.ExitCapTriangulator().triangulate(
            going_in_cap=D("0.0702"), strategy="value_add",
            forward_treasury=D("0.045"), agency_spread=D("0.0150"), neg_leverage_buffer=D("0.0075"),
        )
        # The Esplanade model uses EXIT_CAP=0.06; verify the triangulator max is >= that
        assert result.exit_cap >= D("0.06")
        gate = ax.exit_cap_gate(result, b79_value=result.exit_cap)
        assert gate.ok is True


# =============================================================================
# BL-15 — LTV gate: B52 must be a formula; LTV must tie to target
# =============================================================================

class TestLtvGate:
    """ltv_gate: B52 literal flags ok=False; LTV within tolerance passes."""

    def test_ok_when_formula_and_ltv_ties(self):
        gate = ax.ltv_gate(
            target_ltv=D("0.65"),
            purchase_price=D("34000000"),
            senior_loan=D("22100000"),    # 0.65 * 34M
            b52_formula="=B51*B10",
            b66_formula='=IFERROR(SUM(B52,B67)/B10,"N/A")',
        )
        assert gate.ok is True

    def test_fails_when_b52_is_literal(self):
        """A hardcoded loan amount in B52 (no leading '=') is the BL-15 defect."""
        gate = ax.ltv_gate(
            target_ltv=D("0.65"),
            purchase_price=D("34000000"),
            senior_loan=D("22100000"),
            b52_formula="22100000",           # LITERAL — no '='
            b66_formula='=IFERROR(SUM(B52,B67)/B10,"N/A")',
        )
        assert gate.ok is False
        assert gate.b52_is_formula is False
        assert "literal" in gate.reason.lower() or "b52" in gate.reason.lower()

    def test_fails_when_b66_is_literal(self):
        gate = ax.ltv_gate(
            target_ltv=D("0.65"),
            purchase_price=D("34000000"),
            senior_loan=D("22100000"),
            b52_formula="=B51*B10",
            b66_formula="0.65",               # LITERAL combined LTV
        )
        assert gate.ok is False
        assert gate.b66_is_formula is False

    def test_fails_when_computed_ltv_diverges_from_target(self):
        """A hardcoded loan amount that doesn't match target_ltv * price trips the gate."""
        gate = ax.ltv_gate(
            target_ltv=D("0.65"),
            purchase_price=D("34000000"),
            senior_loan=D("28000000"),        # ~82% LTV — does not tie to 0.65
            b52_formula="=B51*B10",
            b66_formula='=IFERROR(SUM(B52,B67)/B10,"N/A")',
        )
        assert gate.ok is False
        assert "computed" in gate.reason.lower() or "ltv" in gate.reason.lower()

    def test_computed_ltv_within_tolerance_passes(self):
        """Small rounding in senior_loan (< 0.5pp) should still pass."""
        price = D("34000000")
        target = D("0.65")
        # Loan rounded to nearest $10K
        loan = D("22100000")   # 22,100,000 / 34,000,000 = 0.6500
        gate = ax.ltv_gate(
            target_ltv=target, purchase_price=price, senior_loan=loan,
            b52_formula="=B51*B10",
        )
        assert gate.ok is True
        assert rel(gate.computed_ltv, target) <= 0.005

    def test_none_formula_strings_skip_formula_check(self):
        """When b52_formula / b66_formula are not supplied, formula checks are skipped
        and ok depends only on the LTV-tie check."""
        gate = ax.ltv_gate(
            target_ltv=D("0.65"),
            purchase_price=D("34000000"),
            senior_loan=D("22100000"),
            # no formula strings supplied
        )
        assert gate.ok is True
        assert gate.b52_is_formula is True   # default: assume intact
        assert gate.b66_is_formula is True

    def test_loan_amount_field_equals_senior_loan(self):
        gate = ax.ltv_gate(
            target_ltv=D("0.70"),
            purchase_price=D("50000000"),
            senior_loan=D("35000000"),
        )
        assert gate.loan_amount == D("35000000")

    def test_target_ltv_field_stored_correctly(self):
        gate = ax.ltv_gate(
            target_ltv=D("0.75"),
            purchase_price=D("40000000"),
            senior_loan=D("30000000"),
        )
        assert gate.target_ltv == D("0.75")


# =============================================================================
# BL-16 — RUBS sign gate: S54 must be negative; recovery jump plausibility
# =============================================================================

class TestRubsSignGate:
    """rubs_sign_gate: S54 positive rejects; upward >max_jump_pp without justification blocks."""

    # Baseline: UW utility expense $400K/yr; T-12 $40K recovery on $400K expense = 10% recovery
    UW_UTIL = D("400000")
    T12_REIMB = D("-40000")    # negative (contra) in T-12 as entered
    T12_UTIL = D("400000")

    def test_ok_when_negative_and_jump_within_band(self):
        # UW recovery: $48K / $400K = 12% — up +2pp vs T-12 10% (within 15pp default)
        gate = ax.rubs_sign_gate(
            reimbursement_value=D("-48000"),
            uw_utility_expense=self.UW_UTIL,
            t12_reimbursement=self.T12_REIMB,
            t12_utility_expense=self.T12_UTIL,
        )
        assert gate.ok is True
        assert gate.is_negative is True

    def test_fails_when_reimbursement_is_positive(self):
        """A positive S54 double-counts revenue — this is the sign defect."""
        gate = ax.rubs_sign_gate(
            reimbursement_value=D("48000"),    # POSITIVE — wrong
            uw_utility_expense=self.UW_UTIL,
        )
        assert gate.ok is False
        assert gate.is_negative is False
        assert "positive" in gate.reason.lower() or "contra" in gate.reason.lower()

    def test_fails_when_upward_jump_exceeds_band_without_justification(self):
        """UW recovery jumps >15pp above T-12 without a documented op plan -> fail."""
        # T-12: 10% recovery; UW: 28% recovery -> +18pp jump (> 15pp default)
        gate = ax.rubs_sign_gate(
            reimbursement_value=D("-112000"),   # 28% of $400K
            uw_utility_expense=self.UW_UTIL,
            t12_reimbursement=self.T12_REIMB,
            t12_utility_expense=self.T12_UTIL,
            justification="",                   # no justification
        )
        assert gate.ok is False
        assert "jump" in gate.reason.lower() or "band" in gate.reason.lower()

    def test_passes_when_upward_jump_exceeds_band_with_justification(self):
        """A >15pp jump is acceptable when a justification note is present (e.g. submetering)."""
        gate = ax.rubs_sign_gate(
            reimbursement_value=D("-112000"),
            uw_utility_expense=self.UW_UTIL,
            t12_reimbursement=self.T12_REIMB,
            t12_utility_expense=self.T12_UTIL,
            justification="submetering install underway per OM p.7; full RUBS rollout by Month 6",
        )
        assert gate.ok is True
        assert "justified" in gate.reason.lower() or "justify" in gate.reason.lower() or "justif" in gate.reason.lower()

    def test_passes_when_downward_jump_exceeds_band(self):
        """A DOWNWARD recovery jump (UW < T-12) is always plausible; gate never blocks it."""
        # T-12: 30% recovery; UW: 8% -> -22pp (large downward jump)
        gate = ax.rubs_sign_gate(
            reimbursement_value=D("-32000"),    # 8% of $400K
            uw_utility_expense=self.UW_UTIL,
            t12_reimbursement=D("-120000"),     # 30% T-12 recovery
            t12_utility_expense=self.T12_UTIL,
        )
        assert gate.ok is True

    def test_custom_max_jump_pp_tighter_band(self):
        """A tighter band (10pp) trips a 12pp jump that would pass the default 15pp."""
        # T-12: 10% recovery; UW: 22% -> +12pp jump
        gate = ax.rubs_sign_gate(
            reimbursement_value=D("-88000"),    # 22% of $400K
            uw_utility_expense=self.UW_UTIL,
            t12_reimbursement=self.T12_REIMB,
            t12_utility_expense=self.T12_UTIL,
            max_jump_pp=D("10"),                # tighter
        )
        assert gate.ok is False

    def test_default_band_passes_12pp_jump(self):
        """Same 12pp jump passes with the default 15pp band."""
        gate = ax.rubs_sign_gate(
            reimbursement_value=D("-88000"),
            uw_utility_expense=self.UW_UTIL,
            t12_reimbursement=self.T12_REIMB,
            t12_utility_expense=self.T12_UTIL,
            # max_jump_pp defaults to 15
        )
        assert gate.ok is True

    def test_sign_check_only_when_no_t12_baseline(self):
        """When no T-12 figures supplied, only the sign check applies; jump_pp == 0."""
        gate = ax.rubs_sign_gate(
            reimbursement_value=D("-50000"),
            uw_utility_expense=self.UW_UTIL,
            # no T-12 args
        )
        assert gate.ok is True
        assert gate.t12_recovery_pct is None
        assert gate.jump_pp == D("0")

    def test_zero_reimbursement_is_acceptable_negative_contra(self):
        """$0 reimbursement (no RUBS program) should pass: 0 <= 0."""
        gate = ax.rubs_sign_gate(
            reimbursement_value=D("0"),
            uw_utility_expense=self.UW_UTIL,
        )
        assert gate.ok is True
        assert gate.is_negative is True

    def test_recovery_pct_field_computed_correctly(self):
        # $60K reimbursement / $400K expense = 15%
        gate = ax.rubs_sign_gate(
            reimbursement_value=D("-60000"),
            uw_utility_expense=self.UW_UTIL,
        )
        assert abs(float(gate.recovery_pct) - 0.15) < 0.001

    def test_jump_pp_field_reflects_upward_move(self):
        # T-12 10% -> UW 22% = +12pp jump
        gate = ax.rubs_sign_gate(
            reimbursement_value=D("-88000"),
            uw_utility_expense=self.UW_UTIL,
            t12_reimbursement=self.T12_REIMB,
            t12_utility_expense=self.T12_UTIL,
        )
        assert abs(float(gate.jump_pp) - 12.0) < 0.5


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
