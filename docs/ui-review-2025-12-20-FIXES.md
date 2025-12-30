# Dream UI Review - Proposed Fixes
**Date:** December 20, 2025  
**Related Document:** `ui-review-2025-12-20.md`

This document contains specific code changes to fix the critical and high-priority issues identified in the UI review.

---

## Critical Fix #1: Add `tabular-nums` to ALL Financial Metrics

### File: `src/components/MetricCard.tsx`

**Change Line 50:**
```typescript
// BEFORE:
<p className={`text-3xl font-heading font-semibold mt-2 ${statusColors[status]}`}>
  {value}
</p>

// AFTER:
<p className={`text-3xl font-heading font-semibold mt-2 tabular-nums ${statusColors[status]}`}>
  {value}
</p>
```

---

### File: `src/pages/AnalysisView.tsx`

**Change Line 23 (MetricCard component):**
```typescript
// BEFORE:
<span className="text-3xl font-bold text-secondary font-heading">{value}</span>

// AFTER:
<span className="text-3xl font-bold text-secondary font-heading tabular-nums">{value}</span>
```

**Change Lines 89, 94 (Executive Summary scores):**
```typescript
// BEFORE (line 89):
<div className="text-4xl font-bold font-heading">87</div>

// AFTER:
<div className="text-4xl font-bold font-heading tabular-nums">87</div>

// BEFORE (line 94):
<div className="text-4xl font-bold font-heading">High</div>

// AFTER:
<div className="text-4xl font-bold font-heading tabular-nums">High</div>
```

**Change Table Cells (Lines 152-166):**
```typescript
// BEFORE:
<td className="py-2 text-secondary">96</td>
<td className="py-2 text-secondary">750</td>
<td className="py-2 text-secondary">$1,250</td>

// AFTER:
<td className="px-4 py-3 text-right text-secondary font-heading tabular-nums">96</td>
<td className="px-4 py-3 text-right text-secondary font-heading tabular-nums">750</td>
<td className="px-4 py-3 text-right text-secondary font-heading tabular-nums">$1,250</td>
```

**Apply same fix to:**
- Lines 158-160 (2 Bed / 2 Bath row)
- Lines 162-166 (3 Bed / 2 Bath row)
- Lines 240-259 (Price sensitivity table)

**Change Financial Analysis Table (Lines 199-213):**
```typescript
// BEFORE:
<span className="font-medium text-secondary">$35,340,000</span>

// AFTER:
<span className="font-medium text-secondary font-heading tabular-nums">$35,340,000</span>
```

Apply to all financial values in the Sources & Uses section.

---

### File: `src/pages/PipelineBoard.tsx`

**Change Line 37:**
```typescript
// BEFORE:
<span className="text-xs font-medium text-secondary">{(deal.price / 1000000).toFixed(1)}M</span>

// AFTER:
<span className="text-xs font-medium text-secondary font-heading tabular-nums">{(deal.price / 1000000).toFixed(1)}M</span>
```

---

## Critical Fix #2: Complete CSS Variables System

### File: `src/index.css`

**Replace entire `:root` and add `.dark` section (Lines 11-42):**

```css
@layer base {
  :root {
    /* Fonts */
    --font-heading: 'Playfair Display', serif;
    --font-body: 'Libre Franklin', sans-serif;

    /* Primary Colors - Dark Slate */
    --color-primary: #28323E;
    --color-primary-light: #3C4856;
    --color-primary-dark: #1A1F26;

    /* Secondary Colors - Charcoal (for text) */
    --color-secondary: #3C4856;
    --color-secondary-light: #5C6876;
    --color-secondary-muted: #9DA3AA;

    /* Accent Colors - Deep Teal */
    --color-accent: #005253;
    --color-accent-dark: #003F3F;
    --color-accent-light: #007A7C;

    /* YinMn Blue - Interactive Elements */
    --color-yinmn-blue: #2E5090;
    --color-yinmn-blue-dark: #1E3A6B;
    --color-yinmn-blue-light: #4A6BA8;

    /* Semantic Colors */
    --color-success: #58ABA8;
    --color-warning: #F3B8A7;
    --color-danger: #C94A3E;
    --color-info: #95C9E6;

    /* Semantic Backgrounds */
    --color-bg-success: #E6F6F6;
    --color-bg-warning: #FEF4F2;
    --color-bg-danger: #FDF2F1;
    --color-bg-info: #F0F8FC;

    /* Background Colors */
    --color-bg-primary: #FFFFFF;
    --color-bg-secondary: #F8F7F5;
    --color-bg-tertiary: #EBE5DE;

    /* Border Colors */
    --color-border: #D6C9BA;
    --color-border-subtle: #E8E0D6;
    --color-border-focus: #005253;
  }

  .dark {
    /* Dark Mode - Primary Colors */
    --color-primary: #F8F7F5;
    --color-primary-light: #E2E8F0;
    --color-primary-dark: #CBD5E1;

    /* Dark Mode - Secondary Text */
    --color-secondary: #D1D5DB;
    --color-secondary-light: #9CA3AF;
    --color-secondary-muted: #6B7280;

    /* Dark Mode - Accent Colors */
    --color-accent: #007A7C;
    --color-accent-dark: #005253;
    --color-accent-light: #009FA2;

    /* Dark Mode - YinMn Blue (enhanced visibility) */
    --color-yinmn-blue: #4A6BA8;
    --color-yinmn-blue-dark: #2E5090;
    --color-yinmn-blue-light: #5B7FC4;

    /* Dark Mode - Semantic Colors */
    --color-success: #58ABA8;
    --color-warning: #F3B8A7;
    --color-danger: #F87171;
    --color-info: #60A5FA;

    /* Dark Mode - Semantic Backgrounds (with opacity) */
    --color-bg-success: rgba(88, 171, 168, 0.15);
    --color-bg-warning: rgba(243, 184, 167, 0.15);
    --color-bg-danger: rgba(248, 113, 113, 0.15);
    --color-bg-info: rgba(96, 165, 250, 0.15);

    /* Dark Mode - Backgrounds */
    --color-bg-primary: #1E293B;
    --color-bg-secondary: #0F172A;
    --color-bg-tertiary: #334155;

    /* Dark Mode - Borders */
    --color-border: #334155;
    --color-border-subtle: #475569;
    --color-border-focus: #4A6BA8;
  }

  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: var(--font-body);
    color: var(--color-secondary);
    background-color: var(--color-bg-secondary);
    min-height: 100vh;
  }

  h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-heading);
    color: var(--color-primary);
  }
}
```

---

### File: `tailwind.config.js`

**Update colors section to include YinMn Blue (Lines 10-41):**

```javascript
colors: {
  primary: {
    DEFAULT: 'var(--color-primary)',
    light: 'var(--color-primary-light)',
    dark: 'var(--color-primary-dark)',
  },
  secondary: {
    DEFAULT: 'var(--color-secondary)',
    light: 'var(--color-secondary-light)',
    muted: 'var(--color-secondary-muted)',
  },
  accent: {
    DEFAULT: 'var(--color-accent)',
    dark: 'var(--color-accent-dark)',
    light: 'var(--color-accent-light)',
  },
  'yinmn-blue': {
    DEFAULT: 'var(--color-yinmn-blue)',
    dark: 'var(--color-yinmn-blue-dark)',
    light: 'var(--color-yinmn-blue-light)',
  },
  background: {
    primary: 'var(--color-bg-primary)',
    secondary: 'var(--color-bg-secondary)',
    tertiary: 'var(--color-bg-tertiary)',
  },
  border: {
    DEFAULT: 'var(--color-border)',
    subtle: 'var(--color-border-subtle)',
    focus: 'var(--color-border-focus)',
  },
  brand: {
    success: 'var(--color-success)',
    warning: 'var(--color-warning)',
    danger: 'var(--color-danger)',
    info: 'var(--color-info)',
    'bg-success': 'var(--color-bg-success)',
    'bg-warning': 'var(--color-bg-warning)',
    'bg-danger': 'var(--color-bg-danger)',
    'bg-info': 'var(--color-bg-info)',
  }
},
```

---

## Critical Fix #3: Replace Hardcoded Colors with Design Tokens

### File: `src/components/Layout.tsx`

**Change Line 32 (Header background):**
```typescript
// BEFORE:
<header className="bg-[#005253] dark:bg-[#2B52EF] border-b border-white/10 ...">

// AFTER:
<header className="bg-accent dark:bg-yinmn-blue border-b border-white/10 ...">
```

**Change Line 39 (Logo text color):**
```typescript
// BEFORE:
<span className="text-[#005253] dark:text-[#2B52EF] font-serif font-bold text-lg">D</span>

// AFTER:
<span className="text-accent dark:text-yinmn-blue font-serif font-bold text-lg">D</span>
```

**Change Line 91 (Avatar color):**
```typescript
// BEFORE:
<div className="h-8 w-8 rounded-full bg-white text-[#005253] dark:text-[#2B52EF] ...">

// AFTER:
<div className="h-8 w-8 rounded-full bg-white text-accent dark:text-yinmn-blue ...">
```

---

### File: `src/pages/AnalysisView.tsx`

**Change Line 20 (MetricCard border):**
```typescript
// BEFORE:
<Card className="p-5 flex flex-col justify-between h-full border-t-4 border-t-[#005253] hover:border-t-accent transition-all">

// AFTER:
<Card className="p-5 flex flex-col justify-between h-full border-t-4 border-t-accent hover:border-t-accent-dark transition-all">
```

**Change Line 41 (Accordion icon background):**
```typescript
// BEFORE:
<div className={`p-2 rounded-md ${isOpen ? 'bg-[#005253] text-white' : 'bg-background-tertiary text-secondary'}`}>

// AFTER:
<div className={`p-2 rounded-md ${isOpen ? 'bg-accent text-white' : 'bg-background-tertiary text-secondary'}`}>
```

**Change Line 82 (Executive Summary gradient):**
```typescript
// BEFORE:
<div className="p-8 md:w-1/3 bg-gradient-to-br from-[#005253] to-primary flex flex-col ...">

// AFTER:
<div className="p-8 md:w-1/3 bg-gradient-to-br from-accent to-primary flex flex-col ...">
```

**Change Line 310 (Navigation active state):**
```typescript
// BEFORE:
<button onClick={() => setExpandedSection('financial')} className="w-full text-left px-2 py-1.5 text-sm text-[#005253] dark:text-accent font-medium bg-[#005253]/10 rounded transition-colors border-l-2 border-[#005253] dark:border-accent pl-1.5">

// AFTER:
<button onClick={() => setExpandedSection('financial')} className="w-full text-left px-2 py-1.5 text-sm text-accent font-medium bg-accent/10 rounded transition-colors border-l-2 border-accent pl-1.5">
```

**Change Line 327 (Avatar background):**
```typescript
// BEFORE:
<div className="h-5 w-5 rounded-full bg-[#005253] text-white ...">

// AFTER:
<div className="h-5 w-5 rounded-full bg-accent text-white ...">
```

---

### File: `src/components/UIComponents.tsx`

**Change Line 23 (Primary button):**
```typescript
// BEFORE:
primary: "bg-[#005253] hover:bg-[#003f3f] text-white focus:ring-[#005253] shadow-sm",

// AFTER:
primary: "bg-accent hover:bg-accent-dark text-white focus:ring-2 focus:ring-accent focus:ring-offset-2 shadow-sm",
```

**Change Line 88 (Input focus ring):**
```typescript
// BEFORE:
className="flex h-10 w-full rounded-md border border-border bg-background-primary px-3 py-2 text-sm text-secondary placeholder:text-secondary-muted focus:outline-none focus:ring-2 focus:ring-[#005253] focus:border-transparent ..."

// AFTER:
className="flex h-10 w-full rounded-md border border-border bg-background-primary px-3 py-2 text-sm text-secondary placeholder:text-secondary-muted focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent ..."
```

---

## High Priority Fix #4-7: Table Styling Improvements

### File: `src/pages/AnalysisView.tsx`

**Fix Table Headers (Lines 141-147):**
```typescript
// BEFORE:
<thead>
  <tr className="border-b border-border text-xs text-secondary-muted">
    <th className="py-2 font-medium">Type</th>
    <th className="py-2 font-medium">Count</th>
    <th className="py-2 font-medium">Sq Ft</th>
    <th className="py-2 font-medium">Rent</th>
  </tr>
</thead>

// AFTER:
<thead>
  <tr className="bg-background-secondary border-b border-border text-sm text-secondary">
    <th className="px-4 py-3 text-left font-semibold">Type</th>
    <th className="px-4 py-3 text-left font-semibold">Count</th>
    <th className="px-4 py-3 text-right font-semibold">Sq Ft</th>
    <th className="px-4 py-3 text-right font-semibold">Rent</th>
  </tr>
</thead>
```

**Fix Table Body Rows with Hover (Lines 150-167):**
```typescript
// BEFORE:
<tbody>
  <tr className="border-b border-border">
    <td className="py-2 text-secondary">1 Bed / 1 Bath</td>
    <td className="py-2 text-secondary">96</td>
    <td className="py-2 text-secondary">750</td>
    <td className="py-2 text-secondary">$1,250</td>
  </tr>
  ...
</tbody>

// AFTER:
<tbody>
  <tr className="border-b border-border hover:bg-background-tertiary transition-colors">
    <td className="px-4 py-3 text-secondary">1 Bed / 1 Bath</td>
    <td className="px-4 py-3 text-secondary">96</td>
    <td className="px-4 py-3 text-right text-secondary font-heading tabular-nums">750</td>
    <td className="px-4 py-3 text-right text-secondary font-heading tabular-nums">$1,250</td>
  </tr>
  ...
</tbody>
```

**Fix Price Sensitivity Table (Lines 232-259):**
```typescript
// BEFORE:
<thead>
  <tr className="text-xs text-secondary-muted bg-background-tertiary">
    <th className="py-2 rounded-l">Purchase Price</th>
    ...
  </tr>
</thead>

// AFTER:
<thead>
  <tr className="bg-background-secondary text-sm text-secondary">
    <th className="px-4 py-3 text-left font-semibold rounded-l">Purchase Price</th>
    <th className="px-4 py-3 text-right font-semibold">$/Unit</th>
    <th className="px-4 py-3 text-right font-semibold">IRR</th>
    <th className="px-4 py-3 text-left font-semibold rounded-r">Rec</th>
  </tr>
</thead>
```

**Fix Highlighted Row (Lines 247-252):**
```typescript
// BEFORE:
<tr className="bg-primary-dark/5 dark:bg-primary-dark/20 font-semibold">
  <td className="py-2 text-primary-dark border-l-2 border-primary-dark">$35.3M (Ask)</td>
  <td className="py-2 text-primary-dark">$142k</td>
  <td className="py-2 text-primary-dark">18.5%</td>
  ...
</tr>

// AFTER:
<tr className="bg-accent/5 dark:bg-accent/20 font-semibold hover:bg-accent/10 transition-colors">
  <td className="px-4 py-3 text-accent border-l-2 border-accent">$35.3M (Ask)</td>
  <td className="px-4 py-3 text-right text-accent font-heading tabular-nums">$142k</td>
  <td className="px-4 py-3 text-right text-accent font-heading tabular-nums">18.5%</td>
  <td className="px-4 py-3"><span className="text-brand-success font-bold text-xs">STRONG</span></td>
</tr>
```

---

## High Priority Fix #9: MetricCard Component

### File: `src/components/MetricCard.tsx`

**Replace entire component (Lines 33-59):**
```typescript
export default function MetricCard({
  label,
  value,
  subtext,
  trend,
  status = 'neutral',
}: MetricCardProps) {
  const TrendIcon = trend ? trendIcons[trend] : null;

  return (
    <div className="bg-background-primary rounded-lg border border-border p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <p className="text-sm text-secondary-muted font-medium">{label}</p>
        {TrendIcon && (
          <TrendIcon size={16} className={trendColors[trend!]} />
        )}
      </div>
      <p className={`text-3xl font-heading font-semibold mt-2 tabular-nums ${statusColors[status]}`}>
        {value}
      </p>
      {subtext && (
        <p className="text-sm text-secondary-muted mt-1">{subtext}</p>
      )}
    </div>
  );
}
```

---

## Implementation Checklist

### Critical Issues (Must Fix First)
- [ ] Issue #1: Add `tabular-nums` to all numeric displays
  - [ ] MetricCard.tsx
  - [ ] AnalysisView.tsx (metric cards, executive summary, tables)
  - [ ] PipelineBoard.tsx
- [ ] Issue #2: Complete CSS variable system in index.css
  - [ ] Add all color variables
  - [ ] Add dark mode variables
  - [ ] Update Tailwind config
- [ ] Issue #3: Replace all hardcoded colors
  - [ ] Layout.tsx (4 locations)
  - [ ] AnalysisView.tsx (5 locations)
  - [ ] UIComponents.tsx (2 locations)

### High Priority Issues
- [ ] Issue #4: Add `tabular-nums` to table cells
- [ ] Issue #5: Fix table header styling
- [ ] Issue #6: Add table row hover states
- [ ] Issue #7: Fix table cell padding
- [ ] Issue #8: Fix button focus states
- [ ] Issue #9: Update MetricCard component
- [ ] Issue #10: Fix input focus states
- [ ] Issue #11: Standardize card shadows

### Testing After Fixes
- [ ] Visual inspection in browser (light mode)
- [ ] Visual inspection in browser (dark mode)
- [ ] Check numeric alignment in tables
- [ ] Test all interactive states (hover, focus)
- [ ] Verify color consistency across pages
- [ ] Test responsive behavior
- [ ] Run accessibility audit

---

## Verification Steps

After implementing fixes:

1. **Visual Check:**
   ```bash
   npm run dev
   ```
   Navigate to http://localhost:5173 and verify:
   - All numbers are properly aligned (tabular-nums working)
   - Colors match design language
   - Dark mode toggle works correctly
   - Tables have hover states

2. **Code Check:**
   ```bash
   # Search for hardcoded colors (should find none in components):
   grep -r "bg-\[#" src/components/
   grep -r "text-\[#" src/components/
   grep -r "border-\[#" src/pages/
   
   # Verify tabular-nums usage:
   grep -r "tabular-nums" src/
   ```

3. **Design Token Check:**
   - All colors should use CSS variables via Tailwind classes
   - No hardcoded hex values in component files
   - Dark mode should work automatically

---

## Notes for Developers

### Fonts
The design language specifies:
- **Heading/Numbers:** `Playfair Display` (serif)
- **Body:** `Libre Franklin` (sans-serif)

Already loaded via Google Fonts in `index.css`. References to "Visby CF" and "Aleo" can be removed.

### Tabular Numerals
**Critical for CRE applications:**
- ALWAYS use `tabular-nums` class on financial data
- Combine with `font-heading` for serif numerals
- Right-align numeric table columns with `text-right`

### Design Token Priority
Use this order when applying colors:
1. Design tokens (e.g., `bg-accent`)
2. Semantic colors (e.g., `text-brand-success`)
3. Theme colors (e.g., `text-primary`)
4. Never hardcoded hex values

### Dark Mode
After CSS variable fix, dark mode should work automatically:
- No need for manual `dark:` classes on design tokens
- Only use `dark:` for structural differences (layout, opacity)
- Test toggle thoroughly after implementing fixes

---

**End of Fixes Document**

*Use this document as implementation guide for resolving UI review findings.*



