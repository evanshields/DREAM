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
- `backend/jobs/analysts.py`: cells are `{cell, value, source, phase}` and `source` is validated as a string. Headline calculations are fed by `assumptions_engine_inputs`, a separate dict of engine input values.
- `backend/routers/deals.py`: the delete route and the `_assert_can_touch` ownership seam with its `DREAM_STRICT_OWNERSHIP` option.
- `backend/adapters/spec_models.py`: the spec is the master record and the view round-trip preserves each cell's original metadata, so a new key on a cell will ride through untouched. A new top-level key such as `assumptions_engine_inputs_evidence` does not ride through on its own, so slice 5 adds it to the round trip.
- `backend/run_status/adapter.py` and `frontend/src/lib/runStatusApi.ts`: the run status screen already has `source_file` and `source_pointer` on headline rows and a closed evidence state list (`ok`, `missing`, `hash_mismatch`, `unverified`, `unreadable`, `invalid`). The viewer reuses that vocabulary.
- `frontend/src/pages/DealDetail.tsx`: headline tiles (`HeadlineMetricsBlock`, `EFBMetricTiles`) and the `AssumptionDashboard` component, and the open questions list with the "Cited" or "LLM-inferred" badge. These are the click targets.
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
    "unit": "currency",
    "citations": [
      {
        "doc_sha256": "<64 hex chars>",
        "doc_name": "Synthetic_Oak_Court_OM.pdf",
        "doc_kind": "pdf",
        "page": 4,
        "page_width_pt": 612.0,
        "page_height_pt": 792.0,
        "rotation": 0,
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
- `page` is 1-based. `rects_pt` are PDF points with the origin at the top left of the page as displayed, with rotation applied (the pymupdf convention), one rectangle per line when the match wraps. `page_width_pt`, `page_height_pt` and `rotation` are read from that same displayed page, so the rectangles and the rendered image share one coordinate space.
- `unit` is a closed set: `currency`, `ratio`, `pct_points`, `count`, `text`. It says how the cell value is stored, so the check never guesses a scale. A `ratio` is stored as a fraction such as 0.055 and shown in a document as 5.5%. A `pct_points` value is stored as 5.5 and shown as 5.5%.
- `matched_text` must normalise to the cell value. Normalising is a text comparison done outside the Decimal seam on purpose, so no Decimal is introduced outside `engine_boundary.py`. Both sides are reduced to a plain digit string: strip `$`, `,`, `%` and spaces, read a value in parentheses as negative, and drop trailing zeros after a decimal point, so `$41,250,000.00` matches 41250000 and `5.50%` matches 5.5. For a `ratio` the document text is shifted two places by moving the point in the string, not by arithmetic. Anything else, such as `$41.25M`, `41.25MM` or a range, does not normalise: the citation is `unverified` with the reason "format not supported in v1", never a guess. A citation whose `matched_text` does not normalise to the cell value is invalid, except inside a `conflict`.
- Two citations that disagree on value make the whole cell `conflict`, shown with both, never resolved silently. This is the only case where a stored citation may disagree with the cell value, and the locator is what produces it (section 3).
- Saving keeps evidence honest. `spec_to_view` and `view_to_spec` carry `evidence` on cells and the top-level `assumptions_engine_inputs_evidence` map through unchanged. When a save changes a cell value or an engine-input value from the stored one, that item's evidence is replaced in the same save with `{"basis": "manual_entry", "citations": [], "reason": "typed by a person"}`, so a stale document line is never kept for a value a person overrode. An unchanged value keeps its evidence byte for byte.
- A spreadsheet citation uses `doc_kind: "xlsx"`, `sheet` and `cell_ref` in place of `page` and `rects_pt`.
- Computed outputs (headline metrics) do not carry `evidence`. They are covered by a fixed lineage table in code, `metric -> [input identifiers]`. An identifier is one of two kinds. A cell address (`B10`) names a mapped spreadsheet cell. An engine-input key (`stabilized_noi`) names a value in `assumptions_engine_inputs`, which is how `backend/jobs/analysts.py` and `backend/jobs/synthesis.py` feed the headline calculations. Example: `irr -> [cell:B10, cell:B45, engine:stabilized_noi, ...]`. The table is written by hand, reviewed, and tested to only name cells that exist in the routing's field map and engine-input keys that exist in the deal's engine inputs.
- Engine-input keys carry evidence too. Each key in `assumptions_engine_inputs` gets a sibling `assumptions_engine_inputs_evidence` map, `key -> evidence object` in the same shape as a cell's `evidence`. The existing engine-input dict is left untouched so the engine bridge and every existing test keep working. A key with no evidence entry is shown as `no_source` with the reason "no source recorded".

### 2. Document store

- New `backend/store/document_store.py`, content-addressed by SHA-256. It is inside `backend/store/` so the rule about database access stays intact.
- Bytes live on disk under a configurable root (`DREAM_DOC_ROOT`), as `<root>/<sha[0:2]>/<sha>.bin`, plus two small tables. `blobs` holds one row per file: `(sha256 primary key, size, doc_kind, uploaded_by, uploaded_at, orphaned_at)`, where `orphaned_at` stays empty until the last link to the file is removed. `deal_documents` holds one row per link: `(deal_id, sha256, doc_name, linked_at)` with primary key `(deal_id, sha256)`. One file can be linked to several deals, and a blob keeps its own dates after any link is deleted.
- Write is idempotent on hash. Read recomputes the hash of the bytes and refuses on mismatch (hash mismatch is a hard stop).
- Size cap per file (proposed 50 MB) and a page cap for rendering (proposed 500 pages).
- `POST /api/intake` keeps its current response and additionally stores the file and returns its `doc_sha256`. Linking a document to a deal happens when the deal is saved.
- Lifecycle contract. Documents are confidential, so the plan states what happens at every end of life:
  - Deal deletion. The existing delete route (`delete_deal` in `backend/routers/deals.py`) must also remove every link row for that deal in the same step. After that, a document with no links left becomes unreferenced, and the same step sets `orphaned_at` on its `blobs` row.
  - Unlinked page requests. A hash with no remaining link to a deal the caller can read answers 404 immediately, even while the bytes still sit on disk.
  - Abandoned uploads. An intake upload that is never attached to a saved deal stays unreferenced. Its `blobs` row has no `deal_documents` row, which is how such rows are found, and its clock is `uploaded_at`.
  - Retention policy for unreferenced blobs (proposed, for Evan to confirm). A scheduled sweep deletes the bytes and the `blobs` row of any blob with no links that is older than 7 days by `uploaded_at`. A blob with `orphaned_at` set and still no links is deleted on the next sweep. A blob that gains a link before the sweep is kept and its `orphaned_at` is cleared. The sweep logs counts only, never file names. A dry run mode reports what it would delete before the first real run.
  - Archive keeps links. Archiving a deal does not remove its documents, and unarchiving works as before.
  - Authorization. Every read of a stored document goes through the current deal check described in section 4. Upload requires `require_auth` and records `uploaded_by`.

### 3. Locator (where on the page)

- New pure module `backend/evidence/locator.py`. Input is document bytes, a label list and a target value. Output is every candidate citation for the label, each with its own `matched_text`, including a line where the label sits next to a value that differs from the target. A candidate is never dropped for differing from the target, because that is how a conflict is seen.
- It uses pymupdf `page.get_text("words")` to get each word with its box, groups words into lines, and looks for every line holding a label and a number, or a number within a fixed distance to the right of or below a label. Words and boxes are taken from the page as displayed, with rotation applied, and `page_width_pt`, `page_height_pt` and `rotation` come from that same page.
- Classification, in this order. No candidate gives `basis: none` with reason "not found in document". Any candidate whose value differs from the target (after the normalisation in section 1) gives `conflict`, which lists every candidate. If every candidate agrees with the target, one location gives a citation and more than one distinct location gives `ambiguous`, which lists every candidate and picks none. It never picks the first match the way the current regex does.
- The current regex extractor stays as is for prefill values. The locator runs after it to attach position, and if the locator cannot confirm the value, the value is still prefilled but marked unverified.

### 4. Backend endpoints

Both live in a new `backend/routers/evidence.py`, mounted in `main.py` with `dependencies=[Depends(require_auth)]` like every other router. Both are GET only.

`GET /api/deals/{deal_id}/evidence/{field}`

- `field` is a cell address (`B10`), an engine-input key (`stabilized_noi`), a headline metric key (`irr`), or a declared target from an open question (see "Assumption and open-question targets" below). The server resolves the kind from the deal itself and never guesses. A name that matches more than one kind is rejected as `invalid`.
- For a cell it returns the stored contract plus a server-computed `state` per citation: the server loads the document by hash, re-extracts the words on that page, and checks that `matched_text` is present inside `rects_pt` (with a small tolerance) and still normalises to the cell value.
- For an engine-input key it returns the stored evidence from `assumptions_engine_inputs_evidence`, verified the same way as a cell.
- For a metric it returns `{kind: "computed", value, inputs: [{field, kind, value, state}]}` from the lineage table, where `kind` is `cell` or `engine_input`.
- Response states reuse the run status vocabulary and add three: `ok`, `missing`, `hash_mismatch`, `unverified`, `unreadable`, `invalid`, `ambiguous`, `conflict`, `no_source`.
- 404 for an unknown deal or field.
- Authorization is checked against the deal on every request, not once at upload. The route calls the same ownership seam the deals router uses (`_assert_can_touch` in `backend/routers/deals.py`) so it honours `DREAM_STRICT_OWNERSHIP`. Under strict ownership another owner's deal answers 404, never 403. Under the current default everyone reads all deals, and the viewer follows that. The viewer never adds a looser rule than the deal page itself.

#### Assumption and open-question targets

- The assumptions area of the deal page is the interactive `AssumptionDashboard` component. Each interactive control is mapped in a fixed table in code, `control -> evidence field`, pointing at the cell or engine-input key it seeds. A control with no mapping shows `no_source` with the reason "not tied to a source". A control the analyst has changed in the browser shows `manual_entry` with the reason "typed by a person", because the viewer must not show a document line for a value a person overrode.
- Open questions can name a target that is not a spreadsheet cell, for example `meta.routing`. Each open question is mapped by a second fixed table, `declared target -> evidence field`. A target that is a deal setting rather than a figure (such as `meta.routing`) returns `{kind: "setting", value, basis, reason}` with the basis taken from how it was decided (a person chose it, a policy default, or a model inferred it). It never returns a page image. A target that is in neither table returns `no_source` with the reason "unknown target". Nothing is ever dropped silently.
- Both tables are tested the same way as the lineage table. Every target they name must exist, and every target the page can display must have an entry.

`GET /api/documents/{sha256}/pages/{page}.png?scale=2`

- Renders one page with pymupdf to PNG, as displayed with rotation applied, the same space the rectangles are measured in. Highlight boxes are drawn by the browser on top, not burned into the image, so one cached page serves every number on it.
- Only serves a hash that is linked to at least one deal the caller is currently allowed to read, using the same ownership seam, so `DREAM_STRICT_OWNERSHIP` applies. A valid hash that is not linked, or linked only to deals the caller may not read, gets 404, the same as a missing one, so hashes cannot be probed.
- Validates `page` within the page count and `scale` within a small allowed set. `Cache-Control: private`.
- Re-hashes the bytes before rendering, and refuses with 409 on mismatch.

### 5. Front-end component

- New `frontend/src/components/evidence/EvidenceDrawer.tsx` plus `frontend/src/lib/evidenceApi.ts` types mirroring the backend contract.
- A shared `SourcedValue` wrapper for any number on the deal page. It renders the value, a small source icon coloured by state, and opens the drawer on click or Enter. It is a real button with an `aria-label` such as "Show source for Purchase Price".
- Drawer layout, top to bottom: field name and value, a state line in words, document name and page, the page image with absolutely positioned highlight boxes scaled from points to pixels using `page_width_pt` for x and `page_height_pt` for y (two separate factors, each against the rendered image's own width and height), then `line_text` as selectable text.
- Computed metric drawer: value, then the list of inputs as `SourcedValue` rows. Clicking one swaps the drawer to that input, with a back link.
- Every non-`ok` state shows a sentence and no page image. Examples: "The file this came from has changed since it was read, so the location cannot be trusted." or "A model estimated this. No document supports it."
- Wired into `HeadlineMetricsBlock`, `EFBMetricTiles` and the `AssumptionDashboard` controls and open questions on `DealDetail.tsx`, using the mapping tables from section 4. The existing "Cited" and "LLM-inferred" badge stays.
- The drawer closes on Escape and returns focus to the number that opened it. It works at phone width as a full-screen sheet.

### 6. Test plan (red first, synthetic only)

Fixtures:

- `backend/fixtures/evidence/build_synthetic_docs.py` generates PDFs at test time with pymupdf for an invented property, "Synthetic Oak Court, 1 Example Way". Every fixture says SYNTHETIC on each page. No real deal file, name or figure is used or copied.
- Fixture set: a clean five-page offering memo with the purchase price on page four, one where the purchase price appears twice with different values (conflict), one where the same value appears under two labels (ambiguous), one with the price split across a line wrap, one image-only page (no text layer), a one-byte-changed copy (hash mismatch), a clean page rotated 90 degrees, and a small synthetic rent roll spreadsheet.

Red tests to write before each slice's code (each must be seen failing first, then passing):

1. Contract: unknown `basis` is invalid. `document` with no citations is invalid. Non-document with citations is invalid. `matched_text` that does not normalise to the value is invalid. Normalisation cases: `$41,250,000.00` matches 41250000, `5.50%` matches a `pct_points` 5.5 and a `ratio` 0.055, `($12,500)` matches -12500, and `$41.25M` is `unverified` with the reason "format not supported in v1".
2. Store: round-trip by hash, idempotent re-write, tampered bytes refuse, oversize refuses, no `sqlite3` import outside `backend/store/` (existing guard still green), one file linked to two deals keeps its bytes until both links are gone, and a `blobs` row keeps its `uploaded_at` after its last link is deleted.
3. Locator: clean memo gives page 4 and a rectangle containing the price words. Duplicate value gives `ambiguous`. The same label next to two different values gives `conflict` listing both, even when one of them equals the target. Image-only gives `none` with a reason. Wrapped value gives two rectangles. On the page rotated 90 degrees, a box drawn from the rectangles onto the rendered PNG covers the price words.
4. Spec round-trip: a spec with `evidence` on cells survives `spec_to_view` then `view_to_spec` byte-identical, and the memo assumptions output is unchanged. The top-level `assumptions_engine_inputs_evidence` map survives the same round trip. Changing a cell value and changing an engine-input value each turn that item's evidence into `manual_entry` on save, and an item left unchanged keeps its evidence byte for byte.
5. Evidence endpoint: 401 without a token, 404 for unknown deal or field, `ok` on clean fixture, `hash_mismatch` after swapping bytes on disk, `unverified` when stored rectangles are moved, computed metric returns its input list.
6. Page endpoint: 401 without a token, 404 for unlinked hash, 400 for page 0 or past the end, 409 on tampered bytes, PNG magic bytes on success.
7. Lineage table: every named cell exists in the routing's field map, every named engine-input key exists in the deal's engine inputs, and every headline metric shown on the page has an entry. A metric whose inputs include an engine-input key returns that key with its evidence or `no_source`.
7a. Targets: every assumption control and open-question target has a table entry. `meta.routing` returns a `setting` answer with no page image. An unknown target returns `no_source`.
7b. Lifecycle: deleting a deal removes its links and the page route then answers 404. Under `DREAM_STRICT_OWNERSHIP` another owner gets 404 on both routes. An unlinked blob older than the retention window is removed by the sweep and a younger one is kept. The sweep dry run deletes nothing.
8. Front end: `tsc --noEmit` and `npm run build` green. A component test (or, if the repo still has no front-end test runner, a fixture-driven story page checked by a Playwright screenshot) for `ok`, `no_source`, `hash_mismatch`, `ambiguous` and computed states.
9. Oracles: Esplanade ACQ IRR 0.2251 and Rayzor EFB $63,868,907 unchanged after every slice. The existing suite stays green on every slice.

### 7. Risks and how each is handled

| Risk | Handling |
|---|---|
| Real deal documents end up in the cloud or in git | Fixtures are generated in tests from invented text. `DREAM_DOC_ROOT` is outside the repo and git-ignored. A test fails if any file under `backend/fixtures/evidence/` lacks the SYNTHETIC marker. |
| A highlight points at the wrong line and looks authoritative | Locator abstains on zero or many matches. The server re-verifies on every view. Non-`ok` states show no image. |
| A computed number pointed at one line gives false comfort | Outputs show their input list only, never a page. |
| Stored confidential memos widen the attack surface | Auth on both routes, deal check on every request including strict ownership, hash only served when linked to a readable deal, links removed on deal deletion, unreferenced blobs swept after the retention window, size and page caps, private caching, files stored outside the web root. Backup of the document folder goes into the deploy runbook before go-live. |
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
| 3 | `backend/store/document_store.py` content-addressed store, link cleanup on deal deletion, unreferenced-blob sweep | Store and lifecycle tests green, existing storage guard still green |
| 4 | `backend/evidence/locator.py` word locator | All locator cases green on fixtures, including conflict and the rotated page |
| 5 | Intake stores the file and attaches `evidence` to extracted cells and engine-input keys | Intake response keeps its shape plus `doc_sha256`. Spec round-trip byte-identical, sibling evidence map included. An edited value becomes `manual_entry` on save. Memo test unchanged |
| 6 | `GET /api/deals/{id}/evidence/{field}` with server re-verify and the per-request deal check | Endpoint and auth tests green, mounted with `require_auth`, strict ownership honoured |
| 7 | `GET /api/documents/{sha}/pages/{n}.png` | Page endpoint tests green |
| 8 | Lineage table (cells and engine-input keys), assumption and open-question target tables, and the computed and setting branches of the evidence endpoint | Lineage and target tests green |
| 9 | `evidenceApi.ts`, `SourcedValue`, `EvidenceDrawer` built against fixture JSON only | Typecheck and build green, state screenshots attached to the PR |
| 10 | Wire into `DealDetail.tsx` tiles, assumptions and open questions. End-to-end run on a synthetic deal locally | Clicking each number on the synthetic deal opens the right page and box. Oracles unchanged |

Dependencies: 1 before everything. 2 before 3 and 4. 3 and 4 before 5. 5 before 6 and 7. 6 before 8. 9 can run in parallel with 3 to 8 because it only needs the contract from slice 1. 10 needs 6, 7, 8 and 9.

Agent use: one implementation agent per slice, no parallel workers by default. Slice 9 is the one candidate to run alongside the backend slices, which stays within the two extra runs ceiling.

### 9. Open questions for Evan

1. Is it acceptable to keep uploaded deal documents on the US server disk (outside the repo, backed up with the database)? The viewer cannot work without stored files.
2. Should the first version cover spreadsheet sources with a highlighted grid, or is "Sheet, cell" text enough for now? This plan assumes text only.
3. Is a 7 day retention window for unreferenced documents right, or should abandoned uploads be kept longer?
