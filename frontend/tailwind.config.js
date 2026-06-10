/** @type {import('tailwindcss').Config} */
// Shieldstone brand tokens (PRD §3 + reference_shieldstone-bd-brand). Deep Teal is the
// structural color; Electric Blue is callout-only; Off-White surfaces; Playfair/Josefin/Noto.
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        teal: {
          DEFAULT: '#005253', // Deep Teal — primary / structural
          tint: '#5EC4C0',    // hover / accent
          panel: '#EAF3F3',   // light teal surface
          panel2: '#E8ECEC',
        },
        slate: {
          DEFAULT: '#3C4856', // Dark Slate — primary text
          near: '#171C26',    // near-black
        },
        taupe: '#D4C4B0',     // secondary accent
        offwhite: '#FAFAF8',  // background
        electric: '#2B52EF',  // CTA / callout — SPARINGLY
        ok: '#16A34A',
        warn: '#D97706',
        warnLight: '#FBBF24',
        danger: '#DC2626',
        dangerLight: '#F87171',
      },
      fontFamily: {
        head: ['"Playfair Display"', 'serif'],
        label: ['"Josefin Sans"', 'sans-serif'],
        body: ['"Noto Sans"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        card: '0 1px 3px rgba(23, 28, 38, 0.06), 0 1px 2px rgba(23, 28, 38, 0.04)',
        cardHover: '0 4px 16px rgba(0, 82, 83, 0.10)',
      },
    },
  },
  plugins: [],
};
