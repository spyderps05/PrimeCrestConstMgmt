# Capture list: PrimeCrest demo film

Every screen in the film is a real capture of the app with the four Pakistan demo projects. `tools/capture.mjs` takes all of them in one run; this page says what each slot shows and how to re-run it.

## Re-run the captures

1. A throwaway stack with fresh demo data (see `scripts/dev/run-local.ps1` for the full env):
   - Postgres: an empty database (for example `primecrest_video` in the `primecrest-qa-pg` container on :55432).
   - Backend without `--reload`: `OE_PACK=pakistan-pk`, `PRIMECREST_DEFAULT_PACK=pakistan-pk`, `SEED_DEMO=true`, `DEMO_USER_PASSWORD=DemoPass1234!`, `OE_DATA_DIR` and `OE_CLI_DATA_DIR` pointing at a new empty folder (so the demos seed), `DATABASE_URL` at the new database. The first boot installs `bhu-punjab`, `lahore-house`, `faisalabad-road` and `school-karachi` (look for `Boot demo installed:` in the log).
   - Frontend: `vite build --outDir <tmp>/dist`, then `VITE_API_TARGET=http://127.0.0.1:<backend port> vite preview --outDir <tmp>/dist --port 5820` (`vite preview` reuses the dev `/api` proxy).
2. `node tools/capture.mjs` (all slots) or `node tools/capture.mjs <slot> ...`. Env: `PC_BASE` (default `http://127.0.0.1:5820`), `PC_EMAIL`, `PC_PASSWORD`, `PC_CHROMIUM`.
3. `npm run draft`, review, then `npm run render`.

The script logs in through the API, injects the session, marks the product tours and the first-run services wizard as done, collapses the "how it works" cards, hides the insights panels where the list reads better, and hides the floating AI button and toasts. Some shots act on the data (open a change order and pick its BOQ, generate the 5D cash flow, run validation), so use a throwaway database.

## Format

- Desktop: 1746x982 CSS viewport at DPR 1.0997, which is 110% browser zoom in a 1920x1080 image. The film shows each capture at about 73% scale.
- Phone: 390x844 at DPR 2 (780x1688 PNG).
- Recordings: Playwright `recordVideo`, trimmed and scaled by ffmpeg to 1920x1080, 30 fps, H.264, yuv420p, no audio, 4.6 to 6 s. Recordings stay out of git (`.gitignore`); PNGs are committed.

## Shots

| # | Scene | File | Route | What it shows |
|---|---|---|---|---|
| 1 | Owner: portfolio | `owner-portfolio.png` | `/projects`, sorted by value | KPI row (4 projects, 8 BOQs, PKR totals) and the four project cards. |
| 2 | Owner: cash flow | `owner-cashflow.png` | `/5d` (Karachi school), Generate Cash Flow | Cash-flow forecast: peak funding PKR 42.9 M, monthly inflow/outflow bars, cumulative line. |
| 3 | Owner: cost vs budget | `owner-cost-budget.png` | `/cost-control` (Karachi school) | Planned PKR 164.8 M, expected final cost, difference to plan, paid so far, "worth a look" list. |
| 4 | Owner: approvals | `owner-approvals.png` | `/changeorders`, CO-004 opened, BOQ picked | Submitted change order (Rainwater harvesting tank, +PKR 870,000) with the armed Approve button. |
| 5 | PM: schedule | `pm-schedule-gantt.mp4` | `/schedule` → Programme, City road, Faisalabad; Critical Path | Gantt with the critical path in red ("437 days, 9 critical activities"); the timeline scrolls Aug 2026 to Feb 2027. |
| 6 | PM: risks | `pm-risk-register.png` | `/risks` (Karachi school) | Coloured probability x impact heat map and the register (score, status, owner). |
| 7 | PM: change orders | `pm-change-orders.png` | `/changeorders` (Karachi school) | Five change orders with PKR cost impact, schedule days and status. |
| 8 | QS: BOQ | `qs-boq-editor.mp4` | `/boq/<Lahore house BOQ id>` | BOQ editor scrolling through MRS chapters (03 Earthwork, 06 Concrete, 07 Brickwork, 08, 09); grand total PKR 39,081,064. |
| 9 | QS: takeoff | `qs-takeoff.mp4` | `/bim` (Lahore house IFC) | BIM viewer orbiting the house model, with filtered quantities (area, length) in the summary panel. |
| 10 | QS: validation | `qs-validation.png` | `/validation`, main Lahore BOQ, Run Validation | Quality score 98%, 0 errors, 966 checks, findings list. |
| 11 | Site: daily diary | `site-daily-diary.png` | `/projects/<BHU id>/daily-diary`, latest day | Weather, labour 54, equipment 6, and the day's entries. |
| 12 | Site: punch list | `site-punch-list.png` | `/punchlist` (BHU Chak 45) | KPI row (12 open, 2 critical/high, 5 resolved) and items with priority, status, trade, assignee. |
| 13 | Site: RFIs | `site-rfi-inspections.png` | `/rfi` (Karachi school), RFI-003 expanded | RFI list with ball-in-court and due dates; RFI-003 question and response. |
| 14 | Site: phone | `site-mobile-field.png` | `/projects/<BHU id>/daily-diary` at 390x844 | The diary at phone size. |
| 15 | Procurement: POs | `proc-purchase-orders.png` | `/procurement` (Faisalabad road) | Purchase orders with vendor, dates, PKR amount and status. |
| 16 | Procurement: subcontractors | `proc-subcontractors.png` | `/subcontractors` (Faisalabad road) | Register (status, insurance, rating) and pay applications held on an expired insurance certificate. |
| 17 | Accounts: sales tax | `accounts-sales-tax.mp4` | `/tax-rates`, Pakistan, PK-PB then PK-SD | PRA (Punjab services) 16%, then SRB (Sindh services) 15%. |
| 18 | Anywhere: Urdu | `lang-urdu.png` | `/dashboard`, UI language Urdu | Dashboard right-to-left in Urdu, PKR KPI cards. |
| 19 | Anywhere: offline | `offline-field-time.png` | `/field-time` with the network cut | "You're offline" bar and the day sheet that keeps the day on the device until the signal returns. |

## What changed from the first storyboard, and why

- **AI cost match** (`/cost-match`) was not filmed: matching needs a regional cost base, and the Pakistan pack ships none (its rates come from the MRS/CSR importer), so every line came back "nothing found". Scene 12 shows BOQ validation instead.
- **FBR withholding (ITO s.153(1)(c))**: the rows exist in the backend (`payment_taxes/data_pk.py`) but the app only draws them on the payment-certificate tax panel, which Pakistan projects do not show, and the Withholding Tax page ships only DE/GB/IE/IT/US schemes. Scene 19 shows provincial sales tax (PRA, SRB) from `/tax-rates` instead.
- **Field app** (`/field`) needs a field session minted from an SMS magic link (`EXPOSE_DEV_AUTH_SECRETS` or an SMS provider), so the phone scene films the main app at phone size.
- **PrimeCrest Desktop** (Tauri) has no build on this machine, so scene 21 films the offline day sheet in the browser with the network cut instead of the desktop window.
- **Takeoff**: the DWG demo drawing carries German room labels and the PDF takeoff needs an uploaded drawing, so the BIM takeoff on the Lahore house IFC model is filmed.
- Hidden on purpose: the floating AI button, toasts, "how it works" cards, the release-notes strip and the German "cases for your market" section on the Urdu dashboard, and four placeholder "Demo Structures Ltd" rows in the subcontractor register.
