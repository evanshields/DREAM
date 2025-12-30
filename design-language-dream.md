# Dream Design Language - Minimal Pro

**Version:** 1.0  
**Last Updated:** December 2025  
**Purpose:** Design system for Dream AI - a professional real estate underwriting platform

---

## Design Philosophy

**Minimal Pro** is a design language optimized for:
- **Numeric legibility**: Financial data must be instantly scannable
- **Professional credibility**: Trustworthy appearance for institutional users
- **Low cognitive load**: Clean, uncluttered interfaces for data-heavy workflows
- **High clarity**: Subtle but clear visual hierarchy

### Core Principles

1. **Low-chroma, high clarity**: Muted colors that don't distract from data
2. **Subtle borders, minimal shadows**: Clean separation without visual noise
3. **Numeric focus**: Typography and spacing optimized for financial metrics
4. **Professional aesthetic**: Suitable for B2B financial applications

---

## Color Palette

### Primary Colors

**Dark Slate** - Primary brand color, used for headers and primary actions
- `#28323E` - Primary (main brand)
- `#3C4856` - Light variant (hover states, secondary elements)
- `#1A1F26` - Dark variant (dark mode primary)

**Deep Teal** - Accent and primary actions
- `#005253` - Primary accent (buttons, links, focus states)
- `#003F3F` - Dark variant (hover states)
- `#007A7C` - Light variant (subtle highlights)

**YinMn Blue** - Secondary accent for buttons and interactive elements
- `#2E5090` - Primary (buttons, interactive elements, highlights)
- `#1E3A6B` - Dark variant (hover states, pressed)
- `#4A6BA8` - Light variant (subtle highlights, backgrounds)

### Secondary Colors

**Charcoal** - Secondary text and UI elements
- `#3C4856` - Default
- `#5C6876` - Light variant
- `#9DA3AA` - Muted variant (placeholder text, secondary labels)

### Semantic Colors

**Success** - Positive metrics, approvals, good scores
- Main: `#58ABA8` (Teal)
- Background: `#E6F6F6` (Very light teal)
- Border: `#58ABA8` with 20% opacity

**Warning** - Caution states, moderate scores
- Main: `#F3B8A7` (Coral)
- Background: `#FEF4F2` (Very light coral)
- Border: `#F3B8A7` with 20% opacity

**Danger** - Negative metrics, rejections, low scores
- Main: `#C94A3E` (Muted red)
- Background: `#FDF2F1` (Very light red)
- Border: `#C94A3E` with 20% opacity

**Info** - Neutral information, data points
- Main: `#95C9E6` (Light blue)
- Background: `#F0F8FC` (Very light blue)
- Border: `#95C9E6` with 20% opacity

### Background Colors

- **Primary**: `#FFFFFF` (Pure white for cards, modals)
- **Secondary**: `#F8F7F5` (Warm off-white for page backgrounds)
- **Tertiary**: `#EBE5DE` (Tan tint for subtle sections, hover states)

### Border Colors

- **Default**: `#D6C9BA` (Warm tan - subtle, low-chroma)
- **Subtle**: `#E8E0D6` (Lighter tan for internal dividers)
- **Focus**: `#005253` (Deep teal) or `#2E5090` (YinMn Blue) for focus states

### Text Colors

- **Primary Text**: `#28323E` (Dark slate - main content)
- **Secondary Text**: `#3C4856` (Charcoal - labels, descriptions)
- **Muted Text**: `#9DA3AA` (Muted gray - placeholders, hints)
- **Inverse Text**: `#FFFFFF` (White for dark backgrounds)

---

## Typography

### Font Families

**Sans Serif (Body)** - `Libre Franklin`
- Used for: Body text, labels, descriptions, UI elements
- Weights: 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold)

**Serif (Headings)** - `Playfair Display`
- Used for: Headings, numeric displays, brand elements
- Weights: 500 (Medium), 600 (Semibold), 700 (Bold)
- **Rationale**: Serif fonts improve numeric legibility and add professional gravitas

### Type Scale

**Headings**
- `h1`: `text-4xl` (36px) / `font-heading` / `font-bold` / `text-primary`
- `h2`: `text-3xl` (30px) / `font-heading` / `font-semibold` / `text-primary`
- `h3`: `text-2xl` (24px) / `font-heading` / `font-semibold` / `text-primary`
- `h4`: `text-xl` (20px) / `font-heading` / `font-medium` / `text-primary`
- `h5`: `text-lg` (18px) / `font-heading` / `font-medium` / `text-secondary`
- `h6`: `text-base` (16px) / `font-heading` / `font-medium` / `text-secondary`

**Body Text**
- `body-lg`: `text-lg` (18px) / `font-sans` / `font-normal` / `text-primary`
- `body`: `text-base` (16px) / `font-sans` / `font-normal` / `text-primary`
- `body-sm`: `text-sm` (14px) / `font-sans` / `font-normal` / `text-secondary`
- `body-xs`: `text-xs` (12px) / `font-sans` / `font-normal` / `text-secondary-muted`

**Numeric Displays** (Critical for financial data)
- `numeric-xl`: `text-4xl` (36px) / `font-heading` / `font-bold` / `text-primary` / `tabular-nums`
- `numeric-lg`: `text-3xl` (30px) / `font-heading` / `font-semibold` / `text-primary` / `tabular-nums`
- `numeric-md`: `text-2xl` (24px) / `font-heading` / `font-semibold` / `text-primary` / `tabular-nums`
- `numeric-sm`: `text-xl` (20px) / `font-heading` / `font-medium` / `text-primary` / `tabular-nums`

**Note**: Always use `tabular-nums` for financial metrics to ensure proper alignment in tables and comparisons.

### Line Heights

- Headings: `leading-tight` (1.2)
- Body: `leading-normal` (1.5)
- Numeric displays: `leading-none` (1.0) for tight vertical spacing

---

## Spacing Scale

Based on Tailwind's 4px base unit, optimized for data-dense interfaces:

### Scale Reference
- `0`: `0px` (no spacing)
- `1`: `4px` (0.25rem)
- `2`: `8px` (0.5rem)
- `3`: `12px` (0.75rem)
- `4`: `16px` (1rem) - **Base unit**
- `5`: `20px` (1.25rem)
- `6`: `24px` (1.5rem)
- `8`: `32px` (2rem)
- `10`: `40px` (2.5rem)
- `12`: `48px` (3rem)
- `16`: `64px` (4rem)
- `20`: `80px` (5rem)

### Usage Guidelines

**Component Internal Spacing**
- Card padding: `p-4` (16px) or `p-6` (24px) for larger cards
- Button padding: `px-4 py-2` (horizontal 16px, vertical 8px)
- Input padding: `px-3 py-2` (horizontal 12px, vertical 8px)

**Component External Spacing**
- Between cards: `gap-4` (16px) or `gap-6` (24px)
- Section spacing: `mb-8` (32px) or `mb-12` (48px)
- Page margins: `px-4 sm:px-6 lg:px-8` (responsive)

**Data Table Spacing**
- Cell padding: `px-4 py-3` (horizontal 16px, vertical 12px)
- Row gap: `gap-2` (8px) for compact tables
- Header spacing: `pb-2` (8px) below headers

---

## Layout & Grid

### Container Widths

- **Max Content Width**: `max-w-[1600px]` (for wide data tables)
- **Standard Container**: `max-w-7xl` (1280px)
- **Narrow Container**: `max-w-4xl` (896px) for forms and focused content

### Grid System

- **Standard Grid**: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3` (responsive)
- **Data Grid**: `grid-cols-1 lg:grid-cols-2 xl:grid-cols-3` (optimized for metrics)
- **Table Layout**: Use CSS Grid or Flexbox for responsive tables

### Breakpoints (Tailwind Default)

- `sm`: 640px (mobile landscape, small tablets)
- `md`: 768px (tablets)
- `lg`: 1024px (desktops)
- `xl`: 1280px (large desktops)
- `2xl`: 1536px (extra large screens)

---

## Component Tokens

### Buttons

**Sizes**
- Small: `px-3 py-1.5 text-xs` (min height: 32px)
- Medium: `px-4 py-2 text-sm` (min height: 40px) - **Default**
- Large: `px-6 py-3 text-base` (min height: 48px)

**Variants**
- Primary (Deep Teal): `bg-[#005253] hover:bg-[#003F3F] text-white`
- Primary (YinMn Blue): `bg-[#2E5090] hover:bg-[#1E3A6B] text-white` - **Recommended for buttons**
- Secondary: `bg-background-primary border border-border text-secondary hover:bg-background-tertiary`
- Outline: `bg-transparent border border-border text-secondary hover:bg-background-tertiary`
- Outline (YinMn Blue): `bg-transparent border border-[#2E5090] text-[#2E5090] hover:bg-[#2E5090] hover:text-white`
- Ghost: `bg-transparent text-secondary hover:bg-background-tertiary`
- Danger: `bg-brand-danger text-white hover:opacity-90`

**Touch Targets**: Minimum 44px height for mobile (use `py-3` on small screens)

### Cards

- Background: `bg-background-primary`
- Border: `border border-border`
- Border Radius: `rounded-lg` (8px)
- Shadow: `shadow-sm` (subtle, minimal)
- Hover: `hover:shadow-md` (slightly more prominent)
- Padding: `p-4` (16px) or `p-6` (24px)

### Inputs

- Height: `h-10` (40px) - standard
- Padding: `px-3 py-2` (12px horizontal, 8px vertical)
- Border: `border border-border`
- Focus: `focus:ring-2 focus:ring-[#005253] focus:border-transparent` or `focus:ring-[#2E5090]` (YinMn Blue)
- Border Radius: `rounded-md` (6px)
- Background: `bg-background-primary`

### Badges

- Padding: `px-2.5 py-0.5`
- Border Radius: `rounded-full`
- Font: `text-xs font-medium`
- Variants use semantic colors with subtle backgrounds

### Tables

- Header: `bg-background-secondary text-secondary font-semibold text-sm`
- Cell Padding: `px-4 py-3`
- Borders: `border-b border-border` (horizontal dividers only)
- Hover: `hover:bg-background-tertiary` (subtle row highlight)
- Numeric Columns: Right-aligned with `tabular-nums`

### Metric Cards

- Background: `bg-background-primary`
- Border: `border border-border`
- Padding: `p-4` or `p-6`
- Value Display: Use `numeric-lg` or `numeric-xl` with `font-heading`
- Label: `text-sm text-secondary-muted font-medium`
- Status Colors: Apply semantic colors to values

---

## Shadows

**Minimal Pro Philosophy**: Use shadows sparingly and subtly

- `shadow-sm`: `0 1px 2px 0 rgba(0, 0, 0, 0.05)` - Cards, subtle elevation
- `shadow-md`: `0 4px 6px -1px rgba(0, 0, 0, 0.1)` - Hover states, modals
- `shadow-lg`: `0 10px 15px -3px rgba(0, 0, 0, 0.1)` - Dropdowns, popovers (rarely used)

**Avoid**: Heavy shadows, multiple shadow layers, colored shadows

---

## Borders

**Default Border**: `border border-border` (1px solid `#D6C9BA`)

**Border Radius**
- Small: `rounded` (4px) - buttons, inputs
- Medium: `rounded-md` (6px) - inputs, small cards
- Large: `rounded-lg` (8px) - cards, containers - **Most common**
- Full: `rounded-full` - badges, pills

**Border Styles**
- Solid: Standard borders
- Dashed: For drag-drop zones, optional sections
- None: For seamless card groups

---

## Focus States

**Focus Ring**: `focus:ring-2 focus:ring-[#005253] focus:ring-offset-2`

**Focus Border**: `focus:border-transparent` (when using ring)

**Accessibility**: All interactive elements must have visible focus states

---

## States

### Interactive States

- **Default**: Base styling
- **Hover**: Subtle background change or shadow increase
- **Active**: Slightly darker background
- **Focus**: Ring with Deep Teal (`#005253`)
- **Disabled**: `opacity-50 cursor-not-allowed`

### Data States

- **Loading**: Skeleton loaders with `bg-background-tertiary animate-pulse`
- **Empty**: Subtle gray text with icon
- **Error**: Red text (`text-brand-danger`) with error icon
- **Success**: Green text (`text-brand-success`) with checkmark

---

## Numeric Legibility Guidelines

**Critical for financial data display**

1. **Use Tabular Numerals**: Always apply `tabular-nums` class
2. **Font Choice**: Prefer serif (`font-heading`) for large numbers
3. **Alignment**: Right-align numeric columns in tables
4. **Spacing**: Use consistent spacing around decimal points
5. **Color Coding**: Use semantic colors sparingly (don't overuse)
6. **Size Hierarchy**: Make key metrics larger than supporting data
7. **Decimal Precision**: Show consistent decimal places (e.g., always 2 for currency)

**Example Numeric Display**
```html
<div class="text-3xl font-heading font-semibold tabular-nums text-primary">
  18.5%
</div>
```

---

## Accessibility

### Color Contrast

- **Text on White**: Minimum 4.5:1 contrast ratio
- **Text on Colored Backgrounds**: Minimum 4.5:1 contrast ratio
- **Large Text** (18px+): Minimum 3:1 contrast ratio

### Touch Targets

- **Minimum Size**: 44px × 44px for mobile
- **Spacing**: 8px minimum between interactive elements

### ARIA Labels

- All icons must have `aria-label` or be wrapped in labeled elements
- Form inputs must have associated labels
- Buttons with only icons need descriptive labels

---

## Dark Mode

Dark mode maintains the Minimal Pro aesthetic while optimizing for low-light viewing and reduced eye strain. Colors are carefully adjusted for contrast and readability.

### Dark Mode Color Palette

#### Background Colors

- **Primary**: `#1E293B` (Slate 800) - Cards, modals, elevated surfaces
- **Secondary**: `#0F172A` (Slate 900) - Page background, main surface
- **Tertiary**: `#334155` (Slate 700) - Subtle sections, hover states, dividers

**Rationale**: Slate tones provide depth without harsh contrast. Avoid pure black (#000000) to reduce eye strain.

#### Text Colors

- **Primary Text**: `#F8F7F5` (Warm off-white) - Main content, headings
- **Secondary Text**: `#D1D5DB` (Light gray) - Labels, descriptions
- **Muted Text**: `#9CA3AF` (Medium gray) - Placeholders, hints, disabled text
- **Inverse Text**: `#0F172A` (Dark slate) - Text on light backgrounds in dark mode

#### Primary Colors (Dark Mode)

**Dark Slate** - Adjusted for dark backgrounds
- `#F8F7F5` - Primary text (inverted from light mode)
- `#E2E8F0` - Light variant (subtle highlights)
- `#CBD5E1` - Muted variant

**Deep Teal** - Slightly brighter for visibility
- `#007A7C` - Primary accent (lighter than light mode for contrast)
- `#009FA2` - Hover state (more vibrant)
- `#005253` - Dark variant (original, for subtle use)

**YinMn Blue** - Enhanced for dark mode prominence
- `#4A6BA8` - Primary (lighter variant for better visibility)
- `#5B7FC4` - Hover state (bright, clear)
- `#2E5090` - Base (original, for contrast)
- **Note**: YinMn Blue works exceptionally well in dark mode - consider using as primary button color

#### Secondary Colors (Dark Mode)

**Charcoal** - Inverted to light grays
- `#D1D5DB` - Default (light gray)
- `#9CA3AF` - Light variant
- `#6B7280` - Muted variant

#### Semantic Colors (Dark Mode)

**Success** - Maintains teal identity
- Main: `#58ABA8` (Same as light mode - works well on dark)
- Background: `rgba(88, 171, 168, 0.15)` (15% opacity overlay)
- Border: `rgba(88, 171, 168, 0.3)` (30% opacity)

**Warning** - Slightly desaturated for dark backgrounds
- Main: `#F3B8A7` (Same as light mode)
- Background: `rgba(243, 184, 167, 0.15)` (15% opacity overlay)
- Border: `rgba(243, 184, 167, 0.3)` (30% opacity)

**Danger** - Maintains visibility
- Main: `#F87171` (Slightly brighter red for dark mode)
- Background: `rgba(248, 113, 113, 0.15)` (15% opacity overlay)
- Border: `rgba(248, 113, 113, 0.3)` (30% opacity)

**Info** - Enhanced for dark mode
- Main: `#60A5FA` (Brighter blue for visibility)
- Background: `rgba(96, 165, 250, 0.15)` (15% opacity overlay)
- Border: `rgba(96, 165, 250, 0.3)` (30% opacity)

#### Border Colors (Dark Mode)

- **Default**: `#334155` (Slate 700 - subtle, low-contrast)
- **Subtle**: `#475569` (Slate 600 - for internal dividers)
- **Focus**: `#4A6BA8` (YinMn Blue light - clear focus indicator)

#### Accent Colors (Dark Mode)

**YinMn Blue** - Recommended primary accent for dark mode
- `#4A6BA8` - Primary (lighter for visibility)
- `#5B7FC4` - Hover (bright, engaging)
- `#2E5090` - Base (original, for contrast)

**Deep Teal** - Alternative accent
- `#007A7C` - Primary (lighter than light mode)
- `#009FA2` - Hover
- `#005253` - Base

### Dark Mode Component Tokens

#### Buttons (Dark Mode)

**Primary (YinMn Blue)** - Recommended for dark mode
- `bg-[#4A6BA8] hover:bg-[#5B7FC4] text-white`
- Excellent contrast and visibility

**Primary (Deep Teal)**
- `bg-[#007A7C] hover:bg-[#009FA2] text-white`

**Secondary**
- `bg-[#1E293B] border border-[#334155] text-[#D1D5DB] hover:bg-[#334155]`

**Outline (YinMn Blue)**
- `bg-transparent border border-[#4A6BA8] text-[#4A6BA8] hover:bg-[#4A6BA8] hover:text-white`

#### Cards (Dark Mode)

- Background: `bg-[#1E293B]` (Slate 800)
- Border: `border border-[#334155]` (Slate 700)
- Hover: `hover:bg-[#334155]` (Slightly lighter)

#### Inputs (Dark Mode)

- Background: `bg-[#1E293B]` (Slate 800)
- Border: `border border-[#334155]`
- Focus: `focus:ring-2 focus:ring-[#4A6BA8]` (YinMn Blue)
- Text: `text-[#F8F7F5]` (Warm off-white)

#### Tables (Dark Mode)

- Header: `bg-[#334155] text-[#D1D5DB]`
- Cell: `bg-[#1E293B] text-[#F8F7F5]`
- Hover: `hover:bg-[#334155]`
- Borders: `border-[#334155]`

### Dark Mode Best Practices

1. **Use YinMn Blue for primary actions** - It has excellent contrast and visibility in dark mode
2. **Avoid pure white** - Use warm off-white (`#F8F7F5`) to reduce eye strain
3. **Maintain subtle borders** - Use Slate 700 (`#334155`) for low-contrast separation
4. **Test numeric legibility** - Ensure financial data is highly readable with serif fonts
5. **Use opacity overlays** - Semantic backgrounds use 15% opacity for subtle indication
6. **Consistent spacing** - Same spacing scale as light mode
7. **Smooth transitions** - Use `transition-colors duration-200` for mode switching

### Accessibility in Dark Mode

- **Contrast Ratios**: All text meets WCAG AA standards (4.5:1 minimum)
- **Focus Indicators**: Use YinMn Blue (`#4A6BA8`) for clear focus rings
- **Color Independence**: Don't rely solely on color - use icons and text labels
- **Test with screen readers**: Ensure all interactive elements are properly labeled

---

## Tailwind Configuration

### Recommended Tailwind Config Extensions

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        DEFAULT: '#28323E',
        light: '#3C4856',
        dark: '#1A1F26',
      },
      secondary: {
        DEFAULT: '#3C4856',
        light: '#5C6876',
        muted: '#9DA3AA',
      },
      accent: {
        DEFAULT: '#005253',
        dark: '#003F3F',
        light: '#007A7C',
      },
      'yinmn-blue': {
        DEFAULT: '#2E5090',
        dark: '#1E3A6B',
        light: '#4A6BA8',
        'dark-primary': '#4A6BA8', // Lighter variant for dark mode
        'dark-hover': '#5B7FC4',   // Hover state in dark mode
      },
      background: {
        primary: '#FFFFFF',
        secondary: '#F8F7F5',
        tertiary: '#EBE5DE',
      },
      border: '#D6C9BA',
      brand: {
        success: '#58ABA8',
        warning: '#F3B8A7',
        danger: '#C94A3E',
        info: '#95C9E6',
        'bg-success': '#E6F6F6',
        'bg-warning': '#FEF4F2',
        'bg-danger': '#FDF2F1',
        'bg-info': '#F0F8FC',
      }
    },
    fontFamily: {
      sans: ['Libre Franklin', 'sans-serif'],
      heading: ['Playfair Display', 'serif'],
    },
  }
}
```

---

## Usage Examples

### Metric Card
```html
<div class="bg-background-primary rounded-lg border border-border p-6">
  <p class="text-sm text-secondary-muted font-medium mb-2">IRR</p>
  <p class="text-3xl font-heading font-semibold tabular-nums text-primary">18.5%</p>
  <p class="text-sm text-secondary mt-1">Above hurdle</p>
</div>
```

### Primary Button (Deep Teal)
```html
<button class="bg-[#005253] hover:bg-[#003F3F] text-white px-4 py-2 rounded-md text-sm font-medium focus:ring-2 focus:ring-[#005253] focus:ring-offset-2">
  Analyze Deal
</button>
```

### Primary Button (YinMn Blue) - Recommended
```html
<!-- Light Mode -->
<button class="bg-[#2E5090] hover:bg-[#1E3A6B] text-white px-4 py-2 rounded-md text-sm font-medium focus:ring-2 focus:ring-[#2E5090] focus:ring-offset-2">
  Analyze Deal
</button>

<!-- Dark Mode (Recommended) -->
<button class="bg-[#4A6BA8] dark:bg-[#4A6BA8] hover:bg-[#5B7FC4] dark:hover:bg-[#5B7FC4] text-white px-4 py-2 rounded-md text-sm font-medium focus:ring-2 focus:ring-[#4A6BA8] focus:ring-offset-2">
  Analyze Deal
</button>
```

### Outline Button (YinMn Blue)
```html
<button class="bg-transparent border border-[#2E5090] text-[#2E5090] hover:bg-[#2E5090] hover:text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
  View Details
</button>
```

### Data Table Cell
```html
<!-- Light Mode -->
<td class="px-4 py-3 text-right">
  <span class="font-heading tabular-nums text-primary">$1,250,000</span>
</td>

<!-- Dark Mode -->
<td class="px-4 py-3 text-right bg-[#1E293B] dark:bg-[#1E293B]">
  <span class="font-heading tabular-nums text-[#F8F7F5] dark:text-[#F8F7F5]">$1,250,000</span>
</td>
```

### Dark Mode Card Example
```html
<div class="bg-[#1E293B] dark:bg-[#1E293B] border border-[#334155] dark:border-[#334155] rounded-lg p-6">
  <h3 class="text-xl font-heading font-semibold text-[#F8F7F5] dark:text-[#F8F7F5] mb-2">Deal Analysis</h3>
  <p class="text-sm text-[#D1D5DB] dark:text-[#D1D5DB]">Financial metrics and insights</p>
</div>
```

---

---

## Analytical Pro Patterns

**Note**: These patterns are for the Analytical Pro UI variant, which is more expressive than Minimal Pro.

### Visual Hierarchy for Key Metrics

**Tier 1 - Primary Metrics** (Most Important)
- Size: `text-5xl` (48px) or `text-4xl` (36px)
- Weight: `font-bold`
- Font: `font-heading` (serif for numeric legibility)
- Color: Primary text color or semantic color based on performance
- Spacing: `mb-2` or `mb-4` below label

**Tier 2 - Secondary Metrics**
- Size: `text-3xl` (30px) or `text-2xl` (24px)
- Weight: `font-semibold`
- Font: `font-heading`
- Color: Secondary text or muted semantic color

**Tier 3 - Supporting Data**
- Size: `text-lg` (18px) or `text-base` (16px)
- Weight: `font-medium` or `font-normal`
- Font: `font-sans`

### Color Coding for Metrics

**Performance-Based Color Coding**
- **Excellent/Positive**: YinMn Blue (`#2E5090`) or Deep Teal (`#005253`)
- **Good/Above Target**: Success color (`#58ABA8`)
- **Caution/Moderate**: Warning color (`#F3B8A7`)
- **Poor/Below Target**: Danger color (`#C94A3E`)

**Delta/Differential Styling**
- **Positive Delta**: `text-[#2E5090] bg-[#2E5090]/10 px-2 py-1 rounded` with `+` prefix
- **Negative Delta**: `text-[#C94A3E] bg-[#C94A3E]/10 px-2 py-1 rounded` with `-` prefix
- **Neutral Delta**: `text-secondary-muted bg-background-tertiary px-2 py-1 rounded`

### Analytical Table Patterns

**Sticky Header**
```html
<thead class="sticky top-0 z-10 bg-background-secondary border-b-2 border-border">
  <tr>
    <th class="px-4 py-3 text-left text-sm font-semibold text-secondary">Column</th>
  </tr>
</thead>
```

**Row Striping**
```html
<tbody>
  <tr class="even:bg-background-secondary hover:bg-[#4A6BA8]/10 transition-colors">
    <td class="px-4 py-3">Content</td>
  </tr>
</tbody>
```

**Highlighted Row** (Important data)
```html
<tr class="bg-[#2E5090]/5 border-l-4 border-[#2E5090] hover:bg-[#2E5090]/10">
```

**Numeric Cell with Emphasis**
```html
<td class="px-4 py-3 text-right">
  <span class="font-heading font-semibold tabular-nums text-[#2E5090]">18.5%</span>
</td>
```

### Comparison Patterns

**Side-by-Side Comparison Cards**
```html
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
  <div class="bg-background-primary border-2 border-[#2E5090] rounded-lg p-6">
    <!-- Scenario A -->
  </div>
  <div class="bg-background-primary border-2 border-border rounded-lg p-6">
    <!-- Scenario B -->
  </div>
</div>
```

**Delta Indicator**
```html
<div class="flex items-center gap-2">
  <span class="text-2xl font-heading font-semibold tabular-nums">18.5%</span>
  <span class="text-sm text-[#2E5090] bg-[#2E5090]/10 px-2 py-1 rounded font-medium">
    +2.3%
  </span>
</div>
```

### Warning Indicators

**Strong Warning Badge**
```html
<div class="bg-[#F3B8A7]/20 border-2 border-[#F3B8A7] rounded-lg p-4">
  <div class="flex items-center gap-2">
    <span class="text-[#C94A3E] font-semibold">⚠️ Warning</span>
    <span class="text-sm text-secondary">Below target threshold</span>
  </div>
</div>
```

**Critical Alert**
```html
<div class="bg-[#C94A3E]/10 border-l-4 border-[#C94A3E] rounded-r-lg p-4">
  <p class="font-semibold text-[#C94A3E]">Critical Issue Detected</p>
</div>
```

### Trend Indicators

**Upward Trend**
```html
<div class="flex items-center gap-2 text-[#2E5090]">
  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
    <path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z"/>
  </svg>
  <span class="font-semibold">+12.5%</span>
</div>
```

**Downward Trend**
```html
<div class="flex items-center gap-2 text-[#C94A3E]">
  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
    <path fill-rule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z"/>
  </svg>
  <span class="font-semibold">-5.2%</span>
</div>
```

### Metric Card (Analytical Pro Style)

**Enhanced Metric Card**
```html
<div class="bg-background-primary border-2 border-[#2E5090] rounded-lg p-6 shadow-md">
  <div class="flex items-center justify-between mb-2">
    <p class="text-sm text-secondary-muted font-medium">IRR</p>
    <span class="text-xs text-[#2E5090] bg-[#2E5090]/10 px-2 py-1 rounded font-medium">
      +2.3%
    </span>
  </div>
  <p class="text-5xl font-heading font-bold tabular-nums text-[#2E5090] mb-1">18.5%</p>
  <p class="text-sm text-secondary">Above 16% target</p>
</div>
```

### Progress Indicators

**Progress Bar with Accent Color**
```html
<div class="w-full bg-background-tertiary rounded-full h-3">
  <div class="bg-[#2E5090] h-3 rounded-full" style="width: 75%"></div>
</div>
```

**Metric Progress Indicator**
```html
<div class="flex items-center gap-4">
  <div class="flex-1 bg-background-tertiary rounded-full h-2">
    <div class="bg-[#2E5090] h-2 rounded-full" style="width: 85%"></div>
  </div>
  <span class="text-sm font-semibold text-[#2E5090]">85%</span>
</div>
```

---

## Version History

- **v1.3** (December 2025): Added Analytical Pro patterns and design specifications for expressive dashboard styling
- **v1.2** (December 2025): Added comprehensive dark mode color specifications with YinMn Blue as recommended primary button color
- **v1.1** (December 2025): Added YinMn Blue (#2E5090) as secondary accent color for buttons and interactive elements
- **v1.0** (December 2025): Initial design language specification for Dream AI Minimal Pro theme

