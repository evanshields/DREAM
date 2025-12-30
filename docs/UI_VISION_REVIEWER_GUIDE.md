# Dream – Vision-based UI Reviewer

**Version:** 1.0  
**Last Updated:** December 2025  
**Purpose:** Visually inspect Dream UI in the browser and critique against design standards

---

## Overview

The Vision-based UI Reviewer is an AI agent that uses browser automation and visual inspection to audit Dream's UI implementation against the design language specification (`design-language-dream.md`) and CRE (Commercial Real Estate) usability best practices.

---

## Core Responsibilities

### 1. Visual Inspection
- Capture screenshots of Dream running in browser (via Playwright/browser tools)
- Analyze visual elements for design consistency
- Identify deviations from `design-language-dream.md`
- Compare UI states (empty, loading, error, populated)

### 2. Design Audit
Identify and document:
- **Spacing Issues**: Misaligned padding, margins, or inconsistent gaps
- **Grid Misalignment**: Broken layouts, uneven columns, improper responsive behavior
- **Color Violations**: Off-palette colors, incorrect semantic color usage
- **Typography Problems**: Wrong font families, sizes, weights, or missing `tabular-nums`
- **Shadow Inconsistencies**: Incorrect shadow depth or inappropriate usage
- **Border Issues**: Wrong colors, thickness, or radius
- **Component Token Violations**: Buttons, cards, inputs not following design specs

### 3. CRE Usability Review
Assess domain-specific usability:
- **Numeric Legibility**: Financial data readability and alignment
- **Table Scannability**: Row striping, hover states, header clarity
- **Metric Hierarchy**: Visual prominence of key underwriting metrics
- **Data Density**: Appropriate information density for professional users
- **Comparison Clarity**: Side-by-side scenario comparisons are easy to understand
- **Action Clarity**: Primary/secondary actions are clearly differentiated
- **Error States**: Financial warnings and validation messages are prominent

### 4. Propose and Implement Fixes
- Document specific issues with file paths and line numbers
- Propose concrete fixes aligned with design language
- Implement fixes when permitted by user
- Verify fixes via re-inspection

---

## Usage

### Activation
The Vision-based UI Reviewer activates when the user mentions:
- "Vision-based UI Reviewer" or "Vision UI Reviewer"
- "UI Vision Review" or "Visual UI Audit"
- "Inspect UI in browser"
- "Screenshot review" or "Visual inspection"

### Prerequisites
- Dream app must be running locally (e.g., `http://localhost:3000`, `http://localhost:5173`)
- Browser automation tools available (Playwright via MCP)
- Design language file exists: `design-language-dream.md`

---

## Process

### Phase 1: Preparation
1. **Confirm app is running**: Ask user for local URL or check terminals
2. **Read design language**: Load `design-language-dream.md` as reference
3. **Identify pages to review**: Dashboard, deal detail, underwriting, scenarios, etc.
4. **Create review document**: Initialize `docs/ui-review-[date].md`

### Phase 2: Visual Inspection
1. **Navigate to page**: Use browser automation to load URL
2. **Capture snapshot**: Take accessibility snapshot (preferred) or screenshot
3. **Analyze elements**: Inspect:
   - Spacing and layout
   - Colors and backgrounds
   - Typography and font usage
   - Component styling
   - Interactive states (hover, focus)
   - Data table structure
   - Metric card hierarchy
4. **Document findings**: Record issues with screenshots and descriptions
5. **Repeat for all key pages**

### Phase 3: Analysis
1. **Categorize issues**: Group by severity and type
   - **Critical**: Broken layouts, illegible text, missing key elements
   - **High**: Color violations, typography inconsistencies, poor metric hierarchy
   - **Medium**: Spacing issues, minor alignment problems
   - **Low**: Subtle shadow/border inconsistencies
2. **Assess CRE usability**: Evaluate domain-specific concerns
3. **Prioritize fixes**: Rank issues by impact on user experience

### Phase 4: Reporting
1. **Create detailed report**: `docs/ui-review-[date].md` with:
   - Executive summary
   - Findings by page and severity
   - Annotated screenshots
   - Specific code fixes
   - Recommendations
2. **Include metrics**:
   - Total issues found
   - Issues by severity
   - Pages reviewed
   - Compliance score (if applicable)

### Phase 5: Fix Implementation (Optional)
1. **Propose fixes**: Specific code changes with before/after examples
2. **Implement if permitted**: Make changes to codebase
3. **Re-inspect**: Verify fixes via visual re-review
4. **Update report**: Mark resolved issues

---

## Output Format

### Review Document Structure

```markdown
# Dream UI Vision Review - [Date]

**Reviewer:** AI Vision-based UI Reviewer  
**Design Language Version:** [version from design-language-dream.md]  
**Pages Reviewed:** [list of pages]  
**Total Issues Found:** [number]

---

## Executive Summary

[High-level overview of findings, key issues, and recommendations]

---

## Review Scope

### Pages Reviewed
- Dashboard (`/`)
- Deal List (`/deals`)
- Deal Detail (`/deals/[id]`)
- Underwriting View (`/deals/[id]/underwriting`)
- Scenarios (`/scenarios`)

### Design Standards Reference
- `design-language-dream.md` (v1.3)

### CRE Usability Checklist
- [ ] Numeric legibility (tabular-nums, proper alignment)
- [ ] Table scannability (row striping, hover states)
- [ ] Metric hierarchy (visual prominence)
- [ ] Data density (appropriate for professional users)
- [ ] Comparison clarity (side-by-side scenarios)
- [ ] Action clarity (primary/secondary differentiation)
- [ ] Error states (warnings, validation)

---

## Findings

### Page: Dashboard (`/`)

#### Issue #1: Spacing - Inconsistent Card Padding [HIGH]
**Severity:** High  
**Category:** Spacing  
**Location:** `components/cards/KpiTile.tsx:12`

**Description:**
KPI cards use `p-3` (12px) instead of standard `p-4` (16px) or `p-6` (24px) per design language.

**Screenshot:**
![Dashboard spacing issue](./screenshots/dashboard-spacing-001.png)

**Design Language Reference:**
- Section: Component Tokens > Cards
- Expected: `p-4` (16px) or `p-6` (24px)
- Actual: `p-3` (12px)

**Proposed Fix:**
```typescript
// components/cards/KpiTile.tsx
- <div className="bg-background-primary border border-border rounded-lg p-3">
+ <div className="bg-background-primary border border-border rounded-lg p-6">
```

**Impact:** 
Card padding is not aligned with design system, creates visual inconsistency across dashboard.

---

#### Issue #2: Typography - Missing tabular-nums on Metrics [CRITICAL]
**Severity:** Critical  
**Category:** Typography  
**Location:** `components/cards/KpiTile.tsx:15`

**Description:**
Financial metrics lack `tabular-nums` class, causing misalignment when values change.

**Screenshot:**
![Missing tabular nums](./screenshots/dashboard-tabular-001.png)

**Design Language Reference:**
- Section: Typography > Numeric Displays
- Expected: All numeric displays must use `tabular-nums`
- Actual: Missing `tabular-nums` class

**Proposed Fix:**
```typescript
// components/cards/KpiTile.tsx
- <p className="text-3xl font-heading font-semibold text-primary">
+ <p className="text-3xl font-heading font-semibold tabular-nums text-primary">
    {value}
  </p>
```

**Impact:** 
Numbers don't align properly in tables and cards, reducing scannability of financial data.

---

### Page: Underwriting View (`/deals/[id]/underwriting`)

#### Issue #3: Tables - Missing Row Hover States [MEDIUM]
**Severity:** Medium  
**Category:** Interactive States  
**Location:** `components/tables/T12Table.tsx:45`

**Description:**
T12 financial table rows lack hover states, making it difficult to track rows across wide tables.

**Screenshot:**
![T12 table no hover](./screenshots/underwriting-table-hover-001.png)

**Design Language Reference:**
- Section: Component Tokens > Tables
- Expected: `hover:bg-background-tertiary` (subtle row highlight)
- Actual: No hover state

**Proposed Fix:**
```typescript
// components/tables/T12Table.tsx
- <tr className="border-b border-border">
+ <tr className="border-b border-border hover:bg-background-tertiary transition-colors">
```

**Impact:** 
Reduces table scannability, especially for wide financial tables common in CRE underwriting.

---

## CRE Usability Analysis

### Numeric Legibility: 7/10
**Strengths:**
- Serif font used for headings and large numbers ✅
- Proper decimal precision (2 places for currency) ✅

**Weaknesses:**
- Missing `tabular-nums` on 15+ metric displays ❌
- Inconsistent numeric hierarchy (IRR same size as supporting metrics) ❌

**Recommendations:**
1. Apply `tabular-nums` to ALL numeric displays
2. Establish clear metric hierarchy (Tier 1: `text-4xl`, Tier 2: `text-2xl`, Tier 3: `text-base`)

---

### Table Scannability: 6/10
**Strengths:**
- Proper borders and dividers ✅
- Numeric columns right-aligned ✅

**Weaknesses:**
- Missing row hover states ❌
- No row striping (even/odd) ❌
- Headers not sticky on scroll ❌

**Recommendations:**
1. Add `hover:bg-background-tertiary` to all table rows
2. Implement `even:bg-background-secondary` for row striping
3. Make headers sticky with `sticky top-0 z-10 bg-background-secondary`

---

### Metric Hierarchy: 5/10
**Strengths:**
- Key metrics have larger font sizes ✅

**Weaknesses:**
- Insufficient visual separation between Tier 1 and Tier 2 metrics ❌
- No color coding for performance (good/bad) ❌
- Supporting data same prominence as key metrics ❌

**Recommendations:**
1. Use `text-5xl` for Tier 1 metrics (IRR, equity multiple)
2. Apply semantic colors: YinMn Blue for positive, Danger for negative
3. Reduce supporting data to `text-sm text-secondary-muted`

---

## Issue Summary

### By Severity
- **Critical:** 3 issues
- **High:** 7 issues
- **Medium:** 12 issues
- **Low:** 5 issues
- **Total:** 27 issues

### By Category
- **Spacing:** 8 issues
- **Typography:** 6 issues
- **Colors:** 4 issues
- **Interactive States:** 5 issues
- **Layout/Grid:** 3 issues
- **Component Tokens:** 1 issue

### By Page
- **Dashboard:** 8 issues
- **Deal List:** 3 issues
- **Deal Detail:** 5 issues
- **Underwriting View:** 9 issues
- **Scenarios:** 2 issues

---

## Recommendations

### Immediate Fixes (Critical/High)
1. **Add `tabular-nums` to all numeric displays** (15+ locations)
2. **Fix card padding inconsistencies** (8 locations)
3. **Implement table hover states** (3 tables)
4. **Correct color palette violations** (4 locations)

### Short-term Improvements (Medium)
1. Add row striping to tables for better scannability
2. Implement sticky table headers
3. Enhance metric hierarchy with proper sizing
4. Add semantic color coding to performance metrics

### Long-term Enhancements (Low)
1. Conduct full dark mode audit
2. Test responsive behavior on tablet/mobile
3. Validate accessibility compliance (WCAG AA)
4. Create visual regression test suite

---

## Compliance Score

**Overall Compliance:** 72%

### Breakdown
- **Color Palette:** 85% compliant
- **Typography:** 60% compliant (missing tabular-nums)
- **Spacing:** 70% compliant
- **Component Tokens:** 75% compliant
- **CRE Usability:** 65% compliant

---

## Next Steps

1. **Review with team**: Discuss findings and prioritize fixes
2. **Implement critical fixes**: Address all critical and high-severity issues
3. **Re-inspect**: Conduct follow-up visual review after fixes
4. **Establish monitoring**: Set up visual regression testing for future changes

---

## Appendix

### Screenshots
All screenshots saved to `docs/screenshots/ui-review-[date]/`

### Tools Used
- Browser: Chrome via Playwright MCP
- Design Reference: `design-language-dream.md` (v1.3)
- Review Date: [date]

### Related Documents
- `design-language-dream.md` - Design language specification
- `docs/design-audit.md` - Code-level design audit (if exists)
- `UI_ENGINEER_RECOMMENDATIONS.md` - UI engineering guidelines
```

---

## Key Inspection Points

### Spacing Audit
- [ ] Card padding matches design tokens (`p-4` or `p-6`)
- [ ] Consistent gaps between elements (`gap-4`, `gap-6`)
- [ ] Proper section spacing (`mb-8`, `mb-12`)
- [ ] Table cell padding (`px-4 py-3`)
- [ ] Button padding (`px-4 py-2`)

### Color Audit
- [ ] All colors from design language palette
- [ ] No hardcoded hex/rgb values (except design tokens)
- [ ] Proper semantic colors (success, warning, danger, info)
- [ ] Background colors correct (primary, secondary, tertiary)
- [ ] Border colors match design tokens

### Typography Audit
- [ ] Correct font families (`font-heading` for headings, `font-sans` for body)
- [ ] Proper type scale (h1-h6 sizes match design language)
- [ ] `tabular-nums` on ALL numeric displays
- [ ] Correct font weights (bold, semibold, medium, normal)
- [ ] Line heights appropriate (tight for headings, normal for body)

### Component Token Audit
- [ ] Buttons match design specs (sizes, variants, colors)
- [ ] Cards use correct styling (borders, shadows, padding)
- [ ] Inputs follow design tokens (height, padding, focus states)
- [ ] Tables have proper structure (headers, borders, hover)
- [ ] Badges use semantic colors and rounded-full

### CRE Usability Audit
- [ ] Key metrics visually prominent (larger size, bold weight)
- [ ] Financial data highly legible (serif font, tabular-nums)
- [ ] Tables easy to scan (row striping, hover, sticky headers)
- [ ] Comparisons clear (side-by-side layouts, visual separation)
- [ ] Actions clear (primary buttons prominent, secondary subtle)
- [ ] Errors/warnings visible (semantic colors, strong indicators)

---

## Browser Testing Workflow

### 1. Navigate to Page
```javascript
// Example: Navigate to dashboard
await browser.navigate('http://localhost:3000');
```

### 2. Take Accessibility Snapshot
```javascript
// Preferred: Accessibility snapshot
await browser.snapshot();
```

### 3. Take Screenshot (Visual Verification)
```javascript
// For visual inspection
await browser.screenshot({ filename: 'dashboard.png', fullPage: true });
```

### 4. Interact with Elements
```javascript
// Test hover states
await browser.hover({ element: 'Table row', ref: '[data-row="1"]' });
await browser.screenshot({ filename: 'table-hover.png' });

// Test focus states
await browser.click({ element: 'Primary button', ref: '[data-action="analyze"]' });
```

### 5. Check Different States
- Empty state (no data)
- Loading state (skeleton loaders)
- Error state (validation messages)
- Populated state (normal data display)

---

## Common Issues Reference

### Spacing Issues
1. **Magic numbers**: `mb-[23px]` instead of `mb-6`
2. **Inconsistent padding**: Mix of `p-3`, `p-4`, `p-5` instead of standardized `p-4` or `p-6`
3. **Uneven gaps**: Different `gap` values in similar contexts

### Typography Issues
1. **Missing `tabular-nums`**: Most common issue for financial data
2. **Wrong font family**: Using sans-serif for numbers instead of serif
3. **Incorrect sizes**: Not following type scale (e.g., `text-[32px]` instead of `text-3xl`)
4. **Wrong weights**: Using `font-[600]` instead of `font-semibold`

### Color Issues
1. **Hardcoded colors**: `#2E5090` instead of `text-yinmn-blue`
2. **Off-palette colors**: Colors not in design language
3. **Wrong semantic colors**: Using success green for warnings

### Component Issues
1. **Button variants**: Using primary styling for secondary actions
2. **Card shadows**: Using `shadow-lg` instead of `shadow-sm`
3. **Input focus**: Wrong focus ring color or missing entirely
4. **Table hover**: Missing hover states or wrong color

---

## Integration with Other Agents

### Works With
- **UI Engineer (Minimal Pro)**: Reviews their styled output
- **UI Engineer (Analytical Pro)**: Reviews expressive dashboard implementations
- **Design System Enforcer**: Provides visual validation of code-level audits
- **Framework Converter**: Reviews converted Next.js implementations

### Workflow
1. **UI Engineer** creates styled HTML
2. **Framework Converter** converts to Next.js
3. **Vision-based UI Reviewer** inspects visual implementation
4. **Design System Enforcer** refactors code based on findings

---

## Tips for Effective Reviews

### 1. Be Specific
- Include file paths and line numbers
- Provide exact code fixes, not just descriptions
- Reference specific design language sections

### 2. Prioritize Impact
- Focus on critical issues first (legibility, broken layouts)
- Don't nitpick minor shadow variations
- Consider user experience impact

### 3. Provide Context
- Explain WHY something is an issue
- Reference CRE usability needs
- Show before/after examples

### 4. Be Actionable
- Every finding should have a proposed fix
- Include code snippets when possible
- Group related issues for batch fixes

### 5. Test Thoroughly
- Check all key pages
- Test different states (empty, loading, error)
- Verify responsive behavior
- Test interactive elements (hover, focus, click)

---

## FAQ

### Q: How do I start a UI review?
**A:** Ask the agent: "Conduct a Vision-based UI review of Dream" or "Inspect the UI in the browser". Ensure your app is running locally first.

### Q: Do I need to provide screenshots?
**A:** No, the agent will capture screenshots automatically using browser automation tools. However, you can provide screenshots if you notice specific issues.

### Q: How long does a review take?
**A:** Typically 10-20 minutes for a full review of 3-5 key pages, depending on the number of issues found.

### Q: Will the agent fix issues automatically?
**A:** The agent will propose fixes but will ask for permission before making code changes. You can request "review only" or "review and fix".

### Q: Can I review just one page?
**A:** Yes, specify: "Review the dashboard page only" or "Inspect the underwriting view".

### Q: What if my app isn't running?
**A:** The agent will prompt you to start the app or provide a URL. Make sure the development server is running before starting the review.

### Q: Can I review dark mode?
**A:** Yes, mention "Review dark mode" and the agent will test dark mode styling against the dark mode section of the design language.

### Q: How do I track fixes over time?
**A:** Review documents are timestamped (`ui-review-2025-12-20.md`). Compare reports to track progress and ensure issues don't regress.

---

## Version History

- **v1.0** (December 2025): Initial Vision-based UI Reviewer documentation


