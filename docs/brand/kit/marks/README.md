# DREAM mark kit

These are code-native SVG reconstructions of the approved four-way rounded interlock. They preserve the reference's four open paths, rounded terminals, central negative-space crossings, and equal visual weight; they are not letter-D marks.

| Asset | Use |
| --- | --- |
| `dream-mark-primary.svg` | Default brand mark on light or neutral surfaces; Nocturne Iris `#6657E8`. |
| `dream-mark-dark.svg` | One-color mark on light surfaces; blue-black `#1B1D29`. |
| `dream-mark-light.svg` | Reversed one-color mark on dark surfaces; white `#FFFFFF`. |
| `dream-mark-icon.svg` | Compact UI icon for light or neutral surfaces; primary iris `#6657E8`. |
| `dream-mark-icon-dark-surface.svg` | Compact UI icon for dark surfaces; bright iris `#9288FF`. |
| `dream-favicon.svg` | Compact-browser treatment for light or neutral surfaces; primary iris `#6657E8` with a 28-unit stroke tuned for 16–32 px rasterization. |
| `dream-favicon-dark-surface.svg` | Compact-browser treatment for dark surfaces; bright iris `#9288FF` with the same 28-unit favicon stroke. |

All assets use the same optically centered geometry in a `320 × 320` viewBox with transparent backgrounds. Keep the square proportions, preserve the clear negative-space cross, and do not add a surrounding container, recolor individual paths, turn the mark into a letterform, or apply gradients. Use `#6657E8` only on light or neutral surfaces and `#9288FF` for compact marks on dark surfaces. For raster export, use the heavier-stroke favicon at 16 px; use the regular icon at 24 px or larger when practical.

Use the SVGs directly where possible. When the mark conveys the product identity rather than serving as decoration, provide the accessible name “DREAM”; otherwise expose it as decorative (`aria-hidden="true"`).
