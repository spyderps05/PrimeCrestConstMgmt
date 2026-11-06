# Review notes (v2: re-shot after the Pakistan cost base, withholding and figure fixes)

## What is on screen
- All 20 feature slots are real captures of PrimeCrest with the four Pakistan demo projects (fresh database `primecrest_video2`, `pakistan-pk` pack, rate books loaded at boot). Four are screen recordings (Gantt scroll, BOQ scroll, BIM orbit, sales tax switching Punjab to Sindh); the rest are 110%-zoom screenshots. `tools/capture.mjs` re-shoots all of them; `CAPTURE-LIST.md` lists each slot and how to run it.
- Tags carry figures read off the v2 captures: Rs 51.8 Cr portfolio (518.2M PKR, each project once), Rs 4.3 Cr peak funding and Rs 16.48 Cr plan (Karachi school), CO-004 Rs 8.7 lakh, 437-day critical path (Faisalabad road), Rs 3.91 Cr with tax (Lahore house BOQ, PKR 39,081,064), RCC roof slab matched to Punjab MRS at Rs 28,353/m³, 54 on site at BHU Chak 45, 12 open snags, 14 POs worth Rs 4.6 Cr, Rs 79,100 withheld under s.153 on PA-003 (PKR 1,054,661 at 7.5%), PRA 16% and SRB 15%.
- The CTA ends on "© 2026 Spyder Solutions. All rights reserved." No caption, tag or card mentions open source.

## Changed from v1
- QS scene 12: AI cost match is back (`/cost-match`): Lahore house BOQ lines matched to Punjab MRS 2-2026 (Lahore) items, the first line confirmed. BOQ validation is out of the film.
- New "FOR ACCOUNTS" section (6 s): FBR s.153(1)(c) withholding worked out on the Withholding Tax page. The sales tax scene (PRA/SRB) stays after it, so the film is 116 s (was 110 s).
- Urdu dashboard: the Pakistan "cases for your market" section is now shown.
- Tags updated to the reconciled demo figures (portfolio, Rs 16.48 Cr, Rs 3.91 Cr, 437-day critical path).

## Not filmed, and why
- The interim payment certificate (PK layout) of the seeded subcontractor pay applications: PRA 16% is drawn (PKR 168,746 on PA-003) but the "Income Tax Withheld (ITO 2001 s.153) (E x 7.5%)" line is Held on every demo certificate ("The tax was computed on 1,223,407.22, this certificate's base is 1,054,661.4": the stored tax used G = E + sales tax as its base). The Withholding Tax page is filmed instead; the certificate can replace it once the seeded taxes use base E.
- The Urdu locale still says "#1 open-source construction ERP" (`dashboard.open_source_badge`, plus about a dozen other `ur.ts` strings). The capture hides the badge.
- DWG takeoff: the demo drawing is now an English ten-marla plan, but the BIM orbit with live quantities reads better, so the takeoff scene stays on BIM.

## Measured vs looked at
- `npx hyperframes check`: exit 0.
- Every capture was opened and checked for spinners, errors, German text and upstream branding before the render; draft frames were checked by eye at 11, 15, 57, 89, 94, 99, 113 and 115 s. The draft showed a ghost copy of the shield behind the PC mark on the brand and CTA cards (also in v1: the shield's scale tween with svgOrigin rendered it half size and off centre); the shield now only fades in.
- Audio: the original synthesised bed and SFX (`tools/make_audio.py`), re-timed to 116 s with a persona fill before "FOR ACCOUNTS".

## Known weak spots
- The BIM capture still shows the "BIM converters" notice and the scan-deviation card over the filter panel; the camera frames the model and the quantities panel.
- The PO list opens with six placeholder rows at PKR 0 (procurement-plan POs with no vendor); the callout sits on the amount column where the vendor POs are.
- Some UI text is small at the film's 73% window scale (tax rates, PO table, cost match descriptions); the camera push and callout carry the read.
- No 1080x1920 vertical cut: the composition and its window geometry are 16:9 only.
