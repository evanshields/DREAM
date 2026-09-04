# DREAM Mini Brand Brief — v0.2

**Status:** Approved for implementation — Nocturne Iris / Step 2 (Evan, 2026-09-03)
**Brand relationship:** A distinct product with a quiet Shieldstone family connection
**Overall confidence:** High for palette, typography, and mark direction; implementation still requires rendered accessibility validation.

## The idea

DREAM is the operating system for clear real-estate decisions. It brings the relationship record, underwriting process, evidence, and human judgment into one calm working environment.

**Positioning:** The operating system for clear real-estate decisions.
**Promise:** Every deal. One clear path to a decision.
**Supporting line:** From first look to investment decision.

## Identity decision

The earlier letter-D concepts are retired. DREAM's mark should be a modern four-way interlock based closely on `DREAM_MARK_REFERENCE_2026-09-03.png`: four open, rounded paths crossing into one balanced system. The geometry communicates connected people, evidence, underwriting, and judgment without spelling a letter or using generic AI imagery.

Preserve the reference mark's essential silhouette, rounded terminals, negative-space cross, and equal visual weight. Modernization should come through cleaner geometry, carefully resolved crossings, optical correction, and a flexible one-color construction—not by turning the mark into a D. It must work at favicon size and in one color before gradients are considered.

## One system, two modes

Light and dark are two expressions of the same identity—not separate brands.

- **Light / Quiet Signal:** warm ivory ground, white working surfaces, blue-black text, and restrained iris focus. Calm, editorial, and excellent for long underwriting sessions.
- **Dark / Open Current:** blue-black ground, softly lifted ink surfaces, warm-white text, and brighter periwinkle focus. Immersive and agent-forward without becoming neon or theatrical.
- **Shieldstone teal:** a secondary family cue for the endorsement, select navigation details, and rare connective moments. It is not the page background or dominant interface color.

## Recommended color architecture

### Nocturne Iris — approved

| Role | Light mode | Dark mode | Purpose |
|---|---:|---:|---|
| Canvas | `#F4F1EB` | `#10131D` | Warm day / deep blue-black night |
| Surface | `#FFFFFF` | `#191D2A` | Primary working layer |
| Primary text | `#1B1D29` | `#F6F3EE` | High-legibility copy |
| Muted text | `#686978` | `#A9A9B6` | Supporting information |
| DREAM iris | `#6657E8` | `#9288FF` | Focus, agent activity, proposed work |
| Soft iris | `#E9E6FF` | `#2B2848` | Selected and conversational surfaces |
| Shieldstone teal | `#2F7773` | `#70AAA5` | Secondary family cue |
| Border | `#DED9D2` | `#303444` | Structure without visual noise |

The system is neutral-first, iris-led, and teal-supported. It is intentionally neither a green product nor a generic blue SaaS interface.

### Semantic colors

- **Agent-generated / proposed:** Iris `#6657E8` / `#9288FF`
- **Human review required:** Amber `#A86612` / `#E5AD52`
- **Blocked / failed:** Red `#B84350` / `#F07882`
- **Completed / passed:** Green `#2F7D5A` / `#67B88F`
- **Engine-confirmed:** Teal `#2F7773` / `#70AAA5`

Every state also uses a plain-English label and, where helpful, an icon. Color never carries meaning alone. Final interface tokens must pass WCAG AA contrast checks before rollout.

## Typography

- **Playfair Display:** only for large landing-page statements, major empty states, and occasional editorial moments.
- **Josefin Sans:** page titles, section headings, navigation labels, and compact display copy.
- **Noto Sans:** records, tables, forms, chat, body copy, numbers, and all dense working UI.
- **Rule:** typography creates hierarchy; font changes never substitute for spacing, labeling, or information structure.

## Personality

| We are | We are not |
|---|---|
| Calmly intelligent | Flashy or theatrical |
| Evidence-led | “AI magic” |
| Institutional but approachable | Cold or bureaucratic |
| Decisive | Reckless or overconfident |
| Built by operators | Generic software for everyone |

## Application principles

1. The product feels like a calm deal room, not a chatbot wrapped around a spreadsheet.
2. Dark mode is deep and focused, never a field of pure black or glowing gradients.
3. Light mode is warm and quiet, never sterile white with corporate teal everywhere.
4. Numbers and gates look authoritative only when confirmed by deterministic systems.
5. Human-review moments remain visible and dignified.
6. Empty, stale, disputed, and blocked states are visually honest.

## Decision record

On 2026-09-03, Evan approved **Nocturne Iris** as DREAM's shared light/dark color architecture. Mineral Blue and Aubergine Current, shown on [`DREAM_BRAND_SYSTEM_V0.2.png`](DREAM_BRAND_SYSTEM_V0.2.png), are not the implementation direction for v0.2. The approved system gives DREAM a recognizable iris signal while allowing Shieldstone teal to recede gracefully. Implementation remains subject to WCAG AA checks and rendered UI review.

On 2026-09-03, Evan also approved the corrected, optically centered four-way interlock in [`kit/marks/dream-mark-primary.svg`](kit/marks/dream-mark-primary.svg). This geometry replaces the earlier provisional redraw. All full-size variants share the approved geometry; favicon variants use only a heavier stroke for 16px legibility.

## Source basis

- Evan's direct feedback on light/dark modes, color balance, typography, and logo geometry on 2026-09-03.
- Evan-provided [`DREAM_MARK_REFERENCE_2026-09-03.png`](DREAM_MARK_REFERENCE_2026-09-03.png) four-way interlock reference image.
- Shieldstone brand standards and source icon.
- DREAM PRD and three-legged product architecture.
- Current DREAM application and live CRM interface review.
