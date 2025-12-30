/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary palette
        primary: {
          DEFAULT: 'var(--color-primary)',
          dark: 'var(--color-primary-dark)',
          alt: 'var(--color-primary-alt)',
          seafoam: 'var(--color-accent-teal)',
        },
        // Secondary text colors
        secondary: {
          DEFAULT: 'var(--color-primary)',
          muted: 'var(--color-muted)',
          gray: 'var(--color-muted)',
        },
        // Accent colors
        accent: {
          DEFAULT: 'var(--color-accent-teal)',
          teal: 'var(--color-accent-teal)',
          blue: 'var(--color-accent-blue)',
          coral: 'var(--color-accent-coral)',
          tan: 'var(--color-accent-tan)',
        },
        // Backgrounds
        background: {
          primary: 'var(--color-background-primary)',
          secondary: 'var(--color-background-secondary)',
          tertiary: 'var(--color-background-tertiary)',
        },
        // Semantic colors
        success: 'var(--color-success)',
        warning: 'var(--color-warning)',
        danger: 'var(--color-danger)',
        info: 'var(--color-info)',
        // Border
        border: 'var(--color-border-default)',
        muted: 'var(--color-muted)',
      },
      fontFamily: {
        sans: ['Libre Franklin', 'sans-serif'],
        serif: ['Playfair Display', 'serif'],
        heading: ['Playfair Display', 'serif'],
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [],
}
