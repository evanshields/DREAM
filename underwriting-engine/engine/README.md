# Dream Underwrite — Calc Engine

The Python calculation engine behind the Dream multifamily underwrite fast path. It computes
a deal end-to-end so the math can be sanity-checked **before** the Mini Model is populated, and
so the Python results can be reconciled against the Excel formulas (the human gate).

## Modules

| File | Origin | Covers |
|---|---|---|
| `lihtc_engine.py` | Adopted from `SHIELDSTONE_LIHTC_PYTHON_CLASSES.py` v1.0 (was unversioned in Downloads; brought into git 2026-06-03) | LIHTC/EFB: eligible & qualified basis, credits, equity pricing, developer fee, sources & uses, **bond sizing**, **AMI rents**, revenue/opex/cash-flow projection, developer & investor returns, partnership splits, **deal scoring**, `DreamAIOrchestrator` workflow skeleton |
| `acq_engine.py` | Built for Dream (the ACQ gap the LIHTC engine doesn't cover) | Conventional value-add: year-by-year vacancy curve, **bridge→agency-refi** debt-service transition, **levered project IRR / equity multiple / cash-on-cash**, agency takeout sizing (DSCR + LTV + Debt-Yield binding constraint), **3-method exit-cap triangulation (take HIGHEST)**, state-specific property-tax reassessment |

## Provenance & caveats

- `lihtc_engine.py` is proprietary Shieldstone code (header: "License: Proprietary"). Reused as-is;
  not modified. The ACQ layer lives in a separate module so the LIHTC core stays clean.
- **Docstring examples in `lihtc_engine.py` are NOT a reliable oracle.** Verified 2026-06-03:
  `BondSizingCalculator.size_bonds(600000, 1.20, 0.05, 35)` returns **$8,255,931** (correct,
  monthly-compounding PV of the debt-service stream) while the docstring claims $7,715,415 (wrong
  comment). Validate against the real Mini Model workbooks, not the docstrings.

## Validation

Engine output is validated against real workbook ground truth (see `tests/`):
- **EFB** → Resia Rayzor Ranch EFB Mini Model.
- **ACQ** → `shieldstone_acquisitions/deal-memos/build_esplanade_acq.py` pre-computed values
  (IRR 22.51%, equity multiple 2.72x, full NOI/DSCR series).

Tiered tolerance: headline metrics (NOI, DSCR, IRR, bond size, exit value) within ~0.5%; line
items within ~2%.

## Run

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```
