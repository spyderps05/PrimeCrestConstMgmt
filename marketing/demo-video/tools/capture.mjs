#!/usr/bin/env node
// Captures every screen the demo film needs (see CAPTURE-LIST.md) from a running
// PrimeCrest stack with the four Pakistan demo projects installed.
//
//   node tools/capture.mjs [slot ...]
//
// Env:
//   PC_BASE   frontend URL (vite preview proxied to the backend)  default http://127.0.0.1:5820
//   PC_EMAIL / PC_PASSWORD                                        default demo@primecrest.pk / DemoPass1234!
//   PC_CHROMIUM  path to chrome.exe (default: newest full Chromium under ms-playwright)
//
// Desktop shots use a 1746x982 CSS viewport at DPR 1.0997 (= 110% browser zoom
// in a 1920x1080 image). Screenshots go to captures/<slot>.png. Recordings
// (Gantt, BOQ, BIM takeoff, sales tax) use Playwright recordVideo and are
// scaled with ffmpeg to 1920x1080 H.264 captures/<slot>.mp4 (ffmpeg on PATH).
// The phone shot is 390x844 at DPR 2. Playwright is loaded from
// ../../frontend/node_modules. Some shots act on the demo data (open a change
// order and pick its BOQ, generate the 5D cash flow, run validation, collapse
// "how it works" cards), so run it against a throwaway demo database.
// Usage of a fresh stack: see CAPTURE-LIST.md.

import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { mkdirSync, readdirSync, rmSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const REPO = resolve(ROOT, "..", "..");
const require = createRequire(join(REPO, "frontend", "package.json"));
const { chromium } = require("playwright");

const BASE = process.env.PC_BASE || "http://127.0.0.1:5820";
const EMAIL = process.env.PC_EMAIL || "demo@primecrest.pk";
const PASSWORD = process.env.PC_PASSWORD || "DemoPass1234!";
const OUT = join(ROOT, "captures");
const TMP = join(ROOT, "out", "rec-tmp");
mkdirSync(OUT, { recursive: true });

const only = new Set(process.argv.slice(2));
const want = (slot) => only.size === 0 || only.has(slot);
const wait = (ms) => new Promise((r) => setTimeout(r, ms));

// ------------------------------------------------------------------ session
async function api(path, opts = {}, token) {
  const res = await fetch(`${BASE}/api${path}`, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(opts.headers || {}),
    },
  });
  const txt = await res.text();
  let body;
  try {
    body = JSON.parse(txt);
  } catch {
    body = txt;
  }
  if (!res.ok) throw new Error(`${opts.method || "GET"} ${path} -> ${res.status} ${txt.slice(0, 200)}`);
  return body;
}

async function login() {
  const j = await api("/v1/users/auth/login/", { method: "POST", body: JSON.stringify({ email: EMAIL, password: PASSWORD }) });
  return { token: j.access_token, refresh: j.refresh_token };
}

const items = (x) => (Array.isArray(x) ? x : x?.items ?? x?.results ?? []);

async function projects(token) {
  const list = items(await api("/v1/projects/?limit=100", {}, token));
  const find = (re) => list.find((p) => re.test(p.name));
  return {
    all: list,
    lahore: find(/lahore|marla|iqbal/i),
    school: find(/school|karachi|gulshan/i),
    bhu: find(/BHU|health|chak/i),
    road: find(/faisalabad/i),
  };
}

// ------------------------------------------------------------------ browser
// Use PC_CHROMIUM, else the newest full Chromium Playwright has downloaded
// (the frontend's pinned Playwright may expect a build that is not installed).
function chromiumPath() {
  if (process.env.PC_CHROMIUM) return process.env.PC_CHROMIUM;
  const base = join(process.env.LOCALAPPDATA || join(process.env.HOME || "", ".cache"), "ms-playwright");
  try {
    const dirs = readdirSync(base)
      .filter((d) => /^chromium-[0-9]+$/.test(d))
      .sort((a, b) => Number(b.split("-")[1]) - Number(a.split("-")[1]));
    for (const d of dirs) {
      for (const exe of ["chrome-win64/chrome.exe", "chrome-win/chrome.exe", "chrome-linux/chrome", "chrome-linux64/chrome"]) {
        if (existsSync(join(base, d, exe))) return join(base, d, exe);
      }
    }
  } catch {
    /* fall through to Playwright's default */
  }
  return undefined;
}
let browser;
let session;
let P;

// The film shows each capture at about 73% scale, so shoot at 110% browser
// zoom: a 1746x982 CSS viewport rendered at DPR 1.0997 = a 1920x1080 image.
const DESK = { width: 1746, height: 982 };
const DESK_DPR = 1920 / 1746;

async function newContext({ phone = false, lang = "en", record = false, project = null } = {}) {
  const ctx = await browser.newContext({
    viewport: phone ? { width: 390, height: 844 } : DESK,
    deviceScaleFactor: phone ? 2 : DESK_DPR,
    isMobile: phone,
    hasTouch: phone,
    colorScheme: "light",
    locale: lang === "ur" ? "ur-PK" : "en-GB",
    timezoneId: "Asia/Karachi",
    ...(record ? { recordVideo: { dir: TMP, size: DESK } } : {}),
  });
  await ctx.addInitScript(
    ({ token, refresh, proj, lang }) => {
      try {
        localStorage.setItem("oe_access_token", token);
        if (refresh) localStorage.setItem("oe_refresh_token", refresh);
        localStorage.setItem("oe_remember", "1");
        sessionStorage.setItem("oe_access_token", token);
        if (refresh) sessionStorage.setItem("oe_refresh_token", refresh);
        if (proj) localStorage.setItem("oe_active_project", JSON.stringify({ id: proj.id, name: proj.name, boqId: null }));
        // first-run wizard, product tours, welcome cards
        localStorage.setItem("oe_onboarding_completed", "true");
        localStorage.setItem("oe_welcome_dismissed", "1");
        for (const t of ["", "boq", "accommodation", "bim", "geo", "propdev", "dashboard"]) {
          localStorage.setItem(t ? `oe.tour_completed.${t}` : "oe.tour_completed", "true");
        }
        localStorage.setItem("oe_theme", "light");
        localStorage.setItem("i18nextLng", lang);
        localStorage.setItem("oe_lang_explicit", "1");
      } catch {
        /* ignore */
      }
    },
    { token: session.token, refresh: session.refresh, proj: project, lang },
  );
  return ctx;
}

// Hide anything that is not the product: toasts, the floating AI chat button,
// dev overlays, "work in progress" beta banners.
const CLEAN_CSS = `
  [data-sonner-toaster], .Toastify, [data-testid*="toast" i],
  [data-testid="floating-chat-button"], [data-testid*="floating-chat" i],
  [id*="tanstack" i], .tsqd-parent-container, vite-error-overlay,
  [data-testid^="beta-banner-"], [data-testid*="review-prompt" i], [data-testid*="cookie" i] { display: none !important; }
  * { caret-color: transparent !important; }
`;

async function settle(page, ms = 1200) {
  await page.waitForLoadState("networkidle", { timeout: 20000 }).catch(() => {});
  await page.addStyleTag({ content: CLEAN_CSS }).catch(() => {});
  for (let i = 0; i < 30; i++) {
    const busy = await page
      .locator('main .animate-spin:visible, main [class*="skeleton" i]:visible, main .animate-pulse:visible')
      .count()
      .catch(() => 0);
    if (!busy) break;
    await wait(500);
  }
  await dismiss(page);
  await wait(ms);
}

// First-run "What will you use?" services wizard (offered once per session),
// and the per-page "How it works" info cards (collapsed; the choice is stored
// per user, so it sticks for later runs).
async function dismiss(page) {
  const later = page.getByTestId("wizard-later");
  if (await later.isVisible().catch(() => false)) {
    await later.click().catch(() => {});
    await wait(500);
  }
  const collapse = page.getByRole("button", { name: "Collapse", exact: true });
  for (let i = 0; i < 4; i++) {
    const b = collapse.first();
    if (!(await b.isVisible().catch(() => false))) break;
    await b.click({ timeout: 2000 }).catch(() => {});
    await wait(300);
  }
  await page.keyboard.press("Escape").catch(() => {});
}

// Remove a block by a text it contains (e.g. the sample-data notice).
async function hideByText(page, text, levels = 1) {
  await page
    .evaluate(
      ({ text, levels }) => {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let n;
        while ((n = walker.nextNode())) {
          if (n.textContent.includes(text)) {
            let el = n.parentElement;
            for (let i = 0; i < levels && el.parentElement; i++) el = el.parentElement;
            el.style.display = "none";
            return;
          }
        }
      },
      { text, levels },
    )
    .catch(() => {});
}

// Hide the card that holds `text`: climb from the text until the block also
// contains `cardText` (its heading).
async function hideCard(page, text, cardText, up = 0) {
  await page
    .evaluate(
      ({ text, cardText, up }) => {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let n;
        while ((n = walker.nextNode())) {
          if (n.textContent.trim() === text || (text.length > 6 && n.textContent.includes(text))) {
            let el = n.parentElement;
            while (el && !el.textContent.includes(cardText)) el = el.parentElement;
            for (let i = 0; i < up && el && el.parentElement; i++) el = el.parentElement;
            // never hide a whole page region by accident
            if (el && el.getBoundingClientRect().height < 900 && el !== document.body) {
              el.style.display = "none";
              return;
            }
          }
        }
      },
      { text, cardText, up },
    )
    .catch(() => {});
}

async function collapseInsights(page) {
  const b = page.getByRole("button", { name: /collapse insights/i });
  if (await b.isVisible().catch(() => false)) {
    await b.click().catch(() => {});
    await wait(600);
  }
}

async function shot(page, slot) {
  await page.mouse.move(5, 5);
  await page.evaluate(() => document.activeElement && document.activeElement.blur && document.activeElement.blur()).catch(() => {});
  await wait(300);
  await page.screenshot({ path: join(OUT, `${slot}.png`) });
  console.log(`  wrote captures/${slot}.png`);
}

// Convert a Playwright .webm to an H.264 mp4, dropping `skip` seconds of load time.
function toMp4(webm, slot, skip, dur) {
  const out = join(OUT, `${slot}.mp4`);
  execFileSync("ffmpeg", [
    "-y", "-loglevel", "error", "-ss", String(skip), "-i", webm, "-t", String(dur),
    "-vf", `crop=${DESK.width}:${DESK.height}:0:0,scale=1920:1080:flags=lanczos,fps=30,format=yuv420p`,
    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-an", "-movflags", "+faststart", out,
  ]);
  console.log(`  wrote captures/${slot}.mp4`);
}

async function record(slot, opts, fn, { dur = 6 } = {}) {
  rmSync(TMP, { recursive: true, force: true });
  mkdirSync(TMP, { recursive: true });
  const ctx = await newContext({ ...opts, record: true });
  const page = await ctx.newPage();
  const t0 = Date.now();
  let markAt = 0;
  // fn calls mark() when the page is ready and the motion starts
  await fn(page, () => {
    markAt = (Date.now() - t0) / 1000;
  });
  const video = page.video();
  await ctx.close();
  const webm = await video.path();
  toMp4(webm, slot, Math.max(0, markAt - 0.3), dur);
}

async function still(slot, opts, fn) {
  const ctx = await newContext(opts);
  const page = await ctx.newPage();
  try {
    await fn(page);
    await shot(page, slot);
  } finally {
    await ctx.close();
  }
}

const go = async (page, route, ms) => {
  await page.goto(`${BASE}${route}`, { waitUntil: "domcontentloaded" });
  await settle(page, ms);
};

async function smoothScroll(page, sel, dy, steps = 30, ms = 40) {
  for (let i = 0; i < steps; i++) {
    if (sel) await page.locator(sel).first().evaluate((el, d) => el.scrollBy(0, d), dy / steps).catch(() => {});
    else await page.mouse.wheel(0, dy / steps);
    await wait(ms);
  }
}

async function glide(page, x0, y0, x1, y1, steps = 25) {
  await page.mouse.move(x0, y0);
  await page.mouse.move(x1, y1, { steps });
}

// ------------------------------------------------------------------ shots
const SHOTS = {};

const proj = (p) => ({ id: p.id, name: p.name });

// Scroll the app's main scroller so `sel` sits `top` px below the header.
async function scrollTo(page, sel, top = 70) {
  const loc =
    sel instanceof RegExp ? page.getByText(sel) : sel.startsWith("text=") ? page.getByText(sel.slice(5)) : page.locator(sel);
  await loc
    .filter({ visible: true })
    .first()
    .evaluate((el, top) => {
      el.scrollIntoView({ block: "start" });
      let sc = el.parentElement;
      while (sc && !(sc.scrollHeight > sc.clientHeight + 4 && /(auto|scroll)/.test(getComputedStyle(sc).overflowY))) sc = sc.parentElement;
      const dy = el.getBoundingClientRect().top - top;
      if (sc) sc.scrollBy(0, dy);
      else window.scrollBy(0, dy);
    }, top)
    .catch((e) => console.log(`  scrollTo(${sel}) failed: ${e.message.split("\n")[0]}`));
  await wait(500);
}

// --- OWNER
SHOTS["owner-portfolio"] = () =>
  still("owner-portfolio", { project: proj(P.school) }, async (page) => {
    await go(page, "/projects");
    await hideByText(page, "of these are sample projects", 1);
    await page.getByRole("button", { name: /^value$/i }).first().click().catch(() => {});
    await settle(page, 2500);
    await scrollTo(page, "text=TOTAL PROJECTS", 70);
  });

SHOTS["owner-cashflow"] = () =>
  still("owner-cashflow", { project: proj(P.school) }, async (page) => {
    await go(page, "/5d");
    await page.getByRole("button", { name: /generate cash flow/i }).first().click().catch(() => {});
    await settle(page, 2500);
    await scrollTo(page, "text=Cash-flow forecast", 120);
    await wait(1200);
  });

SHOTS["owner-cost-budget"] = () =>
  still("owner-cost-budget", { project: proj(P.school) }, async (page) => {
    await go(page, "/cost-control");
  });

SHOTS["owner-approvals"] = () =>
  still("owner-approvals", { project: proj(P.school) }, async (page) => {
    // A submitted change order waiting for the owner's decision.
    await go(page, "/changeorders");
    await collapseInsights(page);
    await page.getByText("Rainwater harvesting tank").first().click();
    await settle(page, 1500);
    // pick the BOQ the change applies to, which arms the Approve button
    const sel = page.locator("select").filter({ hasText: "Select BOQ" }).first();
    const opts = await sel.locator("option").evaluateAll((os) => os.map((o) => o.value).filter(Boolean));
    if (opts.length) await sel.selectOption(opts[opts.length - 1]);
    await wait(800);
  });

// --- PROJECT MANAGER
// Scroll the widest horizontal scroller on the page (a Gantt timeline) by dx, smoothly.
async function hScroll(page, dx, ms) {
  const steps = Math.round(ms / 33);
  for (let i = 0; i < steps; i++) {
    await page.evaluate((d) => {
      const els = [...document.querySelectorAll("main *")].filter(
        (e) => e.scrollWidth > e.clientWidth + 40 && /(auto|scroll)/.test(getComputedStyle(e).overflowX),
      );
      els.sort((a, b) => b.clientWidth * b.clientHeight - a.clientWidth * a.clientHeight);
      if (els[0]) els[0].scrollLeft += d;
    }, dx / steps);
    await wait(33);
  }
}

SHOTS["pm-schedule-gantt"] = () =>
  record("pm-schedule-gantt", { project: proj(P.road) }, async (page, mark) => {
    await go(page, "/schedule");
    await page.getByText("Programme — City road, Faisalabad").first().click();
    await settle(page, 2000);
    await page.getByRole("button", { name: /critical path/i }).first().click();
    await settle(page, 1500);
    await scrollTo(page, "text=Critical Path: ", 40);
    await page.mouse.move(1300, 700);
    await wait(800);
    mark();
    await wait(500);
    await page.mouse.move(1000, 640, { steps: 20 });
    await hScroll(page, 1500, 4200);
    await page.mouse.move(1250, 760, { steps: 15 });
    await wait(900);
  }, { dur: 6 });

// --- QS / ESTIMATOR
async function boqId(projectId, re) {
  const list = items(await api(`/v1/boq/boqs/?project_id=${projectId}`, {}, session.token));
  return (list.find((b) => re.test(b.name)) || list[0]).id;
}

SHOTS["qs-boq-editor"] = () =>
  record("qs-boq-editor", { project: proj(P.lahore) }, async (page, mark) => {
    const id = await boqId(P.lahore.id, /^(?!.*Budget)/);
    await go(page, `/boq/${id}`, 2500);
    await page.mouse.move(1100, 760);
    await wait(600);
    mark();
    await wait(600);
    // glide down the bill: preliminaries, earthwork, MRS chapter 6 concrete ...
    for (let i = 0; i < 70; i++) {
      await page.mouse.wheel(0, 18);
      await wait(33);
    }
    await page.mouse.move(1000, 640, { steps: 12 });
    await wait(600);
    for (let i = 0; i < 40; i++) {
      await page.mouse.wheel(0, 16);
      await wait(33);
    }
    await wait(1200);
  }, { dur: 6 });

// BIM takeoff on the Lahore house IFC model: filter + quantities panel, orbit the model.
SHOTS["qs-takeoff"] = () =>
  record("qs-takeoff", { project: proj(P.lahore) }, async (page, mark) => {
    await go(page, "/bim", 9000);
    await hideCard(page, "BIM converters", "Show details", 0);
    await wait(2500);
    await page.mouse.move(680, 520);
    mark();
    await wait(500);
    // orbit: drag across the empty sky of the viewport
    await page.mouse.down();
    await page.mouse.move(930, 500, { steps: 60 });
    await page.mouse.up();
    await wait(300);
    for (let i = 0; i < 20; i++) {
      await page.mouse.wheel(0, -30);
      await wait(40);
    }
    await page.getByText("Wall", { exact: true }).first().hover().catch(() => {});
    await wait(1500);
  }, { dur: 5 });

// AI cost match: lines of the Lahore house BOQ matched against the loaded
// Pakistan rate books. The run is created through the API (same body the
// "Match a bill" composer sends); the project's province (Punjab) ranks the
// Punjab MRS book first.
const MATCH_LINES = [
  ["06.06", "Reinforced cement concrete 1:2:4 in roof slabs", "m3", "58"],
  ["06.01", "Plain cement concrete 1:4:8 under foundations", "m3", "18"],
  ["07.02", "First class brick masonry in cement sand mortar 1:6 in superstructure", "m3", "135"],
  ["06.11", "Steel reinforcement Grade 60 deformed bars, cut, bent and fixed", "t", "15"],
  ["03.01", "Excavation for foundations in ordinary soil, lift up to 1.5 m", "m3", "165"],
];
const MATCH_RUN_NAME = "10-marla house BOQ vs Punjab MRS 2-2026, Lahore";

SHOTS["qs-cost-match"] = () =>
  still("qs-cost-match", { project: proj(P.lahore) }, async (page) => {
    const runs = items(await api(`/v1/cost-match/runs/?project_id=${P.lahore.id}`, {}, session.token));
    for (const r of runs) await api(`/v1/cost-match/runs/${r.id}`, { method: "DELETE" }, session.token).catch(() => {});
    await api(
      "/v1/cost-match/runs/",
      {
        method: "POST",
        body: JSON.stringify({
          project_id: P.lahore.id,
          name: MATCH_RUN_NAME,
          source_label: "Bill of quantities, House on a 10-marla plot, Lahore",
          cost_source: "rate_book",
          region: "PK",
          source_locale: "en",
          lines: MATCH_LINES.map(([ref, description, unit, quantity]) => ({ source_ref: ref, description, unit, quantity })),
        }),
      },
      session.token,
    );
    await go(page, "/cost-match", 1500);
    await collapseInsights(page);
    await hideCard(page, "Connects with:", "Connects with:");
    await page.getByText(MATCH_RUN_NAME).first().click().catch(() => {});
    await settle(page, 1500);
    await page.getByRole("button", { name: /every line/i }).first().click().catch(() => {});
    await settle(page, 1500);
    // the QS confirms the first suggestion: it shows as "Priced against"
    await page.getByRole("button", { name: "Confirm", exact: true }).first().click().catch(() => {});
    await settle(page, 1500);
    await scrollTo(page, `text=${MATCH_RUN_NAME}`, 70);
  });

// FBR s.153(1)(c) income tax withheld on a subcontractor payment: the
// Withholding Tax page works out PA-003 of the Lahore house subcontract
// (PKR 1,054,661, Ravi Homes, a company on the Active Taxpayer List: 7.5%).
// (The interim payment certificate's own s.153 line is held on these demo
// certificates, see CAPTURE-LIST.md, so the page is filmed instead.)
SHOTS["accounts-withholding"] = () =>
  still("accounts-withholding", { project: proj(P.lahore) }, async (page) => {
    // Ravi Homes (the Lahore house subcontractor) checked on the FBR Active
    // Taxpayer List: recorded once as its standing under the s.153 scheme.
    const regimes = items(await api("/v1/tax-withholding/regimes/", {}, session.token));
    let pk = regimes.find((r) => r.scheme_code === "PK_ITO_153_CONTRACTS");
    if (!pk) {
      await api("/v1/tax-withholding/regimes/seed", { method: "POST" }, session.token).catch(() => {});
      pk = items(await api("/v1/tax-withholding/regimes/", {}, session.token)).find((r) => r.scheme_code === "PK_ITO_153_CONTRACTS");
    }
    const subs = items(await api("/v1/subcontractors/subcontractors/?limit=100", {}, session.token));
    const ravi = subs.find((x) => /Ravi Homes/.test(x.legal_name));
    const standings = items(await api("/v1/tax-withholding/party-status/", {}, session.token));
    if (pk && ravi && !standings.some((x) => x.party_id === ravi.id && x.regime_id === pk.id)) {
      await api(
        "/v1/tax-withholding/party-status/",
        {
          method: "POST",
          body: JSON.stringify({
            party_id: ravi.id,
            party_type: "subcontractor",
            party_name: "Ravi Homes",
            regime_id: pk.id,
            band_code: "COMPANY_ATL",
            verification_reference: "ATL check, NTN on record",
            verified_on: "2026-07-01",
            valid_from: "2026-07-01",
            valid_to: "2027-06-30",
            status: "active",
          }),
        },
        session.token,
      );
    }
    await go(page, "/tax-withholding", 1500);
    await collapseInsights(page);
    await hideCard(page, "How construction tax withholding works, and what it protects", "Connects with");
    const install = page.getByRole("button", { name: /install the shipped schemes/i }).first();
    if (await install.isVisible().catch(() => false)) {
      await install.click();
      await page.waitForLoadState("networkidle", { timeout: 20000 }).catch(() => {});
      await wait(2500);
    }
    // keep only the Pakistan scheme card: hide the DE/GB/IE/IT/US cards
    await page
      .evaluate(() => {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        const ends = [];
        let n;
        while ((n = walker.nextNode())) if (/^Currency [A-Z]{3}\./.test(n.textContent.trim())) ends.push(n.parentElement);
        for (const e of ends) {
          let card = e;
          while (card && !(card.textContent.includes("BAND") || card.textContent.includes("Band")) ) card = card.parentElement;
          if (card && !card.textContent.includes("153") && card.getBoundingClientRect().height < 700) card.style.display = "none";
        }
      })
      .catch(() => {});
    await wait(500);
    // work out the deduction on PA-003 of the Lahore house subcontract (PKR 1,054,661, company on the ATL)
    const selects = page.locator("main select");
    const scheme = selects.filter({ hasText: "Pick a scheme" }).first();
    const schemeOpt = await scheme.locator("option").evaluateAll((os) => (os.find((o) => /153/.test(o.textContent)) || {}).value);
    if (schemeOpt) await scheme.selectOption(schemeOpt);
    await wait(800);
    await page.getByLabel(/gross amount/i).first().fill("1054661").catch((e) => console.log("  gross:", e.message.split("\n")[0]));
    await page.getByLabel(/^currency$/i).first().fill("PKR").catch(() => {});
    const band = selects.filter({ hasText: "Let the scheme decide" }).first();
    const bandOpt = await band.locator("option").evaluateAll((os) => (os.find((o) => /^Company on the Active Taxpayer List/.test(o.textContent.trim())) || {}).value);
    if (bandOpt) await band.selectOption(bandOpt);
    const party = selects.filter({ hasText: "No standing on record" }).first();
    const partyOpt = await party.locator("option").evaluateAll((os) => (os.find((o) => /Ravi Homes/.test(o.textContent)) || {}).value);
    if (partyOpt) await party.selectOption(partyOpt);
    await wait(500);
    await page.getByRole("button", { name: /work out the deduction/i }).first().click().catch((e) => console.log("  work out:", e.message.split("\n")[0]));
    await page.waitForLoadState("networkidle", { timeout: 20000 }).catch(() => {});
    await wait(2000);
    await page.mouse.move(5, 5);
    // the empty "verifications running out" block sits between the preview and the schemes
    await hideCard(page, "Verifications running out", "Nothing lapsing soon");
    await wait(300);
    await scrollTo(page, "text=Schemes and the rates they apply", 90);
  });

// The BOQ checked against the Pakistan rule set (not in the film since the
// AI cost match scene came back; kept for reference).
SHOTS["qs-validation"] = () =>
  still("qs-validation", { project: { ...proj(P.lahore) } }, async (page) => {
    await go(page, "/validation");
    const sel = page.locator("select").filter({ hasText: "Bill of Quantities" }).first();
    const opts = await sel.locator("option").evaluateAll((os) => os.map((o) => `${o.value}|${o.textContent}`));
    const main = opts.find((o) => /Lahore/.test(o) && !/Budget/.test(o));
    if (main) await sel.selectOption(main.split("|")[0]);
    await wait(800);
    await page.getByRole("button", { name: /run validation/i }).first().click().catch(() => {});
    await settle(page, 2500);
  });

// --- SITE ENGINEER
SHOTS["site-daily-diary"] = () =>
  still("site-daily-diary", { project: proj(P.bhu) }, async (page) => {
    await go(page, `/projects/${P.bhu.id}/daily-diary`);
    await collapseInsights(page);
    // open the latest filled day (an "Open" diary in the month calendar)
    await page.getByText("Open", { exact: true }).last().click();
    await settle(page, 2000);
  });

// The same app at phone size on site (the /field SMS-link shell needs a field
// session minted by an SMS provider, so the responsive app is filmed instead).
SHOTS["site-mobile-field"] = () =>
  still("site-mobile-field", { phone: true, project: proj(P.bhu) }, async (page) => {
    await go(page, `/projects/${P.bhu.id}/daily-diary`);
    await collapseInsights(page);
    await page.getByText("Open", { exact: true }).last().click().catch(() => {});
    await settle(page, 2000);
  });

// --- PROCUREMENT & ACCOUNTS
SHOTS["proc-purchase-orders"] = () =>
  still("proc-purchase-orders", { project: proj(P.road) }, async (page) => {
    await go(page, "/procurement");
    await collapseInsights(page);
  });

SHOTS["proc-subcontractors"] = () =>
  still("proc-subcontractors", { project: proj(P.road) }, async (page) => {
    await go(page, "/subcontractors");
    await collapseInsights(page);
    await hideCard(page, "How the subcontractor register fits together", "Connects with");
    // placeholder "Demo Structures Ltd" rows left by a test seeder are not part of the Pakistan story
    await page
      .evaluate(() => {
        for (const tr of document.querySelectorAll("tr")) if (tr.textContent.includes("Demo Structures Ltd")) tr.style.display = "none";
      })
      .catch(() => {});
  });

// Provincial sales tax on services: Punjab (PRA 16%), then Sindh (SRB 15%).
// (ITO s.153 withholding rows exist in the backend but are only drawn on the
// Turkish-style payment certificate panel, which Pakistan projects do not show.)
SHOTS["accounts-sales-tax"] = () =>
  record("accounts-sales-tax", { project: proj(P.road) }, async (page, mark) => {
    await go(page, "/tax-rates");
    const country = page.locator("select").filter({ hasText: "Pick a country" }).first();
    await country.selectOption("PK");
    await settle(page, 1000);
    const region = page.locator("select").filter({ hasText: "Not chosen yet" }).first();
    await region.selectOption("PK-PB");
    await settle(page, 1200);
    await hideCard(page, "How a tax rate is worked out, and when it declines to give one", "Connects with");
    await wait(600);
    mark();
    await wait(2300);
    await region.selectOption("PK-SD");
    await wait(2500);
  }, { dur: 4.6 });

// --- ANYWHERE
// The site day sheet with the network cut: it keeps the day on the device and
// sends it when the signal is back. (No PrimeCrest Desktop build is filmed.)
SHOTS["offline-field-time"] = () =>
  still("offline-field-time", { project: proj(P.bhu) }, async (page) => {
    await go(page, "/field-time", 2000);
    await collapseInsights(page);
    await hideCard(page, "How Field Time fits together", "Connects with");
    await page.getByPlaceholder("What happened on site, in one line").fill("Slab shuttering, ground floor, 14 masons and 22 labour").catch(() => {});
    await page.context().setOffline(true);
    await page.evaluate(() => window.dispatchEvent(new Event("offline"))).catch(() => {});
    await wait(2500);
    await page.addStyleTag({ content: CLEAN_CSS }).catch(() => {});
    await page.evaluate(() => document.activeElement && document.activeElement.blur()).catch(() => {});
    await scrollTo(page, "text=Record a day on site", 150);
  });

SHOTS["lang-urdu"] = () =>
  still("lang-urdu", { lang: "ur", project: proj(P.school) }, async (page) => {
    await go(page, "/dashboard", 2500);
    // the release-notes strip is noise ("cases for your market" now shows Pakistan cases)
    await hideCard(page, "v18.9.0", "tour");
    // the Urdu locale still carries the upstream "#1 open-source construction ERP" badge
    // (dashboard.open_source_badge); PrimeCrest is proprietary, so it stays out of the film
    await page
      .evaluate(() => {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let n;
        while ((n = walker.nextNode())) {
          if (n.textContent.includes("اوپن سورس")) {
            const el = n.parentElement;
            const chip = el.parentElement && el.parentElement.children.length <= 3 ? el.parentElement : el;
            chip.style.display = "none";
          }
        }
      })
      .catch(() => {});
    await wait(500);
  });

SHOTS["site-punch-list"] = () =>
  still("site-punch-list", { project: proj(P.bhu) }, async (page) => {
    await go(page, "/punchlist");
    await collapseInsights(page);
  });

SHOTS["site-rfi-inspections"] = () =>
  still("site-rfi-inspections", { project: proj(P.school) }, async (page) => {
    await go(page, "/rfi");
    await collapseInsights(page);
    await hideCard(page, "How RFIs work and connect", "Connects with");
    await page.getByText("Concrete grade in sea-facing columns").first().click();
    await settle(page, 1500);
  });

SHOTS["pm-risk-register"] = () =>
  still("pm-risk-register", { project: proj(P.school) }, async (page) => {
    await go(page, "/risks");
    await collapseInsights(page);
    // keep the coloured heat map, drop the second (numeric) 5x5 matrix so the register rows follow it
    await hideCard(page, "Low (1-5)", "Risk Matrix");
    await scrollTo(page, "text=Risk Matrix", 75);
  });

SHOTS["pm-change-orders"] = () =>
  still("pm-change-orders", { project: proj(P.school) }, async (page) => {
    await go(page, "/changeorders");
    await collapseInsights(page);
  });

// ------------------------------------------------------------------ run
(async () => {
  session = await login();
  P = await projects(session.token);
  console.log("projects:", P.all.map((p) => `${p.name} (${p.id})`).join(" | "));
  browser = await chromium.launch({ executablePath: chromiumPath() });
  try {
    for (const [slot, fn] of Object.entries(SHOTS)) {
      if (!want(slot)) continue;
      console.log(slot);
      try {
        await fn();
      } catch (e) {
        console.error(`  FAILED ${slot}: ${e.message}`);
      }
    }
  } finally {
    await browser.close();
    if (existsSync(TMP)) rmSync(TMP, { recursive: true, force: true });
  }
})();
