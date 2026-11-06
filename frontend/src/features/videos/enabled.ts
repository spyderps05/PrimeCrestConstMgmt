/**
 * Whether the Video guides library is offered anywhere in the app.
 *
 * The catalogue in this folder plays lessons from the upstream project's
 * YouTube channel, which is not PrimeCrest material. Until PrimeCrest has its
 * own videos the feature stays switched off: no menu row, no command palette
 * entry, no /videos page (it redirects home), no per-screen "videos for this
 * step" panel, and no video strips on the dashboard or in a case. The code is
 * kept so a PrimeCrest catalogue can be dropped in and this flipped back on.
 */
export const VIDEO_GUIDES_ENABLED = false;
