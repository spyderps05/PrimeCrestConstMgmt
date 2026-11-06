# Capture list: PrimeCrest demo film

The demo film needs these screens. Save each file into `marketing/demo-video/captures/` under the **exact name given** (the extension decides the type). Then run `npm run draft` in `marketing/demo-video/` to re-render. Any slot without a file keeps its labelled placeholder card, so you can deliver captures one at a time.

## Global setup

- **Viewport:** 1920x1080 CSS px, deviceScaleFactor 1, browser zoom 110%. The window in the film shows the capture at 73% scale, so 110% keeps table text readable. The one exception is `site-mobile-field.png`, which uses 390x844 at DPR 2.
- **Data:** a fresh database with the four Pakistan demo packs installed: `lahore-house`, `school-karachi`, `bhu-punjab` and `faisalabad-road` (Onboarding, then Demo, or `/onboarding/demo`). Currency must be PKR and the UI language English, except for `lang-urdu`.
- **Branding:** the PrimeCrest name and logo must appear in the app header. Shoot after the rebrand has landed, with no "OpenConstructionERP / DDC" visible anywhere.
- **Clean frame:** no dev tools, no toasts, no cookie or onboarding pop-ups, no debug banners, mouse cursor hidden for screenshots, and no personal emails. Log in as a demo user named like "Ahmed Raza (Director)".
- **Screenshots** are PNG of the viewport only. Do not capture the browser chrome, because the film draws its own.
- **Recordings** (`.mp4`) are 1920x1080, 30 fps, H.264, yuv420p, 6–8 s, no audio. Use smooth, deliberate cursor moves, keep the first and last 0.5 s still, and hold each result for at least 1 s.
- **Focus area:** each scene pushes in toward a focus point and frames a region with a copper callout (`focus` and the optional `box` in `scenes.json`, as fractions of the frame). Keep the feature described below inside the middle 60% of the frame. If it sits elsewhere, update `focus` and `box` in `scenes.json` for that scene.

`{lahore-house}` and the like mean the project id of that demo pack. Open the project from `/projects` and copy the id from the URL.

## Shots

| # | File | Route | Actions | Must be visible |
|---|---|---|---|---|
| 1 | `owner-portfolio.png` | `/portfolio` | Open the portfolio and let it load. Sort by contract value if possible. | All 4 Pakistan projects (Lahore house, Karachi school, BHU Chak 45, Faisalabad road), each with status, budget in PKR and progress. |
| 2 | `owner-cashflow.png` | `/portfolio` | Scroll to the portfolio cash-flow widget and frame it in the upper-middle. | Monthly inflow and outflow bars plus the cumulative line, with PKR axis labels. |
| 3 | `owner-cost-budget.png` | `/cost-control` | Select the Karachi school project. | Budget vs committed vs actual by section, a variance column, and the Rs total (about Rs 16.5 Cr contract). |
| 4 | `owner-approvals.png` | `/governance?tab=approvals` (`/approval-routes` redirects here) | Create or seed one pending approval, such as a change order or payment certificate. | The pending approval row with its approver, amount and **Approve** button. |
| 5 | `pm-schedule-gantt.mp4` | `/schedule` | Select the Faisalabad road project. Start on the Gantt, scroll the timeline right slowly, then toggle or highlight the critical path. If BIM is linked, briefly show the 4D link. | Gantt bars, dependency arrows, the critical path in a distinct colour, and the 14-month span. |
| 6 | `pm-risk-register.png` | `/risks` | Select the Karachi school (or any PK project) with at least 5 risks. | Risk rows with probability x impact score, owner and status, plus the heat matrix if one is shown. |
| 7 | `pm-change-orders.png` | `/changeorders` | Select a PK project with 2–3 change orders. | Change order list with cost impact in PKR and pending/approved status. |
| 8 | `qs-boq-editor.mp4` | `/projects/{lahore-house}/boq` | Open the Lahore house BOQ. Expand "06 - Concrete (MRS chapter 6)", edit one quantity (for example roof slab 18, then 20 m3) so the totals recalculate, then scroll to the markups. | Item descriptions naming MRS chapters, quantities, PKR rates and the markup lines (overhead 5%, profit 10%, Punjab sales tax on services 16%) with the grand total. |
| 9 | `qs-takeoff.mp4` | `/takeoff` (PDF). `/dwg-takeoff` or `/bim` is fine if it reads better. | Load a floor plan and measure one room area or wall length. The quantity appears in the side panel, then link or send it to a BOQ line. | The drawing, the measurement being drawn, and the resulting quantity with its unit. |
| 10 | `qs-ai-cost-match.png` | `/cost-match` | Run a match for 5–10 BOQ descriptions from the Lahore house. | Each description matched to a cost item with a confidence score, with accept/reject controls. |
| 11 | `site-daily-diary.png` | `/projects/{bhu-punjab}/daily-diary` | Open today's (or the latest) diary entry, filled in. | Weather, labour headcount by trade, work done, and 2–4 attached site photos. |
| 12 | `site-punch-list.png` | `/punchlist` | Select a PK project with about 6 items in mixed states. | Items with photo thumbnails, assignee, location, and open/closed status. |
| 13 | `site-rfi-inspections.png` | `/rfi` (alternative: `/inspections`) | Show a list of 4–6 RFIs with one opened in the side panel. | RFI number, subject, due date and status, plus a response thread on the opened one. |
| 14 | `site-mobile-field.png` | `/field` | **Viewport 390x844 at DPR 2** (portrait PNG). Open the field home. | The phone-sized UI: today's tasks or quick diary entry, and the photo capture button. |
| 15 | `proc-purchase-orders.png` | `/procurement` | Select a PK project with requisitions and POs. | Requisitions and purchase orders with supplier, PKR amount, and status (draft, approved, delivered). |
| 16 | `proc-subcontractors.png` | `/subcontractors` | Show the subcontractor register. | Packages (civil, MEP, finishes), contract values in PKR, and payment applications or retention. |
| 17 | `accounts-tax-withholding.png` | `/tax-withholding` | Show the Pakistan rows applied to a payment certificate. | Income tax withholding under ITO s.153(1)(c) (company/non-company, ATL/non-ATL rows), plus the provincial sales tax on services line if shown. |
| 18 | `lang-urdu.png` | `/dashboard` | Switch the interface language to Urdu (اردو) in the language menu or settings, then reload the dashboard. | The dashboard rendered right-to-left in Urdu, with PKR KPI cards. |
| 19 | `desktop-offline.png` | PrimeCrest Desktop app (the Tauri build in `desktop/`) | Launch the installed desktop app with Wi-Fi off and open a project dashboard. A 1920x1080 window screenshot is fine. Showing the OS offline indicator is a plus. | The native PrimeCrest window running locally with project data and no network. |

## Optional upgrades

- Any `.png` slot can be supplied as an `.mp4` of the same name for more motion. When both exist, `build.mjs` uses the `.mp4`.
- `compositions/brand.html` and `compositions/cta.html` carry the real PrimeCrest mark (from `assets/brand/primecrest-mark.svg`).
