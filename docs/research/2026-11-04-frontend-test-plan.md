# DREAM frontend: fail-closed test plan (F01 to F29)

Date 2026-11-04. Report only. No code, config or package changed. Nothing installed. Source: `docs/research/2026-11-04-app-fail-closed-test-gap-map.md` on branch `cloud/2026-11-04-app-test-gap-map`, rows F01 to F29. Line numbers come from that map and may drift.

## 0. Runner note

Every test below needs a frontend test runner. None exists today (`frontend/package.json` has no vitest, jest or testing-library, and there are no `*.test.*` files). Once Evan approves one, the plan assumes this shape (a proposal, not installed):
- Vitest with the jsdom environment, React Testing Library, `@testing-library/user-event`, and `@testing-library/jest-dom`.
- Network mocked by stubbing `globalThis.fetch` with `vi.fn()` that returns `new Response(JSON.stringify(body), {status})`. No live service, no secrets, no real token.
- All data is synthetic: deal id `deal-test-1`, token `test-token`, round numbers such as IRR 0.2 and bond 1000000.
- Pure-function tests (F17, F25) need only the runner, not jsdom.

"Fail closed" here means: when data is missing, wrong, stale or errored, the screen shows a blank (`—`), an error, or nothing. It never shows an old or invented number.

Legend: Pri from the map (H, M, L). HOLD = snapshot panel or evidence viewer area the other team is building. Write the test plan now, do not write the test until HOLD clears.

## 1. Auth and API client

### 1a. `auth/RequireAuth.tsx`, `auth/AuthContext.tsx`, `lib/api.ts`

**F01 (M) RequireAuth redirects without a token**
- Component: `RequireAuth` inside `AuthProvider` and `MemoryRouter` at `/pipeline`, with routes `/login` and a child `<div>secret</div>`.
- Setup: `localStorage` empty. Mock `/api/me` to never be called.
- Action: render.
- Assert: `secret` is not in the document, the login route text is shown. While `ready` is false, neither the child nor a redirect flashes (render with a pending `/api/me` promise, assert the child is absent).
- Runner: needed.

**F02 (M) 401 clears the token**
- Component: `AuthProvider` plus a probe that calls `getJSON('/api/deals')` from `lib/api.ts`.
- Setup: `setAuthToken('test-token')`. Mock fetch to return status 401 `{detail:"expired"}`. Register the handler through `setUnauthorizedHandler`.
- Action: call the API, then render the provider with a stored token and a 401 from `/api/me`.
- Assert: `getAuthToken()` is `null`, the handler fired once, the app shows the "session expired" text and the login route. The child never renders.
- Runner: needed.

**F03 (L) ApiError carries the server detail**
- Component: `lib/api.ts` request helper.
- Setup: fetch returns 422 `{detail:"exit cap must be positive"}`.
- Action: await the call inside `expect(...).rejects`.
- Assert: error is an `ApiError`, `status` is 422, message equals the detail text. A non-JSON 500 body gives a generic message, not `undefined`.
- Runner: needed.

**F26 (L) Unknown URL goes to pipeline**
- Component: `App` routes.
- Setup: token present, `/api/me` mocked 200, `/api/deals` mocked `[]`. `MemoryRouter` at `/nope/nothing`.
- Action: render.
- Assert: location is `/pipeline`. With no token the same URL ends on `/login`.
- Runner: needed.

### 1b. `lib/download.ts`, `lib/api.ts` export path

**F28 (M) Export does not save error JSON as a workbook**
- Component: the export call in `lib/api.ts` (lines 839-870) with `downloadBlob` spied.
- Setup: `vi.spyOn(download, 'downloadBlob')`. Fetch returns 200 with `Content-Type: application/json` and body `{"ok":false,"refusals":["identity mismatch"]}`.
- Action: call the export function.
- Assert: `downloadBlob` called 0 times, the function resolves with the JSON report. Second case: `Content-Type` is the xlsx type, `downloadBlob` called once with a `.xlsx` filename.
- Runner: needed.

## 2. Number formatting and live calc

### 2a. `lib/format.ts`

**F25 (L) Formatters guard bad input**
- Component: `fmtUSD`, `fmtPct`, `fmtEM` (today they have no guard, so this test is red first).
- Setup: none.
- Action: call each with `NaN`, `Infinity`, `-72`, and (cast) `undefined` and `"1"`.
- Assert: `NaN`, `Infinity`, `undefined` and strings return `—`. A negative value is not printed as `$-72` for a bond or loan (decision for Evan, see section 8). Normal inputs still format (`fmtPct(0.2)` is `20.00%`).
- Runner: needed.

### 2b. `components/livecalc.tsx`

**F14 (H) useLiveCalc clears the result when a recalc fails**
- Component: `useLiveCalc` through a small test host that prints `result` and `error`.
- Setup: fake timers. Mock fetch: first call 200 `{irr:0.2}`, second call 422 `{detail:"bad input"}`.
- Action: render, wait for the first result, change the request value, advance past the debounce.
- Assert: after the first call, `0.2` shown. After the failure, `error` equals `bad input` and `result` is `null`. The text `0.2` is gone. Today this fails (result kept), so mark the test red-first.
- Runner: needed.

**F17 (L) Input parsing**
- Component: `fromEditString`, `toEditString`, `displayValue`, and `NumField`.
- Setup: render `NumField` with `kind="pct"`, `optional={false}`, `value=0.065`, an `onCommit` spy.
- Action: type `abc` and blur. Then clear the field and blur. Then type `7` and blur.
- Assert: first two cases: `onCommit` not called, field text restored to the last good value. Third: `onCommit` called once with `0.07`. `displayValue('pct', null)` is `—`.
- Runner: needed.

## 3. AssumptionDashboard (`components/AssumptionDashboard.tsx`)

**F29 (H) Main recalc error clears metrics**
- Component: `AssumptionDashboard` with `seed` of defaults.
- Setup: mock `/api/recalc` first 200 with `{headline_metrics:{irr:0.2, equity_multiple:2.1}}`, then 422 `{detail:"exit cap must be positive"}`.
- Action: wait for the tiles, edit the exit cap field to a value that triggers the second call.
- Assert: error text appears, the tiles for IRR and multiple show `—` or are removed, `20.00%` and `2.10x` are not in the document. Red-first today.
- Runner: needed.

**F15 (H) Sensitivity error clears the grid**
- Component: `AssumptionDashboard`, sensitivity section.
- Setup: mock `/api/sensitivity` first 200 with a 3x3 grid of synthetic values, then 400 `{detail:"unknown metric"}`.
- Action: run the sweep, then run it again with a changed axis.
- Assert: after the failure the grid cells and chart series are gone (query by role or test id returns none), error text is visible. Red-first today.
- Runner: needed.

**F16 (L) Null points show a dash**
- Component: `AssumptionDashboard` sensitivity grid and chart tooltip.
- Setup: sensitivity response with one `null` cell.
- Action: render, read that cell.
- Assert: cell text is `—`, never `0`, `null` or `NaN`.
- Runner: needed.

## 4. Underwrite page (`pages/Underwrite.tsx`)

**F04 (M) Failed job shows no tiles**
- Component: `Underwrite` with a job id in the route.
- Setup: mock `GET /api/jobs/job-1` returning `{status:"failed", error:"analyst error", headline_metrics:{irr:0.2}}` (the trap: stale metrics on a failed job).
- Action: render, wait for polling to settle.
- Assert: `FailedPanel` text shown, no metric tiles, `20.00%` absent.
- Runner: needed.

**F05 (H) Submit stays disabled until blocking questions are answered**
- Component: the question panel in `Underwrite` (lines 874-967).
- Setup: job `awaiting_input` with two blocking questions (`exit_cap`, `hold_years`).
- Action: leave blank, check button. Type `abc` in one, check. Type `0.06` and `5`, check. Type `Infinity`, check.
- Assert: button disabled for blank, `abc`, one-of-two, and `Infinity`. Enabled only when both parse with `Number.isFinite`. Submitting posts exactly the typed numbers.
- Runner: needed.

## 5. Polling hook (`hooks/useJobPolling.ts`)

**F13 (M) Three errors in a row stop polling and report once**
- Component: `useJobPolling` through a host component.
- Setup: fake timers, fetch rejects or returns 500 every time, `onError` spy.
- Action: advance the timer through four intervals.
- Assert: `onError` called exactly once after the third failure, no fourth fetch. A success between failures resets the count. Terminal statuses (`failed`, `cancelled`, `awaiting_cp1`) stop polling after that response, and `RUNNING_STATUSES` keep it going.
- Runner: needed.

## 6. Deal screens

### 6a. `pages/DealDetail.tsx` (HOLD for F06, F07)

**F06 (H, HOLD) Gate-failed deal shows no tiles**
- Component: `DealDetail`.
- Setup: mock `GET /api/deals/deal-test-1` with `status:"gate_failed"` and `headline_metrics:{irr:0.2}`.
- Action: render.
- Assert: no headline tiles, `20.00%` absent, a clear gate-failed message shown. Red-first today. Pair with backend B64 so the API also returns `{}`.
- Runner: needed. Write after HOLD clears.

**F07 (M, HOLD) Non-number metric shows a dash**
- Component: `DealDetail` tile helper (lines 419-434).
- Setup: `headline_metrics:{irr:"0.2", equity_multiple:null}` with status `computed`.
- Action: render.
- Assert: both tiles show `—`.
- Runner: needed. Write after HOLD clears.

**F09 (L) Stored spec seeds only finite numbers**
- Component: `DealDetail` seeding the dashboard.
- Setup: stored `spec` with `exit_cap: NaN` serialized as `null`, `noi_series:[1,"x",null,3]`.
- Action: render and read the seed passed to the dashboard.
- Assert: bad scalars are dropped (defaults used), series keeps only finite numbers or is dropped whole (decide with Evan), no `NaN` text.
- Runner: needed.

### 6b. `components/EFBMetricTiles.tsx` (HOLD for F08)

**F08 (H, HOLD) Negative bond shows a dash**
- Component: `EFBMetricTiles`.
- Setup: props `result` with `bond_amount: -71.79`, then `bond_amount: null`, then `bond_amount: 1000000`.
- Action: render each.
- Assert: negative and null show `—`, never `$-72`. Positive shows `$1.0M` style text. Red-first for the negative case.
- Runner: needed. Write after HOLD clears.

### 6c. `pages/BondScreen.tsx`

**F18 (L) Null max loan shows a dash**
- Component: `BondScreen`.
- Setup: mock the EFB underwrite response with `max_loan: null`, other fields set.
- Action: render, wait for the response.
- Assert: that tile shows `—`, others show their numbers.
- Runner: needed.

## 7. Pipeline page (`pages/Pipeline.tsx`)

**F10 (H, HOLD) Gate-failed card shows no IRR**
- Component: `Pipeline`.
- Setup: mock `GET /api/deals` with one deal `status:"gate_failed"`, `headline_metrics:{irr:0.2}`, and one `computed` deal with IRR 0.18.
- Action: render.
- Assert: the gate-failed card has the status badge and no `20.00%`. The computed card shows `18.00%`. A deal with no metrics shows "Not yet computed".
- Runner: needed. Write after HOLD clears.

**F11 (M) Attention column**
- Component: `Pipeline`.
- Setup: three deals with status `gate_failed`, `failed`, `cancelled`, plus one `computed`.
- Action: render.
- Assert: the first three sit inside the attention column (query by column heading, `within`), the computed one does not.
- Runner: needed.

**F12 (L) Fetch failure and empty list**
- Component: `Pipeline`.
- Setup: case A fetch rejects, case B returns `[]`.
- Action: render each.
- Assert: A shows the error banner and no cards. B shows the empty text.
- Runner: needed.

## 8. Memo, export, run status

### 8a. `components/DealMemo.tsx`

**F19 (M) Memo errors and precedence**
- Component: `DealMemo` with `dealId="deal-test-1"`.
- Setup: `POST /api/deals/deal-test-1/memo` mocked 409 `{detail:"not computed"}`, then 502, then 200 `{memo:"generated"}`. Prop `memo="stored"`.
- Action: click Generate for each response.
- Assert: 409 shows the not-computed message, 502 shows the retry message, neither shows a memo. 200 shows `generated`, not `stored`. Empty memo shows the empty text.
- Runner: needed.

### 8b. `components/DealExport.tsx`

**F20 (M) Refusal groups always visible**
- Component: `DealExport`.
- Setup: reconcile response `{ok:false, refusals:{identity:["name differs"], values:["irr off"]}}`.
- Action: render, run reconcile.
- Assert: both groups and their lines visible with no click, no collapse control present, no download button enabled.
- Runner: needed.

### 8c. Run status (all HOLD, evidence viewer)

**F21 (M, HOLD) Page states**
- Component: `RunStatusDetail` in a `MemoryRouter` at `/run-status/run-x`.
- Setup: cases: pending fetch, 404, 500, empty run. Spy on `AbortController` abort.
- Action: render, then change the route id.
- Assert: loading text, "Run not found." for 404, error text for 500, no data shown on any error, previous request aborted on id change.
- Runner: needed. Write after HOLD clears.

**F22 (M, HOLD) Banner and blank values**
- Component: `StateBanner`, `HeadlineList`.
- Setup: `run` with state `blocked`, `stale`, `failed`. Headline items with `value:null`, `value:undefined`, `value:0`, and `diagnostic` true.
- Action: render.
- Assert: loud banner for the three states. `null` and `undefined` both show "Blank" with the reason, never the word `undefined`. Verified `0` shows `0`. Diagnostic notice appears when flagged. Pair with backend B89.
- Runner: needed. Write after HOLD clears.

**F23 (M, HOLD) Evidence badges**
- Component: `EvidenceList`.
- Setup: items with states `verified`, `unverified`, `hash_mismatch`, `missing`.
- Action: render.
- Assert: each state has its own label, mismatch and missing carry the red tone, none reads as verified.
- Runner: needed. Write after HOLD clears.

**F27 (L, HOLD) Run status API errors**
- Component: `getRunStatus`.
- Setup: fetch returns 404 then 500.
- Action: await both.
- Assert: `ApiError` with text "Run not found." for 404, generic text for 500.
- Runner: needed. Write after HOLD clears.

## 9. Whole app

**F24 (M) Error boundary**
- Component: `App` wrapped by the future `ErrorBoundary` (none exists, test is red-first and drives the build of one).
- Setup: a child that throws in render (`(("x") as any).toFixed(2)`). Silence `console.error`.
- Action: render.
- Assert: a fallback message with a reload hint is shown, the rest of the page chrome (nav) remains, no blank screen.
- Runner: needed.

## 10. Index by row

| Row | Component | Pri | HOLD | Runner |
|---|---|---|---|---|
| F01 | RequireAuth | M | no | needed |
| F02 | api.ts, AuthContext | M | no | needed |
| F03 | api.ts | L | no | needed |
| F04 | Underwrite | M | no | needed |
| F05 | Underwrite questions | H | no | needed |
| F06 | DealDetail | H | yes | needed |
| F07 | DealDetail | M | yes | needed |
| F08 | EFBMetricTiles | H | yes | needed |
| F09 | DealDetail | L | no | needed |
| F10 | Pipeline | H | yes | needed |
| F11 | Pipeline | M | no | needed |
| F12 | Pipeline | L | no | needed |
| F13 | useJobPolling | M | no | needed |
| F14 | useLiveCalc | H | no | needed |
| F15 | AssumptionDashboard | H | no | needed |
| F16 | AssumptionDashboard | L | no | needed |
| F17 | livecalc NumField | L | no | needed |
| F18 | BondScreen | L | no | needed |
| F19 | DealMemo | M | no | needed |
| F20 | DealExport | M | no | needed |
| F21 | RunStatus page | M | yes | needed |
| F22 | RunStatusParts | M | yes | needed |
| F23 | RunStatusParts | M | yes | needed |
| F24 | App | M | no | needed |
| F25 | format.ts | L | no | needed |
| F26 | App routes | L | no | needed |
| F27 | runStatusApi | L | yes | needed |
| F28 | download, api | M | no | needed |
| F29 | AssumptionDashboard | H | no | needed |

All 29 rows need a runner. 8 rows are HOLD (F06, F07, F08, F10, F21, F22, F23, F27).

## 11. Three tests to write first (once Evan approves a runner)

None of these are on HOLD.
1. **F14 useLiveCalc clears result on failure.** One hook feeds BondScreen and the EFB panel, so one fix and one test protect both screens from showing old numbers beside an error.
2. **F29 main recalc error clears metrics.** The main underwriting screen keeps the last good headline numbers visible when the next recalc fails. Same bug family as F14, and it is the first screen a user sees. Writing F29 and F15 in the same file shares the mock setup.
3. **F05 submit disabled until every blocking question has a finite answer.** This is the only guard that stops a blank or non-numeric answer entering the job. A silent pass here sends a wrong input into the engine.

Next in line: F15, then F06 and F10 once HOLD clears (they pair with backend B64).

## 12. Open decisions for Evan

- Runner choice. Vitest is proposed because the app builds with Vite. Needs approval before any install.
- F08 and F25: should a negative bond or loan show `—` or the real negative number? The map treats `$-72` as a bug. The test assumes `—`.
- F09: drop a bad series entirely or keep its finite points.
- F24: approve adding an ErrorBoundary, since the test cannot pass without one.
