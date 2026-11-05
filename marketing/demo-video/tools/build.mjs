#!/usr/bin/env node
// Builds the PrimeCrest demo film from scenes.json.
//
//   node tools/build.mjs
//
// Writes index.html, compositions/feat-<id>.html and compositions/captions.html.
// For every feature scene it looks in captures/ for <capture>.mp4, .webm, .png,
// .jpg or .webp (a "kind": "video" hint only changes the fallback card text).
// A found file is written into the scene as a literal <video>/<img> src
// (HyperFrames extracts video frames at compile time, so a variable-bound src
// would not render). A missing file renders the branded fallback card instead,
// so the film always checks and renders clean.
//
// hook.html, brand.html and cta.html are hand-written and not touched here.

import { existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const cfg = JSON.parse(readFileSync(join(ROOT, "scenes.json"), "utf8"));
const W = cfg.width;
const H = cfg.height;

const esc = (s) =>
  String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
// *accent* -> <em>accent</em>
const accent = (s) => esc(s).replace(/\*([^*]+)\*/g, "<em>$1</em>");
const r2 = (n) => Math.round(n * 1000) / 1000;

const GSAP = '<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>';

function findCapture(name) {
  const order = [
    ["mp4", "video"],
    ["webm", "video"],
    ["png", "image"],
    ["jpg", "image"],
    ["jpeg", "image"],
    ["webp", "image"],
  ];
  for (const [ext, kind] of order) {
    const rel = `captures/${name}.${ext}`;
    if (existsSync(join(ROOT, rel))) return { rel, kind };
  }
  return null;
}

// ---------------------------------------------------------------- feature scene
// Geometry (px, 1920x1080): window body 1408x792 (16:9) under a 40 px chrome bar.
const WIN = { x: 360, y: 36, w: 1408, chrome: 40, h: 792 };
const PHONE = { w: 372, h: 806, x: 960 - 186 + 120, y: 44 };

function featureScene(s, found) {
  const id = s.id;
  const dur = s.duration;
  const phone = s.frame === "phone";
  const intro = !!s.personaIntro;
  const t0 = intro ? 1.05 : 0.05; // window wipe start
  const [fx, fy] = s.focus || [0.5, 0.5];
  // callout box [x, y, w, h] as fractions of the screen body; defaults to a box around focus
  const [bx, by, bw, bh] = s.box || [fx - 0.19, fy - 0.16, 0.38, 0.32];
  const zoom = s.zoom || 1.1;
  const wantKind = s.kind === "video" ? "screen recording (.mp4)" : "screenshot (.png)";
  const ext = s.kind === "video" ? "mp4" : "png";

  let media;
  if (found && found.kind === "video") {
    media = `<video id="${id}-media" class="clip media" src="${found.rel}" muted playsinline data-start="0" data-duration="${dur}" data-track-index="1"></video>`;
  } else if (found) {
    media = `<img id="${id}-media" class="clip media" src="${found.rel}" alt="" data-start="0" data-duration="${dur}" data-track-index="1" />`;
  } else {
    // Fallback card: clearly a placeholder, never a fake dashboard.
    const rows = phone ? 5 : 6;
    media = `<div class="fb${phone ? " fb-phone" : ""}">
          ${phone ? "" : `<div class="fb-side">${'<i></i>'.repeat(8)}</div>`}
          <div class="fb-main">
            <div class="fb-skel">${'<i></i>'.repeat(rows)}</div>
            <div class="fb-card">
              <div class="fb-k">CAPTURE PENDING · ${esc(wantKind)}</div>
              <div class="fb-file">captures/${esc(s.capture)}.${ext}</div>
              <div class="fb-route">${esc(s.route)}</div>
              ${phone ? "" : `<div class="fb-show">${esc(s.show)}</div>`}
            </div>
          </div>
        </div>`;
  }

  const route = esc(String(s.route).replace(/\{([^}]+)\}/g, "$1"));
  const winW = phone ? PHONE.w : WIN.w;
  const winH = phone ? PHONE.h : WIN.h + WIN.chrome;
  const winX = phone ? PHONE.x : WIN.x;
  const winY = phone ? PHONE.y : WIN.y;
  const bodyH = phone ? PHONE.h - 24 : WIN.h;

  const chrome = phone
    ? `<div class="notch"></div>`
    : `<div class="chrome"><b></b><b></b><b></b><span class="url">primecrest.pk${route.startsWith("/") ? route : ""}</span></div>`;

  return `<template>
  <style>
    #root { position: absolute; inset: 0; font-family: Inter, sans-serif; }
    #root .persona { position: absolute; left: 0; top: 0; width: ${WIN.x - 40}px; height: ${winY + winH}px;
      display: flex; align-items: center; justify-content: center; }
    #root .persona span { display: block; transform: rotate(-90deg); white-space: nowrap; color: #F2A900;
      font-family: "Archivo Black", sans-serif; font-size: 56px; letter-spacing: 0.04em; }
    #root .slam { position: absolute; left: 0; top: 330px; width: 1920px; text-align: center; color: #F2A900;
      font-family: "Archivo Black", sans-serif; font-size: 170px; line-height: 1; letter-spacing: -0.01em; }
    #root .slam small { display: block; color: #FFFFFF; font-family: Inter, sans-serif; font-weight: 700;
      font-size: 34px; letter-spacing: 0.3em; margin-bottom: 18px; }
    #root .win { position: absolute; left: ${winX}px; top: ${winY}px; width: ${winW}px; height: ${winH}px;
      border-radius: ${phone ? 46 : 14}px; overflow: hidden; background: ${phone ? "#05101F" : "#13315C"};
      box-shadow: 0 30px 70px rgba(0, 0, 0, 0.45); ${phone ? "padding: 12px;" : ""} }
    #root .chrome { height: ${WIN.chrome}px; display: flex; align-items: center; gap: 9px; padding: 0 18px; background: #13315C; }
    #root .chrome b { width: 13px; height: 13px; border-radius: 50%; background: #3E5C86; }
    #root .chrome .url { margin-left: 18px; flex: 1; max-width: 760px; height: 26px; border-radius: 6px; background: #0B2545;
      color: #C9D6E8; font-size: 16px; line-height: 26px; padding: 0 12px; white-space: nowrap; overflow: hidden; }
    #root .notch { position: absolute; left: 50%; top: 20px; width: 110px; height: 26px; margin-left: -55px; border-radius: 13px; background: #05101F; z-index: 3; }
    #root .body { position: relative; width: 100%; height: ${bodyH}px; overflow: hidden; background: #EEF1F5;
      ${phone ? "border-radius: 36px;" : ""} }
    #root .cam { position: absolute; inset: 0; transform-origin: ${fx * 100}% ${fy * 100}%; }
    #root .media { position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; object-position: top center; }
    #root .callout { position: absolute; left: ${r2(bx * 100)}%; top: ${r2(by * 100)}%; width: ${r2(bw * 100)}%; height: ${r2(bh * 100)}%;
      border: 5px solid #F2A900; border-radius: 10px; box-shadow: 0 0 0 4000px rgba(11, 37, 69, 0.18); }
    #root .tag { position: absolute; left: ${winX + winW - 24}px; top: ${winY + (phone ? 40 : WIN.chrome + 22)}px; transform-origin: 100% 50%;
      background: #F2A900; color: #0B2545; font-weight: 800; font-size: 28px; padding: 12px 22px; border-radius: 6px; white-space: nowrap; }
    #root .tag-in { display: block; }
    #root .wipe { position: absolute; left: 0; top: ${winY - 20}px; width: 150px; height: ${winH + 40}px; background: #F2A900; opacity: 0; }
    #root .fb { position: absolute; inset: 0; display: flex; background: #EEF1F5; }
    #root .fb-side { width: 230px; background: #DDE3EB; padding: 28px 22px; display: flex; flex-direction: column; gap: 18px; }
    #root .fb-side i { display: block; height: 16px; border-radius: 8px; background: #C3CCD8; }
    #root .fb-side i:first-child { height: 30px; background: #0B2545; opacity: 0.25; margin-bottom: 14px; }
    #root .fb-main { position: relative; flex: 1; padding: 34px 40px; }
    #root .fb-skel { display: flex; flex-direction: column; gap: 22px; opacity: 0.6; }
    #root .fb-skel i { display: block; height: 58px; border-radius: 10px; background: #DDE3EB; }
    #root .fb-skel i:first-child { height: 34px; width: 46%; }
    #root .fb-card { position: absolute; left: 70px; right: 70px; top: 50%; transform: translateY(-50%);
      background: #FFFFFF; border-left: 10px solid #F2A900; border-radius: 12px; padding: 36px 44px;
      box-shadow: 0 16px 40px rgba(11, 37, 69, 0.14); color: #0B2545; }
    #root .fb-k { font-weight: 800; font-size: 22px; letter-spacing: 0.14em; color: #8A6400; }
    #root .fb-file { font-family: "JetBrains Mono", monospace; font-weight: 700; font-size: 40px; margin-top: 14px; word-break: break-all; }
    #root .fb-route { font-family: "JetBrains Mono", monospace; font-size: 26px; margin-top: 10px; color: #3E5C86; }
    #root .fb-show { font-size: 26px; line-height: 1.35; margin-top: 18px; color: #22344F; }
    #root .fb-phone .fb-main { padding: 70px 22px 22px; }
    #root .fb-phone .fb-card { left: 18px; right: 18px; padding: 24px 22px; }
    #root .fb-phone .fb-k { font-size: 16px; letter-spacing: 0.08em; }
    #root .fb-phone .fb-file { font-size: 26px; }
    #root .fb-phone .fb-route { font-size: 22px; }
  </style>
  <div id="root" data-composition-id="${id}" data-width="${W}" data-height="${H}">
    <div id="${id}-persona" class="persona"><span id="${id}-persona-t">${esc(s.persona)}</span></div>
    ${intro ? `<div id="${id}-slam" class="slam"><small>${esc(s.kicker || "FOR THE")}</small><span id="${id}-slam-t">${esc(s.persona)}</span></div>` : ""}
    <div id="${id}-win" class="win" data-layout-allow-overflow>
      ${chrome}
      <div class="body">
        <div id="${id}-cam" class="cam">
          ${media}
          ${found ? `<div id="${id}-callout" class="callout"></div>` : ""}
        </div>
      </div>
    </div>
    <div id="${id}-wipe" class="wipe"></div>
    <div id="${id}-tag" class="tag"><span class="tag-in">${esc(s.tag)}</span></div>
  </div>
  <script>
    (function () {
      const tl = gsap.timeline({ paused: true });
      const q = (s) => "#${id}-" + s;
      const t0 = ${t0};
      ${
        intro
          ? `tl.fromTo(q("slam"), { opacity: 0, scale: 1.35 }, { opacity: 1, scale: 1, duration: 0.28, ease: "expo.out" }, 0.02);
      tl.to(q("slam"), { opacity: 0, x: -260, duration: 0.22, ease: "power3.in" }, 0.86);
      tl.fromTo(q("persona-t"), { opacity: 0, y: 120 }, { opacity: 1, y: 0, duration: 0.4, ease: "expo.out" }, 1.0);`
          : `tl.fromTo(q("persona-t"), { opacity: 1 }, { opacity: 1, duration: 0.01 }, 0);`
      }
      // amber slab sweeps across, the window is revealed behind its trailing edge
      tl.fromTo(q("wipe"), { x: ${winX - 160} }, { x: ${winX + winW + 20}, duration: 0.5, ease: "power3.inOut" }, t0);
      tl.fromTo(q("win"), { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.5, ease: "power3.inOut" }, t0);
      tl.set(q("wipe"), { opacity: 1 }, t0);
      tl.to(q("wipe"), { opacity: 0, duration: 0.08 }, t0 + 0.5);
      // slow push toward the feature
      tl.fromTo(q("cam"), { scale: 1 }, { scale: ${zoom}, duration: ${r2(dur - t0 - 0.2)}, ease: "sine.inOut" }, t0 + 0.2);
      // callout frames the part the caption talks about
      ${found ? `tl.fromTo(q("callout"), { opacity: 0, scale: 1.25 }, { opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)" }, t0 + 0.75);` : "// no capture yet: no callout over the placeholder card"}
      tl.fromTo(q("tag"), { opacity: 0, scale: 0.6, xPercent: -100 }, { opacity: 1, scale: 1, xPercent: -100, duration: 0.3, ease: "back.out(2.2)" }, t0 + 0.95);
      tl.to(q("tag"), { opacity: 0, duration: 0.12 }, ${r2(dur - 0.14)});
      window.__timelines["${id}"] = tl;
    })();
  </script>
</template>
`;
}

// ---------------------------------------------------------------- captions
function captionsComp(total, groups) {
  const items = groups
    .map((g, i) => {
      const words = g.text.split(/\s+/);
      // rebuild with accent spans per word, keeping *multi word* accents
      let inAccent = false;
      const spans = words
        .map((w) => {
          let open = w.startsWith("*");
          let close = w.endsWith("*") && (w.length > 1 || inAccent);
          const clean = w.replace(/\*/g, "");
          const acc = inAccent || open;
          if (open) inAccent = true;
          if (close) inAccent = false;
          return `<span class="w${acc ? " acc" : ""}">${esc(clean)}</span>`;
        })
        .join(" ");
      return `    <div id="cap-${i}" class="clip cap" data-start="${r2(g.start)}" data-duration="${r2(g.end - g.start)}" data-track-index="1"><div id="cap-${i}-in" class="cap-in">${spans}</div></div>`;
    })
    .join("\n");

  const tweens = groups
    .map((g, i) => {
      const d = r2(g.end - g.start);
      return `      tl.fromTo("#cap-${i} .w", { opacity: 0, y: 46, scale: 0.9 }, { opacity: 1, y: 0, scale: 1, duration: 0.26, ease: "back.out(2.4)", stagger: 0.06 }, ${r2(g.start)});
      tl.to("#cap-${i}-in", { opacity: 0, duration: 0.12, ease: "power2.in" }, ${r2(g.start + d - 0.13)});`;
    })
    .join("\n");

  return `<template>
  <style>
    #root { position: absolute; inset: 0; pointer-events: none; }
    #root .cap { position: absolute; left: 0; top: 898px; width: 1920px; text-align: center; overflow: visible; }
    #root .cap-in { display: block; font-family: "Archivo Black", sans-serif; font-size: 62px; line-height: 1.1;
      color: #FFFFFF; letter-spacing: -0.005em; text-shadow: 0 4px 0 rgba(5, 16, 31, 0.55); }
    #root .w { display: inline-block; }
    #root .acc { color: #F2A900; }
  </style>
  <div id="root" data-composition-id="captions" data-width="${W}" data-height="${H}">
${items}
  </div>
  <script>
    (function () {
      const tl = gsap.timeline({ paused: true });
${tweens}
      tl.set({}, {}, ${total});
      window.__timelines["captions"] = tl;
    })();
  </script>
</template>
`;
}

// ---------------------------------------------------------------- index
function indexHtml(total, hosts) {
  return `<!doctype html>
<!-- GENERATED by tools/build.mjs from scenes.json. Edit scenes.json, then run: npm run build -->
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=${W}, height=${H}" />
    <title>PrimeCrest Construction Management - product demo</title>
    ${GSAP}
    <style>
      :root { --navy: #0B2545; --amber: #F2A900; --ink: #FFFFFF; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: ${W}px; height: ${H}px; overflow: hidden; background: var(--navy); }
      #root { position: relative; width: 100%; height: 100%; font-family: Inter, sans-serif; }
      /* blueprint ground: navy with a faint 48 px drafting grid */
      #bg { position: absolute; inset: 0; background-color: var(--navy);
        background-image: linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px);
        background-size: 48px 48px; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="${total}" data-width="${W}" data-height="${H}">
      <div id="bg"></div>
${hosts}
      <audio id="music" class="clip" src="assets/audio/music.wav" data-start="0" data-duration="${total}" data-track-index="20" data-volume="1"></audio>
      <audio id="sfx" class="clip" src="assets/audio/sfx.wav" data-start="0" data-duration="${total}" data-track-index="21" data-volume="0.8"></audio>
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      tl.set({}, {}, ${total});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
`;
}

// ---------------------------------------------------------------- run
mkdirSync(join(ROOT, "compositions"), { recursive: true });
let t = 0;
const hosts = [];
const groups = [];
const report = [];
const cuts = [];
for (const s of cfg.scenes) {
  cuts.push(t);
  let src = s.src;
  if (s.type === "feature") {
    const found = findCapture(s.capture);
    src = `compositions/feat-${s.id}.html`;
    writeFileSync(join(ROOT, src), featureScene(s, found));
    report.push(`${found ? "OK      " : "MISSING "} ${s.id.padEnd(22)} ${found ? found.rel : `captures/${s.capture}.${s.kind === "video" ? "mp4" : "png"}`}`);
  }
  hosts.push(
    `      <div id="${s.id}" data-composition-id="${s.id}" data-composition-src="${src}" data-start="${t}" data-duration="${s.duration}" data-track-index="1" data-track-kind="graphics" data-width="${W}" data-height="${H}" style="z-index: 2"></div>`,
  );
  for (const c of s.captions || []) groups.push({ start: t + c.start, end: t + c.end, text: c.text });
  t += s.duration;
}
hosts.push(
  `      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="${t}" data-track-index="2" data-track-kind="captions" data-width="${W}" data-height="${H}" style="z-index: 10"></div>`,
);
writeFileSync(join(ROOT, "compositions/captions.html"), captionsComp(t, groups));
writeFileSync(join(ROOT, "index.html"), indexHtml(t, hosts.join("\n")));
// cut list for the audio generator (tools/make_audio.py)
writeFileSync(join(ROOT, "assets/audio/cuts.json"), JSON.stringify({ total: t, bpm: cfg.bpm, cuts }, null, 1));
console.log(`Film length ${t}s, ${cfg.scenes.length} scenes, ${groups.length} caption groups`);
console.log(report.join("\n"));
