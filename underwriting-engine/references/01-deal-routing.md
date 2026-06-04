# 01: Deal Routing (ACQ vs EFB)

## Purpose

Every deal that enters the master skill must be routed to one of two underwriting tracks: ACQ (conventional value-add or core-plus, full property tax, equity capital, agency or bridge debt) or EFB (Essential Function Bond workforce housing, 100% bond-financed, $0 property tax, ROFR exit). This reference encodes the auto-detection logic, the single-question fallback, edge cases (near-stabilized core-plus, GA bond-lease PILOT, Texas PFC vs HFC choice), and the decision tree for ambiguous deals. Phase 0 of the workflow is gated on getting routing right, every downstream phase branches differently for ACQ vs EFB.

---

## Auto-Detection Signal Map

### Filename signals (strongest)

| Filename contains | Route |
|---|---|
| `EFB Mini Model`, `EFB`, `Bond Mini Model`, `Essential Function`, `Shieldstone EFB` | EFB |
| `ACQ Mini Model`, `Flex Model`, `Shieldstone Acq Mini`, `Acquisition Model` | ACQ |
| `Multifamily Model`, `MF Model`, no qualifier | Ambiguous, check OM/keyword signals |

If the uploaded model filename includes either "EFB" or "ACQ" / "Flex", that's a high-confidence signal. Note the routing in chat ("Routing to EFB based on filename") and proceed. Do not ask.

### OM / deal-name keyword signals

| Keyword cluster | Route |
|---|---|
| "tax-exempt bond", "essential function bond", "PFC", "HFC", "housing finance corporation", "housing authority", "HFA bond", "501(c)(3) owner", "nonprofit ownership", "Chapter 303", "Chapter 394", "Chapter 392", "§196.1978", "QMC", "bond trustee" | EFB |
| "value-add", "core-plus", "bridge-to-agency", "bridge-to-HUD", "conventional financing", "Fannie Mae", "Freddie Mac", "agency refi", "renovation premium", "rent gain" | ACQ |
| "market-rate only", "no affordability", "pure market-rate" | ACQ, apply market-rate override (see [references/04-acq-revenue.md](.skills/dream-underwrite/references/04-acq-revenue.md) Market-Rate Override section) |

### Financial assumption signals

| Assumption pattern | Route |
|---|---|
| "$0 property tax", "100% exemption", "PILOT", "property tax = $0" | EFB |
| "reassessment ratio", "millage rate × purchase price", "property tax growth" | ACQ |
| "1.15x DSCR", "Year 1 DSCR floor", "turbo amortization" | EFB |
| "1.25x agency DSCR", "75% LTV", "90/90", "HUD 223(f)" | ACQ |
| "bond proceeds = Total Project Cost", "100% bond-financed", "no equity" | EFB |
| "LP equity required", "GP/LP waterfall", "8% pref, 70/30", "IRR / EM / CoC" | ACQ |

### Rent strategy signals

| Strategy hint | Route |
|---|---|
| "60/20/20 AMI allocation", "80% AMI tier", "Novogradac MTSP rents", "LIHTC rent limits", "AMI ceiling", "missing middle" | EFB |
| "market rent only", "P65 CoStar", "rent comp percentile", "renovation premium $/unit/month", "classic vs renovated", "pure market-rate", "no affordability" | ACQ, market-rate override |
| "4-tier MLA/HAP/80% AMI/Market" | ACQ or EFB default (see Four-Tier Default below) |

---

## Decision Tree

```
Step 1: Check uploaded model filename
   ├── Contains "EFB" or "Bond"  → Route EFB
   ├── Contains "ACQ" or "Flex"  → Route ACQ
   └── No clear filename signal  → Step 2

Step 2: Scan OM and chat history for keyword clusters
   ├── 2+ EFB cluster keywords, 0 ACQ  → Route EFB
   ├── 2+ ACQ cluster keywords, 0 EFB  → Route ACQ
   ├── Mixed signals or both          → Step 3
   └── No signals at all              → Step 3

Step 3: Check property attributes
   ├── Property in TX with mention of PFC/HFC/Hays Co              → Route EFB (high probability)
   ├── Property in GA with mention of DA/DDA/URA/bond-lease         → Route EFB with PILOT (see §GA Exception)
   ├── Property in FL with mention of HFA / nonprofit / §196.1978   → Route EFB
   └── Property fits none of the above                              → Step 4

Step 4: Check for market-rate override signal
   ├── User specifies "market-rate only" / "no affordability"  → ACQ, market-rate override
   └── No market-rate-only signal                              → ACQ, four-tier default
        (four-tier default applies to ALL deals including
         2020+ vintage near-stabilized; see §Near-Stabilized below)

Step 5: If still ambiguous after Steps 1-4
   └── Present A/B with consequence summary (see SKILL.md Phase 0)
```

---

## When to Ask vs When to Auto-Route

**Auto-route without asking when:**
- Filename has a clear EFB or ACQ signal AND no contradicting keyword signals.
- 2+ keyword cluster signals all pointing the same way, 0 pointing the other way.
- User explicitly said "underwrite as EFB" or "underwrite as ACQ" earlier in the session.

**Always ask when:**
- Both EFB Mini Model and ACQ Mini Model are uploaded.
- The model is uploaded but no OM, comps, or context exists yet.
- Near-stabilized 2020+ vintage deal without an explicit structure indicator (EFB vs ACQ execution).
- Property in Georgia (PILOT vs $0 is structurally different, see §GA Exception).

**Default when truly unable to decide:** Route ACQ with four-tier mixed-income default. Conventional underwriting is the broader use case and the user can override if needed.

---

## Four-Tier Default (Applies to ALL ACQ Deals Unless Overridden)

The default revenue approach for any ACQ deal is the four-tier mixed-income structure: 49% market-rate (MLA) / 51% affordable. The 51% affordable block is split into HAP (25-50% of the affordable block, concentrated on larger bedroom types) and 80% AMI (balance). See [references/04-acq-revenue.md](.skills/dream-underwrite/references/04-acq-revenue.md) for full tier allocation methodology.

The market-rate override applies only when the user explicitly says so. Do not default to pure market-rate.

---

## Edge Cases

### Near-Stabilized Core-Plus (2020+ Vintage Institutional-Quality)

Near-stabilized 2020+ vintage institutional-quality deals in late lease-up are NOT a special routing case. Route as ACQ or EFB based on the standard signals above, then apply the four-tier default for revenue (unless user specifies market-rate only). The near-stabilized designation affects hurdle treatment and vacancy curves, not routing.

**When routed ACQ, apply Near-Stabilized Core-Plus Hurdle Relaxation (see below):**
- Treat as core-plus, not value-add. Manual's absolute minimums (14% IRR, 1.5x EM, 15% net investor IRR) are reference points, not hard cuts.
- Vintage CoC floors still apply: 2020+ → 6.0%, 2000-2019 → 7.0%.
- Throw out the 90/90 rule as a CLOSING gate. Discuss path to 90/90 for the refi but do not gate close.
- Exit cap typically 50-100 bps tighter than comparable taxable product.

### Near-Stabilized Core-Plus Hurdle Relaxation

When a near-stabilized 2020+ vintage institutional-quality deal routes ACQ, the Shieldstone Multifamily Manual v2 absolute minimums are reference points, not hard cuts. This applies regardless of property brand or builder. The relaxation logic is encoded in [references/04-acq-revenue.md](.skills/dream-underwrite/references/04-acq-revenue.md) Near-Stabilized Core-Plus Hurdle Relaxation section.

### Georgia Bond-Lease PILOT Exception

GA has a unique exemption mechanism: Development Authority (DA, DDA, URA) bond-lease structures produce a **PILOT** (Payment in Lieu of Taxes) schedule, not a pure $0 exemption. PILOT is typically 40-60% of fee-simple ad valorem.

**Route a GA deal as EFB, BUT do not set tax = $0.** Underwrite the modeled PILOT schedule per [references/06-property-tax.md](.skills/dream-underwrite/references/06-property-tax.md) GA Bond-Lease section. Note in chat: "GA DA bond-lease produces PILOT ~$X/year over 10-year hold, NOT $0 exemption."

The only GA path that produces a clean $0 is §8-3-8 Housing Authority fee ownership with a Private Enterprise Agreement covering substantially all units, AND it carries a hard April 1 filing deadline. A GA deal closing after Q3 will NOT pick up the HA exemption until the following tax year.

### Texas PFC vs HFC vs HA Choice

Three Texas vehicles produce a 100% property tax exemption:

| Vehicle | Statute | Notes for routing |
|---|---|---|
| **PFC** (Public Facility Corporation, Chapter 303) | Tex. Loc. Gov. Code Ch 303, Tex. Tax Code §11.11 | Post-HB 2071 set-asides: 50% @ 80% AMI etc. Local jurisdiction must have PFC. |
| **HFC** (Housing Finance Corporation, Chapter 394) | Tex. Loc. Gov. Code Ch 394 | Post-HB 21 (2025): "traveling HFC" deals dead. Issuer must have jurisdiction over the asset. Legacy cure deadline 12/31/2026. |
| **HA** (Housing Authority, Chapter 392) | Tex. Loc. Gov. Code Ch 392 | Governmental ownership. Most stable post-HB 2071 / HB 21 reform environment. |

Routing decision: route EFB regardless of vehicle choice. The vehicle choice (PFC vs HFC vs HA) is a deal-structuring question that bond counsel resolves, not a UW routing question. Document the assumed vehicle in chat but proceed with EFB workflow.

### Texas Non-Ad-Valorem Special Districts (MUD/PID)

When routing a TX deal as EFB, ALWAYS check whether the property is in a MUD (Municipal Utility District), PID (Public Improvement District), or other special district. These assessments are NOT covered by the governmental-ownership exemption, they continue regardless of ownership structure. Flag this for Phase 9 ([references/06-property-tax.md](.skills/dream-underwrite/references/06-property-tax.md) TX Non-Ad-Valorem section).

### Florida Live Local Act (§196.1979): Upside Layer Only

The Live Local Act provides a property tax exemption for for-profit ownership of properties with 40% of units at 80% or 120% AMI set-asides. **It requires annual recertification**, which means it is NOT lender-underwritable as primary. Route a Live Local deal as ACQ (because ownership is for-profit) but note Live Local as an upside layer in the property tax analysis.

### Pre-2020 ACQ Value-Add (the Manual's primary use case)

Pre-2020 vintage, traditional value-add, full reassessment, equity-required, bridge-to-agency at 5-7 year hold, this is the Shieldstone Multifamily Manual v2's primary use case. Route ACQ. Apply Manual's full hurdle stack (Gateway 14-16%, Secondary 16-19%, Tertiary 18-22% IRR; vintage CoC floors; risk premia for occupancy/age/renovation/financing per [references/13-manual-standards.md](.skills/dream-underwrite/references/13-manual-standards.md)).

---

## Routing Output (What to Tell the User)

After determining routing, surface this in chat:

```
Routing: [EFB or ACQ]
Basis: [filename match, keyword signals, OM context, or user confirmation]
Primary template: [EFB Mini Model or ACQ Mini Model / Flex Model]
Tax logic: [$0 exemption / state-specific reassessment / GA PILOT]
Financing logic: [bond sizing 1.15x / bridge-to-agency 1.25x / HUD 223(f)]
Return logic: [DSCR-driven, no equity / IRR + EM + CoC + net investor IRR]
Revenue default: [four-tier mixed-income / market-rate override (user-specified)]
Key references for this routing:
  - [references/0X.md and 0Y.md]
```

This becomes the routing audit trail. Note it once and proceed.

---

## Failure Modes to Avoid

1. **Routing ACQ but writing $0 property tax:** happens when the master skill is run on an ACQ deal but the EFB Mini Model template's tax exemption breaker is left ON. Always verify the exemption switch state matches the routing.
2. **Routing EFB but using ACQ fees:** the EFB Mini Model template defaults to 5% acquisition fee. If routed EFB, that's correct. If accidentally routed EFB but the deal is actually ACQ, 5% will be 5-10x too high.
3. **Routing EFB on a Georgia deal without flagging PILOT:** produces a $0 tax assumption that is structurally wrong. Always check state when routing EFB.
4. **Routing ACQ on a near-stabilized core-plus deal but applying full Manual hurdles:** near-stabilized core-plus is not traditional value-add. Apply relaxed hurdles per Near-Stabilized Core-Plus Hurdle Relaxation section.
5. **Asking the routing question when filename clearly tells you:** wastes a turn. Auto-route when filename is unambiguous.
6. **Defaulting to pure market-rate revenue when user has not specified it:** the four-tier mixed-income structure is the default. Market-rate override requires explicit user instruction.
