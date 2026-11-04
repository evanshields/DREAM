# Evidence viewer on the deal page: plan

Date: 2026-11-03. Status: plan only, no code. Branch `cloud/2026-11-03-app-evidence-viewer-plan`.

## Bottom line

An analyst clicks any number on the deal page and a side panel opens showing the source document, the page, and the exact line highlighted, or an honest "no source on file" with the reason. Ten small slices get there, each one a 45-minute job, each starting with a failing test on invented documents.

## Plain English

### What the analyst will see

1. The deal page shows the numbers it shows today (purchase price, units, exit cap, IRR and so on).
2. Every number gets a small source marker. Clicking the number or the marker opens a panel on the right.
3. For a number typed straight from a document (an input), the panel shows the document name, the page number, a picture of that page, and a yellow box over the line the number came from. Below the picture is the line as plain text, so it can be copied.
4. For a number the engine calculated (an output such as IRR), there is no single line to point at. The panel instead lists the inputs that fed it. Each input is clickable and opens its own page and line. This avoids the false comfort of pointing an IRR at one random line.
5. When a number has no document behind it, the panel says so in words. The possible reasons are: a model guessed it, it is a policy default, a person typed it, the file it came from has changed since, or the source could not be found. It never shows a page that only looks right.

### Why it matters

- Review gets faster. Today the analyst has to open the offering memo and hunt for each figure.
- It enforces the house rule that a made-up number is worse than a blank one. A number that cannot show its line is visibly marked.
- It keeps the engine as the only calculator. The viewer only displays and checks. It never computes or changes a figure.

### What has to be true underneath

- The uploaded documents must be kept. Today the intake step reads a file, pulls numbers out of it, and throws the file away, so there is nothing to show later.
- Each extracted number must remember where it was found: which file, which page, and where on the page.
- The server must re-check that location itself every time it is shown, rather than trusting what was stored. If the file changed or the line no longer says that number, the panel says "could not verify" instead of showing it.

### What it deliberately does not do

- No editing of numbers from the panel.
- No reading of scanned image-only PDFs in the first version (no text layer means no line to point at, so it abstains and says so).
- No spreadsheet cell highlighting in the first version. A rent roll value from a spreadsheet shows "Sheet name, cell address" as text only.
- No model call anywhere in the viewer path.
- No real deal files in tests, fixtures or this cloud session.

## Inputs read for this plan

All read at main commit `953cda4835602bbdfcf3df767adca936ddece3b5`. No real deal file was opened.

- `AGENTS.md` and `docs/DREAM_PRD_V4.md` (governing rules: fail closed, flag never guess, no self-certification, engines only for numbers).
- `backend/intake/intake_service.py`: intake uses pymupdf (`fitz`) to flatten the PDF to one text string, then regex finds the first dollar figure near a label. Page and position are lost, and the file bytes are not stored.
- `backend/jobs/contracts.py`: values carry a `source` string, either `llm-inferred` or a free-text citation such as "OM p.3". That free text is the only provenance today.
- `backend/jobs/analysts.py`: cells are `{cell, value, source, phase}` and `source` is validated as a string.
- `backend/adapters/spec_models.py`: the spec is the master record and the view round-trip preserves each cell's original metadata, so a new key on a cell will ride through untouched.
- `backend/run_status/adapter.py` and `frontend/src/lib/runStatusApi.ts`: the run status screen already has `source_file` and `source_pointer` on headline rows and a closed evidence state list (`ok`, `missing`, `hash_mismatch`, `unverified`, `unreadable`, `invalid`). The viewer reuses that vocabulary.
- `frontend/src/pages/DealDetail.tsx`: headline tiles (`HeadlineMetricsBlock`, `EFBMetricTiles`) and the open questions list with the "Cited" or "LLM-inferred" badge. These are the click targets.
- `backend/requirements.txt`: `pymupdf==1.24.11` is already a dependency, so word positions and page rendering need no new library.

## Technical detail

### 1. Data contract (what the pipeline must emit per number)

"Engine" here means the app's deterministic pipeline around the engine (intake, spec, `engine_boundary`). The vendored `underwriting-engine/` is untouched and is not asked to emit anything new.

Each spec cell gains one optional key, `evidence`. The existing `source` string stays exactly as it is, so older deals, the memo writer and every existing test keep working.

```json
{
  "cell": "B10",
  "value": 41250000,
  "source": "OM p.4",
  "phase": 3,
  "evidence": {
    "schema": "dream.evidence.v1",
    "basis": "document",
    "citations": [
      {
        "doc_sha256": "<64 hex chars>",
        "doc_name": "Synthetic_Oak_Court_OM.pdf",
        "doc_kind": "pdf",
        "page": 4,
        "page_width_pt": 612.0,
        "page_height_pt": 792.0,
        "rects_pt": [[72.0, 310.5, 388.2, 324.1]],
        "line_text": "Purchase Price $41,250,000",
        "matched_text": "$41,250,000",
        "label_text": "Purchase Price",
        "locator": "intake.word_locator",
        "locator_version": "1"
      }
    ]
  }
}
```

Rules for the contract:

- `basis` is a closed set: `document`, `llm_inferred`, `policy_default`, `manual_entry`, `none`. Anything else is rejected as `invalid`.
- `document` needs at least one citation. Every other basis must have zero citations and a `reason` string.
- `page` is 1-based. `rects_pt` are PDF points with the origin at the top left of the page (the pymupdf convention), one rectangle per line when the match wraps.
- `matched_text` must normalise to the cell value. Normalising means stripping `$`, `,`, `%` and spaces and comparing as text against the cell value written the same way, with a percent cell compared after a fixed scale of 100. This is a text comparison done outside the Decimal seam on purpose, so no Decimal is introduced outside `engine_boundary.py`.
- Two citations that disagree on value make the whole cell `conflict`, shown with both, never resolved silently.
- A spreadsheet citation uses `doc_kind: "xlsx"`, `sheet` and `cell_ref` in place of `page` and `rects_pt`.
- Computed outputs (headline metrics) do not carry `evidence`. They are covered by a fixed lineage table in code, `metric -> [input cell addresses]`, for example `irr -> [B10, B45, B79, B80, B81, ...]`. The table is written by hand, reviewed, and tested to only name cells that exist in the routing's field map.

### 2. Document store

- New `backend/store/document_store.py`, content-addressed by SHA-256. It is inside `backend/store/` so the rule about database access stays intact.
- Bytes live on disk under a configurable root (`DREAM_DOC_ROOT`), as `<root>/<sha[0:2]>/<sha>.bin`, plus a small index table `(sha256, deal_id, doc_name, doc_kind, size, uploaded_by, uploaded_at)`.
- Write is idempotent on hash. Read recomputes the hash of the bytes and refuses on mismatch (hash mismatch is a hard stop).
- Size cap per file (proposed 50 MB) and a page cap for rendering (proposed 500 pages).
- `POST /api/intake` keeps its current response and additionally stores the file and returns its `doc_sha256`. Linking a document to a deal happens when the deal is saved.

### 3. Locator (where on the page)

- New pure module `backend/evidence/locator.py`. Input is document bytes, a label list and a target value. Output is zero, one or many candidate citations.
- It uses pymupdf `page.get_text("words")` to get each word with its box, groups words into lines, and looks for a line holding both a label and the value, or the value within a fixed distance to the right of or below a label.
- One match gives a citation. Zero matches gives `basis: none` with reason "not found in document". More than one distinct match gives `ambiguous`, which lists every candidate and picks none. It never picks the first match the way the current regex does.
- The current regex extractor stays as is for prefill values. The locator runs after it to attach position, and if the locator cannot confirm the value, the value is still prefilled but marked unverified.

### 4. Backend endpoints

Both live in a new `backend/routers/evidence.py`, mounted in `main.py` with `dependencies=[Depends(require_auth)]` like every other router. Both are GET only.

`GET /api/deals/{deal_id}/evidence/{field}`

- `field` is a cell address (`B10`) or a headline metric key (`irr`).
- For a cell it returns the stored contract plus a server-computed `state` per citation: the server loads the document by hash, re-extracts the words on that page, and checks that `matched_text` is present inside `rects_pt` (with a small tolerance) and still normalises to the cell value.
- For a metric it returns `{kind: "computed", value, inputs: [{field, value, state}]}` from the lineage table.
- Response states reuse the run status vocabulary and add three: `ok`, `missing`, `hash_mismatch`, `unverified`, `unreadable`, `invalid`, `ambiguous`, `conflict`, `no_source`.
- 404 for an unknown deal or field. Ownership follows the current deals router read rule (everyone reads all).

`GET /api/documents/{sha256}/pages/{page}.png?scale=2`

- Renders one page with pymupdf to PNG. Highlight boxes are drawn by the browser on top, not burned into the image, so one cached page serves every number on it.
- Only serves a hash that is linked to at least one deal the caller can read. A valid hash that is not linked gets 404, the same as a missing one, so hashes cannot be probed.
- Validates `page` within the page count and `scale` within a small allowed set. `Cache-Control: private`.
- Re-hashes the bytes before rendering, and refuses with 409 on mismatch.

### 5. Front-end component

- New `frontend/src/components/evidence/EvidenceDrawer.tsx` plus `frontend/src/lib/evidenceApi.ts` types mirroring the backend contract.
- A shared `SourcedValue` wrapper for any number on the deal page. It renders the value, a small source icon coloured by state, and opens the drawer on click or Enter. It is a real button with an `aria-label` such as "Show source for Purchase Price".
- Drawer layout, top to bottom: field name and value, a state line in words, document name and page, the page image with absolutely positioned highlight boxes scaled from points to pixels using `page_width_pt`, then `line_text` as selectable text.
- Computed metric drawer: value, then the list of inputs as `SourcedValue` rows. Clicking one swaps the drawer to that input, with a back link.
- Every non-`ok` state shows a sentence and no page image. Examples: "The file this came from has changed since it was read, so the location cannot be trusted." or "A model estimated this. No document supports it."
- Wired into `HeadlineMetricsBlock`, `EFBMetricTiles` and the assumptions and open questions lists on `DealDetail.tsx`. The existing "Cited" and "LLM-inferred" badge stays.
- The drawer closes on Escape and returns focus to the number that opened it. It works at phone width as a full-screen sheet.

### 6. Test plan (red first, synthetic only)

Fixtures:

- `backend/fixtures/evidence/build_synthetic_docs.py` generates PDFs at test time with pymupdf for an invented property, "Synthetic Oak Court, 1 Example Way". Every fixture says SYNTHETIC on each page. No real deal file, name or figure is used or copied.
- Fixture set: a clean three-page offering memo, one where the purchase price appears twice with different values (conflict), one where the same value appears under two labels (ambiguous), one with the price split across a line wrap, one image-only page (no text layer), a one-byte-changed copy (hash mismatch), and a small synthetic rent roll spreadsheet.

Red tests to write before each slice's code (each must be seen failing first, then passing):

1. Contract: unknown `basis` is invalid. `document` with no citations is invalid. Non-document with citations is invalid. `matched_text` that does not normalise to the value is invalid.
2. Store: round-trip by hash, idempotent re-write, tampered bytes refuse, oversize refuses, no `sqlite3` import outside `backend/store/` (existing guard still green).
3. Locator: clean memo gives page 4 and a rectangle containing the price words. Duplicate value gives `ambiguous`. Conflicting values give `conflict`. Image-only gives `none` with a reason. Wrapped value gives two rectangles.
4. Spec round-trip: a spec with `evidence` on cells survives `spec_to_view` then `view_to_spec` byte-identical, and the memo assumptions output is unchanged.
5. Evidence endpoint: 401 without a token, 404 for unknown deal or field, `ok` on clean fixture, `hash_mismatch` after swapping bytes on disk, `unverified` when stored rectangles are moved, computed metric returns its input list.
6. Page endpoint: 401 without a token, 404 for unlinked hash, 400 for page 0 or past the end, 409 on tampered bytes, PNG magic bytes on success.
7. Lineage table: every named input exists in the routing's field map, and every headline metric shown on the page has an entry.
8. Front end: `tsc --noEmit` and `npm run build` green. A component test (or, if the repo still has no front-end test runner, a fixture-driven story page checked by a Playwright screenshot) for `ok`, `no_source`, `hash_mismatch`, `ambiguous` and computed states.
9. Oracles: Esplanade ACQ IRR 0.2251 and Rayzor EFB $63,868,907 unchanged after every slice. The existing suite stays green on every slice.

### 7. Risks and how each is handled

| Risk | Handling |
|---|---|
| Real deal documents end up in the cloud or in git | Fixtures are generated in tests from invented text. `DREAM_DOC_ROOT` is outside the repo and git-ignored. A test fails if any file under `backend/fixtures/evidence/` lacks the SYNTHETIC marker. |
| A highlight points at the wrong line and looks authoritative | Locator abstains on zero or many matches. The server re-verifies on every view. Non-`ok` states show no image. |
| A computed number pointed at one line gives false comfort | Outputs show their input list only, never a page. |
| Stored confidential memos widen the attack surface | Auth on both routes, hash only served when linked to a readable deal, size and page caps, private caching, files stored outside the web root. Backup and retention of the document folder goes into the deploy runbook before go-live. |
| A future agent driver supplies its own citations | Treated as claims. The server locator and verifier must confirm them before `ok`. No self-certification. |
| Scanned PDFs without text | Shown as `unreadable` with a reason. OCR is a separate later decision. |
| pymupdf version change moves boxes | `locator_version` stored. Verification tolerates small drift. A version bump is its own slice with fixture re-checks. |
| Page rendering is slow on big files | One page per request, cached by hash, page, scale. Page cap. |
| Older deals have no `evidence` | Panel shows the old free-text `source` with state `unverified` and the line "Recorded before source tracking." |
| Malicious PDF | Rendering stays in-process for v1 with caps. Moving rendering to a separate worker process is noted as a hardening follow-up. |

### 8. Slice order (each one 45-minute job)

Each slice is one branch, one draft PR, red tests first, full backend suite green, front-end typecheck and build green where touched, oracles checked. No slice deploys. Deploy is a separate step after slice 10 per the runbook.

| # | Slice | Done when |
|---|---|---|
| 1 | Contract module `backend/evidence/contract.py` with a pure validator and closed state list | Contract red tests written, seen failing, then green |
| 2 | Synthetic fixture builder plus SYNTHETIC-marker guard test | Fixture set builds in a temp folder during tests, guard green |
| 3 | `backend/store/document_store.py` content-addressed store | Store tests green, existing storage guard still green |
| 4 | `backend/evidence/locator.py` word locator | All locator cases green on fixtures |
| 5 | Intake stores the file and attaches `evidence` to extracted cells | Intake response keeps its shape plus `doc_sha256`. Spec round-trip byte-identical. Memo test unchanged |
| 6 | `GET /api/deals/{id}/evidence/{field}` with server re-verify | Endpoint and auth tests green, mounted with `require_auth` |
| 7 | `GET /api/documents/{sha}/pages/{n}.png` | Page endpoint tests green |
| 8 | Lineage table for headline metrics plus the computed branch of the evidence endpoint | Lineage tests green |
| 9 | `evidenceApi.ts`, `SourcedValue`, `EvidenceDrawer` built against fixture JSON only | Typecheck and build green, state screenshots attached to the PR |
| 10 | Wire into `DealDetail.tsx` tiles, assumptions and open questions. End-to-end run on a synthetic deal locally | Clicking each number on the synthetic deal opens the right page and box. Oracles unchanged |

Dependencies: 1 before everything. 2 before 3 and 4. 3 and 4 before 5. 5 before 6 and 7. 6 before 8. 9 can run in parallel with 3 to 8 because it only needs the contract from slice 1. 10 needs 6, 7, 8 and 9.

Agent use: one implementation agent per slice, no parallel workers by default. Slice 9 is the one candidate to run alongside the backend slices, which stays within the two extra runs ceiling.

### 9. Open questions for Evan

1. Is it acceptable to keep uploaded deal documents on the US server disk (outside the repo, backed up with the database)? The viewer cannot work without stored files.
2. Should the first version cover spreadsheet sources with a highlighted grid, or is "Sheet, cell" text enough for now? This plan assumes text only.
