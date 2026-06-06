export const meta = {
  name: 'dream-wave2',
  description: 'Dream underwrite Wave 2: engine wiring + new build + pinned UW-Snapshot doc fix (drafts only; parent applies)',
  phases: [
    { title: 'Schema', detail: 'design the shared spec-schema fields once (Opus)' },
    { title: 'Independent', detail: 'BL-08 doc fix + BL-13 tax range + BL-19 reprice solver (parallel)' },
    { title: 'EpicC', detail: 'Epic C synthesis wiring design + small gates (Opus) then tests (Sonnet)' },
  ],
}

// Wave-2 drafts CODE; the parent applies it to the shared acq_engine.py / schema in-context.
// This avoids racing six agents at one file. Each agent returns structured drafts + tests.

const REPO = 'c:\\Users\\evana\\shieldstone_os\\.skills\\dream-underwrite'
const CTX = `
You are improving the Dream multifamily underwriting skill (Wave 2 of the Envy 3-way forensic
backlog). Repo root: ${REPO}. The Python calc engine is engine/acq_engine.py (ACQ) and
engine/lihtc_engine.py (EFB/LIHTC). The fast-path spec is fastpath/underwrite-spec.schema.json;
the populator is fastpath/populator.py; the synthesis flow is documented in fastpath/agent-contracts.md
(§"Wave 2 synthesis"). All money math uses Decimal (D = Decimal). Tests live in engine/tests/ and
fastpath/tests/ and run with: python -m pytest engine/tests/ fastpath/tests/ -q (currently 61/61).

KEY ALREADY-BUILT classes in engine/acq_engine.py (Wave 1 verified — DO NOT rebuild, only wire/enforce):
- FourTierOptimizer.allocate(units, tier_shares, tier_ceilings) -> dict (market-max GPR allocation)
- InterestReserveSizer.size(noi_series, debt_service, dscr_floor, buffer, round_to, max_cover_years)
- LeaseUpRamp.noi_series(stabilized_noi, stabilized_egi, vacancy_curve, concession_curve, ...)
- ExitCapTriangulator.triangulate(going_in_cap, strategy, forward_treasury, ...) -> ExitCapResult (already takes max())
- AgencyTakeoutSizer.size(...), ACQCashFlowProjector.project(...), PropertyTaxCalculator.project(...) [flat ratio only]
- HurdleCalculator.compute(...)
EFB side: lihtc_engine.BondSizingCalculator.size_bonds(...) -> BondSizingResult.

KEY CELLS (ACQ Mini Model, field-mapping-acq.md): B79 = Exit Cap (INPUT, take HIGHEST); B52 = Loan
Amount FORMULA =B51*B10; B51 = LTV input; B66 = combined LTV =IFERROR(SUM(B52,B67)/B10,"N/A");
S54 = Utility Reimbursements (INPUT, NEGATIVE/contra).

GROUND TRUTH the engine must keep passing (engine/tests/test_acq_esplanade.py): Esplanade ACQ
IRR 22.51%, EM 2.72, exit value 55,870,669; the 1.16% servicing spread; DSCR series within 2%.
NEVER break these. Your additions must be ADDITIVE — new classes/functions, new spec fields, new
tests — with no edit to the validated SeniorDebtCalculator / ACQCashFlowProjector / ExitCapTriangulator
math.

LOCKED DECISIONS (Evan 2026-06-05):
- BL-04 EFB auto-route: the engine DETECTS NOAH/EFB-structural and emits a routing RECOMMENDATION,
  but the fast path STOPS at CP-1 for a human glance before building the EFB four-tier. Do NOT
  auto-produce the EFB model unattended. Build the detection + recommendation signal only.
- BL-13 FL tax: assume agent-marketdata supplies the county assessment method + market-derived
  assessed value (no manual-input fallback needed; keep the existing flat-ratio path as a documented default).

OUTPUT DISCIPLINE: You DRAFT code; you do NOT write to disk (the parent applies it carefully to the
shared file in-context). Return complete, paste-ready Python (full function/class bodies, not diffs),
matching the existing style (Decimal math, dataclasses, docstrings that cite the forensic origin).
`

const DRAFT_SCHEMA = {
  type: 'object',
  required: ['summary', 'engine_code', 'tests', 'doc_edits', 'schema_fields', 'integration_notes'],
  additionalProperties: false,
  properties: {
    summary: { type: 'string', description: 'one-paragraph what-and-why' },
    engine_code: { type: 'string', description: 'paste-ready Python to ADD to acq_engine.py (new classes/functions + dataclasses). Empty string if none.' },
    tests: { type: 'string', description: 'paste-ready pytest test file content (self-contained, imports acq_engine). Empty string if none.' },
    test_filename: { type: 'string', description: 'e.g. test_property_tax_range.py' },
    doc_edits: { type: 'string', description: 'exact before/after edits for SKILL.md / agent-contracts.md / field-mapping / 12-uw-snapshot.md (old_string -> new_string blocks). Empty string if none.' },
    schema_fields: { type: 'string', description: 'JSON snippet of the spec-schema fields this item needs (under qa/meta/headline_metrics). Empty string if none.' },
    integration_notes: { type: 'string', description: 'where in the Wave-2 synthesis flow the parent must CALL this; any ordering constraints; risks to the Esplanade ground truth.' },
  },
}

// ---------------------------------------------------------------------------
// Phase 1 — Schema first (Opus). One agent designs all shared spec fields so
// the downstream drafts emit consistent field names.
// ---------------------------------------------------------------------------
phase('Schema')
const schema = await agent(
  `${CTX}

TASK (schema-first): Read fastpath/underwrite-spec.schema.json. Design the COMPLETE set of new
spec fields Wave 2 needs, so every downstream draft emits consistent names. Cover:
- tier_allocation (BL-04: the FourTierOptimizer output — allocations[], gpr, gpr_delta_pct, tier_targets)
- efb_route_signal (BL-04: {noah_detected:bool, efb_recommended:bool, reason, stop_at_cp1:true})
- interest_reserve (BL-11: shortfall_years, gross_shortfall, reserve_sized, covered_dscr_floor)
- lease_up_ramp (BL-12: the data-derived noi ramp + the vacancy/concession curves it came from)
- exit_cap_gate (BL-10: methods{}, selected, max, ok:bool — assert populated B79 == max)
- ltv_gate (BL-15: target_ltv, computed_ltv, b52_is_formula:bool, ok)
- rubs_sign (BL-16: reimbursement_value, is_negative:bool, recovery_pct, t12_recovery_pct, jump_pp, ok)
- property_tax_range (BL-13: low, high, point, basis, exemption_delta)
- reprice (BL-19: below_hurdle:bool, clearing_price, target_metric, iterations)
Return ONLY the schema_fields (a JSON snippet showing exactly where each nests under qa/meta/
headline_metrics) and integration_notes (which Wave-2 synthesis step writes each). engine_code/
tests/doc_edits empty.`,
  { schema: DRAFT_SCHEMA, label: 'schema-design', phase: 'Schema' }
)

// ---------------------------------------------------------------------------
// Phase 2 — Independent items in parallel (different files / new classes).
//   BL-08 doc (Sonnet) | BL-13 tax range (Sonnet) | BL-19 reprice solver (Opus)
// ---------------------------------------------------------------------------
phase('Independent')
const SCHEMA_REF = `\n\nThe shared spec fields were designed as:\n${schema?.schema_fields || '(see integration_notes)'}\n`

const independent = await parallel([
  // BL-08 — pinned UW-Snapshot scope fix (pure doc).
  () => agent(
    `${CTX}

TASK (BL-08, pinned by Evan — pure doc): Remove the Financing/DSCR/Returns/Exit scope from the
UW-Snapshot spec. The Snapshot ENDS AT THE CAP-RATE/NOI BLOCK by design; DSCR routes to the Checks
tab, returns/exit to the Pro Forma. Files + exact edits:
1. references/12-uw-snapshot.md — in the "UW Snapshot Sheet Structure" table (rows: Capital Stack,
   Debt Service, Returns(ACQ), Bond Metrics(EFB), Exit, Sensitivity), REMOVE those 6 rows; keep Deal
   Identity, Revenue Summary, Expense Summary, NOI. Add an explicit note "The Snapshot ends at the
   cap-rate block; DSCR is verified on the Checks tab and returns/exit on the Pro Forma." Relabel the
   "Financing Sanity / Returns Sanity / Exit Sanity" checklist sections as CHECKS-TAB / PRO-FORMA-TAB
   checks (not Snapshot). Keep the Final Metrics Audit headline block (it is the CHAT summary, sourced
   from Checks + Pro Forma — clarify that).
2. SKILL.md Phase 11b — mirror: the Snapshot populates only revenue->OpEx->NOI->cap; DSCR verified on
   Checks, returns/exit on Pro Forma; reported in chat. Update the Phase 11 QA gate items accordingly.
3. templates/field-mapping-acq.md + field-mapping-efb.md — if either lists a Snapshot financing/
   returns/exit CELL block, remove it; otherwise note no change.
Preserve Universal Rule 9 (never add rows/sections to a populated template). Read each file first,
then return doc_edits as precise old_string -> new_string blocks. engine_code/tests/schema_fields empty.`,
    { schema: DRAFT_SCHEMA, label: 'BL-08-snapshot', phase: 'Independent', model: 'sonnet' }
  ),

  // BL-13 — FL property-tax reassessment estimator -> a RANGE (new class).
  () => agent(
    `${CTX}${SCHEMA_REF}

TASK (BL-13, new build): Add a PropertyTaxRangeEstimator to acq_engine.py that REPLACES the flat
PP x ratio x millage with an assessor/CoStar-driven estimate producing a tax RANGE (low/high), not a
point. Assume agent-marketdata supplies: county assessment method, market-derived assessed value,
millage, and (for FL) the sale-triggered reassessment behavior (Save Our Homes cap resets on transfer).
Produce a low/high band around the reassessed basis + a point estimate, and quantify the EFB exemption
as the delta (full estimated tax x hold years). Keep the existing PropertyTaxCalculator flat-ratio path
as a documented fallback (do not delete it). Match the existing dataclass+Decimal style. Provide a
self-contained pytest file (test_property_tax_range.py) asserting: an FL waterfront produces low<point<high;
the exemption delta is positive; the flat-ratio fallback still works. Return engine_code + tests +
test_filename + integration_notes (which synthesis step calls it; it feeds the ACQ property-tax cells
and the EFB exemption narrative). doc_edits: a one-line note in references/06-property-tax.md pointing to
the new estimator. schema_fields: confirm the property_tax_range shape.`,
    { schema: DRAFT_SCHEMA, label: 'BL-13-tax-range', phase: 'Independent', model: 'sonnet' }
  ),

  // BL-19 — reprice / goal-seek solver (new class, Opus — convergence judgment).
  () => agent(
    `${CTX}${SCHEMA_REF}

TASK (BL-19, new build — needs care): Add a RepriceSolver to acq_engine.py. When a deal is BELOW
hurdles, goal-seek the purchase price that clears the IRR/EM floor, to surface at CP-3 (Envy clears
around $56-57M vs the $74-75M ask). Approach: bisection / secant on purchase price, re-running the
ACQCashFlowProjector each iteration, converging when the chosen target metric (IRR or EM) hits the
floor within tolerance. GUARD against non-monotonic IRR curves: bracket the search, cap iterations,
and return below_hurdle + the clearing_price + iterations + a converged flag (or a clear "no clearing
price in range" result). Reuse the EXISTING ACQCashFlowProjector / SeniorDebtCalculator — do not
reimplement the cash-flow math. Provide test_reprice_solver.py: a below-hurdle deal returns a clearing
price that, re-run, hits the floor within tolerance; a deal already above hurdle returns below_hurdle=false;
a pathological no-solution case returns converged=false (no crash). Return engine_code + tests +
test_filename + integration_notes (CP-3 surfacing; must run AFTER returns are realistic, i.e. after
Epic C's interest-reserve wiring). schema_fields: confirm the reprice shape.`,
    { schema: DRAFT_SCHEMA, label: 'BL-19-reprice', phase: 'Independent', model: 'opus' }
  ),
])

// ---------------------------------------------------------------------------
// Phase 3 — Epic C: the coupled synthesis wiring. One Opus agent designs the
// whole wiring coherently (so the shared synthesis path isn't raced), then a
// Sonnet agent drafts the integration tests against that design.
// ---------------------------------------------------------------------------
phase('EpicC')
const epicCDesign = await agent(
  `${CTX}${SCHEMA_REF}

TASK (Epic C — wire the already-built classes into the Wave-2 synthesis + add 3 small gates).
This is the analyst-divergence closer. Design ONE coherent set of additions to acq_engine.py +
the synthesis flow (documented in agent-contracts.md §"Wave 2 synthesis"). Cover all six:

- BL-04: the Wave-2 synthesis must CALL FourTierOptimizer.allocate() (today it only mentions NOAH/HAP).
  Add a NOAH-detection helper (in-place rent vs 85% of the 80%-AMI ceiling, per bedroom) and an
  efb_route_signal: when the conventional case FAILS hurdles AND NOAH/exemption indicates EFB, set
  efb_recommended=true, stop_at_cp1=true, and a reason — but DO NOT build the EFB model (locked: stop
  at CP-1 and ask). Emit tier_allocation + efb_route_signal to the spec.
- BL-11: synthesis calls InterestReserveSizer.size(); fund the reserve from sources; run DSCR NET of
  reserve draws so Y1 DSCR is realistic (not 0.41-0.77x). Emit interest_reserve.
- BL-12: synthesis feeds LeaseUpRamp.noi_series() the forensic vacancy + concession curves from
  agent-t12 instead of the hardcoded 0.62/0.85/1.0; expose the curve as the auditable source. Emit
  lease_up_ramp.
- BL-10: an exit_cap_gate function that asserts the populated B79 == ExitCapTriangulator max and that
  3 method inputs are documented; ok=false blocks.
- BL-15: an ltv_gate function: assert computed senior LTV == target within tolerance; FLAG B52 if it
  is a literal where the =B51*B10 formula belongs. (populator already refuses formula cells; this is
  the assertion side.)
- BL-16: a rubs_sign assertion: utility reimbursements (S54) must net NEGATIVE (contra); reject a
  positive booking; cap the RUBS recovery jump vs the T-12 actual (>5-10pp flags, requires a documented
  op plan).

Return: engine_code (the NOAH helper + the 3 gate functions + their result dataclasses — NEW additions
only, do NOT edit the validated cash-flow classes); doc_edits (agent-contracts.md §Wave-2 synthesis
steps that now CALL these + emit the spec fields; SKILL.md Phase 4 BL-04 note, Phase 7 BL-16 note,
Phase 10 BL-10/BL-15 notes); schema_fields (confirm tier_allocation/efb_route_signal/interest_reserve/
lease_up_ramp/exit_cap_gate/ltv_gate/rubs_sign); integration_notes (exact call order in synthesis,
and how the interest-reserve net-of-draws DSCR must NOT change the Esplanade ground-truth result —
gate the reserve logic so a stabilized deal with no shortfall behaves exactly as today).`,
  { schema: DRAFT_SCHEMA, label: 'EpicC-design', phase: 'EpicC', model: 'opus' }
)

const epicCTests = await agent(
  `${CTX}${SCHEMA_REF}

The Epic C wiring/gates were designed as follows (engine_code + integration_notes):
--- ENGINE CODE ---
${epicCDesign?.engine_code || ''}
--- INTEGRATION NOTES ---
${epicCDesign?.integration_notes || ''}
--- END ---

TASK: Draft the pytest tests for these Epic C additions. One self-contained test file
(test_wave2_epicc.py) asserting: NOAH detection fires on an in-place-near-ceiling bedroom; the
efb_route_signal sets stop_at_cp1=true and does NOT build an EFB model; interest reserve makes a
lease-up Y1 DSCR clear the floor (and a STABILIZED deal with no shortfall is unchanged — protects the
Esplanade ground truth); the lease-up ramp is data-derived (changes when the vacancy curve changes);
exit_cap_gate blocks when B79 != triangulator max; ltv_gate flags a literal B52 + asserts LTV==target;
rubs_sign rejects a positive reimbursement and flags a >10pp recovery jump. Return ONLY tests +
test_filename. Keep imports to acq_engine; match the existing test style (Decimal, rel() helper).`,
  { schema: DRAFT_SCHEMA, label: 'EpicC-tests', phase: 'EpicC', model: 'sonnet' }
)

return {
  schema,
  independent: {
    'BL-08': independent[0],
    'BL-13': independent[1],
    'BL-19': independent[2],
  },
  epicC: { design: epicCDesign, tests: epicCTests },
}
