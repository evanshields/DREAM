# 17: Trigger Vocabulary and Scope

## Purpose

Comprehensive vocabulary for the Shieldstone Master Underwriting skill. The SKILL.md frontmatter description carries only the highest-frequency triggers (Claude.ai caps that field at 1024 characters). This reference is the full vocabulary, organized by category, useful for:

- Onboarding users who need to know what the skill handles
- Cross-referencing terms during a deal walkthrough
- Disambiguating overlapping concepts (e.g., bridge-to-HUD vs. bridge-to-agency)
- Confirming whether a particular asset, structure, or methodology is in scope

Every term below is a valid trigger phrase. If a user mentions any of these, the skill is the right tool.

---

## Deal types

- **EFB** (Essential Function Bond), tax-exempt bond financing for workforce housing under non-profit ownership; $0 property tax via the exemption
- **ACQ** (Conventional value-add), traditional multifamily acquisition with conventional debt and property tax reassessment
- **Mixed-income**, four-tier rent structure (MLA, HAP, 80% AMI, Market) used for Shieldstone mixed-income core-plus
- **Workforce housing**, generally 60-120% AMI; eligible for EFB structuring
- **Core-plus**, near-stabilized 2020+ vintage institutional quality (Shieldstone standard)

## Deal documents and inputs

T-12, rent roll, OM (Offering Memorandum), CoStar Full UW Report, CoStar Property Summary, CoStar Transaction History, CoStar Sales Comps, CoStar Rent Comps, aged receivables, box score, ACQ Mini Model, EFB Mini Model, Shieldstone Flex Model, broker survey, tax bill, millage rate report, insurance quote.

## Revenue concepts

- **AMI** (Area Median Income), HUD-published; used for LIHTC and 80% AMI tiers
- **HUD FMR** (Fair Market Rent), county-level HUD rent ceiling
- **SAFMR** (Small Area FMR), ZIP-level HUD rent ceiling
- **LIHTC rents**, Novogradac-published rent limits at 30/40/50/60/70/80/100/120% AMI tiers
- **HAP** (Housing Assistance Payments), Section 8 voucher rents at FMR
- **MLA** (Maximum Lease Allowed), top of market-rate tier
- **Three-tier AMI allocation**, default 60% / 20% / 20% split (80% AMI / HAP / Market) for typical EFB
- **Four-tier rent structure**, MLA / HAP / 80% AMI / Market for Shieldstone mixed-income
- **Rent achievability stress test**, cross-check AMI/HAP rents against market comps; cap at 75th percentile when AMI exceeds market
- **HAP optimization**, concentrate vouchers where FMR spread vs. market is widest
- **Vacancy curve**, Year 1-10 vacancy assumption, NOT a flat rate

## OpEx concepts

- **Agency manual triangulation**, cross-check pro forma OpEx against Fannie S&S Guide, Freddie S&S Guide, HUD MAP Guide minimums (per [references/15-opex-agency-triangulation.md](.skills/dream-underwrite/references/15-opex-agency-triangulation.md))
- **Property tax exemption**, $0 taxes for EFB via non-profit fee ownership
- **State-specific reassessment**, FL 70%, TX 65%, GA 40% of new assessed value vs. purchase price for ACQ deals
- **GA bond-lease PILOT**, PILOT 40-60% of fee-simple taxes for GA Development Authority bond-lease structures
- **TX non-ad-valorem**, MUD / PID assessments outside the standard tax bill
- **RUBS** (Ratio Utility Billing System), tenant utility reimbursements
- **Replacement reserves**, $250/unit/year flat across vintages (matches Fannie/HUD agency floor)
- **T-12 forensic analysis**, red-flag scan for seller manipulations (lease-up bonuses, mid-year service drops, $0 line items, RUBS misclassification)

## Property tax exemption pathways

- **Texas PFC** (Public Facility Corporation)
- **Texas HFC** (Housing Finance Corporation)
- **Texas HA** (Housing Authority)
- **Texas CHDO** (Community Housing Development Organization)
- **Florida §196.1978**, nonprofit + bonds exemption
- **Florida §196.199**, government ownership exemption
- **Florida §196.1979**, Live Local Act for-profit exemption
- **Georgia DA bond-lease**, Development Authority bond-lease with PILOT

## Financing concepts

- **Bond sizing**, max bond proceeds at 1.15x Year 1 DSCR
- **Turbo amortization**, principal paid only from available cash; no default if no cash for principal
- **Interest reserve sizing**, when Year 1 DSCR less than 1.15x; reserve = shortfall x 1.25 to 1.35 (25-35% buffer)
- **Sponsor bonds**, subordinate B-piece bonds held by Shieldstone
- **Bridge-to-HUD**, bridge loan that refinances into HUD 223(f) within 24-36 months
- **Bridge-to-agency**, bridge loan that refinances into Fannie Mae DUS or Freddie Mac SBL agency takeout
- **Agency takeout**, refi at 1.25x DSCR, 75-80% LTV, 30-year amortization
- **90/90 rule**, agency refi requires 90 consecutive days at >= 90% economic occupancy
- **HUD 223(f) LTV**, 87% market-rate / 90% affordable per HUD Mortgagee Letter 2025-03
- **HUD 223(f) DSCR**, 1.15x market-rate / 1.11x affordable per ML 2025-03
- **Section 232**, HUD healthcare facility loan (NOT covered by this skill)
- **DUS Guide**, Fannie Mae Delegated Underwriting and Servicing Guide (same document as Multifamily Selling and Servicing Guide)
- **MAP Guide**, HUD Multifamily Accelerated Processing Guide (Handbook 4430.G)
- **ROFR** (Right of First Refusal), structural exit at bond maturity for EFB deals

## Returns and screening

- **Return hurdles**, market-tier specific minimums: Gateway 14-16% IRR / Secondary 16-19% / Tertiary 18-22%
- **Vintage CoC floors**, 2020+ at 6%, 2000-2019 at 7%, pre-2000 at 7.5-8%
- **Exit cap triangulation**, three-method (Treasury spread, exit comp, entry cap + strategy spread); use HIGHEST
- **Equity multiple**, 1.5x minimum across all markets
- **Net investor IRR**, 15% minimum after all fees and promote
- **Promote structure**, 8% preferred return, then 70/30 (LP/GP) to 15% IRR, then 50/50 above
- **Risk adjustments**, +bps to base hurdle for heavy reno, vintage, occupancy stress, floating-rate bridge

## Comps build

- **Recency-weighted sales comps**, 16 slots, descending by date; weighting formula `=IFERROR(IF(D10<>"",MAX(0.01,1-(TODAY()-H10)/365*0.05),0),0)`
- **Submarket rent comps**, 10 primary
- **New construction comps**, 2 sub-3-year-old properties
- **Vintage rent comps**, 3 same-vintage cohort
- **Affordability benchmark rows**, 5 slots (LIHTC 60/80/100 AMI, FMR, SAFMR); weight = 0 always
- **Per-BR breakout**, 10 submarket + 5 affordability rows, weighted average per bedroom type
- **Subject per-BR row**, always linked to Pro Forma, never hardcoded

## Output deliverables

- **UW Snapshot tab**, finalization output; T-12/T-3 reconciliation, with/without-tax pulls, sanity-check list, final metrics audit
- **HTML investment memo**, Phase 12 single-file HTML with Chart.js DSCR/vacancy charts, base64 image embeds, GS Residential / Shieldstone brand
- **Deal memo**, shorthand for the HTML investment memo
- **GS Residential**, Shieldstone's workforce housing brand applied to EFB deal memos and IC materials
- **Phase 5 narrative memo**, IC-facing 6-8 page underwriting narrative (Deal Snapshot + Sections I-VII + Appendix); covered in [.skills/shieldstone-efb-uw/SKILL.md](.skills/shieldstone-efb-uw/SKILL.md) for EFB-only workflow

## Environment markers

- **Claude for Excel**, primary execution environment for Phases 1-11 (model population)
- **Claude Code**, Phase 12 HTML render, companion scripts (`fetch-hud-fmr.py`), bond sizing sensitivity, deploy to VPS
- **Claude.ai Chat**, conversational underwriting, methodology Q&A, IC prep

## Companion infrastructure

- **fetch-hud-fmr.py**, Tier 1 local HUD FMR + SAFMR fetcher; outputs CSV to `shieldstone_acquisitions/reference-data/`
- **HUD MCP server (planned)**, Tier 2 custom MCP on US VPS exposing `get_fmr`, `get_safmr`, `get_lihtc_rent` tools via Claude.ai connectors
- **Agency manuals**, firm-wide reference at [shieldstone_acquisitions/agency-manuals/](shieldstone_acquisitions/agency-manuals/) (Fannie S&S, Freddie S&S, HUD MAP Guide, HUD ML 2025-03)

---

## See also

- [.skills/dream-underwrite/references/16-glossary.md](.skills/dream-underwrite/references/16-glossary.md), formal CRE term definitions
- [.skills/dream-underwrite/SKILL.md](.skills/dream-underwrite/SKILL.md), primary entry point and 12-phase workflow
- [.skills/shieldstone-efb-uw/SKILL.md](.skills/shieldstone-efb-uw/SKILL.md), focused EFB-only specialist (coexists with this master skill)
