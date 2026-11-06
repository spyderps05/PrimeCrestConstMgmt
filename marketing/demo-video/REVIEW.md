# Review notes (final cut with real captures)

## What is on screen
- All 19 feature slots are real captures of PrimeCrest with the four Pakistan demo projects (fresh database, `pakistan-pk` pack). Four are screen recordings (Gantt scroll, BOQ scroll, BIM orbit, sales tax switching Punjab to Sindh); the rest are 110%-zoom screenshots. `tools/capture.mjs` re-shoots all of them; `CAPTURE-LIST.md` lists each slot and how to run it.
- Tags carry figures read off the captures: Rs 16.5 Cr plan and Rs 4.3 Cr peak funding (Karachi school), CO-004 Rs 8.7 lakh, Lahore house BOQ PKR 39,081,064 (Rs 3.9 Cr), 966 checks at 98%, 54 on site at BHU Chak 45, 12 open snags, 14 POs on the Faisalabad road, PRA 16% and SRB 15%.
- Callout boxes and focus points in `scenes.json` were set against the real UI and checked on the draft render.

## Changed from the storyboard (and why)
- QS scene 12: BOQ validation instead of AI cost match. The Pakistan pack ships no regional cost base, so the matcher returns "nothing found" on every line.
- Accounts scene 19: provincial sales tax (PRA/SRB, `/tax-rates`) instead of FBR s.153 withholding. The withholding rows exist in the backend but the UI draws them only on the payment-certificate panel, which Pakistan projects do not show; the Withholding Tax page ships only DE/GB/IE/IT/US schemes.
- Site scene 16: the main app at phone size. The `/field` shell needs a field session from an SMS magic link.
- Anywhere scene 21: the field day sheet with the network cut ("You're offline", "kept on this device") instead of the PrimeCrest Desktop window, which has no build on this machine.
- Takeoff scene 11: BIM takeoff on the Lahore house IFC model. The DWG demo drawing has German room labels and the PDF takeoff has no drawing loaded.

## Measured vs looked at
- `npx hyperframes check`: passed, 0 errors. Warnings kept: 12 craft `line_unread` warnings on the hook chat sender names (the flood is meant to be unreadable) and 2 lint density warnings on the generated caption track.
- Draft frames were checked by eye at 5, 11, 15.5, 20, 22, 24, 32, 35, 40, 48, 52, 56, 62, 66, 70, 74, 78, 83, 87, 94, 99 and 105 s. Captions sit in the band under the window and every group is on screen for at least 3.5 s.
- Audio unchanged: original synthesised bed and SFX (`tools/make_audio.py`).

## Known weak spots
- The 4D schedule capture shows a squeezed schedule title at 110% zoom above the Gantt; the scene frames the KPIs and Gantt below it.
- Some UI text is small at the film's 73% window scale (tax rates, PO table); the camera push and callout carry the read.
- The portfolio KPI "1,036.4M PKR" counts both BOQs of each project; the tag avoids quoting it.
- No 1080x1920 vertical cut: the composition and its window geometry are 16:9 only.
