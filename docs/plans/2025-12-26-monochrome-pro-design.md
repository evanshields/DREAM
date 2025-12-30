# Monochrome Pro Design Specification

**Version:** 1.0
**Date:** 2025-12-26
**Purpose:** Design specification for DREAM AI Monochrome Pro variant - a teal monochrome fork with maximum data clarity

---

## Design Philosophy

**Monochrome Pro** is a minimal, data-focused design language optimized for:
- **Maximum data clarity**: Remove visual noise, focus on numbers and metrics
- **Professional credibility**: Clean, sophisticated aesthetic for institutional users
- **High data density**: Efficient use of screen space for data-heavy workflows
- **Minimal distraction**: Single color family with one strategic accent color

### Core Principles

1. **Teal monochrome foundation**: All UI derives from teal base (#005253)
2. **YinMn Blue accent**: Single contrasting accent for key actions and emphasis
3. **Sans-serif only**: Remove serif typography, use Libre Franklin exclusively
4. **Increased data density**: Tighter spacing, more information per screen
5. **Light shadows only**: Subtle elevation, no heavy drop shadows
6. **No decorative elements**: Functional UI only, remove ornamental components

---

## Color Palette

### Teal Monochrome Scale

All colors derived from Deep Teal (#005253) with varying lightness:

**Background Tones** (Lightest)
- `bg-primary`: `#FFFFFF` - Pure white for maximum contrast with text
- `bg-secondary`: `#F0F7F7` - Very light teal tint (5% teal)
- `bg-tertiary`: `#E0F0F0` - Light teal tint (10% teal) for subtle sections
- `bg-hover`: `#D6EBEB` - Slightly darker teal (15% teal) for hover states

**Border & Divider Tones**
- `border-subtle`: `#C2E0E0` - Light teal border (20% teal)
- `border-default`: `#99CCCC` - Medium-light teal border (35% teal)
- `border-strong`: `#66B3B3` - Medium teal border (50% teal)

**Text & UI Tones**
- `text-muted`: `#7FA6A6` - Muted teal (40% teal + 40% gray) for secondary text
- `text-secondary`: `#3D7A7A` - Medium-dark teal (60% teal) for labels
- `text-primary`: `#005253` - Deep teal (100%) for primary text
- `text-emphasis`: `#003F3F` - Darkest teal (120% darkness) for emphasis

**Interactive Tones**
- `interactive-base`: `#005253` - Deep teal for buttons and links
- `interactive-hover`: `#007A7C` - Lighter teal for hover states
- `interactive-pressed`: `#003F3F` - Darker teal for pressed states
- `interactive-disabled`: `#99CCCC` - Light teal (35%) with reduced opacity

### YinMn Blue Accent (Single Accent Color)

**Primary Accent** - Used sparingly for key actions and critical data
- `accent-primary`: `#2E5090` - YinMn Blue base
- `accent-hover`: `#4A6BA8` - Lighter YinMn Blue for hover
- `accent-pressed`: `#1E3A6B` - Darker YinMn Blue for pressed
- `accent-subtle`: `#E8EDF6` - Very light YinMn Blue (5%) for backgrounds
- `accent-muted`: `#B8C5DD` - Muted YinMn Blue (35%) for secondary accents

**Accent Usage Guidelines**
- Primary action buttons (Analyze Deal, Submit, etc.)
- Critical metrics that exceed targets
- Active navigation states
- Focus indicators
- Key data highlights (NOT for all positive metrics - use sparingly)

### Semantic Colors (Derived from Teal + Accent)

**Success** - Use teal tones
- Main: `#007A7C` - Lighter teal variant
- Background: `#E0F0F0` - Light teal tint
- Border: `#99CCCC` - Medium-light teal

**Warning** - Use muted teal
- Main: `#7FA6A6` - Muted teal-gray
- Background: `#F0F7F7` - Very light teal
- Border: `#C2E0E0` - Light teal

**Error/Danger** - Use darkest teal (NOT red, maintaining monochrome)
- Main: `#003F3F` - Darkest teal
- Background: `#E0F0F0` - Light teal (same as success for consistency)
- Border: `#66B3B3` - Medium teal

**Info/Highlight** - Use YinMn Blue accent
- Main: `#2E5090` - YinMn Blue
- Background: `#E8EDF6` - Very light YinMn Blue
- Border: `#B8C5DD` - Muted YinMn Blue

---

## Typography

### Font Family

**Sans-Serif Only** - `Libre Franklin`
- Remove Playfair Display serif entirely
- Use Libre Franklin for ALL text (headings, body, numerics)
- Weights: 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold)

### Type Scale (Reduced from original)

**Headings** - Smaller, more compact
- `h1`: `text-3xl` (30px) / `font-bold` / `text-primary` (was 36px)
- `h2`: `text-2xl` (24px) / `font-semibold` / `text-primary` (was 30px)
- `h3`: `text-xl` (20px) / `font-semibold` / `text-primary` (was 24px)
- `h4`: `text-lg` (18px) / `font-medium` / `text-secondary` (was 20px)
- `h5`: `text-base` (16px) / `font-medium` / `text-secondary` (was 18px)
- `h6`: `text-sm` (14px) / `font-medium` / `text-secondary` (was 16px)

**Body Text** - Standard sizes
- `body-lg`: `text-base` (16px) / `font-normal` / `text-primary` (was 18px)
- `body`: `text-sm` (14px) / `font-normal` / `text-primary` (was 16px)
- `body-sm`: `text-xs` (12px) / `font-normal` / `text-secondary` (was 14px)
- `body-xs`: `text-[11px]` (11px) / `font-normal` / `text-muted` (was 12px)

**Numeric Displays** - Sans-serif with tabular numerals
- `numeric-xl`: `text-3xl` (30px) / `font-bold` / `text-primary` / `tabular-nums` (was 36px)
- `numeric-lg`: `text-2xl` (24px) / `font-semibold` / `text-primary` / `tabular-nums` (was 30px)
- `numeric-md`: `text-xl` (20px) / `font-semibold` / `text-primary` / `tabular-nums` (was 24px)
- `numeric-sm`: `text-lg` (18px) / `font-medium` / `text-primary` / `tabular-nums` (was 20px)

**Note**: Always use `tabular-nums` for financial metrics to ensure proper alignment.

### Line Heights

- Headings: `leading-tight` (1.2)
- Body: `leading-normal` (1.5)
- Numeric displays: `leading-tight` (1.2) for compact vertical spacing
- Tables: `leading-snug` (1.375) for data density

---

## Spacing Scale (Increased Data Density)

Reduce spacing by ~25% from original Minimal Pro design:

### Scale Reference (Compact)
- `0`: `0px`
- `0.5`: `2px` (NEW - very tight spacing)
- `1`: `4px`
- `2`: `6px` (was 8px)
- `3`: `10px` (was 12px)
- `4`: `12px` (was 16px) - **Base unit (reduced)**
- `5`: `16px` (was 20px)
- `6`: `20px` (was 24px)
- `8`: `24px` (was 32px)
- `10`: `32px` (was 40px)
- `12`: `40px` (was 48px)

### Usage Guidelines

**Component Internal Spacing** (Tighter)
- Card padding: `p-3` (12px) or `p-4` (16px) for larger cards (was p-4/p-6)
- Button padding: `px-3 py-1.5` (horizontal 12px, vertical 6px) (was px-4 py-2)
- Input padding: `px-2.5 py-1.5` (horizontal 10px, vertical 6px) (was px-3 py-2)

**Component External Spacing** (Compact)
- Between cards: `gap-3` (12px) or `gap-4` (16px) (was gap-4/gap-6)
- Section spacing: `mb-6` (24px) or `mb-8` (32px) (was mb-8/mb-12)
- Page margins: `px-3 sm:px-4 lg:px-6` (was px-4 sm:px-6 lg:px-8)

**Data Table Spacing** (Very Compact)
- Cell padding: `px-3 py-2` (horizontal 12px, vertical 8px) (was px-4 py-3)
- Row gap: `gap-1` (4px) for compact tables (was gap-2)
- Header spacing: `pb-1.5` (6px) below headers (was pb-2)

---

## Component Tokens

### Buttons

**Sizes** (Compact)
- Small: `px-2.5 py-1 text-xs` (min height: 28px) (was 32px)
- Medium: `px-3 py-1.5 text-sm` (min height: 36px) - **Default** (was 40px)
- Large: `px-5 py-2.5 text-base` (min height: 44px) (was 48px)

**Variants**
- Primary (Teal): `bg-[#005253] hover:bg-[#007A7C] text-white`
- Primary (YinMn Blue Accent): `bg-[#2E5090] hover:bg-[#4A6BA8] text-white` - **For key actions**
- Secondary: `bg-white border border-[#99CCCC] text-[#005253] hover:bg-[#F0F7F7]`
- Outline (Teal): `bg-transparent border border-[#005253] text-[#005253] hover:bg-[#F0F7F7]`
- Outline (Accent): `bg-transparent border border-[#2E5090] text-[#2E5090] hover:bg-[#E8EDF6]`
- Ghost: `bg-transparent text-[#005253] hover:bg-[#E0F0F0]`

**Shadows**: `shadow-sm` only (no heavy shadows)

### Cards

- Background: `bg-white`
- Border: `border border-[#99CCCC]`
- Border Radius: `rounded-md` (6px) (was rounded-lg 8px)
- Shadow: `shadow-sm` (subtle) - `0 1px 2px 0 rgba(0, 82, 83, 0.05)`
- Hover: `hover:shadow` (slightly more prominent) - `0 1px 3px 0 rgba(0, 82, 83, 0.1)`
- Padding: `p-3` (12px) or `p-4` (16px) (was p-4/p-6)

### Inputs

- Height: `h-9` (36px) - compact (was h-10 40px)
- Padding: `px-2.5 py-1.5` (10px horizontal, 6px vertical) (was px-3 py-2)
- Border: `border border-[#99CCCC]`
- Focus: `focus:ring-1 focus:ring-[#2E5090] focus:border-[#2E5090]` (1px ring, was 2px)
- Border Radius: `rounded` (4px) (was rounded-md 6px)
- Background: `bg-white`
- Text: `text-sm` (14px) (was text-base 16px)

### Badges

- Padding: `px-2 py-0.5` (was px-2.5 py-0.5)
- Border Radius: `rounded` (4px) (was rounded-full)
- Font: `text-[11px] font-medium` (was text-xs 12px)
- Variants use monochrome teal colors with subtle backgrounds

### Tables

- Header: `bg-[#E0F0F0] text-[#005253] font-semibold text-xs` (was text-sm)
- Cell Padding: `px-3 py-2` (was px-4 py-3)
- Borders: `border-b border-[#C2E0E0]` (horizontal dividers only)
- Hover: `hover:bg-[#F0F7F7]` (subtle row highlight)
- Numeric Columns: Right-aligned with `tabular-nums`
- Row Height: Compact, `leading-snug`

### Metric Cards

- Background: `bg-white`
- Border: `border border-[#99CCCC]`
- Padding: `p-3` or `p-4` (was p-4/p-6)
- Value Display: Use `numeric-lg` or `numeric-xl` with `font-bold`
- Label: `text-xs text-[#7FA6A6] font-medium uppercase tracking-wide` (was text-sm)
- Status Colors: Use teal shades or YinMn Blue accent (sparingly)

---

## Shadows (Light Only)

**Monochrome Pro Philosophy**: Use light shadows only, derived from teal

- `shadow-sm`: `0 1px 2px 0 rgba(0, 82, 83, 0.05)` - Cards, subtle elevation
- `shadow`: `0 1px 3px 0 rgba(0, 82, 83, 0.1)` - Hover states
- `shadow-md`: `0 4px 6px -1px rgba(0, 82, 83, 0.1)` - Modals, dropdowns (rarely used)

**Avoid**: Heavy shadows, multiple shadow layers, colored shadows beyond teal

---

## Borders

**Default Border**: `border border-[#99CCCC]` (1px solid medium-light teal)

**Border Radius** (More angular, less rounded)
- Small: `rounded` (4px) - buttons, inputs, badges (was rounded 4px, no change)
- Medium: `rounded-md` (6px) - cards, containers (was rounded-lg 8px)
- Large: `rounded-lg` (8px) - modals, major sections (was rounded-lg 8px, use sparingly)
- Full: AVOID - no rounded-full except for avatars

**Border Styles**
- Solid: Standard borders
- Dashed: For drag-drop zones, optional sections
- None: For seamless card groups

---

## Decorative Elements to Remove

**Remove Completely:**
1. **Serif typography** - Playfair Display font family
2. **Heavy shadows** - No shadow-lg or shadow-xl
3. **Rounded-full elements** - Use rounded or rounded-md only (except avatars)
4. **Gradient backgrounds** - Solid colors only
5. **Decorative icons** - Keep functional icons only (navigation, actions, status)
6. **Ornamental dividers** - Use simple border-b only
7. **Brand logo decorations** - Simplify logo to minimal lettermark
8. **Background patterns** - Solid backgrounds only
9. **Colored backgrounds for emphasis** - Use borders instead
10. **Multiple accent colors** - One accent color only (YinMn Blue)

**Simplify:**
1. **Navigation** - Minimal nav bar, text-based links, remove extra visual flourishes
2. **Search bar** - Simple input with icon, no fancy styling
3. **User avatar** - Simple circle with initials
4. **Metric cards** - Border, padding, value, label only. No backgrounds, no icons
5. **Buttons** - Flat with light shadow, remove gradient hover effects
6. **Tables** - Horizontal borders only, no alternating row colors (use hover instead)

---

## Layout & Grid

### Container Widths (Maximize screen usage)

- **Max Content Width**: `max-w-[1800px]` (wider for data tables) (was 1600px)
- **Standard Container**: `max-w-7xl` (1280px)
- **Narrow Container**: `max-w-3xl` (768px) for forms (was max-w-4xl 896px)

### Grid System (Higher density)

- **Standard Grid**: `grid-cols-1 md:grid-cols-3 lg:grid-cols-4` (was 1/2/3)
- **Data Grid**: `grid-cols-1 lg:grid-cols-3 xl:grid-cols-4` (was 1/2/3)
- **Metric Grid**: `grid-cols-2 md:grid-cols-4 lg:grid-cols-6` (more columns)

---

## Focus States

**Focus Ring**: `focus:ring-1 focus:ring-[#2E5090] focus:ring-offset-1` (thinner ring)

**Focus Border**: `focus:border-[#2E5090]`

**Accessibility**: All interactive elements must have visible focus states using YinMn Blue

---

## Dark Mode (Optional - Future)

For now, Monochrome Pro will be light mode only. If dark mode is needed:
- Invert teal scale (darkest becomes lightest)
- Maintain YinMn Blue accent
- Use dark teal (#003F3F) as background base

---

## Tailwind Configuration

### Recommended Tailwind Config Extensions

```javascript
theme: {
  extend: {
    colors: {
      // Teal Monochrome Scale
      'mono-bg-primary': '#FFFFFF',
      'mono-bg-secondary': '#F0F7F7',
      'mono-bg-tertiary': '#E0F0F0',
      'mono-bg-hover': '#D6EBEB',
      'mono-border-subtle': '#C2E0E0',
      'mono-border': '#99CCCC',
      'mono-border-strong': '#66B3B3',
      'mono-text-muted': '#7FA6A6',
      'mono-text-secondary': '#3D7A7A',
      'mono-text-primary': '#005253',
      'mono-text-emphasis': '#003F3F',
      'mono-interactive': '#005253',
      'mono-interactive-hover': '#007A7C',
      'mono-interactive-pressed': '#003F3F',

      // YinMn Blue Accent
      'accent': '#2E5090',
      'accent-hover': '#4A6BA8',
      'accent-pressed': '#1E3A6B',
      'accent-subtle': '#E8EDF6',
      'accent-muted': '#B8C5DD',
    },
    fontFamily: {
      sans: ['Libre Franklin', 'sans-serif'],
      // Remove heading font family
    },
    boxShadow: {
      'sm': '0 1px 2px 0 rgba(0, 82, 83, 0.05)',
      'DEFAULT': '0 1px 3px 0 rgba(0, 82, 83, 0.1)',
      'md': '0 4px 6px -1px rgba(0, 82, 83, 0.1)',
    }
  }
}
```

---

## Implementation Checklist

- [ ] Create new git branch: `monochrome-pro`
- [ ] Update Tailwind config with monochrome color palette
- [ ] Remove Playfair Display font imports
- [ ] Update all heading components to use Libre Franklin
- [ ] Reduce spacing scale across all components
- [ ] Update button sizes and padding
- [ ] Update card padding and border radius
- [ ] Update input heights and padding
- [ ] Simplify metric cards (remove backgrounds, icons)
- [ ] Update table styling (compact, monochrome)
- [ ] Remove decorative elements from Layout component
- [ ] Simplify navigation bar
- [ ] Update all color references to teal monochrome scale
- [ ] Add YinMn Blue accent to primary action buttons only
- [ ] Test data density across all views
- [ ] Verify accessibility (contrast ratios, focus states)

---

## Version History

- **v1.0** (2025-12-26): Initial Monochrome Pro design specification for DREAM AI variant
