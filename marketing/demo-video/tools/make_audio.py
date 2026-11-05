#!/usr/bin/env python3
"""Synthesise the demo film's music bed and sound effects locally.

    python tools/make_audio.py        (needs numpy + scipy)

Everything here is generated from oscillators and seeded noise, so the audio is
original, royalty-free and reproducible bit for bit. No samples, no downloads.

Reads assets/audio/cuts.json (written by tools/build.mjs) for the film length
and the scene cut times, and writes:
    assets/audio/music.wav  - 120 BPM energetic bed in A minor (Am F C G),
                              tense build under the hook, drop on the brand reveal,
                              fills into each persona section, resolve under the CTA
    assets/audio/sfx.wav    - whooshes on scene wipes, thuds/pops on the hook beats,
                              a click on the CTA button
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.signal import butter, lfilter, sosfilt

SR = 44100
ROOT = Path(__file__).resolve().parent.parent
AUD = ROOT / "assets" / "audio"
RNG = np.random.default_rng(20261106)

cuts_file = AUD / "cuts.json"
if cuts_file.exists():
    meta = json.loads(cuts_file.read_text())
else:  # sensible default if build.mjs has not been run yet
    meta = {"total": 110, "bpm": 120, "cuts": [0, 8, 12]}
TOTAL = float(meta["total"])
BPM = float(meta.get("bpm", 120))
BEAT = 60.0 / BPM
BAR = BEAT * 4
CUTS = [float(c) for c in meta["cuts"]]
N = int(TOTAL * SR)

# scene landmarks (seconds) - derived from the storyboard
HOOK_END = CUTS[1] if len(CUTS) > 1 else 8.0
CTA_START = CUTS[-1] if CUTS else TOTAL - 10
PERSONA_INTROS = []  # cut times of scenes that open a persona section
scenes_file = ROOT / "scenes.json"
if scenes_file.exists():
    sc = json.loads(scenes_file.read_text(encoding="utf-8"))["scenes"]
    t = 0.0
    for s in sc:
        if s.get("personaIntro"):
            PERSONA_INTROS.append(t)
        t += s["duration"]


def buf(seconds: float) -> np.ndarray:
    return np.zeros(int(seconds * SR))


def env_ad(n: int, attack: float, decay: float) -> np.ndarray:
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    d = np.exp(-np.maximum(t - attack, 0) / max(decay, 1e-4))
    return a * d


def lp(x, cutoff, order=2):
    sos = butter(order, min(cutoff, SR / 2 - 100) / (SR / 2), btype="low", output="sos")
    return sosfilt(sos, x)


def hp(x, cutoff, order=2):
    sos = butter(order, cutoff / (SR / 2), btype="high", output="sos")
    return sosfilt(sos, x)


def bp(x, lo, hi, order=2):
    sos = butter(order, [lo / (SR / 2), hi / (SR / 2)], btype="band", output="sos")
    return sosfilt(sos, x)


def place(dst: np.ndarray, src: np.ndarray, at: float, gain: float = 1.0) -> None:
    i = int(at * SR)
    if i >= len(dst) or i + len(src) <= 0:
        return
    j = min(len(dst), i + len(src))
    s0 = max(0, -i)
    dst[max(i, 0):j] += src[s0:j - i] * gain


def note(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def saw(freq, seconds, detune=0.0):
    t = np.arange(int(seconds * SR)) / SR
    out = np.zeros_like(t)
    for d in (-detune, 0.0, detune):
        ph = (t * freq * (1 + d)) % 1.0
        out += 2 * ph - 1
    return out / 3


# ------------------------------------------------------------------ drums
def kick():
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 7.5)
    click = hp(RNG.standard_normal(n), 2500) * np.exp(-t * 180) * 0.25
    return np.tanh((body + click) * 1.6) * 0.9


def clap():
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    noise = bp(RNG.standard_normal(n), 900, 5200)
    e = np.zeros(n)
    for off in (0.0, 0.011, 0.022):
        e += np.where(t >= off, np.exp(-(t - off) * 60), 0)
    e += np.exp(-t * 14) * 0.5
    return noise * e * 0.35


def hat(open_=False):
    n = int((0.22 if open_ else 0.06) * SR)
    t = np.arange(n) / SR
    noise = hp(RNG.standard_normal(n), 7000)
    return noise * np.exp(-t * (18 if open_ else 90)) * (0.16 if open_ else 0.12)


def crash():
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    noise = hp(RNG.standard_normal(n), 3500)
    return noise * np.exp(-t * 2.2) * 0.22


def snare():
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.4
    noise = bp(RNG.standard_normal(n), 1200, 8000) * np.exp(-t * 26) * 0.5
    return (tone + noise) * 0.5


def riser(seconds):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    noise = RNG.standard_normal(n)
    # sweep a band upward by mixing progressively brighter high-passes
    a = hp(noise, 400)
    b = hp(noise, 3000)
    k = (t / seconds) ** 2
    return ((1 - k) * a * 0.3 + k * b) * k * 0.35


# ------------------------------------------------------------------ music
music = np.zeros(N)
drums = np.zeros(N)
bass = np.zeros(N)
pads = np.zeros(N)
lead = np.zeros(N)

K, C, HC, HO, CR, SN = kick(), clap(), hat(), hat(True), crash(), snare()

# progression: Am  F  C  G  (one chord per bar)
PROG = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [52, 55, 60]), (55, [55, 59, 62])]
ARP = [0, 1, 2, 1, 2, 0, 2, 1]

n_beats = int(TOTAL / BEAT)
for b in range(n_beats):
    t = b * BEAT
    bar = int(t // BAR)
    in_hook = t < HOOK_END
    in_cta = t >= CTA_START
    beat_in_bar = b % 4
    root, chord = PROG[bar % 4]

    if in_hook:
        # tension: offbeat ticks from the start, kick enters for the last beat (chat flood)
        place(drums, HC, t + BEAT / 2, 0.8)
        if t >= HOOK_END - 3.0:
            place(drums, K, t, 0.85)
        # pulsing low A eighths, filter opens toward the drop
        for e in (0, 1):
            seg = saw(note(45), BEAT / 2 * 0.9, 0.004) * env_ad(int(BEAT / 2 * 0.9 * SR), 0.005, 0.12)
            cutoff = 250 + 1800 * (t / HOOK_END) ** 2
            place(bass, lp(seg, cutoff), t + e * BEAT / 2, 0.55)
        continue

    cta_tail = t >= CTA_START + 3.0  # after the button click: kick out, pads ring
    # drums
    if not cta_tail:
        place(drums, K, t, 1.0)
        place(drums, HO, t + BEAT / 2, 1.0)
        place(drums, HC, t + BEAT / 4, 0.7)
        place(drums, HC, t + 3 * BEAT / 4, 0.7)
        if beat_in_bar in (1, 3):
            place(drums, C, t, 1.0)
    # bass: eighths on the root, octave jump on the last eighth of each beat pair
    if not cta_tail:
        for e in (0, 1):
            m = root - 12 + (12 if (e == 1 and beat_in_bar % 2 == 1) else 0)
            seg = saw(note(m), BEAT / 2 * 0.85, 0.003)
            seg = lp(seg * env_ad(len(seg), 0.004, 0.16), 900)
            place(bass, seg, t + e * BEAT / 2, 0.75)
    # arp pluck in sixteenths (rests in the first bar after each cut for air)
    if not in_cta:
        for s16 in range(4):
            idx = (b * 4 + s16) % 8
            m = chord[ARP[idx] % 3] + 12
            seg = saw(note(m), BEAT / 4 * 0.9, 0.006)
            seg = lp(seg * env_ad(len(seg), 0.002, 0.07), 3200)
            place(lead, seg, t + s16 * BEAT / 4, 0.22)

# pads: one chord per bar from the drop to the end
bar_t = HOOK_END
while bar_t < TOTAL:
    bar = int(bar_t // BAR)
    _, chord = PROG[bar % 4]
    length = min(BAR, TOTAL - bar_t)
    seg = sum(saw(note(m), length, 0.008) for m in chord) / 3
    e = np.minimum(1, np.arange(len(seg)) / (0.08 * SR)) * np.minimum(1, (len(seg) - np.arange(len(seg))) / (0.05 * SR))
    place(pads, lp(seg * e, 1600), bar_t, 0.32)
    bar_t += BAR

# crash + sub hit on the drop (the riser is added after the mix)
place(drums, CR, HOOK_END, 1.2)
place(drums, K, HOOK_END, 1.3)

# a snare fill in the half bar before each persona section, a crash on its downbeat
for pt in PERSONA_INTROS:
    if pt <= HOOK_END + 0.1:
        continue
    for i in range(8):
        place(drums, SN, pt - BAR / 2 + i * BEAT / 4, 0.5 + 0.07 * i)
    place(drums, CR, pt, 0.9)

# CTA: crash on entry, final impact as the button is clicked
place(drums, CR, CTA_START, 1.1)
place(drums, K, CTA_START + 2.75, 1.2)
place(drums, CR, CTA_START + 2.75, 0.8)

# sidechain-style pump on pads/lead from the kick grid (after the drop, before the tail)
pump = np.ones(N)
t_axis = np.arange(N) / SR
ph = (t_axis % BEAT) / BEAT
mask = (t_axis >= HOOK_END) & (t_axis < CTA_START + 6)
pump[mask] = 0.55 + 0.45 * np.minimum(1, ph[mask] / 0.35)
music = drums + lp(bass, 2200) + (pads + lead) * pump
place(music, riser(2.5), HOOK_END - 2.5, 1.0)

# master: fade-out over the last 2.5 s, soft clip, normalise for headroom
fade = np.ones(N)
fl = int(2.5 * SR)
fade[-fl:] = np.linspace(1, 0, fl) ** 1.5
music = np.tanh(music * fade * 1.1)
music = music / (np.max(np.abs(music)) + 1e-9) * 0.42  # about -15 LUFS integrated

# ------------------------------------------------------------------ sfx
sfx = np.zeros(N)


def whoosh(seconds=0.42, bright=1.0):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    noise = RNG.standard_normal(n)
    lo = bp(noise, 300 * bright, 1600 * bright)
    hi = bp(noise, 1600 * bright, 7000)
    k = t / seconds
    shape = np.sin(np.pi * np.clip(k, 0, 1)) ** 2
    return (lo * (1 - k) + hi * k) * shape * 0.5


def thud():
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 18)
    paper = bp(RNG.standard_normal(n), 800, 4000) * np.exp(-t * 40) * 0.4
    return (body * 0.6 + paper) * 0.8


def pop():
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    return bp(RNG.standard_normal(n), 1500, 4500) * np.exp(-t * 70) * 0.5


def click():
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return bp(RNG.standard_normal(n), 2000, 9000) * np.exp(-t * 160) * 0.9


variants = [whoosh(0.42, 1.0), whoosh(0.38, 1.3), whoosh(0.46, 0.8)]
for i, c in enumerate(CUTS[2:-1]):  # feature scenes: the amber wipe sweeps at the start
    lead_in = 1.05 if c in PERSONA_INTROS else 0.05
    place(sfx, variants[i % 3], c + lead_in - 0.1, 0.9)
# brand slab and CTA entry
place(sfx, variants[0], HOOK_END - 0.05, 0.8)
# hook beats: stamp, paper drops, chat pops
place(sfx, thud(), 1.82, 1.0)
for i in range(7):
    place(sfx, thud(), 2.5 + i * 0.22 + 0.34, 0.55)
for i in range(7):
    place(sfx, pop(), 5.2 + i * 0.27 + 0.04, 0.6)
# CTA button click
place(sfx, click(), CTA_START + 2.75, 1.0)
sfx = sfx / (np.max(np.abs(sfx)) + 1e-9) * 0.7


def write_wav(path: Path, x: np.ndarray) -> None:
    import wave

    stereo = np.stack([x, x], axis=1)
    data = (np.clip(stereo, -1, 1) * 32767).astype("<i2").tobytes()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)


AUD.mkdir(parents=True, exist_ok=True)
write_wav(AUD / "music.wav", music)
write_wav(AUD / "sfx.wav", sfx)
print(f"music.wav + sfx.wav written: {TOTAL:.1f}s at {BPM:.0f} BPM, persona fills at {PERSONA_INTROS}")
