# Design System Audit: ShadCN Component Migration

**Date:** December 26, 2025  
**Status:** Audit Complete  
**Priority:** High

---

## Executive Summary

This audit identifies all components that need to be migrated from custom `UIComponents.tsx` to ShadCN UI components. The codebase currently has a **mixed state**: newer components use ShadCN, while older components still use custom implementations.

**Key Findings:**
- ✅ **ShadCN is installed and configured** (`components.json` exists)
- ✅ **9 ShadCN components available**: button, card, badge, input, textarea, select, table, accordion
- ❌ **5 page components** still using custom UIComponents
- ❌ **1 custom component file** (`UIComponents.tsx`) that should be deprecated
- ⚠️ **Custom Input component** defined but not used (ShadCN Input is used instead)

---

## Components Requiring Migration

### 🔴 High Priority (Pages Using Custom Components)

#### 1. `src/pages/Dashboard.tsx`
**Status:** Uses custom `Card` and `Button`  
**Custom Imports:**
```typescript
import { Card, Button } from '../components/UIComponents';
```

**ShadCN Replacement:**
```typescript
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
```

**Migration Notes:**
- Replace `<Card className="...">` with `<Card><CardContent className="...">`
- Replace `<Button variant="primary">` with `<Button variant="default">` (ShadCN uses "default" instead of "primary")
- Replace `<Button variant="secondary">` → same (already matches)
- Replace `<Button variant="ghost">` → same (already matches)
- Custom Button has `icon` prop; ShadCN Button accepts children with icons (just place icon element inside)
- Button size "sm" maps to ShadCN "sm" size

**Impact:** 19 usages of Button, 4 usages of Card

---

#### 2. `src/pages/PipelineBoard.tsx`
**Status:** Uses custom `Badge` and `Button`  
**Custom Imports:**
```typescript
import { Badge, Button } from '../components/UIComponents';
```

**ShadCN Replacement:**
```typescript
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
```

**Migration Notes:**
- Replace `<Badge variant="success">` → `<Badge variant="success">` (ShadCN has success variant)
- Replace `<Badge variant="danger">` → `<Badge variant="danger">` (ShadCN has danger variant)
- Replace `<Badge variant="default">` → `<Badge variant="default">` (matches)
- Button migration same as Dashboard.tsx

**Impact:** ~5 usages of Badge, ~3 usages of Button

---

#### 3. `src/pages/DealIntake.tsx`
**Status:** Uses custom `Card`, `Button`, and `Badge`  
**Custom Imports:**
```typescript
import { Card, Button, Badge } from '../components/UIComponents';
```

**ShadCN Replacement:**
```typescript
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
```

**Migration Notes:**
- Same migration patterns as Dashboard.tsx and PipelineBoard.tsx
- May need CardHeader/CardTitle structure for proper card layout

**Impact:** Unknown exact count, need to check file

---

#### 4. `src/pages/AnalysisView.tsx`
**Status:** Mixed - uses custom `Button`, `Badge`, `Card` AND ShadCN `Table`  
**Custom Imports:**
```typescript
import { Button, Badge, Card } from '../components/UIComponents';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
```

**ShadCN Replacement:**
```typescript
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
```

**Migration Notes:**
- Already using ShadCN Table ✅
- Needs Button, Badge, Card migration (same patterns as above)
- Uses Card in MetricCard component - should use CardContent wrapper

**Impact:** ~10 usages of Button, ~2 usages of Badge, ~8 usages of Card

---

#### 5. `src/pages/DealsList.tsx`
**Status:** Mixed - uses ShadCN `Input`, `Button`, `Select` BUT custom `Card`  
**Custom Imports:**
```typescript
import { Card } from '@/components/UIComponents';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
```

**ShadCN Replacement:**
```typescript
import { Card, CardContent } from '@/components/ui/card';
// Already using ShadCN Input and Button ✅
```

**Migration Notes:**
- Only needs Card migration
- Already using ShadCN Input, Button, Select ✅

**Impact:** ~10-20 usages of Card (check file for exact count)

---

### 🟡 Medium Priority (Custom Components in UIComponents.tsx)

#### 6. `CircularProgress` Component
**Status:** Defined in `UIComponents.tsx` but usage unclear  
**Location:** `src/components/UIComponents.tsx` lines 94-138

**Migration Options:**
- **Option A:** Use ShadCN `progress` component (horizontal bar) - different UI pattern
- **Option B:** Use ShadCN `chart` component for circular charts
- **Option C:** Create custom circular progress using ShadCN styling tokens
- **Option D:** Install a separate circular progress library if needed

**Recommendation:** Check if CircularProgress is actually used. If not used, remove. If used, evaluate if ShadCN Progress component can replace it, or create custom component using ShadCN design tokens.

**Action Required:** Search codebase for `CircularProgress` usage

---

#### 7. Custom `Input` Component
**Status:** Defined in `UIComponents.tsx` but NOT USED  
**Location:** `src/components/UIComponents.tsx` lines 86-91

**Finding:** All components are using ShadCN `Input` from `@/components/ui/input` ✅

**Action Required:** **REMOVE** custom Input from UIComponents.tsx (dead code)

---

### 🟢 Low Priority (Component Deprecation)

#### 8. `src/components/UIComponents.tsx`
**Status:** Should be deprecated after migration  
**Components to Remove:**
- `Button` (replace with ShadCN)
- `Badge` (replace with ShadCN)
- `Card` (replace with ShadCN)
- `Input` (dead code - remove)

**Components to Evaluate:**
- `CircularProgress` (check usage first)

**Action Required:** After all migrations complete, delete `UIComponents.tsx` file

---

## Component Comparison Matrix

| Component | Custom (UIComponents.tsx) | ShadCN Replacement | Variant Mapping | Status |
|-----------|---------------------------|-------------------|-----------------|--------|
| Button | `variant="primary"` | `variant="default"` | ✅ Maps | ⚠️ Need migration |
| Button | `variant="secondary"` | `variant="secondary"` | ✅ Direct match | ⚠️ Need migration |
| Button | `variant="outline"` | `variant="outline"` | ✅ Direct match | ⚠️ Need migration |
| Button | `variant="ghost"` | `variant="ghost"` | ✅ Direct match | ⚠️ Need migration |
| Button | `variant="danger"` | `variant="destructive"` | ⚠️ Name change | ⚠️ Need migration |
| Button | `icon` prop | Icon as child element | ⚠️ API change | ⚠️ Need migration |
| Button | `size="sm/md/lg"` | `size="sm/default/lg"` | ⚠️ "md" → "default" | ⚠️ Need migration |
| Badge | `variant="success"` | `variant="success"` | ✅ Direct match | ⚠️ Need migration |
| Badge | `variant="warning"` | `variant="warning"` | ✅ Direct match | ⚠️ Need migration |
| Badge | `variant="danger"` | `variant="danger"` | ✅ Direct match | ⚠️ Need migration |
| Badge | `variant="info"` | `variant="info"` | ✅ Direct match | ⚠️ Need migration |
| Badge | `variant="default"` | `variant="default"` | ✅ Direct match | ⚠️ Need migration |
| Badge | `variant="outline"` | `variant="outline"` | ✅ Direct match | ⚠️ Need migration |
| Card | Simple wrapper | `Card` + `CardContent` | ⚠️ Structure change | ⚠️ Need migration |
| Input | Defined but unused | `@/components/ui/input` | N/A | ✅ Already migrated |
| CircularProgress | Custom implementation | None (custom or Progress) | N/A | 🔍 Need to evaluate |

---

## Migration Strategy

### Phase 1: Quick Wins (Low Risk)
1. ✅ **Remove unused Input component** from UIComponents.tsx
2. ✅ **Audit CircularProgress usage** - remove if unused, or create migration plan

### Phase 2: Component Migrations (Page by Page)
3. ✅ **Migrate DealsList.tsx** (only Card needs migration)
4. ✅ **Migrate AnalysisView.tsx** (Button, Badge, Card)
5. ✅ **Migrate PipelineBoard.tsx** (Button, Badge)
6. ✅ **Migrate DealIntake.tsx** (Button, Badge, Card)
7. ✅ **Migrate Dashboard.tsx** (Button, Card)

### Phase 3: Cleanup
8. ✅ **Delete UIComponents.tsx** after all migrations complete
9. ✅ **Update imports** across codebase to ensure consistency
10. ✅ **Run design system audit** to verify ShadCN styling matches Dream design tokens

---

## Key Migration Patterns

### Button Migration Pattern

**Before (Custom):**
```tsx
<Button variant="primary" icon={Icon} size="sm">
  Click me
</Button>
```

**After (ShadCN):**
```tsx
<Button variant="default" size="sm">
  <Icon className="w-4 h-4" />
  Click me
</Button>
```

**Notes:**
- `variant="primary"` → `variant="default"`
- `variant="danger"` → `variant="destructive"`
- `size="md"` → `size="default"` (or omit, default is "default")
- `icon={Icon}` prop → `<Icon />` as child element

---

### Card Migration Pattern

**Before (Custom):**
```tsx
<Card className="p-4">
  <h3>Title</h3>
  <p>Content</p>
</Card>
```

**After (ShadCN):**
```tsx
<Card>
  <CardContent className="p-4">
    <h3>Title</h3>
    <p>Content</p>
  </CardContent>
</Card>
```

**Or for structured cards:**
```tsx
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Content</p>
  </CardContent>
</Card>
```

---

### Badge Migration Pattern

**Before (Custom):**
```tsx
<Badge variant="success">Complete</Badge>
```

**After (ShadCN):**
```tsx
<Badge variant="success">Complete</Badge>
```

**Notes:**
- Most variants map directly ✅
- API is identical, just import path changes

---

## Design Token Considerations

**Important:** ShadCN components should be styled with Dream design tokens. Verify:

1. ✅ ShadCN Button uses `bg-[#005253]` for primary (Deep Teal)
2. ✅ ShadCN Badge variants match Dream semantic colors
3. ✅ ShadCN Card uses Dream border and background colors
4. ✅ All components respect dark mode (if applicable)

**Reference:** `design-language-dream.md` for token definitions

---

## Testing Checklist

After each migration:

- [ ] Visual regression check (compare before/after screenshots)
- [ ] Interactive states work (hover, focus, active)
- [ ] Dark mode works (if applicable)
- [ ] Variants render correctly
- [ ] Sizes render correctly
- [ ] Icons display correctly (for Button)
- [ ] No console errors
- [ ] TypeScript types are correct

---

## Issue Summary

| Category | Count | Status |
|----------|-------|--------|
| Pages needing migration | 5 | 🔴 High Priority |
| Custom components to remove | 4 | 🟡 Medium Priority |
| Dead code to remove | 1 (Input) | 🟢 Low Priority |
| Components to evaluate | 1 (CircularProgress) | 🟡 Medium Priority |
| **Total Issues** | **11** | |

---

## Recommendations

1. **Prioritize Page Migrations**: Start with `DealsList.tsx` (easiest - only Card), then work through others
2. **Use ShadCN Design Tokens**: Ensure all ShadCN components are styled with Dream design tokens
3. **Create Migration Script**: Consider creating a codemod script for Button icon prop migration
4. **Document Patterns**: Create a migration guide document for future reference
5. **Run Design Audit**: After migrations, run Vision-based UI Reviewer to verify styling compliance

---

## Next Steps

1. ✅ **This audit is complete** - review and approve migration strategy
2. ⏭️ **Start Phase 1**: Remove unused Input, audit CircularProgress
3. ⏭️ **Start Phase 2**: Begin page-by-page migrations
4. ⏭️ **Complete Phase 3**: Cleanup and verification

---

*Audit completed: December 26, 2025*  
*Next review: After Phase 2 migrations complete*

