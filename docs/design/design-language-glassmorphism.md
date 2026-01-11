# Dream Design Language - Glassmorphism

**Version:** 1.0
**Last Updated:** December 2025
**Purpose:** Glassmorphism design system variant for Dream AI - modern, frosted glass aesthetic

---

## Design Philosophy

**Glassmorphism Pro** is a design language optimized for:
- **Modern aesthetic**: Frosted glass effects with translucent layers
- **Visual depth**: Layered transparency creates sophisticated hierarchy
- **Data clarity**: Clean overlays don't obscure background context
- **Professional yet contemporary**: Trustworthy with a modern edge
- **Ethereal feel**: Light, airy interfaces that feel premium

### Core Principles

1. **Frosted glass effect**: Backdrop blur creates visual separation
2. **High transparency**: 75-85% opacity for semi-transparent surfaces
3. **Vibrant accents**: Rich colors that pop against blurred backgrounds
4. **Subtle separation**: Minimal borders, focus on transparency
5. **Soft lighting**: Gentle shadows for elevation
6. **Contemporary styling**: Modern, premium appearance

---

## Color Palette

### Primary Colors

**Glassmorphic Blue** - Primary brand color (vibrant against frosted glass)
- `#4A6BA8` - Primary (YinMn Blue - excellent on glass)
- `#5B7FC4` - Lighter variant (highlights, hover states)
- `#2E5090` - Dark variant (active states, text)

**Crystalline Teal** - Accent and interactive elements
- `#00B4B8` - Primary accent (brighter than Minimal Pro)
- `#008B8F` - Dark variant (hover, active)
- `#00D4D9` - Light variant (highlights, subtle backgrounds)

**Frosted White** - Semi-transparent base for glass effect
- `#FFFFFF` with 80% opacity - Primary glass surface
- `#FFFFFF` with 60% opacity - Secondary glass surface
- `#FFFFFF` with 40% opacity - Subtle glass dividers

### Background Colors

**Light Mode Backgrounds** (behind glass)
- **Primary**: `#F0F4FF` (Subtle blue tint for tech feel)
- **Secondary**: `#E8ECFF` (Slightly darker for contrast)
- **Tertiary**: `#E0E5FF` (For sections, hover states)

**Dark Mode Backgrounds** (behind glass)
- **Primary**: `#0F1428` (Deep blue-black)
- **Secondary**: `#1A1F3A` (Slightly lighter)
- **Tertiary**: `#252B4A` (For sections, hover states)

### Semantic Colors

**Success** - Positive metrics, approvals
- Main: `#00D084` (Vibrant green)
- Glass overlay: `#FFFFFF` at 75% opacity
- Border: `#00D084` with 40% opacity

**Warning** - Caution states, moderate scores
- Main: `#FFB84D` (Vibrant orange)
- Glass overlay: `#FFFFFF` at 75% opacity
- Border: `#FFB84D` with 40% opacity

**Danger** - Negative metrics, rejections
- Main: `#FF5555` (Vibrant red)
- Glass overlay: `#FFFFFF` at 75% opacity
- Border: `#FF5555` with 40% opacity

**Info** - Neutral information
- Main: `#4A9DFF` (Bright blue)
- Glass overlay: `#FFFFFF` at 75% opacity
- Border: `#4A9DFF` with 40% opacity

### Text Colors

**Light Mode**
- **Primary Text**: `#0F1428` (Deep blue-black)
- **Secondary Text**: `#4A5B7A` (Muted blue-gray)
- **Muted Text**: `#8899BB` (Light blue-gray)

**Dark Mode**
- **Primary Text**: `#F8F9FC` (Off-white)
- **Secondary Text**: `#C5D0E8` (Light blue-gray)
- **Muted Text**: `#8899BB` (Medium blue-gray)

---

## Typography

### Font Families

**Sans Serif (Body)** - `Inter` or `Poppins`
- Used for: Body text, labels, UI elements
- Rationale: Modern, clean sans-serif for glassmorphic aesthetic
- Weights: 400, 500, 600, 700

**Display (Headings)** - `Playfair Display` or `Syne`
- Used for: Headings, key metrics
- Weights: 600, 700
- Rationale: Elegant serif adds sophistication to glass design

### Type Scale

**Headings**
- `h1`: `text-5xl` (48px) / `font-display` / `font-bold` / Glassmorphic Blue
- `h2`: `text-4xl` (36px) / `font-display` / `font-bold`
- `h3`: `text-3xl` (30px) / `font-display` / `font-semibold`
- `h4`: `text-2xl` (24px) / `font-display` / `font-semibold`
- `h5`: `text-lg` (18px) / `font-display` / `font-medium`
- `h6`: `text-base` (16px) / `font-display` / `font-medium`

**Body Text**
- `body-lg`: `text-lg` (18px) / `font-sans` / `font-normal`
- `body`: `text-base` (16px) / `font-sans` / `font-normal`
- `body-sm`: `text-sm` (14px) / `font-sans` / `font-normal`
- `body-xs`: `text-xs` (12px) / `font-sans` / `font-normal`

**Numeric Displays**
- `numeric-xl`: `text-5xl` (48px) / `font-display` / `font-bold` / `tabular-nums`
- `numeric-lg`: `text-4xl` (36px) / `font-display` / `font-semibold` / `tabular-nums`
- `numeric-md`: `text-3xl` (30px) / `font-display` / `font-semibold` / `tabular-nums`

---

## Spacing Scale

Same as Minimal Pro (4px base unit):
- `0`: 0px
- `1`: 4px
- `2`: 8px
- `3`: 12px
- `4`: 16px (base)
- `6`: 24px
- `8`: 32px
- `12`: 48px

---

## Glass Effect Specifications

### Backdrop Blur Values

- **Strong blur (primary surfaces)**: `backdrop-blur-xl` (16px) - Cards, containers
- **Medium blur (secondary surfaces)**: `backdrop-blur-lg` (12px) - Overlays, modals
- **Light blur (subtle effects)**: `backdrop-blur-md` (8px) - Dividers, borders

### Opacity Specifications

- **Primary glass surfaces**: 75-80% opacity (0.75-0.80)
- **Secondary surfaces**: 65-70% opacity (0.65-0.70)
- **Subtle dividers**: 40-50% opacity (0.40-0.50)

### Border Treatment

- **Default border**: 1px solid with 30% opacity of text color
- **Glass border**: `border border-white/30` (light mode) or `border-white/20` (dark mode)
- **Accent border**: 2px solid with full color (for emphasis)

### Shadow Treatment

- **Subtle elevation**: `drop-shadow-sm` with blur
- **Card elevation**: `drop-shadow-md`
- **Modal elevation**: `drop-shadow-lg`
- **Focus state**: Soft glow effect using box-shadow

---

## Component Tokens

### Glass Card

```css
.glass-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
}

.glass-card:hover {
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 8px 40px 0 rgba(31, 38, 135, 0.15);
}
```

**Tailwind**: `bg-white/75 backdrop-blur-xl border border-white/30 rounded-3xl shadow-lg`

### Glass Button - Primary

```css
.glass-btn-primary {
  background: linear-gradient(135deg, #4A6BA8 0%, #5B7FC4 100%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px 0 rgba(74, 107, 168, 0.2);
  transition: all 0.3s ease;
}

.glass-btn-primary:hover {
  background: linear-gradient(135deg, #5B7FC4 0%, #6B8BD8 100%);
  box-shadow: 0 4px 20px 0 rgba(74, 107, 168, 0.3);
  transform: translateY(-2px);
}
```

**Tailwind**: `bg-gradient-to-br from-[#4A6BA8] to-[#5B7FC4] hover:from-[#5B7FC4] hover:to-[#6B8BD8] text-white px-6 py-2 rounded-full shadow-lg hover:shadow-xl border border-white/30 transition-all`

### Glass Button - Secondary

```css
.glass-btn-secondary {
  background: rgba(255, 255, 255, 0.7);
  border: 2px solid rgba(74, 107, 168, 0.4);
  color: #4A6BA8;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.glass-btn-secondary:hover {
  background: rgba(255, 255, 255, 0.85);
  border-color: rgba(74, 107, 168, 0.6);
}
```

**Tailwind**: `bg-white/70 hover:bg-white/85 border-2 border-[#4A6BA8]/40 hover:border-[#4A6BA8]/60 text-[#4A6BA8] px-6 py-2 rounded-full backdrop-blur-md transition-all`

### Glass Input

```css
.glass-input {
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(10px);
  color: #0F1428;
  padding: 12px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.glass-input:focus {
  background: rgba(255, 255, 255, 0.8);
  border-color: #4A6BA8;
  box-shadow: 0 0 0 3px rgba(74, 107, 168, 0.1);
}
```

**Tailwind**: `bg-white/60 border border-white/40 backdrop-blur-md focus:bg-white/80 focus:border-[#4A6BA8] focus:ring-4 focus:ring-[#4A6BA8]/10 rounded-lg px-4 py-3 transition-all`

### Metric Display (Glassmorphic)

```css
.glass-metric {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s ease;
}

.glass-metric:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: translateY(-4px);
  box-shadow: 0 12px 40px 0 rgba(74, 107, 168, 0.15);
}

.glass-metric-value {
  font-size: 48px;
  font-weight: bold;
  background: linear-gradient(135deg, #4A6BA8 0%, #00B4B8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

**Tailwind**:
- Card: `bg-white/70 backdrop-blur-lg border border-white/40 rounded-3xl p-6 hover:bg-white/80 hover:shadow-xl transition-all`
- Value: `text-5xl font-bold bg-gradient-to-r from-[#4A6BA8] to-[#00B4B8] bg-clip-text text-transparent`

---

## Navigation (Glassmorphic)

### Top Navigation

```css
.glass-nav {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 30px 0 rgba(31, 38, 135, 0.05);
  position: sticky;
  top: 0;
  z-index: 40;
}
```

**Tailwind**: `bg-white/70 backdrop-blur-3xl border-b border-white/30 shadow-md sticky top-0 z-40`

### Navigation Item

```css
.glass-nav-item {
  color: #4A5B7A;
  transition: all 0.3s ease;
  position: relative;
}

.glass-nav-item:hover {
  color: #4A6BA8;
}

.glass-nav-item.active {
  color: #4A6BA8;
  font-weight: 600;
}

.glass-nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, #4A6BA8, #00B4B8);
  border-radius: 1px;
}
```

---

## Dark Mode

### Dark Mode Color Adjustments

**Background**
- Primary: `#0F1428` (Deep blue-black)
- Secondary: `#1A1F3A` (Dark slate blue)
- Tertiary: `#252B4A` (Medium dark blue)

**Glass Surfaces (Dark Mode)**
- Primary glass: `rgba(26, 31, 58, 0.75)` with `backdrop-blur-xl`
- Secondary glass: `rgba(26, 31, 58, 0.65)` with `backdrop-blur-lg`
- Border: `border-white/15` (subtle on dark)

**Text Colors**
- Primary: `#F8F9FC` (Off-white)
- Secondary: `#C5D0E8` (Light blue-gray)
- Muted: `#8899BB` (Medium blue-gray)

**Glassmorphic Blue (Dark Mode)**
- Primary: `#5B7FC4` (Lighter for visibility)
- Hover: `#6B8BD8` (Brighter)
- Dark: `#4A6BA8` (Original for contrast)

### Dark Mode Glass Card

```css
.dark .glass-card {
  background: rgba(26, 31, 58, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}
```

**Tailwind**: `dark:bg-slate-900/75 dark:border-white/15 dark:shadow-2xl`

---

## Tailwind Configuration

### Recommended Extensions

```javascript
theme: {
  extend: {
    colors: {
      glass: {
        primary: 'rgba(255, 255, 255, 0.8)',
        secondary: 'rgba(255, 255, 255, 0.65)',
        subtle: 'rgba(255, 255, 255, 0.4)',
      },
      'glass-dark': {
        primary: 'rgba(26, 31, 58, 0.8)',
        secondary: 'rgba(26, 31, 58, 0.65)',
        subtle: 'rgba(26, 31, 58, 0.4)',
      },
      primary: '#4A6BA8',
      'primary-light': '#5B7FC4',
      'primary-dark': '#2E5090',
      accent: '#00B4B8',
      'accent-light': '#00D4D9',
      'accent-dark': '#008B8F',
    },
    backdropBlur: {
      xs: '4px',
      sm: '8px',
      md: '12px',
      lg: '16px',
      xl: '20px',
      '2xl': '24px',
      '3xl': '32px',
    },
    fontFamily: {
      sans: ['Inter', 'Poppins', 'sans-serif'],
      display: ['Playfair Display', 'serif'],
    },
  }
}
```

---

## Usage Examples

### Glass Card with Metric

```html
<div class="bg-white/75 backdrop-blur-xl border border-white/30 rounded-3xl p-6 shadow-lg">
  <h3 class="text-sm text-gray-600 font-medium">IRR</h3>
  <p class="text-5xl font-display font-bold bg-gradient-to-r from-[#4A6BA8] to-[#00B4B8] bg-clip-text text-transparent mt-2">18.5%</p>
  <p class="text-sm text-gray-500 mt-1">Above 16% target</p>
</div>
```

### Glass Button Primary

```html
<button class="bg-gradient-to-br from-[#4A6BA8] to-[#5B7FC4] hover:from-[#5B7FC4] hover:to-[#6B8BD8] text-white px-6 py-2 rounded-full shadow-lg hover:shadow-xl border border-white/30 transition-all hover:translate-y-[-2px]">
  Analyze Deal
</button>
```

### Glass Modal Overlay

```html
<div class="fixed inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center">
  <div class="bg-white/80 backdrop-blur-xl border border-white/40 rounded-3xl p-8 max-w-md shadow-2xl">
    <h2 class="text-2xl font-display font-bold mb-4">Confirm Action</h2>
    <p class="text-gray-700 mb-6">Are you sure you want to proceed?</p>
    <div class="flex gap-3">
      <button class="flex-1 bg-white/70 border border-gray-300 rounded-lg py-2 font-medium">Cancel</button>
      <button class="flex-1 bg-gradient-to-r from-[#4A6BA8] to-[#5B7FC4] text-white rounded-lg py-2 font-medium">Confirm</button>
    </div>
  </div>
</div>
```

---

## Glassmorphism Best Practices

1. **Always use backdrop-blur** - Essential to the aesthetic
2. **Layer transparency** - 75-80% opacity on primary surfaces, lower on secondary
3. **Subtle borders** - Use white with 30% opacity (light mode)
4. **Vibrant accents** - Colors pop more on frosted glass
5. **Soft shadows** - Drop shadows for elevation, not hard shadows
6. **Smooth transitions** - 0.3s ease for hover/active states
7. **Rich backgrounds** - Ensure backgrounds behind glass are visually interesting
8. **Rounded corners** - Use 12px or larger for modern feel
9. **Gradient text** - Works beautifully on glass (use text-gradient technique)
10. **Dark mode contrast** - Ensure 4.5:1 contrast ratio for readability

---

## Version History

- **v1.0** (December 2025): Initial Glassmorphism design language specification

