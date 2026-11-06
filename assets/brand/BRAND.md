# PrimeCrest brand guide

PrimeCrest Construction Management, developed by Spyder Solutions.

The canonical source of the mark is the in-app component `frontend/src/shared/ui/Logo.tsx`; the palette and
type come from `frontend/src/index.css` and `frontend/src/shared/lib/appearance.ts`. Every file in this folder
is drawn from those, so the favicon, app icons and documents match what the app shows.

## The mark

A "PC" monogram on an ink shield, framed by a copper rim with a copper rule under the letters. The shield
stands for trust and control; copper is the construction accent used throughout the app.

Geometry (512 grid, as in `Logo.tsx`): shield `M256 40 L440 110 V250 C440 360 360 440 256 472 C152 440 72 360 72 250 V110 Z`
filled with the ink gradient; rim inset by 16 with a 14-unit copper stroke at 90 % opacity; "PC" in Georgia
Bold 168, tracking -6, centred on x 256 with the baseline at 292; copper rule 176 x 12 at (168, 328).

| File | Use |
| --- | --- |
| `primecrest-mark.svg` | Primary mark, full colour. Works on light and dark backgrounds. |
| `primecrest-mark-white.svg` | One-colour outline mark (rim, monogram, rule) for photos and dark fills. |
| `primecrest-mark-navy.svg` | One-colour outline mark in ink for print and light fills. |
| `primecrest-favicon.svg` | Mark cropped to the shield with a heavier, opaque rim. Use at 16-48 px. |
| `primecrest-wordmark.svg` / `-dark.svg` | Name and descriptor without the mark. |
| `primecrest-lockup.svg` / `-dark.svg` | Mark + wordmark, horizontal. The default logo for headers, documents and slides. |
| `primecrest-app-tile.svg` | Square app icon: the mark on a cream field (PWA, iOS, Android). |
| `primecrest-app-tile-maskable.svg` | Same, with the mark inside the 80 % maskable safe zone. |
| `primecrest-og.svg`, `primecrest-og-image.png` | 1200x630 social card on ink. |
| `primecrest-banner.svg` | 1800x1210 README banner (`docs/screenshots/banner.png`). |
| `*.png` | Rendered from the SVGs above (`-1024`, lockups at 2000x400). |

All text in the SVGs is converted to outlines, so they render identically without the fonts installed.

### Usage rules

- Clear space around the mark: at least the height of the copper rule's gap to the rim (about 1/10 of the
  mark's width); for the lockup, at least the cap height of "P".
- Minimum size: full mark 24 px / 8 mm; below that use `primecrest-favicon.svg`. Lockup minimum width 140 px.
- On light backgrounds use `primecrest-lockup.svg` (ink "Prime", copper "Crest").
  On ink or dark backgrounds use `primecrest-lockup-dark.svg` (cream "Prime", light copper "Crest").
- Do not recolour the mark, stretch it, add effects, rotate it, or set the name in another typeface.
- Copper `#C4622D` is an accent and large-text colour; for small copper text on light surfaces use
  Copper Text `#8F431C` (AA), as the app does.

## Colours

| Token | Hex | Role | App token |
| --- | --- | --- | --- |
| Ink | `#12202B` | Primary. Shield (gradient start), wordmark on light, `theme-color`, PDF header accent. | Logo.tsx |
| Ink Slate | `#1A3344` | Shield gradient end, raised dark surfaces. | Logo.tsx |
| Copper | `#C4622D` | Accent. Rim, rule, "Crest", primary actions on light. | `--oe-blue` (light) |
| Copper Light | `#E08A55` | Accent on ink / dark mode. | `--oe-blue` (dark) |
| Copper Text | `#8F431C` | Copper for small text on light surfaces. | `--oe-blue-text` |
| Cream | `#F6F3EE` | Monogram, app background, PWA `background_color`, icon tiles. | `--oe-bg-secondary` |
| Paper | `#F0EBE3` | Page wash, tile gradient end. | `--oe-bg-page` |
| Stone | `#5E584F` | Descriptor text on light. | `--oe-text-secondary` |
| Mist | `#A9B6BF` | Descriptor text on ink. | - |

Cream on ink: about 15:1. Copper Light on ink: about 6:1. Ink on cream: about 15:1.

## Typography

- **Display: Fraunces** SemiBold (SIL OFL 1.1), tracking -2 %. Used for the "PrimeCrest" wordmark, as in the
  app header (`--oe-font-display`).
- **UI and descriptor: Source Sans 3** (SIL OFL 1.1), the app's default font (`appearance.ts`). Descriptor
  "CONSTRUCTION MANAGEMENT": Source Sans 3 SemiBold, all caps, tracking about +14 %, justified to the width of
  the wordmark.
- **Monogram: Georgia Bold**, as drawn by `Logo.tsx`.
- Fonts are bundled under `frontend/public/assets/vendor/fonts`.

## Where the assets live

- `assets/brand/` - source of truth (this folder).
- `frontend/public/favicon.svg`, `favicon.ico` (16/32/48), `apple-touch-icon.png` (180), `logo.svg`, `og-image.png`.
- `frontend/public/pwa/` - `icon-{192,256,384,512}.svg`, `icon-maskable-512.svg`, PNG `icon-192`, `icon-512`,
  `icon-maskable-512`. Manifest: `theme_color #12202B`, `background_color #F6F3EE`.
- `frontend/public/brand/` - `primecrest-*.svg`. `ddc-logo.webp` / `ddc-logo.png` keep their upstream filenames
  because `frontend/src` still imports them, but contain the PrimeCrest lockup / mark.
- `frontend/public/splash.html` - desktop start-up screen; carries the mark inline.
- `desktop/src-tauri/icons/` - Tauri desktop, Windows Store, iOS and Android icon set (`icon.ico`, `icon.icns`
  as a macOS rounded cream tile; Android adaptive background `#F6F3EE`).
