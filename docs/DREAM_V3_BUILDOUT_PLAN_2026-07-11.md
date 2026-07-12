# DREAM v3.0 — 24-Hour Buildout Plan (2026-07-11, Fable sprint)

**Goal:** complete the v3.0 MVP so Evan underwrites BOTH market-rate (ACQ) and bond (EFB)
opportunities in the live app. Fable builds/orchestrates for ~24h; Opus polishes after.
Governing docs: `DREAM_PRD.md` (v3.0 master) + `DREAM_FRONTEND_PRD_v1.md` (app spec).

**Baseline (start of sprint):** app LIVE at dream.shieldstone.co @ branch `wave-a-foundation`
cac2d81. Full ACQ chat-bot underwrite verified in production to CP-1 (Esplanade truth). 318 tests
green. PR #3 awaiting Evan's one-click merge.

## PRD scorecard at sprint start
- Waves A0/A1/B/E: done. Wave C: C.1–C.3 done; C.4 memo NOT wired; C.5 audit log not readable.
- Wave D: endpoints done, no UI. Wave F: F.1 done; F.2/F.3 deferred (stay deferred).
- Jobs pipeline hard-blocks EFB (v1 design) — the bond half of Evan's ask.

## Phases

### Phase 1 — Bond side (IN PROGRESS)
- **1a Bond Screen page** (frontend): deterministic EFB sizing via POST /api/underwrite/efb +
  exit-cap triangulation + agency-sizing calculators. Instant, no LLM. Route /bond-screen.
- **1b EFB jobs unlock** (backend): wave0 accepts explicit routing=EFB (EFB critical input:
  stabilized_noi; ambiguous still asks); synthesis dispatches ACQ|EFB; _coerce_efb_inputs w/
  MissingEngineInputsError; EFB stub fixture; e2e test vs Rayzor truth; ACQ regression untouched.
- **1c EFB frontend**: underwrite intake routing selector + EFB fields; EFB CP-1 metric cards.
- Deploy + live-verify an EFB job to CP-1.

### Phase 2 — Real deal-flow intake
- **2a `GET /api/deals/{id}`** single-deal view (spec + gates + open questions + latest job) —
  fixes the cold-reload gap; DealDetail loads everything from the store.
- **2b PDF intake**: wire the EXISTING /api/intake (pymupdf + Kimi extraction) into the underwrite
  flow — upload OM/T-12 → parsed summary prefills the form + becomes deal_docs.

### Phase 3 — Complete the PRD loop
- **3a Memo (C.4)**: MemoGenerator wired at CP-1 (+ endpoint if needed) + memo view/download.
- **3b Excel export UI (D.1/D.2)**: export button on DealDetail; surface BL refusals + CP-2
  reconcile results; template upload.
- **3c Audit trail (C.5)**: per-deal readable audit log (LLM calls, gates, spec mutations) —
  endpoint + a clean timeline view.

### Phase 4 — Hardening polish (stretch)
- **4a Async submit**: enqueue + poll (runner is already the worker body) — no more multi-minute
  held HTTP connections.
- **4b Pipeline richness**: archive/delete, owner scoping, load ANY deal into the assumption
  dashboard from its spec (not Esplanade defaults).
- **4c Misc**: Google cert caching, retire /api/underwrite legacy-engine drift (or mark),
  'hap'/'noah' substring fix in wave0 routing detection.

## Rules of the sprint
- Every phase: build (subagents, non-overlapping surfaces) → I review the diff → full test suite
  green → commit → deploy w/ timestamped backups → live-verify → update this doc.
- Locked contracts (never violate): Decimal only in engine_boundary; spec canonical; HITL stops at
  CP-1; no sqlite3 outside store; headline/qa never from LLM; fail closed on RED gates; vendored
  engine untouched; slices get scalar critical inputs only.
- LLM spend: live verifications use the sparse-intake pattern (~1 short Kimi run per verify).
- Rollback: every deploy has a timestamped .bak on the VPS.

## Log
- 2026-07-11: Sprint start. Phase 1a + 1b builders launched in parallel.
- 2026-07-11: **Phase 1a SHIPPED** — Bond Screen live at /bond-screen (commit 5d3b76e, deployed,
  live-verified: $2.5M NOI @ 1.15x/5%/35yr → $35.9M max bonds, $2.17M DS, $3.5M 10-yr tax
  savings). Backup frontend.bak-20260711-152059-p1a. Phase 1b (EFB jobs unlock) still building.
- 2026-07-11: **Phase 1b SHIPPED** — EFB route live through the chat-bot pipeline (commit de88d9e,
  backup backend.bak-20260711-153527-p1b). FIRST LIVE EFB UNDERWRITE verified to CP-1 with exact
  Rayzor truth: $63,868,907 max bonds / $3,868,062 DS / 1.15 DSCR / $9M tax savings; formula_audit
  explicitly skipped (documented). 333 tests green. Launched next: Phase 1c (EFB frontend) + Phase
  2a (GET /api/deals/{id}) builders in parallel.
- 2026-07-11: **Phase 2a SHIPPED** (commit a09e7b0) — GET /api/deals/{deal_id} full view live.
  Live verify caught a real bug: computed deals LOST their names at CP-1 (synthesis spec replaced
  seed meta) — **fixed** (4b72b3f, name carry-forward, 340 tests). Both verified live on a fresh
  named EFB run.
- 2026-07-11: **Phase 1c SHIPPED** (commit 82ac6dc, backup frontend.bak-20260711-154650-p1c) —
  EFB frontend live: ACQ/EFB intake selector, bond-metric CP-1 tiles + seeded EFB sizing panel,
  documented-skip gate badges, EFB pipeline cards. PHASE 1 COMPLETE. Launched: Phase 2b (PDF
  intake + /api/intake auth-gating — found UNGATED) + Phase 3a/3c (memo + audit trail backend).
- 2026-07-11: **Phase 2b + 3a/3c SHIPPED** (commit 5af9d58, backups *-p2b3). LIVE: PDF/T-12
  drag-drop intake w/ routing-aware prefill + deal_docs; POST /deals/{id}/memo (draft-marked,
  persisted, verified live 2145-char memo off the Rayzor EFB deal); GET /deals/{id}/audit
  (9-event trail verified). SECURITY: /api/intake + /api/agent/chat + /api/agent/memo were ALL
  ungated Kimi doors — closed (401 bare verified). 356 tests. Launched: Phase 3b frontend
  (memo view + audit timeline + Excel export button).
