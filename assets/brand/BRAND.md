# PrimeCrest brand guide

PrimeCrest Construction Management, developed by Spyder Solutions.

## The mark

A crest (shield) holding a mountain peak with a tower crane on the skyline. The shield stands for
trust and control, the peak for the "crest" of a finished project, the crane for active construction.

| File | Use |
| --- | --- |
| `primecrest-mark.svg` | Primary mark, full colour. Works on light and dark backgrounds (the `#1D4E89` rim separates it from navy). |
| `primecrest-mark-white.svg` | One-colour outline mark for photos and dark fills. |
| `primecrest-mark-navy.svg` | One-colour outline mark for print and light fills. |
| `primecrest-favicon.svg` | Simplified mark (no crane) for 16-48 px. Use only at small sizes. |
| `primecrest-wordmark.svg` / `-dark.svg` | Name and descriptor without the mark. |
| `primecrest-lockup.svg` / `-dark.svg` | Mark + wordmark, horizontal. The default logo for headers, documents and slides. |
| `primecrest-app-tile.svg` | Square navy app icon (PWA, iOS, Android). |
| `primecrest-app-tile-maskable.svg` | Same, with the mark inside the 80 % maskable safe zone. |
| `primecrest-og.svg`, `primecrest-og-image.png` | 1200x630 social card. |
| `primecrest-banner.svg` | 1800x1210 README banner (`docs/screenshots/banner.png`). |
| `*.png` | Rendered from the SVGs above (`-1024`, lockups at 2000x400). |

All text in the SVGs is converted to outlines, so they render identically without the font installed.

### Usage rules

- Clear space around the mark: at least the width of the crane jib's counterweight block (about 1/15 of the
  mark's width); for the lockup, at least the cap height of "P".
- Minimum size: full mark 32 px / 10 mm; below that use `primecrest-favicon.svg`. Lockup minimum width 140 px.
- On light backgrounds use `primecrest-lockup.svg` (navy name, amber underline under "Crest").
  On dark or navy backgrounds use `primecrest-lockup-dark.svg` (white "Prime", amber "Crest").
- Do not recolour the mark, stretch it, add effects, rotate it, or set the name in another typeface.
- Do not put amber text on white for body copy (contrast about 2:1); amber is an accent, not a text colour on light.

## Colours

| Token | Hex | Role |
| --- | --- | --- |
| Crest Navy | `#0B2545` | Primary. Shield, wordmark, app tiles, `theme-color`. |
| Deep Navy | `#13315C` | Secondary fills, descriptor text on light. |
| Steel Blue | `#1D4E89` | Mark rim, borders, hover states. |
| Construction Amber | `#F2A900` | Accent. Peak, highlights, primary call-to-action on dark. |
| Slate | `#8DA9C4` | Descriptor text on dark, muted UI text on navy. |
| White | `#FFFFFF` | Crane, snow line, text on navy. |

Text on navy: white (15.6:1) or slate (about 6.4:1). Amber on navy: about 7.8:1.

## Typography

- **Inter** (SIL OFL 1.1). Wordmark: Inter ExtraBold, tracking -1 %. Descriptor "CONSTRUCTION MANAGEMENT":
  Inter SemiBold, all caps, tracking +15-16 %, set to the width of the wordmark.
- UI text uses the app's configured font stack (Inter / IBM Plex Sans / Source Sans 3, bundled under
  `frontend/public/assets/vendor/fonts`).

## Where the assets live

- `assets/brand/` - source of truth (this folder).
- `frontend/public/favicon.svg`, `favicon.ico` (16/32/48), `apple-touch-icon.png` (180), `logo.svg`, `og-image.png`.
- `frontend/public/pwa/` - `icon-{192,256,384,512}.svg`, `icon-maskable-512.svg`, PNG `icon-192`, `icon-512`,
  `icon-maskable-512`.
- `frontend/public/brand/` - `primecrest-*.svg`. `ddc-logo.webp` / `ddc-logo.png` keep their upstream filenames
  because `frontend/src` still imports them, but now contain the PrimeCrest lockup / mark.
- `desktop/src-tauri/icons/` - Tauri desktop, Windows Store, iOS and Android icon set (`icon.ico`, `icon.icns`
  as a macOS rounded tile).
