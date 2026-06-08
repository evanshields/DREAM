# Wave E — Hermes intake seam (DESIGN-ONLY)

> **Status:** design-only. **Do NOT build the runtime here.** This document defines the *seam* — the
> normalized envelope and the single landing function — so that when Shieldstone Hermes is installed,
> a deal arriving from Drive / email / Slack lands as the **same `DealStore` deal instance** a manual
> upload would create, and flows through the **same** Wave-0 → Wave-1 → Wave-2 → CP-1 pipeline (Wave C).
> Aligns with `DREAM_PRD.md` §Wave E and the locked Hermes design in
> `shieldstone_acquisitions/HERMES_DREAM_AUTONOMY_DESIGN.md` + `HERMES_DREAM_BUILD_SPEC.md`.

## The principle

A Hermes-sourced deal must be **indistinguishable downstream** from a user-uploaded one. The only
difference is *provenance*. So the seam is: every intake path (manual upload, Drive, email, Slack)
normalizes to **one envelope**, and one function (`land_deal_source`) turns that envelope into a
`DealStore` deal + a Wave C job. Manual upload is just the envelope with `source.kind = "upload"`.

```
 manual upload ─┐
 Drive watcher ─┤        DealSourceEnvelope          land_deal_source()        Wave C job
 email triage  ─┼──────────────────────────────►  (normalize + dedup)  ─────► (same pipeline,
 Slack message ─┘     (one normalized shape)          DealStore.create         same CP-1 HITL stop)
```

Hermes itself (the runtime that watches Drive/email/Slack and calls this) is **out of scope**. We
build only: (1) the envelope schema, (2) the `land_deal_source` contract, (3) the idempotency rule.
Today the manual-upload path (Wave C `/api/jobs` submit) is the *first and only* implementation of
this seam — built so the Hermes paths are a registration, not a refactor.

## The envelope — `DealSourceEnvelope`

Mirrors the Shieldstone Hermes `HermesInvoke` contract (`[[reference_shieldstone-hermes]]`) so a
Hermes agent can construct it directly. Floats/JSON-native; no Decimal.

```jsonc
{
  "source": {
    "kind": "upload" | "drive" | "email" | "slack",   // provenance — the ONLY thing that differs
    "ref": "string",            // upload: client filename batch id; drive: fileId; email: messageId; slack: ts
    "received_at": "ISO-8601",  // when the source produced it (caller-stamped; no clock in the seam)
    "actor": "string"           // who/what: the user email, or "hermes:dream.intake"
  },

  // The deal documents, already fetched to a location the backend can read. Hermes resolves
  // Drive/email/Slack attachments to files BEFORE calling the seam (the seam does not reach out).
  "documents": [
    { "path": "string", "kind": "t12"|"rent_roll"|"om"|"costar"|"mini_model"|"other",
      "filename": "string", "fingerprint": "string" }   // fingerprint = size:mtime or a hash
  ],

  // Optional pre-extracted hints (email triage / Slack may already know these). The Wave-0 gate
  // still validates; these just pre-fill so a complete envelope can run without an extra ask.
  "hints": {
    "deal_name": "string?",
    "routing": "ACQ" | "EFB" | null,        // null => Wave-0 decides / asks once
    "critical_inputs": { "purchase_price": 0, "hold_years": 0, "exit_cap": 0 }  // partial ok
  },

  // Mirrors HermesInvoke.metadata so a Hermes trace threads through to the audit log.
  "metadata": {
    "trace_id": "string",
    "invoked_by": "string",                 // "manual" | the Hermes agentId that dispatched
    "trigger": "manual" | "schedule" | "webhook",
    "mode": "HITL"                          // LOCKED HITL for outward; HOTL is a separate unlock
  },

  // Idempotency: the dedup key. Same key => same deal instance, no duplicate, no double LLM spend.
  // upload: hash(actor + sorted document fingerprints). drive/email/slack: source.kind + source.ref.
  "idempotency_key": "string"
}
```

## The landing contract — `land_deal_source`

One function, the seam's whole API. (Signature is the contract; the body is Wave-C/runtime work.)

```python
def land_deal_source(env: DealSourceEnvelope, store: DealStore, job_store: JobStore,
                     now_iso: str) -> LandResult:
    """Normalize any intake source into a DealStore deal + a Wave C job. Idempotent on
    env.idempotency_key. Returns the deal_id + job_id (existing ones if the key was seen).

    Behavior (all of which the manual /api/jobs submit ALSO does — that's the point):
      1. Dedup: if a job exists for env.idempotency_key -> return it (no new deal/job).
      2. Create a DealStore deal: spec.meta seeded from hints (deal_name, routing, mode=HITL);
         spec starts empty (cells[]/qa/headline_metrics filled by Wave C synthesis).
      3. Seed the state_ledger: critical_inputs from hints (partial ok); record each document as a
         ParsedSource stub (path + fingerprint) so Wave-0 knows what's available.
      4. Create a Wave C job (status=submitted) bound to that deal_id, carrying metadata.trace_id
         into the audit log and source.* into the first AuditEvent (provenance is auditable).
      5. Kick Wave-0 (critical-input gate + routing). If inputs incomplete OR routing ambiguous ->
         the job parks at awaiting_input with OpenQuestions; for a Hermes source that means Hermes
         (or Avery) gets an 'I need X' callback — the SAME pause/resume the UI uses.
    """
```

```jsonc
// LandResult — mirrors HermesResult enough that a Hermes caller can act on it.
{ "deal_id": "string", "job_id": "string", "status": "submitted"|"awaiting_input"|"existing",
  "open_questions": [ /* OpenQuestion[] if awaiting_input */ ], "trace_id": "string" }
```

## Why this is the whole seam (and what is deliberately NOT here)

- **Same instance, same pipeline:** because every path funnels through `land_deal_source` →
  `DealStore.create` → Wave C job, a Drive deal and an uploaded deal are byte-identical downstream.
  The CP-1 HITL stop, the BL gates, the open-questions ledger — all unchanged.
- **Idempotency is first-class:** Hermes watchers re-fire (a Drive poll re-sees a file; an email
  thread gets a reply). The `idempotency_key` guarantees one deal per real-world deal, matching the
  Wave C C.1 acceptance criterion.
- **Provenance is auditable, not behavioral:** `source.*` lands in the audit log's first event;
  it does NOT change the math, the gates, or the mode. (Mode stays HITL for outward work — locked.)
- **NOT built here:** the Drive/email/Slack *watchers*, the Hermes runtime, attachment resolution,
  any HOTL unattended completion. Those are the Hermes track
  (`HERMES_DREAM_AUTONOMY_DESIGN.md`), build-blocked until Hermes is installed on the US VPS.

## Implementation note for whoever wires Hermes later

The manual-upload path built in Wave C (`POST /api/jobs`) **is** the reference implementation of
`land_deal_source` with `source.kind="upload"`. To add a Hermes path: construct a `DealSourceEnvelope`
with the right `source.kind` + resolved `documents`, then call the *same* `land_deal_source`. No new
pipeline. Register the DREAM intake agent under the `dream.*` namespace per
`[[reference_shieldstone-hermes]]`; the envelope's `metadata` already matches `HermesInvoke`.
