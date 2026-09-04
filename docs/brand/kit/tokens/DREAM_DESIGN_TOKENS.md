# DREAM Design Tokens — Nocturne Iris

**Step:** 2 — production-ready design-system specification
**Version:** 0.2
**Status:** Approved for implementation (Evan, 2026-09-03)
**Sources:** [`DREAM_BRAND_BRIEF_V0.2.md`](../../DREAM_BRAND_BRIEF_V0.2.md), [`DREAM_BRAND_SYSTEM_V0.2.png`](../../DREAM_BRAND_SYSTEM_V0.2.png), and [`kit/marks/README.md`](../marks/README.md)

This is the portable token contract for DREAM's two-mode visual system. The CSS file in this folder contains no framework, reset, component selectors, or build-time dependencies; it can be imported by React, server-rendered HTML, or another product surface.

## Design intent

Nocturne Iris is neutral-first, iris-led, and teal-supported. Light mode is a warm, quiet working room. Dark mode is a deep blue-black room with lifted surfaces and brighter periwinkle focus. The two modes share the same hierarchy and state vocabulary.

Shieldstone teal is a secondary family cue and the visual language for deterministic engine confirmation. It is not the dominant page color. DREAM iris marks agent activity and proposed work; it does not imply that a result is numerically confirmed.

The system should feel calmly intelligent, evidence-led, institutional but approachable, and decisive without being overconfident. Empty, stale, disputed, and blocked states remain visually honest.

## Installation and theme contract

Import `DREAM_DESIGN_TOKENS.css` once at the application boundary. An explicit theme is set on the document root:

```html
<html data-theme="light">
```

Use `data-theme="dark"` for dark mode. If the attribute is omitted, the file follows `prefers-color-scheme`; an explicit attribute always wins. A nested component can also use the attribute when it is intentionally isolated.

Use semantic tokens such as `--dream-color-text-primary`, `--dream-state-review-fg`, and `--dream-interaction-selected-surface` in components. The source palette tokens are available for brand-level artwork and controlled exceptions, but should not be used to make arbitrary UI colors.

## Token families

### Canvas, surfaces, text, and borders

| Token | Light | Dark | Use |
|---|---|---|---|
| `--dream-color-canvas` | `#F4F1EB` | `#10131D` | Page background / lowest layer |
| `--dream-color-surface` | `#FFFFFF` | `#191D2A` | Primary cards, panels, working surfaces |
| `--dream-color-surface-raised` | `#FFFFFF` | `#202433` | Lifted cards, menus, popovers |
| `--dream-color-surface-inset` | `#EEECE7` | `#151923` | Inset fields, code/evidence wells |
| `--dream-color-surface-selected` | `#E9E6FF` | `#2B2848` | Selected and conversational surfaces |
| `--dream-color-surface-conversation` | `#F3F1FF` | `#22203B` | Agent thread / conversational grouping |
| `--dream-color-text-primary` | `#1B1D29` | `#F6F3EE` | Body, labels, values, headings |
| `--dream-color-text-secondary` | `#686978` | `#A9A9B6` | Supporting copy, metadata |
| `--dream-color-text-tertiary` | `#7E7F8C` | `#858693` | Decorative metadata only; not labels, instructions, or decision-critical copy |
| `--dream-color-text-tertiary-accessible` | `#5F606C` | `#858693` | AA-safe tertiary/caption text |
| `--dream-color-text-disabled` | `#A4A3AA` | `#626472` | Disabled controls only; never critical information |
| `--dream-color-border-subtle` | `#EBE7E0` | `#252936` | Decorative/quiet separation only |
| `--dream-color-border` | `#DED9D2` | `#303444` | Decorative card structure; not a control boundary |
| `--dream-color-border-strong` | `#C6C1BB` | `#484D60` | Decorative hover/emphasis; not a sole control boundary |
| `--dream-color-border-control` | `#696A75` | `#74798E` | AA-safe boundary for inputs, buttons, selected controls, and meaningful data-grid edges |

The first three border tokens are intentionally quiet and do not meet the 3:1 non-text boundary target on every surface. Use `--dream-color-border-control` for interactive controls and any boundary whose presence is necessary to identify or operate the element. Avoid borders as the only indication of a state; pair a state border with a label, icon, text, or changed structure. State `*-border` tokens are decorative state accents unless the component also uses the control-boundary token.

### Agent, confirmation, review, blocked, and pass states

Each state has four tokens: `*-fg` is the accessible text color for its tinted surface; `*-accent` is the brand/state signal for icons, rules, and focus-adjacent marks; `*-bg` is the supporting surface; `*-border` is its boundary.

| State | Meaning | Light fg / accent / bg | Dark fg / accent / bg |
|---|---|---|---|
| Agent / proposed | DREAM-generated or not yet human-confirmed work | `#3D34A8` / `#6657E8` / `#E9E6FF` | `#C2BCFF` / `#9288FF` / `#2B2848` |
| Engine-confirmed | Deterministic engine result or receipt | `#235D5A` / `#2F7773` / `#E5F1F0` | `#A5D6D1` / `#70AAA5` / `#203A3A` |
| Human review required | An open question, warning, or decision request | `#8B5200` / `#A86612` / `#FFF1D9` | `#E5AD52` / `#E5AD52` / `#3A2B1B` |
| Blocked / failed | A hard stop, failed gate, or unavailable result | `#993640` / `#B84350` / `#FCE5E7` | `#F07882` / `#F07882` / `#3A2228` |
| Completed / passed | A completed workflow or passing gate | `#236044` / `#2F7D5A` / `#E2F2E8` | `#67B88F` / `#67B88F` / `#1E3528` |

The source colors from the brief remain available as `--dream-color-iris`, `--dream-color-teal`, `--dream-color-amber`, `--dream-color-red`, and `--dream-color-green` (with `*-bright` variants in dark mode). The slightly darker light-mode `*-fg` values are intentional: they make text on tinted state surfaces meet AA while preserving the requested accent colors for visual signals.

State rendering rules:

- Agent/proposed work must say “Proposed”, “DREAM draft”, or equivalent plain-English text. It is not a confirmation badge.
- Engine-confirmed content must say “Engine confirmed” or identify the deterministic receipt/source. Do not use teal to certify an LLM claim.
- Review, blocked, and pass states must include a text label. Icons may reinforce the label, never replace it.
- A blocked state is a hard stop in language as well as color. Do not style it as a neutral warning or success.

### Focus, hover, selected, and disabled

| Token | Purpose |
|---|---|
| `--dream-focus-ring` + `--dream-focus-ring-offset` | Visible keyboard focus ring with separation from the surface |
| `--dream-interaction-hover-surface` | Pointer/keyboard hover fill |
| `--dream-interaction-hover-border` | Hover boundary emphasis |
| `--dream-interaction-active-surface` | Pressed / active control fill |
| `--dream-interaction-selected-surface` + `*-border` | Persistent selection; use selected text or an icon too |
| `--dream-interaction-disabled-surface` + `*-content` | Disabled controls; also set `disabled` and remove interaction |

Recommended focus declaration:

```css
:where(button, a, input, select, textarea, [tabindex]):focus-visible {
  outline: 2px solid var(--dream-focus-ring);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px var(--dream-focus-ring-offset);
}
```

Do not remove the focus indicator for pointer users at the expense of keyboard users. Hover must never be the only way to discover an affordance.

## Typography roles

The CSS variables define font stacks, sizes, line heights, and tracking. The host application must self-host approved OFL font files in WOFF2 format; no runtime third-party font fetch is permitted. If a font file is unavailable, the declared system fallback is used without changing the role hierarchy.

| Role | Family | Use |
|---|---|---|
| Display | `--dream-font-display` (Playfair Display) | Large landing statements, major empty states, occasional editorial moments only |
| Title / heading | `--dream-font-heading` (Josefin Sans) | Page titles, section headings, navigation, compact display copy |
| Body / UI / numbers | `--dream-font-body` (Noto Sans) | Records, tables, forms, chat, body copy, labels, and all dense working UI |
| Monospace | `--dream-font-mono` | Technical identifiers, source snippets, and machine-readable evidence only |

Approved self-hosted WOFF2 weights:

- Noto Sans: 400, 500, 600, 700
- Josefin Sans: 500, 600, 700
- Playfair Display: 600, 700

The host should load only these weights with `font-display: swap`; do not fetch fonts from Google Fonts or another third-party origin at runtime.

Playfair creates an editorial signal, not a replacement for information hierarchy. Josefin should be used with restraint in long labels. Noto Sans owns the working surface and all decision-critical numbers. Typography must not be the only distinction between states.

## Spacing and geometry

Spacing follows a 4px base rhythm: `--dream-space-1` through `--dream-space-24` are 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, and 96px. Use the nearest token; do not introduce arbitrary values for ordinary layout.

Radii are intentionally soft but not playful:

- `none` for data grids and deliberate hard edges
- `xs` (4px) for compact controls
- `sm` (8px) for inputs and small cards
- `md` (12px) for standard cards and panels
- `lg` (16px) for major working surfaces
- `xl` (24px) for hero/empty-state surfaces
- `pill` for status chips and compact filters only

## Elevation and shadows

`--dream-shadow-sm` separates a control or small card, `--dream-shadow-md` lifts a working panel, and `--dream-shadow-lg` is reserved for modal/popover-level elevation. Use one elevation level at a time and prefer borders for dense data. Dark mode uses black-alpha shadows to avoid a glowing interface.

## Motion

Use `--dream-duration-fast` for hover/color response, `--dream-duration-standard` for panel and control transitions, `--dream-duration-slow` for intentional layout movement, and `--dream-duration-emphasis` for an occasional state reveal. Use the supplied standard and emphasis easing curves. Motion communicates state change; it must not be required to understand a result.

The stylesheet collapses durations and transitions when `prefers-reduced-motion: reduce` is active. Components must still avoid auto-playing decorative motion and must not use flashing effects.

## Accessibility acceptance criteria

The target is WCAG 2.2 AA for normal text (4.5:1), large text (3:1), and non-text UI boundaries/focus indicators (3:1 where applicable). Color is never a sole carrier of meaning: every state has a plain-English label and, where useful, an icon or structural treatment.

Representative contrast ratios, calculated with the WCAG relative-luminance formula, are:

| Pair | Ratio |
|---|---:|
| Light primary text on canvas / surface | 14.85:1 / 16.74:1 |
| Light secondary text on canvas / surface | 4.80:1 / 5.41:1 |
| Light iris / teal accent on surface | 5.13:1 / 5.24:1 |
| Light amber / red / green accent on surface | 4.59:1 / 5.31:1 / 5.00:1 |
| Dark primary text on canvas / surface | 16.75:1 / 15.17:1 |
| Dark secondary text on canvas / surface | 7.98:1 / 7.23:1 |
| Dark iris / teal accent on surface | 5.75:1 / 6.38:1 |
| Dark amber / red / green accent on surface | 8.34:1 / 6.17:1 / 7.06:1 |
| Light state fg on its state bg (agent / engine / review / blocked / pass) | 7.64:1 / 6.53:1 / 5.70:1 / 5.92:1 / 6.40:1 |
| Dark state fg on its state bg (agent / engine / review / blocked / pass) | 7.96:1 / 7.60:1 / 6.77:1 / 5.36:1 / 5.54:1 |
| Light accessible control boundary on surface / canvas | 5.36:1 / 4.75:1 |
| Dark accessible control boundary on surface / canvas | 3.89:1 / 3.83:1 |
| Light accessible tertiary text on surface / canvas | 6.22:1 / 5.52:1 |
| Dark accessible tertiary text on surface / canvas | 4.66:1 / 5.14:1 |

These are token-pair checks, not a substitute for checking a rendered component. Before rollout, validate every text/background and icon/boundary pairing used by a component at its actual font size and weight. A small, dependency-free validation method is:

1. Convert each sRGB channel to linear light: `v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ^ 2.4`.
2. Compute relative luminance `L = 0.2126R + 0.7152G + 0.0722B`.
3. Compute `(lighter + 0.05) / (darker + 0.05)`.
4. Require 4.5:1 for normal text, 3:1 for large text and meaningful non-text boundaries, and 3:1 for keyboard focus against adjacent colors.

The exact brief colors are preserved as accents. Where a light tinted state surface would not provide AA for the raw accent, use that state's `*-fg` token for text and the `*-accent` token for the icon/rule. Never put white text on the light semantic colors or dark text on the light state surfaces without rechecking the pair. Use `--dream-color-text-tertiary-accessible` for any tertiary text that a user needs to read; reserve `--dream-color-text-tertiary` for decorative metadata that is duplicated elsewhere. Use `--dream-color-border-control` for all required control boundaries.

## Naming and implementation rules

- Prefix every token with `--dream-` to prevent collisions when this file is consumed outside the DREAM app.
- Prefer semantic tokens in components; source palette tokens are for controlled brand expressions.
- Keep light/dark values in the same token name. Components should not branch on mode.
- Do not encode business verdicts into visual styling. The deterministic engine and gate vocabulary remain authoritative; tokens only express the already-known state.
- Preserve the distinction between proposed/agent-generated and engine-confirmed work.
- If a new token is needed, add it here first with a defined light and dark value, intended role, and accessibility check.
