# Review notes (draft with fallback cards)

## Creative calls
- The tour is organised by persona: Owner, PM, QS, Site, Procurement and Accounts, then Anywhere. Each section opens with a 1 s role "slam" and keeps the role name as a vertical label in the left gutter, so the viewer always knows whose day this scene belongs to.
- The hook is drawn, not captured. It has three beats on the bar lines: a budget overrun (Rs 4.0 Cr becomes Rs 5.6 Cr, stamped "+40%"), a pile of paper forms (DPR, IPC, MB, PO, RFI, BOQ, GRN), and a site WhatsApp-style group flooding with Urdu/English messages. The chat is generic, with no WhatsApp logo or branding.
- One reusable feature-scene template: the copper wipe reveals the window, the camera pushes slowly toward the focus point, a copper callout frames the feature, and a copper tag carries a real demo-pack fact.
- A missing capture shows a clearly labelled "CAPTURE PENDING" card naming the file, route and required state, never an invented dashboard. The callout is hidden until a real capture exists.
- The music is original and synthesised locally (120 BPM, Am F C G). Every cut sits on a bar line, and the persona sections get a snare fill and a crash.

## Measured vs looked at
- `npx hyperframes check`: ok=true with 0 errors. The warnings kept on purpose: the persona slams are held for about 1.0 s (the 3–4 word floor is 1.05–1.27 s, but the role word is the read and it stays in the gutter afterwards); the hook chat sender names are on screen briefly during the flood (the flood is meant to be unreadable chaos); and the chat header subtext is under 28 px.
- Snapshot frames were checked by eye at 0.5, 1.5, 3.8, 6, 6.8, 9.5, 12.6, 13, 15.5, 20, 33, 35.5, 47, 73, 87, 93, 101.5 and 105 s. I verified both a `.png` and an `.mp4` capture slot rendering inside the window using test patterns, then removed them.
- The audio was measured, not heard. The music bed is mixed (music + SFX) to −15.8 LUFS integrated, −2.9 dBTP peak (ffmpeg ebur128).

## Weakest shots / next steps
- The fallback cards are stand-ins. The film comes alive once the 19 captures land; then retune `focus` and `box` per scene in `scenes.json` so the callout frames the real control.
- The brand mark is the app's own PC shield (`frontend/src/shared/ui/Logo.tsx`, `assets/brand/primecrest-mark.svg`) inlined as SVG, with the wordmark outlined in Fraunces.
- The 4 s feature scenes are fast by design. If viewers find them too quick, raise the key scenes to 6 s in `scenes.json`. The film stays on the beat as long as durations stay even.
