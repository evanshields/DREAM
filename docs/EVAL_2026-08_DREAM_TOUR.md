# DREAM v4 Phase 0 — Evaluation Test Drives (2026-08-31)

Two test drives, ~90 min each, then the CRM decision gate. Score each item 1-5 and jot one-line notes; Claude Code transcribes and commits the filled version.

## Part 1 — DREAM app tour (dream.shieldstone.co)

Login with Google or username/password.

| # | Stop | What to do | Score 1-5 | Notes |
|---|------|-----------|-----------|-------|
| 1 | First impression | Log in cold. Is the home/pipeline view self-explanatory? | | |
| 2 | Pipeline views | Flip Cards / Table / Kanban. Try the 3 presets and sorting. Find Esplanade three different ways, then once more with Cmd-K. | | |
| 3 | ACQ underwrite | /underwrite, pick ACQ, drag in an OM or T-12 PDF. Watch prefill, submit, follow the phase readout to the CP-1 stop. | | |
| 4 | EFB underwrite | Same flow with an EFB deal. Check the bond sizing against your gut. | | |
| 5 | Bond screen | /bond-screen: run a quick sizing with exit-cap triangulation. Fast enough for a phone-call screen? | | |
| 6 | Deal page metrics | Open Esplanade (oracle: IRR 0.2251) and Rayzor (oracle: $63,868,907 bonds). Do the headline metrics read right? | | |
| 7 | Assumption dashboard | Change 2-3 assumptions, watch live recalc + sensitivity tables. Would an analyst trust this loop? | | |
| 8 | Memo + Excel | Generate the memo; export the Excel Mini Model. Close enough to house standard to hand to a partner after review? | | |
| 9 | Timeline | Activity tab on a deal: is the unified feed (jobs, notes, tasks) actually useful? | | |
| 10 | CRM rail | On a real deal: add a broker contact, a task with a due date, a note. Rayzor/Esplanade already carry demo CRM data. | | |

**The question that decides Phase 4:** could you run your whole seller / broker / housing-authority / HFA / bank book in this rail as it exists today? What exactly is missing?

**Wrap:** 3 things you'd change tomorrow · 3 things that surprised you (good or bad).

## Part 2 — Twenty CRM spin (dreamcre.co)

The instance already running on the UK VPS (`/opt/twenty-crm`, live at https://dreamcre.co).

| # | Stop | What to do | Score 1-5 | Notes |
|---|------|-----------|-----------|-------|
| 1 | Setup honesty | Load ~20 REAL partner records: mix of sellers, brokers, housing authorities, HFAs, banks (People + Companies). | | |
| 2 | Sourcing pipeline | Build an Opportunities pipeline: Target → Contacted → OM received → Underwriting → LOI → Dead/Won. Drag a few deals through stages. | | |
| 3 | Daily driver test | Log one real day: a call note, 2 tasks, a follow-up. Is this where you'd WANT to live daily? | | |
| 4 | Email | Try the email integration/sync. Does correspondence land on the right records? | | |
| 5 | Views + filters | Build a "my HFAs in Florida" style filtered view. Kanban + table both. | | |
| 6 | Team fit | Imagine Chuck/Alton in here: permissions, assignment, visibility. | | |
| 7 | The seam | With a deal in Underwriting stage: how painful is it that the numbers live in the DREAM app? Would a link-out per deal be enough? | | |

**Wrap:** what does Twenty do that the DREAM rail never will? What does it lack that the deal pages give you?

## Decision gate (fill after both)

Pick one, with a sentence of why:
- [ ] **A. DREAM-on-Twenty** — Twenty is the system of record for people/orgs/pipeline; DREAM keeps deals/underwriting, synced via Twenty's API.
- [ ] **B. Sales CRM inside DREAM** — extend the app's own CRM with orgs, stages, activities. One login, most build time.
- [ ] **C. Twenty beside DREAM** — run both with link-outs only. Cheapest, reversible.

Where does the sales book actually live daily: ______________
