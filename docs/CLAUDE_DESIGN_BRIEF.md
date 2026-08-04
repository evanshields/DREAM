# DREAM, Claude Design Restyle Brief

This is a design brief for Claude Design. Your job is to make DREAM look like institutional-grade financial software while keeping every wire intact. Restyle the presentation. Do not touch the plumbing. The "Hard constraints" section below is the contract, copy it verbatim into anything you export.

## 1. What this app is

DREAM is Shieldstone's in-house multifamily real-estate underwriting app. An investor drops in a deal (a market-rate acquisition or a tax-exempt bond deal), a set of AI analysts run a first-pass underwrite to a review checkpoint called CP-1, and then the investor can model assumptions live, read a generated memo, and push the numbers into an Excel model. The only users are Evan and Charles, who are investors and not engineers, so the interface has to feel like something you would show an investment committee: precise, calm, credible, never toy-like or playful. Every number on the screen is computed by a validated deterministic engine, so the design should make those numbers feel trustworthy and easy to read at a glance.

## 2. Stack and how to work

- React 19 + TypeScript, built with Vite. Tailwind CSS 3 for styling.
- The UI primitives are hand-rolled in `frontend/src/components/ui.tsx` (Card, Button, Input, Badge, Spinner). There is NO component library (no MUI, no shadcn, no Chakra). Keep it that way.
- Routing is react-router 7 (`react-router-dom`). Charts are `recharts`. Icons are `lucide-react`.
- This is a restyle of presentation ONLY. You may change Tailwind classes, the `@layer components` recipes in `index.css`, the color and font tokens in `tailwind.config.js`, spacing, borders, shadows, rounded corners, chart colors, and the internal markup of a component's visual layout. You may NOT change what data a component receives, what it does, how it fetches, or what it is named. Think of it as repainting and re-arranging rooms in a house whose wiring and plumbing must stay exactly where they are.

## 3. Screen-by-screen map

The app has one public route and four gated routes. All gated routes render inside `AppShell` (sticky top bar with the DREAM wordmark, a nav for Pipeline / New Underwrite / Bond Screen, the signed-in user's email + avatar, and a Logout button; a footer line at the bottom).

### `/login` (public), `pages/Login.tsx`

- Purpose: gate the app to authorized Shieldstone users.
- Layout: centered card on an off-white field. Wordmark + tagline above the card. Inside: a "Sign in" heading, a username field, a password field, an error banner slot, a primary "Sign in" button, an "or" divider, and a Google sign-in button that Google itself renders into an empty div.
- States to design: idle, submitting (button shows a spinner + "Signing in..."), and an error banner (wrong password, not authorized, Google failure).

### `/pipeline`, `pages/Pipeline.tsx`

- Purpose: the deal list. This is the app's home and the screen Evan sees most.
- Layout: a header row ("Pipeline" + a live deal count, a Refresh button, a "New Underwrite" button), then a row of filter pills, then a responsive grid of deal cards (1 / 2 / 3 columns).
- Key states to design:
  - Filter pills: All, Computed, Awaiting Input, Gate Failed, Draft, and Archived. Each pill shows a count. The active pill is filled teal; the rest are outlined. "All" counts only non-archived deals; "Archived" is its own view.
  - Deal cards come in two variants. ACQ (acquisition) cards get a teal top border and show IRR + Equity Multiple. EFB (bond) cards get a taupe top border, a small landmark icon on the routing badge, and show Bond Proceeds + Year-1 DSCR. A card with no computed metrics shows a muted "Not yet computed" line instead of the metric pair. Every card is a clickable link to the deal.
  - Each card has a kebab (three-dot) menu in the top-right corner. It opens a small popover with Archive (or Unarchive, if the deal is archived) and a red Delete. Delete asks for confirmation first. While an action runs, the kebab shows a spinner.
  - Empty state (no deals, or no deals in the current filter) and an error banner.
  - Loading state (spinner + "Loading pipeline...").

### `/underwrite`, `pages/Underwrite.tsx`

- Purpose: start a new underwrite. This is a guided intake, not a form dump.
- Layout: a narrow single-column page. It moves through four stages: intake, running, questions, failed.
  - Intake stage: an upload card at top (drag-and-drop an OM / T-12 / rent roll PDF, XLSX, or CSV; the backend extracts it and prefills fields, which get a small "prefilled from document" sparkle tag). Below it, the intake form: deal name, a routing selector (two big selectable cards: "Market-Rate Acquisition" and "Tax-Exempt Bond (EFB)"), then routing-specific inputs (ACQ shows purchase price / hold / exit cap; EFB shows stabilized NOI / target DSCR / bond rate / amortization / tax exempted / hold), a notes textarea, and a "Run Underwrite" button.
  - Running stage: the RunningPanel. Today it is a centered card with a spinning loader, an "Underwriting..." heading, a teal badge showing the current phase in plain English (for example "Reading the T-12", "Synthesizing + running the engine", "Preparing CP-1 review"), a paragraph saying the run continues in the background, and a Cancel button. The phase badge updates live because the app polls the job in the background. This panel is a top priority to make more satisfying (see Design priorities).
  - Questions stage: when the analysts need inputs, a card lists blocking questions (each a labelled field or dropdown) with a "Submit & Resume" button and a Cancel button.
  - Failed stage: a red-accented card with the failure reason in a mono block and a "Back to intake" button.

### `/bond-screen`, `pages/BondScreen.tsx`

- Purpose: a standalone bond calculator, no deal required. Deterministic, no AI.
- Layout: a header (title with a landmark icon, EFB + "Live Recalc" badges, a subtitle, a Reset button), then the EFB Bond Sizing panel, then two companion calculator panels side by side: Exit-Cap Triangulation and Agency Takeout Sizing. Each panel has a big teal headline number, a list of the sub-methods with the binding one highlighted, a live "recalculating / up to date" status line, and a grid of numeric inputs. A teal info note at the bottom explains no AI touches these numbers.
- States to design: live-recalc "recalculating..." vs "up to date", the binding-method highlight, and inputs mid-edit.

### `/deal/:id`, `pages/DealDetail.tsx`

- Purpose: the deal's home. Shows the CP-1 review and the live modelling tools.
- Layout: a back link, a title row (deal name + routing badge + status badge + updated date), then a tab strip: Overview, Memo, Activity, Export.
  - Overview tab: headline metric tiles (ACQ shows IRR / Equity Multiple / CoC / Exit Value as four large teal-topped tiles; EFB shows the four bond tiles). Below that, a Gate Summary block (a list of quality-check gates, each badged Pass / Fail / Skipped; "Skipped" is a neutral documented-skip, not a failure, and can carry a reason). Then an Open Questions block (non-blocking items to confirm at CP-1). Then the live modelling area: for ACQ, the full AssumptionDashboard (see below); for EFB, the EFBSizingPanel. When the ACQ dashboard is seeded from a real deal, a small caption above it reads either "Seeded from this deal's underwrite" or a "Partially seeded, debt terms show Esplanade defaults" note for older deals. Design that caption so it reads as a helpful provenance note, not an error.
  - The AssumptionDashboard is the centerpiece of ACQ modelling: four live headline-return tiles with target labels (on-target vs off-target color), then grouped editable assumption cards (Bridge Debt, Refinance / Takeout, Equity & Exit, Costs & Spreads), each card showing a value input plus Range / Benchmark / Source context, then a Sensitivity Grid (a recharts line chart sweeping one field against one metric, with a base-value reference line and a target reference line, plus a data table below).
  - Memo tab: the generated one-page deal memo (markdown), with Download and Regenerate buttons, a "generating..." state, and a "no memo yet" empty state.
  - Activity tab: a vertical timeline of every job event (phase, LLM call, gate, spec write, error), color-coded by kind.
  - Export tab: upload a Mini Model .xlsx and populate a copy with the deal's inputs. Renders a detailed write report with refusal groups when gates block cells.

## 4. Brand system (MUST follow)

Shieldstone's palette and type. The good news: `tailwind.config.js` already defines every one of these tokens, so KEEP them and design with them. Do not introduce off-brand colors or fonts.

- Colors:
  - Deep Teal `#005253`, the primary structural color (headline numbers, active nav, primary buttons). In config as `teal.DEFAULT`, with `teal.tint #5EC4C0`, `teal.panel #EAF3F3`, `teal.panel2 #E8ECEC`.
  - Dark Slate `#3C4856`, primary text (`slate.DEFAULT`), with `slate.near #171C26` for near-black headings.
  - Taupe `#D4C4B0`, secondary accent (marks EFB deals). In config as `taupe`.
  - Off-White `#FAFAF8`, the page background (`offwhite`).
  - Electric Blue `#2B52EF`, accent / CTA / callout, use SPARINGLY (in config as `electric`; today it appears only on "Live Recalc" badges).
  - Status colors already defined: `ok #16A34A`, `warn #D97706`, `danger #DC2626` (plus lighter variants).
- Fonts (already wired in config): Playfair Display for display and headlines (`font-head`), Josefin Sans for UI labels, buttons, eyebrows (`font-label`), Noto Sans for body and data (`font-body`). A mono face (JetBrains Mono) is used for field keys and code. NEVER use Cormorant. NEVER use Inter. The fonts load from the app's `index.html`, so keep referencing the same family names.
- What is currently defined vs the target: the config is ALREADY on-brand and correct. Your upgrade is in how these tokens are applied, not in the tokens themselves. You may add new shades, shadows, or component recipes, but the five core hex values and the three font families above must remain the identity. If you add a token, extend the existing `theme.extend`, do not replace it.
- Financial data presentation: use tabular numerals for every number (the `.tnum` utility and `tnum` class already do this, keep using them). Right-align currency and numeric columns in tables. Give the numbers room, generous whitespace reads as expensive. Big headline numbers should feel like the hero of each tile.

## 5. Hard constraints (copy verbatim into any export)

These rules are the contract between the design and the working app. Copy this section verbatim into any export or handoff. Breaking any one of them breaks the app.

DO NOT modify, rename, move, or delete any of these files, or change what they do:
- `frontend/src/lib/api.ts` (all fetch calls, endpoints, and type definitions)
- `frontend/src/lib/format.ts` (all display formatters)
- `frontend/src/hooks/useJobPolling.ts` (the background job poller)
- `frontend/src/auth/AuthContext.tsx` and `frontend/src/auth/RequireAuth.tsx`
- Any fetch, polling, abort-controller, or auth logic in any file.

DO NOT change any of the following, anywhere:
- Route paths: `/login`, `/pipeline`, `/underwrite`, `/bond-screen`, `/deal/:id`. Keep `App.tsx` routing structure intact.
- Form field names and the shape of any object sent to the backend. The `critical_inputs` keys (`purchase_price`, `hold_years`, `exit_cap`, `stabilized_noi`, `target_dscr`, `bond_rate`, `amortization_years`, `annual_property_tax_exempted`), the `SubmitJobRequest` shape, and every request/response interface must stay byte-for-byte.
- The prop interfaces and data flow of components. You may restyle a component's internal markup, but its props in and its data out must not change. In particular these must survive verbatim:
  - `DealCard` receives `{ deal: DealListItem; onChanged: () => void; onError: (msg: string) => void }`. `DealListItem` has `deal_id, deal_name, slug, routing, mode, status, owner, version, created_at, updated_at, headline_metrics`.
  - `RunningPanel` receives `{ job?: JobView | null; onCancel: () => void }` and reads `job.phase` (mapped through `phaseLabel`). `JobView` has `job_id, deal_id, status, phase, routing, mode, cancel_requested, error, open_questions, blocking_questions` and optionally `spec, headline_metrics, gate_summary`.
  - `AssumptionDashboard` receives `{ seed?: Partial<ACQRecalcRequest> }`. `ACQRecalcRequest` keys: `bridge_loan, bridge_rate, bridge_io_years, refi_loan, refi_rate, refi_io_years, refi_amort_years, refi_year, total_equity, noi_series, exit_cap, sale_year, costs_of_sale, servicing_spread, refi_cost_pct, exit_on_forward_noi` (+ optional series and `years`).
  - `EFBSizingPanel` receives `{ seed?: Partial<EFBUnderwriteRequest>; title?: string }`. `EFBUnderwriteRequest` keys: `stabilized_noi, target_dscr, bond_rate, amortization_years, annual_property_tax_exempted, hold_years`.
  - `DealDetail` tab ids are exactly `'overview' | 'memo' | 'activity' | 'export'`. Do not rename them.
  - `statusTone(status)` in `ui.tsx` maps status strings to badge tones and MUST keep handling every current status, including `'archived'` (neutral). Keep the full switch: `computed`/`completed`/`awaiting_cp1` -> ok, `gate_failed`/`failed`/`cancelled` -> danger, `awaiting_input`/`analyzing`/`synthesizing`/`routing`/`submitted` -> warn, `exported`/`populated` -> teal, `archived` -> neutral.
- Every existing interactive behavior must keep working exactly:
  - The kebab menu lives inside a card that is itself a link. Every kebab handler calls `preventDefault()` + `stopPropagation()` FIRST so clicking the menu never navigates. Preserve that suppression.
  - Delete asks `window.confirm(...)` before deleting. Keep the confirm-before-delete.
  - The underwrite run polls in the background and auto-navigates to the deal page when the job reaches CP-1 (`awaiting_cp1` / `completed`). Preserve the polling and the auto-navigation.
  - Live-recalc panels debounce edits (450ms), abort in-flight requests, and show a status line. Keep that behavior.

Build rules:
- TypeScript must still compile with `npx tsc --noEmit`, and `npm run build` must succeed.
- No new runtime dependencies without flagging them explicitly in the handoff. Stay on React 19, react-router 7, recharts, lucide-react, Tailwind 3. If a look needs a new package, call it out rather than adding it silently.
- Keep using lucide-react for icons and recharts for charts. Do not swap icon sets or charting libraries.

## 6. Design priorities

In the order Evan cares about:

1. The Pipeline deal cards and the DealDetail headline metric tiles should read like an institutional dashboard, not a demo. This is the first thing a partner sees. Make the numbers the hero, make ACQ vs EFB visually distinct, make status legible at a glance.
2. Turn the RunningPanel into a satisfying progress experience. Right now it is a spinner and a phase badge. Make the live phase readout feel like the app is working hard for you: a sense of sequence or steps, momentum, and a calm "you can walk away" reassurance. It polls in the background, so the phase label changes over time, design for that motion.
3. Make the intake form feel guided, not like a government form. The routing selector cards, the upload-to-prefill flow, and the field grouping should feel like a confident wizard walking the investor through a deal.
4. Carry one consistent dark-slate + teal identity across every screen, so login, pipeline, underwrite, bond screen, and deal detail feel like one product.
5. Design the empty states and error states, do not leave them default. Empty pipeline, no-memo-yet, failed underwrite, and error banners should all feel intentional and on-brand.

## 7. What to deliver back

- The restyled components, delivered either through "Handoff to Claude Code" or as a zip export. A later Claude Code session will drop them in, run `npx tsc --noEmit`, run `npm run build`, verify the API wiring still works, and deploy. So keep the file structure and component names aligned with the constraints above to make that integration clean.
- Screenshots of each screen (Login, Pipeline, Underwrite in each stage, Bond Screen, Deal Detail with each tab) at both a desktop width and a narrow / mobile width, so the responsive behavior is reviewable before integration.
- A short note listing any new Tailwind tokens or `index.css` recipes you added, and flagging any new dependency you think the design needs (do not add it yourself).
