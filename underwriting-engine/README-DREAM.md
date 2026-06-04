# Dream Underwriting Engine (in the DREAM repo)

This is the **`dream-underwrite` skill + Python calc engine** — the underwriting brain behind
DreamVision (DREAM.AI Domain 1, the Unified Acquisitions Intelligence Platform). It is the
Phase-2 "AI-native underwriting + Excel export with working formulas" capability the
`DreamVision_PRD_v3.md` describes.

It is mirrored here from the canonical source in Evan's `shieldstone_os` repo
(`.skills/dream-underwrite/`). **`shieldstone_os` remains the source of truth for the skill;**
this copy is for the DREAM product to consume. Keep them in sync when the skill changes.

## What's here

- `engine/` — the Python calc engine. `lihtc_engine.py` (LIHTC/EFB: bond sizing, AMI rents, cash
  flow, deal scoring) + `acq_engine.py` (conventional value-add: bridge→agency-refi debt, levered
  IRR/EM/CoC, exit-cap triangulation, agency sizing, interest-reserve sizing, lease-up NOI ramp,
  four-tier GPR optimizer). Validated against Rayzor (EFB) + Esplanade (ACQ) ground truth.
- `fastpath/` — the Claude Code fast-path infra: `underwrite-spec.schema.json` (the contract),
  `agent-contracts.md` (the 5 parallel analytical subagents), `populator.py` (openpyxl Mini Model
  writer + Python↔Excel reconciliation gate + template-fork identity check).
- `references/`, `templates/`, `scripts/`, `SKILL.md` — the full skill methodology (12 phases),
  cell maps, agency-OpEx triangulation, the Mission Driven HUD/LIHTC API reference, and the
  Phase-12 canonical GS Residential memo spec.

## Run

```bash
pip install -r engine/requirements.txt
python -m pytest engine/tests/ fastpath/tests/ -q   # 25 tests
```

## Architecture (how DreamVision uses it)

A deal lands → fast path runs 3 waves: (1) parallel analytical subagents parse T-12 / rent roll /
comps + pull HUD data, (2) the Python engine computes the deal end-to-end + emits
`underwrite-spec.json`, (3) `populator.py` writes the Mini Model + reconciles Python vs Excel.
~30 min vs the 90 min–2 hr serial Claude-for-Excel flow. Target: Human-out-of-the-Loop, with the
Avery (orchestrator) → Dream (underwriter) Hermes topology driving it autonomously once Shieldstone
Hermes is live.
