"""
Shieldstone EFB Underwriting Mini-App — FastAPI Backend
========================================================
Routes:
  POST /api/intake          — Upload + auto-detect + extract deal document
  POST /api/underwrite      — Run full financial model
  POST /api/validate        — Validate inputs vs T-Manual V2
  POST /api/agent/chat      — Streaming Kimi agent (SSE)
  POST /api/agent/memo      — Generate deal memo
  GET  /api/health          — Health check
"""

import os
import json
import asyncio
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from fastapi import Depends
from auth_dep import require_auth, auth_enabled  # A0.2: OAuth re-enabled (configurable)

# Load env
load_dotenv(Path(__file__).parent / ".env")

# Internal imports
from models import (
    DealInputs,
    UnderwriteResponse,
    ValidationResponse,
    IntakeResponse,
    AgentChatRequest,
    MemoRequest,
    ProFormaYear,
    SourcesUses,
    ExitAnalysis,
    ReturnsSummary,
    EFBTaxAdvantage,
    SensitivityGrid,
    ValidationFlag,
)
from calculations import (
    compute_sources_and_uses,
    compute_pro_forma,
    compute_exit_analysis,
    compute_sensitivity_grid,
    compute_efb_tax_advantage,
    calculate_irr,
    build_investor_cash_flows,
    compute_returns_summary,
    size_bond_to_dscr,
)
from calculations.validator import DealValidator
from intake.intake_service import IntakeService
from agent import AsyncKimiClient, MemoGenerator
from agent.prompts import (
    GUIDED_ONBOARDING_SYSTEM,
    VALIDATION_SYSTEM,
    build_validation_user_message,
    build_onboarding_context,
)

# ============================================================================
# APP SETUP
# ============================================================================

app = FastAPI(
    title="DREAM Underwriting API",
    version="3.0.0-wave-a",
    description="DREAM — Shieldstone Dev/RE/Asset-Mgmt underwriting (ACQ + EFB).",
)

# /api/recalc lives in its own router whose import graph is deliberately LLM-free (A1.5).
# ALL Wave A-D routers are auth-gated at mount time (router files stay dependency-free so their
# standalone test harnesses run without tokens; production enforcement lives HERE).
from routers.recalc import router as recalc_router  # noqa: E402
app.include_router(recalc_router, dependencies=[Depends(require_auth)])

# Wave D — App->Excel push (populate + reconcile against a user Mini Model template).
from routers.export_excel import router as export_router  # noqa: E402
app.include_router(export_router, dependencies=[Depends(require_auth)])

# Wave C — chat-bot fast-path job service (submit/status/answer/cancel; HITL stop at CP-1).
from routers.jobs import router as jobs_router  # noqa: E402
app.include_router(jobs_router, dependencies=[Depends(require_auth)])

# Task C — username/password login (issues a short-lived app JWT accepted by require_auth
# alongside Google OAuth). Urgent stopgap before Google Test Users propagate.
from routers.auth_login import router as auth_login_router  # noqa: E402
app.include_router(auth_login_router)


# A0.2 — configurable Google OAuth lives in auth_dep.require_auth (imported above).
# Enforced when GOOGLE_CLIENT_ID is set; transparent local-dev pass-through otherwise.

# CORS — allow Vite dev server and Vercel production frontend
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton clients (initialized on first use)
_kimi_client: AsyncKimiClient | None = None
_intake_service: IntakeService | None = None
_memo_generator: MemoGenerator | None = None
_validator = DealValidator()


def get_kimi_client() -> AsyncKimiClient:
    global _kimi_client
    if _kimi_client is None:
        _kimi_client = AsyncKimiClient()
    return _kimi_client


def get_intake_service() -> IntakeService:
    global _intake_service
    if _intake_service is None:
        from agent.kimi_client import KimiClient
        _intake_service = IntakeService(KimiClient())
    return _intake_service


def get_memo_generator() -> MemoGenerator:
    global _memo_generator
    if _memo_generator is None:
        _memo_generator = MemoGenerator()
    return _memo_generator


# ============================================================================
# HELPERS — flatten Pydantic inputs to the flat dict the engine expects
# ============================================================================

def flatten_inputs(deal: DealInputs) -> dict:
    """Convert nested DealInputs to a flat dict for the calculation engine."""
    p = deal.property
    r = deal.revenue
    e = deal.expenses
    gp = deal.general_partner
    c = deal.capital
    cc = deal.closing_costs
    b = deal.bonds
    t = deal.property_tax
    x = deal.exit
    w = deal.waterfall

    # Compute GPR from unit mix if provided
    if p.unit_mix:
        monthly_gpr = sum(u.count * u.market_rent for u in p.unit_mix)
        annual_gpr = monthly_gpr * 12
    else:
        annual_gpr = 0.0

    return {
        # Property
        "property_name": p.property_name,
        "city": p.city,
        "state": p.state,
        "total_units": p.total_units,
        "unit_count": p.total_units,
        "rentable_sf": p.rentable_sf,
        "year_built": p.year_built,
        "purchase_price": p.purchase_price,
        "asking_price": p.asking_price,
        "unit_mix": [u.model_dump() for u in p.unit_mix],
        # Revenue
        "annual_gpr": annual_gpr,
        "gpr_yr1": annual_gpr,
        "vacancy_yr1": r.vacancy_yr1,
        "vacancy_stable": r.vacancy_stable,
        "other_income_per_unit_yr": r.other_income_per_unit_yr,
        "revenue_growth": r.revenue_growth,
        # Expenses — per unit (stored for reference) + totals the engine reads
        "payroll_per_unit": e.payroll_per_unit,
        "payroll_yr1": e.payroll_per_unit * p.total_units,
        "general_admin_per_unit": e.general_admin_per_unit,
        "general_admin_yr1": e.general_admin_per_unit * p.total_units,
        "marketing_per_unit": e.marketing_per_unit,
        "marketing_yr1": e.marketing_per_unit * p.total_units,
        "turnover_per_unit": e.turnover_per_unit,
        "turnover_yr1": e.turnover_per_unit * p.total_units,
        "rm_per_unit": e.rm_per_unit,
        "rm_services_yr1": e.rm_per_unit * p.total_units,
        "contract_services_per_unit": e.contract_services_per_unit,
        "contract_services_yr1": e.contract_services_per_unit * p.total_units,
        "utilities_per_unit": e.utilities_per_unit,
        "utilities_yr1": e.utilities_per_unit * p.total_units,
        "utility_reimbursements_per_unit": e.utility_reimbursements_per_unit,
        "utility_reimbursements_yr1": e.utility_reimbursements_per_unit * p.total_units,
        "insurance_per_unit": e.insurance_per_unit,
        "insurance_yr1": e.insurance_per_unit * p.total_units,
        "capital_expense_reserves_per_unit": e.capital_expense_reserves_per_unit,
        "mgmt_fee_pct": e.mgmt_fee_pct,
        "expense_growth": e.expense_growth,
        # General Partner
        "acquisition_fee_pct": gp.acquisition_fee_pct,
        "asset_mgmt_fee_pct": gp.asset_mgmt_fee_pct,
        "disposition_fee_pct": gp.disposition_fee_pct,
        "construction_mgmt_pct": gp.construction_mgmt_pct,
        "other_closing_costs_pct": gp.other_closing_costs_pct,
        # Capital
        "capital_budget": c.capital_budget,
        "capital_reserve_amount": c.capital_reserve_amount,
        "use_capital_budget_reserves": c.use_capital_budget_reserves,
        "renovation_start_year": c.renovation_start_year,
        "renovation_end_year": c.renovation_end_year,
        # Closing Costs (direct dollar amounts)
        "gp_bond_counsel": cc.gp_bond_counsel,
        "lenders_counsel": cc.lenders_counsel,
        "cost_of_issuance": cc.cost_of_issuance,
        "transfer_recordation": cc.transfer_recordation,
        "title": cc.title,
        "property_condition_report": cc.property_condition_report,
        "file_inspection": cc.file_inspection,
        "environmental": cc.environmental,
        "survey": cc.survey,
        "appraisal": cc.appraisal,
        "market_study": cc.market_study,
        "capital_reserve": cc.capital_reserve,
        "insurance_escrow": cc.insurance_escrow,
        "soft_cost_cushion": cc.soft_cost_cushion,
        "working_capital": cc.working_capital,
        "replacement_reserves_capitalized": cc.replacement_reserves_capitalized,
        "enhancements_and_reserves": cc.enhancements_and_reserves,
        "financial_advisor_issuance": cc.financial_advisor_issuance,
        "bond_counsel_coi": cc.bond_counsel_coi,
        "underwriter_counsel": cc.underwriter_counsel,
        "trustee": cc.trustee,
        "trustee_counsel": cc.trustee_counsel,
        "other_bond_closing_costs": cc.other_bond_closing_costs,
        # Bonds
        "loan_amount": b.loan_amount,
        "b_note_amount": b.b_note_amount,
        "b_note_loan_type": b.b_note_loan_type,
        "b_note_refi_valuation": b.b_note_refi_valuation,
        "b_note_origination_year": b.b_note_origination_year,
        "b_note_io_period_year": b.b_note_io_period_year,
        "b_note_origination_fees_pct": b.b_note_origination_fees_pct,
        "b_note_interest_rate_current": b.b_note_interest_rate_current,
        "b_note_interest_rate_accrued": b.b_note_interest_rate_accrued,
        "b_note_loan_maturity_year": b.b_note_loan_maturity_year,
        "b_note_exit_fees_pct": b.b_note_exit_fees_pct,
        "b_note_amortization_years": b.b_note_amortization_years,
        "a_bond_rate": b.a_bond_rate,
        "io_period_years": b.io_period_years,
        "io_period_months": int(b.io_period_years * 12),
        "loan_term_years": b.loan_term_years,
        "amortization_years": b.amortization_years,
        "origination_pct": b.origination_pct,
        "financial_advisory_pct": b.financial_advisory_pct,
        "exit_fee_pct": b.exit_fee_pct,
        # Property Tax
        "efb_exempt": t.efb_exempt,
        "pilot_annual": t.pilot_annual,
        "property_tax_rate": t.property_tax_rate,
        "current_assessed_value": t.current_assessed_value,
        "assessment_ratio": t.assessment_ratio,
        "non_ad_valorem_taxes": t.non_ad_valorem_taxes,
        "reassessed_upon_acquisition": t.reassessed_upon_acquisition,
        "pct_taxes_exempt": t.pct_taxes_exempt,
        "reassessed_upon_sale": t.reassessed_upon_sale,
        "ad_valorem_tax_growth_rate": t.ad_valorem_tax_growth_rate,
        "non_ad_valorem_growth_rate": t.non_ad_valorem_growth_rate,
        # Exit
        "hold_period": x.hold_period,
        "exit_cap_rate": x.exit_cap_rate,
        "sale_transaction_cost": x.sale_transaction_cost,
        "exit_to_conventional_buyer": x.exit_to_conventional_buyer,
        # Waterfall
        "lp_preferred_return": w.lp_preferred_return,
        "lp_equity_split_to_hurdle": w.lp_equity_split_to_hurdle,
        "irr_hurdle": w.irr_hurdle,
        "lp_residual_split": w.lp_residual_split,
    }


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "efb-underwriting-api", "version": "0.1.0"}


@app.get("/api/me")
def me(user: dict = Depends(require_auth)):
    """Return the authenticated user profile (stub user in local dev)."""
    return {
        "email": user.get("email"),
        "name": user.get("name"),
        "picture": user.get("picture"),
    }


@app.post("/api/underwrite", response_model=UnderwriteResponse)
def underwrite(deal: DealInputs, user: dict = Depends(require_auth)):
    """Run the full EFB financial model and return all outputs."""
    try:
        inputs = flatten_inputs(deal)

        # Core calculations — compute pro forma first so we can derive going_in_cap
        sources_uses_raw = compute_sources_and_uses(inputs)
        pro_forma_raw = compute_pro_forma(inputs)

        # Derive going_in_cap from yr1 NOI and pass back into inputs for exit analysis
        yr1 = pro_forma_raw[0] if pro_forma_raw else {}
        yr1_noi = yr1.get("noi", 0.0)
        purchase_price = float(inputs.get("purchase_price", 1.0))
        inputs["going_in_cap"] = yr1_noi / purchase_price if purchase_price else 0.05

        exit_raw = compute_exit_analysis(inputs, pro_forma_raw)
        sensitivity_raw = compute_sensitivity_grid(inputs)
        tax_advantage_raw = compute_efb_tax_advantage(inputs, pro_forma_raw)

        # Returns — use proper signature: (pro_forma, exit_analysis, equity_invested)
        equity_invested = max(sources_uses_raw.get("lp_equity", 0.0), 0.0)
        returns_raw = compute_returns_summary(pro_forma_raw, exit_raw, equity_invested)

        # Hurdle IRR — market_tier removed, default to secondary (16%)
        hurdle = 0.16
        irr_val = returns_raw.get("irr")
        em_val = returns_raw.get("equity_multiple", 0.0)

        # Flatten closing costs for SourcesUses model
        cc = sources_uses_raw["closing_costs"]

        # Compute conventional DSCR for tax advantage comparison
        yr1_ds = yr1.get("a_bond_interest", 0.0) + yr1.get("a_bond_principal_scheduled", 0.0)
        conventional_tax = tax_advantage_raw["conventional_annual_tax"]
        yr1_dscr_conv = (yr1_noi - conventional_tax) / yr1_ds if yr1_ds > 0 else float("inf")

        # Build exit analysis fields
        exit_cap = exit_raw["exit_cap"]
        sale_price = exit_raw["sale_price"]
        total_units = int(inputs.get("total_units", 1))
        going_in_cap = inputs["going_in_cap"]
        exit_cap_method = "Direct Input"

        return UnderwriteResponse(
            sources_uses=SourcesUses(
                loan_amount=sources_uses_raw["loan_amount"],
                b_note_amount=sources_uses_raw["b_note_amount"],
                lp_equity=sources_uses_raw["lp_equity"],
                total_sources=sources_uses_raw["total_sources"],
                purchase_price=purchase_price,
                acquisition_fee=cc["acquisition_fee"],
                gp_bond_counsel=cc["gp_bond_counsel"],
                lenders_counsel=cc["lenders_counsel"],
                cost_of_issuance=cc["cost_of_issuance"],
                transfer_recordation=cc["transfer_recordation"],
                title=cc["title"],
                property_condition_report=cc["property_condition_report"],
                file_inspection=cc["file_inspection"],
                environmental=cc["environmental"],
                survey=cc["survey"],
                appraisal=cc["appraisal"],
                market_study=cc["market_study"],
                capital_reserve=cc["capital_reserve"],
                insurance_escrow=cc["insurance_escrow"],
                soft_cost_cushion=cc["soft_cost_cushion"],
                working_capital=cc["working_capital"],
                replacement_reserves_capitalized=cc["replacement_reserves_capitalized"],
                enhancements_and_reserves=cc.get("enhancements_and_reserves", 0.0),
                other_closing_costs=cc.get("other_closing_costs", 0.0),
                financial_advisor_issuance=cc.get("financial_advisor_issuance", 0.0),
                bond_counsel_coi=cc.get("bond_counsel_coi", 0.0),
                underwriter_counsel=cc.get("underwriter_counsel", 0.0),
                trustee=cc.get("trustee", 0.0),
                trustee_counsel=cc.get("trustee_counsel", 0.0),
                other_bond_closing_costs=cc.get("other_bond_closing_costs", 0.0),
                capital_budget_reserves_account=cc.get("capital_budget_reserves_account", 0.0),
                total_closing_costs=sources_uses_raw["total_closing_costs"],
                total_uses=sources_uses_raw["total_uses"],
                ltv=sources_uses_raw["ltv"],
            ),
            pro_forma=[ProFormaYear(**y) for y in pro_forma_raw],
            exit_analysis=ExitAnalysis(
                hold_year=exit_raw["hold_period"],
                exit_noi=exit_raw["exit_noi"],
                method1_cap=exit_raw["method1_cap"],
                method2_cap=exit_raw["method2_cap"],
                method3_cap=exit_raw["method3_cap"],
                exit_cap_used=exit_cap,
                exit_cap_method=exit_cap_method,
                sale_price=sale_price,
                price_per_unit=sale_price / total_units if total_units else 0.0,
                outstanding_bonds=exit_raw["total_outstanding_bonds"],
                sale_costs=sale_price * exit_raw["sale_transaction_cost"],
                net_proceeds=exit_raw["net_proceeds_to_equity"],
                going_in_cap=going_in_cap,
            ),
            returns=ReturnsSummary(
                property_irr=irr_val,
                equity_multiple=em_val,
                coc_yr1=returns_raw.get("coc_yr1", 0.0),
                net_proceeds=returns_raw.get("exit_proceeds", 0.0),
                equity_invested=equity_invested,
                irr_formatted=returns_raw.get("irr_pct", "N/A"),
                em_formatted=f"{em_val:.2f}x",
                coc_formatted=returns_raw.get("coc_yr1_pct", "N/A"),
                hurdle_irr=hurdle,
                passes_irr=(irr_val or 0) >= hurdle,
                passes_em=em_val >= 1.5,
            ),
            tax_advantage=EFBTaxAdvantage(
                efb_annual_tax=tax_advantage_raw["efb_annual_tax"],
                conventional_annual_tax=tax_advantage_raw["conventional_annual_tax"],
                annual_savings=tax_advantage_raw["annual_savings"],
                cumulative_savings=tax_advantage_raw["cumulative_savings"],
                yr1_dscr_conventional=yr1_dscr_conv,
                yr1_dscr_efb=yr1.get("dscr", 0.0),
            ),
            sensitivity=SensitivityGrid(
                a_bond_rates=sensitivity_raw["a_bond_rates"],
                exit_caps=sensitivity_raw["exit_caps"],
                dscr_grid=sensitivity_raw["dscr_grid"],
            ),
            yr1_dscr=yr1.get("dscr", 0.0),
            yr1_noi=yr1_noi,
            going_in_cap=going_in_cap,
            price_per_unit=purchase_price / total_units if total_units else 0.0,
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/validate", response_model=ValidationResponse)
def validate(deal: DealInputs, user: dict = Depends(require_auth)):
    """Validate deal inputs against T-Manual V2 standards."""
    try:
        inputs = flatten_inputs(deal)
        flags = _validator.validate_inputs_only(inputs)
        summary = _validator.get_summary(flags)
        return ValidationResponse(
            flags=[ValidationFlag(**f.__dict__) for f in flags],
            **summary,
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/intake", response_model=IntakeResponse)
async def intake(file: UploadFile = File(...)):
    """
    Upload a deal document (PDF, XLSX, CSV).
    Auto-detects type, extracts data, returns prefill map for the form.
    """
    try:
        file_bytes = await file.read()
        service = get_intake_service()
        result = await service.process_file(file_bytes, file.filename or "")
        return IntakeResponse(
            doc_type=result.doc_type,
            confidence=result.confidence,
            detection_method=result.detection_method,
            prefill_map=result.prefill_map,
            warnings=result.warnings,
            fields_filled_count=len([v for v in result.prefill_map.values() if v is not None]),
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/agent/chat")
async def agent_chat(request: AgentChatRequest):
    """
    Streaming Kimi agent endpoint (SSE).
    Modes: onboarding | validation | free
    Returns text/event-stream with token chunks.
    """
    kimi = get_kimi_client()

    # Build system prompt based on mode
    if request.mode == "onboarding":
        system_content = GUIDED_ONBOARDING_SYSTEM
        if request.current_inputs:
            context = build_onboarding_context(
                current_section="",
                filled_inputs=flatten_inputs(request.current_inputs),
            )
            # Inject context into the last user message
    elif request.mode == "validation":
        system_content = VALIDATION_SYSTEM
    else:
        system_content = (
            "You are an expert EFB real estate underwriter at Shieldstone Holdings. "
            "Answer questions about the deal model, EFB structure, and underwriting standards."
        )

    # Assemble messages
    messages = [{"role": "system", "content": system_content}]
    messages += [{"role": m.role, "content": m.content} for m in request.messages]

    # If validation mode and model results provided, prepend context
    if request.mode == "validation" and request.model_results and request.current_inputs:
        flags_raw = [f.model_dump() for f in (request.validation_flags or [])]
        context_msg = build_validation_user_message(
            inputs=flatten_inputs(request.current_inputs),
            model_results=request.model_results,
            flags=flags_raw,
        )
        # Insert context before last user message
        if len(messages) > 1:
            messages.insert(-1, {"role": "user", "content": context_msg})

    async def event_stream() -> AsyncIterator[str]:
        try:
            async for token in kimi.stream(messages):
                # SSE format
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/agent/memo")
def agent_memo(request: MemoRequest):
    """Generate a 1-page institutional deal memo."""
    try:
        generator = get_memo_generator()
        inputs_flat = flatten_inputs(request.inputs)
        memo_markdown = generator.generate(inputs_flat, request.model_results)
        summary = generator.generate_executive_summary(inputs_flat, request.model_results)
        return {
            "memo_markdown": memo_markdown,
            "executive_summary": summary,
        }
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
