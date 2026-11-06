#!/usr/bin/env node
/**
 * QA crawl: log in, visit every route in the frontend router, record problems.
 *
 * Routes come from frontend/src/app/App.tsx (`path="..."`) plus module manifests
 * (frontend/src/modules/<name>/manifest.ts, `path: '...'`). Parameterised segments are
 * filled from live API data (first project / first BOQ etc.); routes whose params cannot be
 * filled are visited with a placeholder id and flagged `param-guess`.
 *
 * Per route it records: console errors, page errors (uncaught exceptions), failed
 * requests (network failure or HTTP >= 400 on /api), error-boundary / not-found / blank
 * render, final URL (redirects), and a full-page screenshot.
 *
 * Usage (from repo root; needs the stack from scripts/dev/run-local.* running):
 *   node scripts/dev/qa-crawl.mjs [--base http://127.0.0.1:5810] [--api http://127.0.0.1:8810]
 *        [--out <dir>] [--only <substring>] [--limit N] [--wait 2500]
 * Env: QA_EMAIL / QA_PASSWORD (default demo@openconstructionerp.com / DemoPass1234!)
 * Output: <out>/results.json, <out>/summary.md, <out>/<slug>.png
 */
import { readFileSync, readdirSync, existsSync, mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const here = path.dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, a, i, arr) => {
    if (a.startsWith('--')) acc.push([a.slice(2), arr[i + 1] && !arr[i + 1].startsWith('--') ? arr[i + 1] : 'true']);
    return acc;
  }, []),
);
const ROOT = path.resolve(args.root ?? path.join(here, '..', '..'));
const FRONTEND = path.join(ROOT, 'frontend');
const BASE = args.base ?? 'http://127.0.0.1:5810';
const API = args.api ?? 'http://127.0.0.1:8810';
const OUT = path.resolve(args.out ?? path.join(here, '.local', 'qa-crawl'));
const WAIT = Number(args.wait ?? 2500);
const EMAIL = process.env.QA_EMAIL ?? 'demo@openconstructionerp.com';
const PASSWORD = process.env.QA_PASSWORD ?? 'DemoPass1234!';

// Resolve playwright from frontend/node_modules (or the main checkout as a fallback).
const req = createRequire(path.join(FRONTEND, 'package.json'));
let chromium;
for (const cand of [FRONTEND, 'H:/PrimeCrestConstMgmt/frontend', 'H:/PrimeCrestConstMgmt']) {
  try {
    ({ chromium } = createRequire(path.join(cand, 'package.json'))('playwright'));
    break;
  } catch {}
}
if (!chromium) ({ chromium } = req('@playwright/test'));

// ── Route discovery ───────────────────────────────────────────────────────────
function discoverRoutes() {
  const set = new Map();
  const app = readFileSync(path.join(FRONTEND, 'src/app/App.tsx'), 'utf8');
  for (const m of app.matchAll(/<Route[^>]*?\spath="([^"]+)"/gs)) set.set(m[1], 'App.tsx');
  const modDir = path.join(FRONTEND, 'src/modules');
  for (const d of readdirSync(modDir)) {
    const mf = path.join(modDir, d, 'manifest.ts');
    if (!existsSync(mf)) continue;
    for (const m of readFileSync(mf, 'utf8').matchAll(/path:\s*['"`](\/[^'"`]*)['"`]/g)) set.set(m[1], `modules/${d}`);
  }
  set.delete('*');
  return [...set.entries()].map(([p, src]) => ({ pattern: p, source: src }));
}

// ── Param filling from live data ──────────────────────────────────────────────
async function apiGet(token, p) {
  try {
    const r = await fetch(API + p, { headers: { Authorization: `Bearer ${token}` } });
    if (!r.ok) return null;
    return await r.json();
  } catch {
    return null;
  }
}
const firstId = (d) => {
  const arr = Array.isArray(d) ? d : d?.items ?? d?.results ?? d?.data ?? null;
  return Array.isArray(arr) && arr.length ? arr[0].id ?? arr[0].uuid ?? null : null;
};

async function buildParams(token) {
  const p = {};
  p.projectId = p.id = firstId(await apiGet(token, '/api/v1/projects/?limit=5')) ?? firstId(await apiGet(token, '/api/v1/projects?limit=5'));
  if (p.projectId) {
    p.boqId = firstId(await apiGet(token, `/api/v1/boq/boqs/?project_id=${p.projectId}`)) ?? firstId(await apiGet(token, `/api/v1/boq/?project_id=${p.projectId}`));
  }
  return p;
}

function fill(pattern, params) {
  let guessed = false;
  const url = pattern
    .replace(/\/\*$/, '')
    .replace(/:(\w+)\??/g, (_, name) => {
      const v = params[name] ?? (/project/i.test(name) ? params.projectId : /boq/i.test(name) ? params.boqId : null);
      if (v) return encodeURIComponent(v);
      guessed = true;
      return name === 'token' ? 'qa-invalid-token' : '00000000-0000-0000-0000-000000000000';
    });
  return { url: url || '/', guessed };
}

const slug = (s) => (s.replace(/^\//, '').replace(/[^a-zA-Z0-9]+/g, '_') || 'root').slice(0, 120);

// ── Main ──────────────────────────────────────────────────────────────────────
mkdirSync(OUT, { recursive: true });
// If the bundled browser revision is missing (offline box), fall back to QA_CHROMIUM or the
// newest chromium-* build already in the ms-playwright cache.
async function launch() {
  try {
    return await chromium.launch({ executablePath: process.env.QA_CHROMIUM || undefined });
  } catch (e) {
    const cache = process.env.PLAYWRIGHT_BROWSERS_PATH || path.join(process.env.LOCALAPPDATA ?? path.join(process.env.HOME ?? '', '.cache'), 'ms-playwright');
    const builds = existsSync(cache) ? readdirSync(cache).filter((d) => /^chromium-\d+$/.test(d)).sort().reverse() : [];
    for (const b of builds) {
      for (const exe of ['chrome-win64/chrome.exe', 'chrome-win/chrome.exe', 'chrome-linux64/chrome', 'chrome-linux/chrome']) {
        const p = path.join(cache, b, exe);
        if (existsSync(p)) {
          console.warn(`bundled browser missing; using ${p}`);
          return chromium.launch({ executablePath: p });
        }
      }
    }
    throw e;
  }
}
const browser = await launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, ignoreHTTPSErrors: true });
const page = await ctx.newPage();

// Login through the UI so the app stores its token the way it normally does.
await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded', timeout: 600000 });
await page.locator('#login-email').waitFor({ timeout: 600000 });
await page.fill('#login-email', EMAIL);
await page.fill('input[type="password"]', PASSWORD);
await Promise.all([
  page.waitForURL((u) => !u.pathname.startsWith('/login'), { timeout: 60000 }).catch(() => null),
  page.locator('form button[type="submit"]').first().click(),
]);
await page.waitForTimeout(2000);
const loginOk = !new URL(page.url()).pathname.startsWith('/login');
// The SPA may keep its token in memory or an httpOnly cookie, so get a separate API token
// for param discovery straight from the login endpoint.
let token = null;
try {
  const r = await fetch(`${API}/api/v1/users/auth/login/`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ email: EMAIL, password: PASSWORD }),
  });
  token = r.ok ? (await r.json()).access_token ?? null : null;
} catch {}
console.log(`login ${loginOk ? 'OK' : 'FAILED'} -> ${page.url()} token=${token ? 'yes' : 'no'}`);
if (!loginOk) {
  await page.screenshot({ path: path.join(OUT, 'login-failed.png') });
  throw new Error('UI login failed; see login-failed.png');
}

const params = token ? await buildParams(token) : {};
console.log('params', params);

let routes = discoverRoutes();
if (args.only) routes = routes.filter((r) => r.pattern.includes(args.only));
if (args.limit) routes = routes.slice(0, Number(args.limit));
console.log(`${routes.length} routes`);

const results = [];
let cur = null;
page.on('console', (m) => {
  if (cur && m.type() === 'error') cur.consoleErrors.push(m.text().slice(0, 500));
});
page.on('pageerror', (e) => cur && cur.pageErrors.push(String(e?.message ?? e).slice(0, 500)));
page.on('requestfailed', (r) => {
  if (!cur) return;
  const f = r.failure()?.errorText ?? '';
  if (/ERR_ABORTED/.test(f)) return; // navigations / cancelled fetches
  cur.failedRequests.push(`${r.method()} ${r.url()} :: ${f}`);
});
page.on('response', (r) => {
  if (cur && r.status() >= 400 && r.url().includes('/api/'))
    cur.failedRequests.push(`${r.request().method()} ${r.url().replace(BASE, '')} -> ${r.status()}`);
});

for (const [i, r] of routes.entries()) {
  const { url, guessed } = fill(r.pattern, params);
  cur = { ...r, url, paramGuess: guessed, consoleErrors: [], pageErrors: [], failedRequests: [], status: 'ok', notes: [] };
  const t0 = Date.now();
  try {
    await page.goto(BASE + url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => cur.notes.push('networkidle timeout'));
    await page.waitForTimeout(WAIT);
    cur.finalUrl = new URL(page.url()).pathname;
    const info = await page.evaluate(() => {
      const txt = document.body?.innerText ?? '';
      return {
        len: txt.trim().length,
        errorBoundary: /Something went wrong/i.test(txt),
        notFound: /page not found|404/i.test(txt) && txt.length < 3000,
        snippet: txt.replace(/\s+/g, ' ').slice(0, 300),
      };
    });
    cur.textLength = info.len;
    if (info.errorBoundary) cur.status = 'error-boundary';
    else if (info.len < 20) cur.status = 'blank';
    else if (info.notFound) cur.status = 'not-found';
    else if (cur.finalUrl.startsWith('/login')) cur.status = 'redirect-login';
    if (cur.status !== 'ok') cur.snippet = info.snippet;
    await page.screenshot({ path: path.join(OUT, `${String(i).padStart(3, '0')}_${slug(url)}.png`), fullPage: false });
  } catch (e) {
    cur.status = 'nav-error';
    cur.notes.push(String(e?.message ?? e).split('\n')[0]);
  }
  cur.ms = Date.now() - t0;
  const bad = cur.status !== 'ok' || cur.pageErrors.length || cur.failedRequests.length || cur.consoleErrors.length;
  console.log(`[${i + 1}/${routes.length}] ${bad ? 'XX' : 'ok'} ${url} ${cur.status} ce=${cur.consoleErrors.length} pe=${cur.pageErrors.length} fr=${cur.failedRequests.length}`);
  results.push(cur);
  cur = null;
}
await browser.close();

writeFileSync(path.join(OUT, 'results.json'), JSON.stringify({ base: BASE, loginOk, params, results }, null, 2));
const bad = results.filter((r) => r.status !== 'ok' || r.pageErrors.length || r.failedRequests.length || r.consoleErrors.length);
const lines = [`# QA crawl ${new Date().toISOString()}`, `login: ${loginOk}`, `routes: ${results.length}, with problems: ${bad.length}`, ''];
for (const r of bad) {
  lines.push(`## ${r.pattern} (${r.source}) -> ${r.url}${r.paramGuess ? ' [param-guess]' : ''}  status=${r.status}`);
  if (r.snippet) lines.push(`- text: ${r.snippet}`);
  for (const x of [...new Set(r.pageErrors)]) lines.push(`- uncaught: ${x}`);
  for (const x of [...new Set(r.failedRequests)]) lines.push(`- request: ${x}`);
  for (const x of [...new Set(r.consoleErrors)].slice(0, 5)) lines.push(`- console: ${x}`);
}
writeFileSync(path.join(OUT, 'summary.md'), lines.join('\n'));
console.log(`done: ${bad.length}/${results.length} routes with problems -> ${OUT}`);
