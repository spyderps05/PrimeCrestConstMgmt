# Capture list: PrimeCrest demo film

Every screen in the film is a real capture of the app with the four Pakistan demo projects. `tools/capture.mjs` takes all of them in one run; this page says what each slot shows and how to re-run it.

## Re-run the captures

1. A throwaway stack with fresh demo data (see `scripts/dev/run-local.ps1` for the full env):
   - Postgres: an empty database (for example `primecrest_video2` in the `primecrest-qa-pg` container on :55432).
   - Backend without `--reload`: `OE_PACK=pakistan-pk`, `PRIMECREST_DEFAULT_PACK=pakistan-pk`, `SEED_DEMO=true`, `DEMO_USER_PASSWORD=DemoPass1234!`, `OE_DATA_DIR` and `OE_CLI_DATA_DIR` pointing at a new empty folder (so the demos seed), `DATABASE_URL` at the new database. The first boot installs `bhu-punjab`, `lahore-house`, `faisalabad-road` and `school-karachi` (look for `Boot demo installed:` in the log).
   - Frontend: `node --max-old-space-size=10240 node_modules/vite/bin/vite.js build --outDir <tmp>/dist` (the default 4 GB heap runs out), then `VITE_API_TARGET=http://127.0.0.1:<backend port> vite preview --outDir <tmp>/dist --port 5820` (`vite preview` reuses the dev `/api` proxy).
2. `node tools/capture.mjs` (all slots) or `node tools/capture.mjs <slot> ...`. Env: `PC_BASE` (default `http://127.0.0.1:5820`), `PC_EMAIL`, `PC_PASSWORD`, `PC_CHROMIUM`.
3. `npm run draft`, review, then `npm run render`.

The script logs in through the API, injects the session, marks the product tours and the first-run services wizard as done, collapses the "how it works" cards, hides the insights panels where the list reads better, and hides the floating AI button and toasts. Some shots act on the data (open a change order and pick its BOQ, generate the 5D cash flow, run validation, create and confirm a cost-match run, install the withholding schemes and record Ravi Homes' ATL standing), so use a throwaway database.

## Format

- Desktop: 1746x982 CSS viewport at DPR 1.0997, which is 110% browser zoom in a 1920x1080 image. The film shows each capture at about 73% scale.
- Phone: 390x844 at DPR 2 (780x1688 PNG).
- Recordings: Playwright `recordVideo`, trimmed and scaled by ffmpeg to 1920x1080, 30 fps, H.264, yuv420p, no audio, 4.6 to 6 s. Recordings stay out of git (`.gitignore`); PNGs are committed.

## Shots

| # | Scene | File | Route | What it shows |
|---|---|---|---|---|
| 1 | Owner: portfolio | `owner-portfolio.png` | `/projects`, sorted by value | KPI row (4 projects, 8 BOQs, total value 518.2M PKR with each project counted once) and the four project cards. |
| 2 | Owner: cash flow | `owner-cashflow.png` | `/5d` (Karachi school), Generate Cash Flow | Cash-flow forecast: peak funding PKR 42.9 M, monthly inflow/outflow bars, cumulative line. |
| 3 | Owner: cost vs budget | `owner-cost-budget.png` | `/cost-control` (Karachi school) | Planned PKR 164.8 M, expected final cost, difference to plan, paid so far, "worth a look" list. |
| 4 | Owner: approvals | `owner-approvals.png` | `/changeorders`, CO-004 opened, BOQ picked | Submitted change order (Rainwater harvesting tank, +PKR 870,000) with the armed Approve button. |
| 5 | PM: schedule | `pm-schedule-gantt.mp4` | `/schedule` → Programme, City road, Faisalabad; Critical Path | Gantt with the critical path in red ("437 days, 9 critical activities"); the timeline scrolls Aug 2026 to Feb 2027. |
| 6 | PM: risks | `pm-risk-register.png` | `/risks` (Karachi school) | Coloured probability x impact heat map and the register (score, status, owner). |
| 7 | PM: change orders | `pm-change-orders.png` | `/changeorders` (Karachi school) | Five change orders with PKR cost impact, schedule days and status. |
| 8 | QS: BOQ | `qs-boq-editor.mp4` | `/boq/<Lahore house BOQ id>` | BOQ editor scrolling through MRS chapters (03 Earthwork, 06 Concrete, 07 Brickwork, 08, 09); grand total PKR 39,081,064. |
| 9 | QS: takeoff | `qs-takeoff.mp4` | `/bim` (Lahore house IFC) | BIM viewer orbiting the house model, with filtered quantities (area, length) in the summary panel. |
| 10 | QS: AI cost match | `qs-cost-match.png` | `/cost-match` (Lahore house); run "10-marla house BOQ vs Punjab MRS 2-2026, Lahore" created through the API, first line confirmed | Five BOQ lines matched to Punjab MRS items (code `punjab_mrs/MRS-…`, PKR rate, confidence); line 1 (RCC roof slab, 58 m3) priced against MRS-06-006-a-3 at PKR 28,353.15/m3. |
| 11 | Site: daily diary | `site-daily-diary.png` | `/projects/<BHU id>/daily-diary`, latest day | Weather, labour 54, equipment 6, and the day's entries. |
| 12 | Site: punch list | `site-punch-list.png` | `/punchlist` (BHU Chak 45) | KPI row (12 open, 2 critical/high, 5 resolved) and items with priority, status, trade, assignee. |
| 13 | Site: RFIs | `site-rfi-inspections.png` | `/rfi` (Karachi school), RFI-003 expanded | RFI list with ball-in-court and due dates; RFI-003 question and response. |
| 14 | Site: phone | `site-mobile-field.png` | `/projects/<BHU id>/daily-diary` at 390x844 | The diary at phone size. |
| 15 | Procurement: POs | `proc-purchase-orders.png` | `/procurement` (Faisalabad road) | Purchase orders with vendor, dates, PKR amount and status. |
| 16 | Procurement: subcontractors | `proc-subcontractors.png` | `/subcontractors` (Faisalabad road) | Register (status, insurance, rating) and pay applications held on an expired insurance certificate. |
| 17a | Accounts: FBR withholding | `accounts-withholding.png` | `/tax-withholding`: shipped schemes installed, Ravi Homes recorded as a company on the Active Taxpayer List (party standing, via the API), PA-003 worked out | s.153(1)(c) scheme, gross PKR 1,054,661, 7.5% band, tax withheld PKR 79,100, net payable PKR 975,561; the Pakistan scheme card (7.5 / 8 / 15 / 16%) below. The other countries' scheme cards are hidden. |
| 17b | Accounts: sales tax | `accounts-sales-tax.mp4` | `/tax-rates`, Pakistan, PK-PB then PK-SD | PRA (Punjab services) 16%, then SRB (Sindh services) 15%. |
| 18 | Anywhere: Urdu | `lang-urdu.png` | `/dashboard`, UI language Urdu | Dashboard right-to-left in Urdu, the Pakistan pack card and the Pakistan "cases for your market". |
| 19 | Anywhere: offline | `offline-field-time.png` | `/field-time` with the network cut | "You're offline" bar and the day sheet that keeps the day on the device until the signal returns. |

## What changed from the first storyboard, and why

v2 (re-shot on `primecrest_video2` after the Pakistan cost base, s.153 withholding and figure fixes landed):

- **AI cost match is back** (scene 12). The `pakistan-pk` pack now loads Punjab MRS 2-2026 (Lahore), KP MRS-2025, Balochistan CSR 2026 and MES SR 2014 (about 22k items) at boot, and matching ranks the project's own province first, so the Lahore house lines land on Punjab MRS items. The script also keeps the old `qs-validation` slot, which is no longer in the film.
- **FBR withholding is back** (new scene "FOR ACCOUNTS", before the sales tax scene). It is filmed on the Withholding Tax page, which now ships the Pakistan s.153(1)(c) scheme. The interim payment certificate of the seeded PK pay applications was tried first: it shows PRA 16% (PKR 168,746 on PA-003) but its "Income Tax Withheld (ITO 2001 s.153) (E x 7.5%)" line is **Held** with "The tax was computed on 1,223,407.22, this certificate's base is 1,054,661.4" on every demo certificate (the stored tax was worked out on G = E + sales tax, the certificate checks it against E), so it is not filmed until that is fixed in the backend.
- **Sales tax kept** (PRA 16%, SRB 15%): the film grew from 110 s to 116 s.
- **Urdu dashboard**: "cases for your market" now shows Pakistan cases, so it is no longer hidden. The Urdu locale still carries the upstream "#1 open-source construction ERP" badge (`dashboard.open_source_badge` and about a dozen other `ur.ts` strings); the capture hides that badge because PrimeCrest is proprietary.
- **Takeoff stays on BIM**: the DWG demo drawing is now an English ten-marla ground floor plan, but its summary reads 0 m2 until something is measured, while the BIM orbit shows live quantities; `/dwg-takeoff` is a good alternative slot.
- **Figures** in the tags are read off the v2 captures: Rs 51.8 Cr portfolio (518.2M PKR), Rs 16.48 Cr plan, Rs 4.3 Cr peak funding, Rs 3.91 Cr with tax (PKR 39,081,064), 437-day critical path, 14 POs worth Rs 4.6 Cr (PKR 45,990,000), Rs 79,100 withheld.

Still true from v1:

- **Field app** (`/field`) needs a field session minted from an SMS magic link (`EXPOSE_DEV_AUTH_SECRETS` or an SMS provider), so the phone scene films the main app at phone size.
- **PrimeCrest Desktop** (Tauri) has no build on this machine, so the offline scene films the day sheet in the browser with the network cut instead of the desktop window.
- Hidden on purpose: the floating AI button, toasts, "how it works" cards, the release-notes strip, the Urdu open-source badge, the non-Pakistan withholding schemes, and four placeholder "Demo Structures Ltd" rows in the subcontractor register.
