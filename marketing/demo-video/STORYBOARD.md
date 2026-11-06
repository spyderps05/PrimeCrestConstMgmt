# PrimeCrest Construction Management: product demo film

**Film:** "PrimeCrest Construction Management, by Spyder Solutions". About 110 s at 1920x1080 and 30 fps, for Pakistani contractors, developers and consultants.
**Shape:** pain hook, brand reveal, a tour by persona (Owner, PM, QS, Site Engineer, Procurement and Accounts), Urdu and offline, call to action.
**Sound:** an original 120 BPM bed in A minor (Am F C G), synthesised locally by `tools/make_audio.py` with no samples and no licensed tracks. Under the hook it holds back to a filtered pulse, then drops on the brand reveal. A snare fill and a crash lead into each persona section, and the bed resolves under the CTA. A separate track carries the SFX: whooshes on the wipes, thuds and pops in the hook, and a click on the CTA button.
**Captions:** on screen from start to finish. They use Archivo Black at 62 px in white, with the key words in light copper `#E08A55`. Words pop in with a 60 ms stagger and the caption sits in the band under the app window (y around 888 px).

## Spec (numbers, not adjectives)

| | |
|---|---|
| GOAL | A Pakistani builder sees their own pain, then sees one system that covers office and site. They leave with "primecrest.pk, book a demo". |
| OUTPUT | HyperFrames, 1920x1080, 30 fps, 110 s = 3300 frames. 120 BPM, so 1 beat = 15 frames and 1 bar = 60 frames. Every cut lands on a bar line (an even second). |
| LOOK | The ground is PrimeCrest ink `#12202B` with a 48 px drafting grid at 3.5% white. Copper is the only accent, as in the app: `#C4622D` fills the wipe slab, the callout frame and the tag; light copper `#E08A55` (the app's dark-mode accent) colours caption key words and the persona label. Real app UI sits in a 1408x792 window (16:9) under a 40 px chrome bar showing `primecrest.pk/<route>`, with radius 14 and shadow 0 30 70 at 45%. Display type is Archivo Black and body type is Inter 600 to 800. |
| MOTION | Window entry: a 150 px copper slab sweeps left to right over 0.5 s (power3.inOut) and the window is revealed behind its trailing edge. Camera: a slow push from 1.0 to 1.06–1.16 toward the feature's focus point (sine.inOut) for the length of the scene. Callout: a 5 px copper frame pops in with back.out(2) at +0.75 s and dims the rest of the screen by 18%. Persona intro (the first scene of each section): the role name slams in at 170 px (from 1.35x to 1x in 0.28 s, expo.out), holds about 0.85 s, then exits left. |
| BANNED | Invented dashboards, which is why a missing capture shows a labelled placeholder card. Also banned: glow, bloom, particles, purple gradients, three cards in a row, a title over a dimmed screenshot, a logo docked in a corner, and copyrighted music. |

## Scene list

The timing is in `scenes.json` (the single source of truth). The `route` column is the app URL to capture, and `{lahore-house}` means the id of the project installed from that demo pack.

| # | t (s) | Dur | Scene / persona | Caption (copper words in *italics*) | Capture slot | Route and state | Motion / sound |
|---|---|---|---|---|---|---|---|
| 1 | 0–8 | 8 | **Hook** | "Budgets *blow up*." then "Paperwork *piles up*." then "Site updates *vanish* in WhatsApp." | none (drawn) | n/a | Beat 1: a BUDGET bar of Rs 4.0 Cr against an ACTUAL bar that overshoots a dashed limit to Rs 5.6 Cr, then a red "+40%" stamp and a shake (thud). Beat 2: seven paper forms (DPR, IPC #7, MB, PO, RFI, BOQ v9, GRN) drop and pile up (paper thuds). Beat 3: a chat phone "Site Team - Block 7" floods with Urdu/English messages while the unread badge runs from 243 to 999+ (pops). Under the hook the music is a filtered pulse with a riser. |
| 2 | 8–12 | 4 | **Brand reveal** | "One platform. *Office to site.*" | none | n/a | A copper slab wipes off. The PC shield mark lands and its copper rim draws itself, the PrimeCrest letters (Fraunces, outlined) stagger in, "CONSTRUCTION MANAGEMENT" settles, then "by Spyder Solutions". This is the drop, with a crash. |
| 3 | 12–18 | 6 | OWNER: portfolio | "Every project. *One screen.*" | `owner-portfolio.png` | `/projects`: the 4 PK demo projects, KPI row in PKR | Persona slam "FOR THE OWNER" and a crash. Tag: "4 projects · Lahore · Karachi · Punjab · Faisalabad". Callout on the KPI row. |
| 4 | 18–22 | 4 | OWNER: cash flow | "Cash flow in *PKR*, month by month." | `owner-cashflow.png` | `/5d` (Karachi school), cash-flow forecast | Push toward the chart; callout on peak funding. Tag: "School, Karachi · peak funding Rs 4.3 Cr". |
| 5 | 22–26 | 4 | OWNER: cost vs budget | "Cost vs budget, *before* it overruns." | `owner-cost-budget.png` | `/cost-control`, Karachi school | Tag: "School, Karachi · Rs 16.5 Cr plan". |
| 6 | 26–30 | 4 | OWNER: approvals | "Approvals in *one click*." | `owner-approvals.png` | `/changeorders`, submitted CO-004 opened | Callout on the Approve button. Tag: "CO-004 · Rs 8.7 lakh · awaiting owner". |
| 7 | 30–36 | 6 | PROJECT MANAGER: 4D schedule | "4D schedule. *Gantt* to critical path." | `pm-schedule-gantt.mp4` (recording) | `/schedule`, Faisalabad road programme, critical path on | Persona slam. Timeline scrolls. Tag: "Faisalabad city road · 14 months". |
| 8 | 36–40 | 4 | PM: risks | "Risks scored and *owned*." | `pm-risk-register.png` | `/risks` (Karachi school) | Callout on the heat map. |
| 9 | 40–44 | 4 | PM: change orders | "Change orders with *cost impact*." | `pm-change-orders.png` | `/changeorders` (Karachi school) | Callout on the PKR cost-impact column. |
| 10 | 44–50 | 6 | QS / ESTIMATOR: BOQ | "BOQ with Punjab *MRS rates*." | `qs-boq-editor.mp4` (recording) | `/boq/{lahore-house BOQ}` | Persona slam. The bill scrolls through the MRS chapters. Tag: "10-marla house, Lahore · Rs 3.9 Cr BOQ". |
| 11 | 50–54 | 4 | QS: takeoff | "Take off from *CAD, BIM and PDF*." | `qs-takeoff.mp4` (recording) | `/bim`, Lahore house IFC model | The model orbits; callout on the quantities panel. |
| 12 | 54–58 | 4 | QS: validation | "Every BOQ *checked* before it goes out." | `qs-validation.png` | `/validation`, Lahore house BOQ | Tag: "966 checks · 98% quality score". (Replaces AI cost match, see CAPTURE-LIST.) |
| 13 | 58–64 | 6 | SITE ENGINEER: daily diary | "Daily diary: *weather, labour, site log.*" | `site-daily-diary.png` | `/projects/{bhu-punjab}/daily-diary`, latest day | Persona slam. Tag: "BHU Chak 45, Punjab · 54 on site". |
| 14 | 64–68 | 4 | SITE: punch list | "Punch lists *closed*, not forgotten." | `site-punch-list.png` | `/punchlist` (BHU Chak 45) | |
| 15 | 68–72 | 4 | SITE: RFIs | "RFIs and inspections, *on record*." | `site-rfi-inspections.png` | `/rfi` (Karachi school), RFI-003 opened | Callout on the response. |
| 16 | 72–76 | 4 | SITE: mobile | "Works on the *phone*, on site." | `site-mobile-field.png` (390x844) | daily diary at phone size | Shown in a phone frame instead of the browser window. |
| 17 | 76–82 | 6 | PROCUREMENT: POs | "Requisition to *PO* to delivery." | `proc-purchase-orders.png` | `/procurement` (Faisalabad road) | Persona slam "FOR PROCUREMENT". |
| 18 | 82–86 | 4 | PROCUREMENT: subcontractors | "Subcontractors and *payments*, tracked." | `proc-subcontractors.png` | `/subcontractors` (Faisalabad road) | Callout on the held pay applications. |
| 19 | 86–90 | 4 | ACCOUNTS: sales tax | "Provincial sales tax, *PRA to SRB.*" | `accounts-sales-tax.mp4` (recording) | `/tax-rates`, Pakistan, Punjab then Sindh | Tag: "PRA 16% Punjab · SRB 15% Sindh". |
| 20 | 90–96 | 6 | ANYWHERE: Urdu UI | "Urdu or English. *Your call.*" | `lang-urdu.png` | `/dashboard` with the language set to Urdu (RTL) | Persona slam "WORKS ANYWHERE". |
| 21 | 96–100 | 4 | ANYWHERE: offline | "No signal on site? It works *offline*." | `offline-field-time.png` | `/field-time` with the network cut | Tag: "No signal · kept on the device". |
| 22 | 100–110 | 10 | **CTA** | "Built for Pakistan. *Book your demo.*" | none | n/a | The mark draws and the wordmark punches in. The "Book a free demo" button rises, then "primecrest.pk · support@primecrest.pk". At 102.75 s a cursor clicks the button (press, ripple, click and impact). The music resolves and fades over the last 2.5 s. |

The capture work is listed shot by shot in [CAPTURE-LIST.md](CAPTURE-LIST.md).

## Demo data the captions lean on

These come from `backend/app/core/demo_packs/` and are all shown in PKR:

- **lahore-house**: a private 10-marla house in Allama Iqbal Town, Lahore. The priced BOQ totals PKR 39,081,064 (about Rs 3.9 Cr) across 11 MRS sections and 81 positions. The BOQ follows Punjab MRS chapters (Jan–Jun 2025) and carries 5% overhead, 10% profit and Punjab sales tax on services at 16%.
- **school-karachi**: Government Primary School, Gulshan Block 7, Karachi. The contract is Rs 164,779,340 (Rs 16.5 Cr) over 12 months, under PEC SBD Dec-2023 and Sindh sales tax on services at 15%.
- **bhu-punjab**: Basic Health Unit Chak 45, Punjab. The contract is Rs 50,695,500 over 12 months.
- **faisalabad-road**: City road, Faisalabad. A 14-month programme (Apr 2026 to May 2027) with a 437-day critical path; 14 purchase orders worth PKR 45,990,000.
- **Sales tax**: provincial sales tax on services from `/tax-rates`: PRA (Punjab) 16%, SRB (Sindh) 15%. (The FBR s.153(1)(c) withholding rows are in the backend but not drawn for Pakistan projects; see CAPTURE-LIST.)

## How the composition works

- `scenes.json` holds every scene: its duration, persona, captions, capture slot, route, tag, focus point and zoom.
- `node tools/build.mjs` reads it and generates `index.html`, `compositions/feat-*.html` and `compositions/captions.html`. For each feature scene it looks in `captures/` for `<slot>.mp4|.webm|.png|.jpg|.webp`. If it finds a file, the scene shows the real screen inside the window (all 19 slots are filled; `tools/capture.mjs` re-shoots them). If not, it renders a branded fallback card that names the missing file, its route and what it must show. A missing capture therefore never breaks `check` or `render`.
- `compositions/hook.html`, `brand.html` and `cta.html` are hand-written and are not regenerated.
- `python tools/make_audio.py` (needs numpy and scipy) writes `assets/audio/music.wav` and `sfx.wav`, timed from the cut list that `build.mjs` produces.

## Re-render once captures exist

```bash
cd marketing/demo-video
# drop files into captures/ using the exact slot names from CAPTURE-LIST.md, then:
npm run draft        # = node tools/build.mjs && python tools/make_audio.py && npx hyperframes render -o out/draft.mp4
npm run render       # same, written to out/primecrest-demo.mp4
npm run dev          # Studio preview, to review before rendering
```

To retime the film or change the copy, edit `scenes.json` and run `npm run build`. Every cut should stay on an even second so it stays on the beat.
