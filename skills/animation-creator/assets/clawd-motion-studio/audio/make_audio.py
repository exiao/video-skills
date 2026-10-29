#!/usr/bin/env python
"""Synthesize soundtrack.wav (48k stereo 24-bit, 12.000 s) from timeline.py.
Run: ROOT/.venv/bin/python ROOT/audio/make_audio.py"""
import os, sys, zlib
import numpy as np
from scipy import signal as sg
from pedalboard import (Pedalboard, Reverb, Compressor, Limiter, HighpassFilter,
                        LowpassFilter, Gain)
from pedalboard.io import AudioFile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import timeline

SR = 48000
N = int(round(timeline.DURATION * SR))
BEAT = timeline.BEAT
T_DROP, T_PLAY, T_END = timeline.T_POP, timeline.T_PLAY, timeline.DURATION
rng = np.random.default_rng(20240612)


def tt(d):
    return np.arange(int(round(d * SR))) / SR


def expenv(t, tau):
    return np.exp(-t / tau)


def att(x, ms=0.7):
    n = max(1, int(SR * ms / 1000))
    x = x.copy()
    n = min(n, len(x))
    x[:n] *= np.linspace(0, 1, n)
    return x


def noise(n):
    return rng.standard_normal(n)


def bp(x, lo, hi, order=2):
    hi = min(hi, SR * 0.45)
    return sg.sosfilt(sg.butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return sg.sosfilt(sg.butter(order, f, 'high', fs=SR, output='sos'), x)


def lp(x, f, order=2):
    return sg.sosfilt(sg.butter(order, min(f, SR * .45), 'low', fs=SR, output='sos'), x)


def sweep(t, f0, f1, curve='exp'):
    d = t[-1] if len(t) else 1
    d = max(d, 1e-6)
    if curve == 'exp':
        f = f0 * (f1 / f0) ** (t / d)
    else:
        f = f0 + (f1 - f0) * t / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def nrm(x):
    return x / (np.max(np.abs(x)) + 1e-9)


# ------------------------------------------------------------ effects
def glass_knock(p):
    t = tt(.25)
    x = np.zeros_like(t)
    for f, a, tau in [(1180, 1, .05), (1870, .6, .035), (2950, .4, .025), (4300, .2, .015)]:
        x += a * np.cos(2 * np.pi * f * t) * expenv(t, tau)
    x += 1.2 * np.sin(2 * np.pi * 170 * t) * expenv(t, .03)
    x += .8 * bp(noise(len(t)), 1500, 6000) * expenv(t, .006)
    return nrm(x) * .9

def sticker_peel(p):
    d = p.get('dur', .4); t = tt(d + .05)
    n = noise(len(t))
    f = 1500 + 3500 * (t / d)
    # sweeping band via mixing of two bands
    x = bp(n, 1000, 3000) * (1 - t / d).clip(0) + bp(n, 3000, 9000) * (t / d).clip(0, 1)
    crack = (rng.random(len(t)) < 0.012).astype(float)
    crack = sg.lfilter([1], [1, -.9], crack)
    mod = .5 + .5 * np.abs(np.sin(2 * np.pi * 47 * t + 3 * np.sin(2 * np.pi * 9 * t)))
    x = x * mod + 4 * hp(crack * noise(len(t)), 2500)
    e = np.minimum(1, t / .02) * np.exp(-np.maximum(t - d, 0) / .01) * (.6 + .4 * t / d)
    return nrm(x * e)

def riser(p):
    d = p.get('dur', .5); t = tt(d)
    n = noise(len(t))
    f = 300 * (6000 / 300) ** (t / d)
    saw = sg.sawtooth(2 * np.pi * np.cumsum(f * .5) / SR) * .4
    # noise band rising: crossfade filters
    nz = bp(n, 800, 2500) * (1 - t / d) + hp(n, 3500) * (t / d) * .8
    e = (t / d) ** 2
    x = (saw * .5 + nz) * e
    x[-int(SR * .004):] *= np.linspace(1, 0, int(SR * .004))
    return nrm(x) * .8

def pop(p):
    t = tt(.18)
    x = sweep(t, 1100, 150) * expenv(t, .04) * 1.2
    x += bp(noise(len(t)), 800, 9000) * expenv(t, .01) * .8
    return nrm(att(x, .3))

def glass_break(p):
    t = tt(1.0)
    n = noise(len(t))
    x = hp(n, 2500) * expenv(t, .05) * .8
    for _ in range(46):
        st = int(rng.random() ** 2 * .35 * SR)
        f = rng.uniform(2800, 9500)
        tl = tt(.45)
        ping = np.sin(2 * np.pi * f * tl) * expenv(tl, rng.uniform(.03, .15)) * rng.uniform(.15, .6)
        x[st:st + len(ping)] += ping[:len(x) - st]
    x[:int(SR * .002)] *= 0
    x = x + 0  # noise burst at sample 0
    x[:96] += hp(noise(96), 3000) * 1.5
    return nrm(x)

def sub_boom(p):
    t = tt(1.1)
    x = sweep(t, 95, 38) * expenv(t, .35)
    return nrm(att(x, .5)) * 1.0

def beat_drop(p):  # marker: soft reversed-tail crash that lands on the drop
    t = tt(.9)
    x = hp(noise(len(t)), 5000) * expenv(t, .22)
    return nrm(att(x, .3)) * .35

def boing(p):
    t = tt(.28)
    f = 260 * (2.4) ** (t / .28 * .6) * (1 + .06 * np.sin(2 * np.pi * 24 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + .35 * np.sin(2 * ph + 1) + .15 * np.sin(3 * ph)) * expenv(t, .11)
    return nrm(att(x, .8)) * .7

def pomf(p):
    t = tt(.2)
    x = sweep(t, 150, 55) * expenv(t, .06)
    x += lp(noise(len(t)), 600) * expenv(t, .02) * .8
    return nrm(att(x, .8)) * .8

def whoosh(p):
    d = p.get('dur', .5); t = tt(d)
    n = noise(len(t))
    # moving band
    x = np.zeros_like(t)
    seg = 8
    edges = np.linspace(0, len(t), seg + 1).astype(int)
    for i in range(seg):
        c = 500 + 2600 * np.sin(np.pi * (i + .5) / seg) ** 1.3
        x[edges[i]:edges[i + 1]] = bp(n, c * .6, c * 1.6)[edges[i]:edges[i + 1]]
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return nrm(x * e) * .6

def keycap_click(p):
    t = tt(.12)
    x = bp(noise(len(t)), 1800, 6500) * expenv(t, .004) * 1.0
    x += np.sin(2 * np.pi * 820 * t) * expenv(t, .018) * .8
    x += np.sin(2 * np.pi * 240 * t) * expenv(t, .03) * .9
    return nrm(att(x, .2)) * .9

def ui_blip(p):
    t = tt(.14)
    x = np.sin(2 * np.pi * 1760 * t) * expenv(t, .045) + .4 * np.sin(2 * np.pi * 2640 * t) * expenv(t, .03)
    return nrm(att(x, .6)) * .5

def key_tap(p):
    ch = p.get('char', 'A'); h = zlib.crc32(str(p.get('i', 0)).encode()) % 100 / 100
    t = tt(.05)
    f = 1500 + 700 * h
    x = bp(noise(len(t)), 2200, 8000) * expenv(t, .002) + np.sin(2 * np.pi * f * t) * expenv(t, .008) * .6
    x += np.sin(2 * np.pi * 330 * t) * expenv(t, .012) * .5
    return nrm(att(x, .15)) * (.4 if ch != ' ' else .5)

def bloop(p):
    t = tt(.2)
    x = sweep(t, 280, 900) * expenv(t, .07)
    return nrm(att(x, 1.0)) * .6

def pen_scribble(p):
    d = p.get('dur', .43); t = tt(d)
    n = bp(noise(len(t)), 1800, 7000)
    m = np.abs(sg.sosfilt(sg.butter(2, 18, 'low', fs=SR, output='sos'), noise(len(t))))
    m = m / m.max()
    stroke = .5 + .5 * np.sin(2 * np.pi * 11 * t)
    e = np.minimum(1, t / .01) * np.minimum(1, (d - t) / .04)
    return nrm(n * (.3 + .7 * m * stroke) * e) * .5

def select_blip(p):
    t = tt(.16)
    x = np.sin(2 * np.pi * 988 * t) * (t < .06) + np.sin(2 * np.pi * 1480 * t) * (t >= .06) * expenv(t - .06, .05).clip(0, 1)
    x = x * expenv(t, .08)
    x[:] = x
    return nrm(att(x, .6)) * .5

def thwack(p):
    t = tt(.3)
    x = sweep(t, 420, 70) * expenv(t, .06) * 1.2
    x += bp(noise(len(t)), 500, 7000) * expenv(t, .012) * 1.0
    x += sweep(t, 90, 50) * expenv(t, .15) * .6
    return nrm(att(x, .2)) * 1.0

def magic_shimmer(p):
    d = p.get('dur', .9); t = tt(d)
    x = np.zeros_like(t)
    for _ in range(14):
        f = rng.choice([1046.5, 1318.5, 1568, 2093, 2637, 3136, 4186])
        s0 = rng.uniform(0, d * .6)
        env = np.exp(-np.maximum(t - s0, 0) / .22) * (t >= s0)
        x += np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * env * (1 + .5 * np.sin(2 * np.pi * rng.uniform(6, 12) * t))
    x[0] = 0
    x += np.sin(2 * np.pi * 2093 * t) * .6 * expenv(t, .3)
    e = np.minimum(1, t / .004) * np.minimum(1, (d - t) / .2)
    return nrm(x * e) * .5

def _bell(f, dur=1.0, tau=.35, ratio=3.5, idx=2.0):
    t = tt(dur)
    mod = np.sin(2 * np.pi * f * ratio * t) * idx * expenv(t, tau * .5)
    return np.sin(2 * np.pi * f * t + mod) * expenv(t, tau)

def bells(p):
    out = np.zeros(int(SR * 1.6))
    for i, f in enumerate([1046.5, 1318.5, 1568.0, 2093.0]):
        s = int(i * .09 * SR)
        b = att(_bell(f, 1.0, .3), .4)
        out[s:s + len(b)] += b * (1 - i * .1)
    return nrm(out) * .6

def ding(p):
    f = p.get('freq', 880); t = tt(1.4)
    x = np.zeros_like(t)
    for r, a, tau in [(1, 1, .5), (2.76, .35, .25), (5.4, .2, .12), (8.9, .1, .06)]:
        x += a * np.sin(2 * np.pi * f * r * t) * expenv(t, tau)
    x += bp(noise(len(t)), 3000, 9000) * expenv(t, .004) * .4
    return nrm(att(x, .3)) * .75

def tape_rewind(p):
    d = p.get('dur', .4); t = tt(d)
    x = np.zeros_like(t)
    rate = 52
    ph = (t * rate) % 1.0
    f = 3200 - 2000 * ph
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - ph) ** .7
    x += .3 * bp(noise(len(t)), 2000, 7000) * (.5 + .5 * np.sin(2 * np.pi * 180 * t))
    e = np.minimum(1, t / .003) * np.minimum(1, (d - t) / .03)
    return nrm(x * e) * .55

def skate_roll(p):
    d = p.get('dur', 1.1); t = tt(d)
    n = noise(len(t))
    x = bp(n, 150, 700) * (.6 + .4 * np.sin(2 * np.pi * 7 * t)) + .5 * bp(n, 1500, 4000) * (.5 + .5 * np.sin(2 * np.pi * 13 * t + 1)) ** 2
    e = np.minimum(1, t / .08) * np.minimum(1, (d - t) / .15)
    return nrm(x * e) * .5

def scrub_tick(p):
    ct = p.get('comp_t', 0); t = tt(.03)
    f = 1800 + 280 * ct
    x = np.sin(2 * np.pi * f * t) * expenv(t, .004) + bp(noise(len(t)), 3000, 9000) * expenv(t, .0012) * .6
    return nrm(att(x, .1)) * .35

def ui_click(p):
    t = tt(.1)
    x = bp(noise(len(t)), 1500, 6000) * expenv(t, .004) + np.sin(2 * np.pi * 180 * t) * expenv(t, .03) * 1.0 + np.sin(2 * np.pi * 1200 * t) * expenv(t, .01) * .5
    return nrm(att(x, .2)) * .8

def brass_stab(p):
    d = .55; t = tt(d)
    x = np.zeros_like(t)
    for f in [130.81, 261.63, 329.63, 392.0, 523.25]:
        for det in (-.004, 0, .004):
            ff = f * (1 + det)
            x += sg.sawtooth(2 * np.pi * np.cumsum(np.full(len(t), ff)) / SR + rng.uniform(0, 6.28))
    # filter swell (brassy): sweep lowpass via blocks
    out = np.zeros_like(x)
    blocks = np.array_split(np.arange(len(x)), 24)
    zi = None
    for i, b in enumerate(blocks):
        cut = 700 + 4500 * np.exp(-i * d / 24 / .08)
        sos = sg.butter(2, cut, 'low', fs=SR, output='sos')
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        out[b], zi = sg.sosfilt(sos, x[b], zi=zi)
    e = np.minimum(1, t / .004) * np.exp(-t / .25)
    e = np.where(t > d - .05, e * np.maximum(0, (d - t) / .05), e)
    return nrm(out * e) * .9

def shimmer(p):
    d = p.get('dur', 1.2); t = tt(d)
    x = np.zeros_like(t)
    for _ in range(18):
        f = rng.choice([1046.5, 1318.5, 1568, 2093, 2637, 3136, 4186])
        s0 = rng.uniform(0, d * .5)
        x += np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-np.maximum(t - s0, 0) / .3) * (t >= s0) * rng.uniform(.3, 1)
    e = np.minimum(1, t / .003) * np.minimum(1, (d - t) / .3)
    return nrm(x * e) * .4

def power_down(p):
    t = tt(.35)
    x = sweep(t, 1400, 70) * expenv(t, .15)
    x += .4 * sg.sawtooth(2 * np.pi * np.cumsum(900 * (60 / 900) ** (t / .35)) / SR) * expenv(t, .08)
    x += hp(noise(len(t)), 3000) * expenv(t, .01) * .5
    return nrm(att(lp(x, 6000), .3)) * .55

def boom(p):
    t = tt(1.0)
    x = sweep(t, 110, 42) * expenv(t, .3) + lp(noise(len(t)), 300) * expenv(t, .1) * .5
    return nrm(att(x, .4)) * .9

def yay_chirps(p):
    out = np.zeros(int(SR * .8))
    for i, (s, f0, f1) in enumerate([(0, 1100, 1900), (.17, 1300, 2300), (.36, 1500, 2800)]):
        t = tt(.14)
        f = f0 * (f1 / f0) ** (t / .14) * (1 + .03 * np.sin(2 * np.pi * 35 * t))
        c = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * np.clip(t / .14, 0, 1)) ** .5
        c = c + .25 * np.sin(4 * np.pi * np.cumsum(f) / SR) * expenv(t, .05)
        c = att(c, .5)
        st = int(s * SR)
        out[st:st + len(c)] += c
    return nrm(out) * .55

def sparkles(p):
    d = p.get('dur', .7); t = tt(d)
    x = np.zeros_like(t)
    for k in range(22):
        s0 = 0 if k == 0 else int(rng.uniform(0, d * .85) * SR)
        f = rng.choice([2093, 2637, 3136, 3951, 4186, 5274, 6272])
        tl = tt(.25)
        x[s0:s0 + len(tl)] += (np.sin(2 * np.pi * f * tl) * expenv(tl, .06) * rng.uniform(.4, 1))[:len(x) - s0]
    return nrm(x) * .4

def fade_out(p):
    d = p.get('dur', .5); t = tt(d)
    x = sweep(t, 1568, 392, 'exp') * (1 - t / d) ** 2 * .6 + .3 * sweep(t, 784, 196) * (1 - t / d)
    return nrm(att(x, 1.0)) * .25

FX = dict(glass_knock=glass_knock, sticker_peel=sticker_peel, riser=riser, pop=pop,
          glass_break=glass_break, sub_boom=sub_boom, beat_drop=beat_drop, boing=boing,
          whoosh=whoosh, pomf=pomf, keycap_click=keycap_click, ui_blip=ui_blip,
          key_tap=key_tap, bloop=bloop, pen_scribble=pen_scribble, select_blip=select_blip,
          thwack=thwack, magic_shimmer=magic_shimmer, bells=bells, ding=ding,
          tape_rewind=tape_rewind, skate_roll=skate_roll, scrub_tick=scrub_tick,
          ui_click=ui_click, brass_stab=brass_stab, shimmer=shimmer, power_down=power_down,
          boom=boom, yay_chirps=yay_chirps, sparkles=sparkles, fade_out=fade_out)
# relative level per kind (dB) and base pan (small)
LEVEL = dict(glass_knock=0, sticker_peel=-4, riser=-8, pop=0, glass_break=-6, sub_boom=-2,
             beat_drop=-6, boing=-9, whoosh=-12, pomf=-8, keycap_click=-6, ui_blip=-12,
             key_tap=-10, bloop=-8, pen_scribble=-10, select_blip=-11, thwack=-2,
             magic_shimmer=-12, bells=-10, ding=-6, tape_rewind=-10, skate_roll=-12,
             scrub_tick=-12, ui_click=-6, brass_stab=-3, shimmer=-12, power_down=-9,
             boom=-5, yay_chirps=-8, sparkles=-12, fade_out=-12)
# per-kind level at specific times (e.g. the loudest section is just muscle, keep kind-level)
FXGAIN = 1.0


def place(buf, sig, t, pan=0.0, gain=1.0):
    s = int(round(t * SR))
    if s >= N:
        return
    m = min(len(sig), N - s)
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    buf[0, s:s + m] += sig[:m] * gain * l
    buf[1, s:s + m] += sig[:m] * gain * r


# ------------------------------------------------------------ music
NOTE = lambda m: 440.0 * 2 ** ((m - 69) / 12)
CHORDS = [(41, [53, 57, 60]), (43, [55, 59, 62]), (45, [57, 60, 64]), (36, [55, 60, 64])]  # F G Am C(bass midi, tones)
CH = [(41, [57, 60, 65]), (43, [59, 62, 67]), (45, [60, 64, 69]), (48, [60, 64, 67])]


def kick():
    t = tt(.3)
    x = sweep(t, 160, 46) * expenv(t, .11)
    x += bp(noise(len(t)), 1500, 6000) * expenv(t, .004) * .3
    return nrm(att(x, .3))

def snare():
    t = tt(.25)
    x = bp(noise(len(t)), 1200, 9000) * expenv(t, .07) + np.sin(2 * np.pi * 195 * t) * expenv(t, .05) * .7
    return nrm(att(x, .3))

def hat(open_=False, soft=1.0):
    t = tt(.16 if open_ else .05)
    x = hp(noise(len(t)), 7000) * expenv(t, .05 if open_ else .012)
    return nrm(att(x, .2)) * soft

def bass_note(m, d):
    t = tt(d)
    f = NOTE(m) * 2 ** ((1.5 / 12) * np.exp(-t / .05))  # rubbery pitch bend
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + .5 * sg.sawtooth(ph, .5) * .6 + .3 * np.sin(2 * ph)
    # wah-ish filter envelope
    out = np.zeros_like(x); zi = None
    for b in np.array_split(np.arange(len(x)), 16):
        i0 = b[0] / SR
        sos = sg.butter(2, 250 + 900 * np.exp(-i0 / .08), 'low', fs=SR, output='sos')
        if zi is None: zi = np.zeros((1, 2))
        out[b], zi = sg.sosfilt(sos, x[b], zi=zi)
    e = np.minimum(1, t / .006) * np.exp(-t / .35) * np.minimum(1, (d - t) / .02)
    return out * e

def fm_key(m, d=.45):
    f = NOTE(m); t = tt(d)
    mod = np.sin(2 * np.pi * f * 3.5 * t) * 1.8 * expenv(t, .08) + np.sin(2 * np.pi * f * t) * .5
    x = np.sin(2 * np.pi * f * t + mod) * expenv(t, .16)
    return att(x, 1.0) * np.minimum(1, (d - t) / .03)

def pad_chord(ms, d, lpf=1100):
    t = tt(d)
    x = np.zeros_like(t)
    for m in ms:
        for det in (-.006, .006):
            f = NOTE(m) * (1 + det) / 2
            x += sg.sawtooth(2 * np.pi * np.cumsum(np.full(len(t), f)) / SR + rng.uniform(0, 6.28))
    x = lp(x, lpf)
    return x * np.minimum(1, t / .4) * np.minimum(1, (d - t) / .3)


def build_music():
    bed = np.zeros((2, N))      # pad / bass / keys (ducked)
    drums = np.zeros((2, N))
    duck_times = []
    # pre-drop pad (F chord) and ticking hats
    pre = pad_chord(CH[0][1], T_DROP + .4, 900)
    pre *= np.minimum(1, tt(T_DROP + .4) / .05)  # present from sample 0
    pre = pre / np.max(np.abs(pre)) * .12
    place(bed, pre, 0, 0)
    for k in range(int(T_DROP / .25)):
        t0 = k * .25
        place(drums, hat(False, .5 if k % 2 == 0 else .3), t0 + 0, .2 * (1 if k % 2 else -1) * .5, .22)
    # groove from drop to play
    nbars = int((T_PLAY - T_DROP) / 2)
    for bar in range(nbars):
        b0 = T_DROP + bar * 2.0
        root, tones = CH[bar % 4]
        pd = pad_chord(tones, 2.3, 1000); pd = pd / np.max(np.abs(pd)) * .07
        place(bed, pd, b0, 0)
        # kick: beats 1,2.5?,3 -> times in eighths: 0, 3, 4, 7? lo-fi: 0, 3, 4
        for e8 in (0, 3, 4):
            place(drums, kick(), b0 + e8 * .25, 0, .9)
            duck_times.append(b0 + e8 * .25)
        for e8 in (2, 6):
            place(drums, snare(), b0 + e8 * .25, .05, .55)
        for e8 in range(8):
            place(drums, hat(e8 == 7), b0 + e8 * .25 + 0, .25 * (1 if e8 % 2 else -1), .24 if e8 % 2 else .16)
        # bass
        for e8, off, d in [(0, 0, .45), (3, 0, .2), (4, 7, .2), (5, 12, .2), (6, 0, .45)]:
            if e8 == 6: d = .2
            place(bed, bass_note(root + off, d) * .55 if off == 0 else bass_note(root + off, d) * .5, b0 + e8 * .25, 0)
        # keys on the off-beats
        for j, e8 in enumerate((1, 3, 5, 7)):
            m = tones[(j + bar) % 3] + (12 if j % 2 else 0)
            place(bed, fm_key(m) * .06, b0 + e8 * .25, .3 if j % 2 else -.3)
    # sidechain duck on bed, only after drop
    g = np.ones(N)
    for tk in duck_times:
        s = int(round(tk * SR))
        m = min(int(.4 * SR), N - s)
        tl = np.arange(m) / SR
        g[s:s + m] = np.minimum(g[s:s + m], 1 - .65 * np.exp(-tl / .11))
    bed *= g
    # ring-out chord from the play stab (C major), ~ends in the 0.5 s fade
    rd = T_END - T_PLAY
    ring = pad_chord([60, 64, 67, 72], rd + .3, 1600)
    ring = ring * np.minimum(1, tt(rd + .3) / .004)
    ring = ring / np.max(np.abs(ring)) * .16
    ring = ring * (.55 + .45 * np.exp(-tt(rd + .3) / .6))
    place(bed, ring, T_PLAY, 0)
    for m_, a in [(48, .22), (60, .09)]:
        t = tt(rd + .3)
        place(bed, np.sin(2 * np.pi * NOTE(m_) * t) * a * np.minimum(1, t / .004) * (.6 + .4 * np.exp(-t / .5)), T_PLAY)
    return bed, drums


def fxbus():
    bus = np.zeros((2, N))
    ev = timeline.events()
    for (t, kind, params) in ev:
        if kind not in FX:
            raise SystemExit(f"unhandled event kind {kind}")
        sig = FX[kind](params)
        h = zlib.crc32(f"{t:.4f}{kind}".encode()) % 1000 / 1000
        pan = (h - .5) * .3
        place(bus, sig, t, pan, 10 ** (LEVEL[kind] / 20) * FXGAIN)
    return bus


def master(bed, drums, fx, gains_db, fade=True):
    r_bed = Pedalboard([Reverb(room_size=.35, damping=.6, wet_level=.14, dry_level=.86)])(bed.astype(np.float32), SR)
    r_fx = Pedalboard([Reverb(room_size=.25, damping=.5, wet_level=.1, dry_level=.9)])(fx.astype(np.float32), SR)
    mix = (r_bed + drums + r_fx).astype(np.float32)
    mix = Pedalboard([HighpassFilter(28)])(mix, SR)
    wc = (np.arange(24) + .5) * .5
    g = 10 ** (np.interp(np.arange(N) / SR, wc, gains_db) / 20)
    mix = mix * g.astype(np.float32)
    mix = np.tanh(mix * .9) / .9  # gentle glue saturation
    mix = Pedalboard([Compressor(threshold_db=-16, ratio=3, attack_ms=8, release_ms=120),
                      Gain(2.0), Limiter(threshold_db=-1.0, release_ms=60)])(mix, SR)
    if fade:
        t = np.arange(N) / SR
        x = np.clip((t - 11.5) / .5, 0, 1)
        mix = mix * ((1 - x) ** 2).astype(np.float32)
    mix = np.clip(mix, -10 ** (-1.0 / 20), 10 ** (-1.0 / 20))
    return mix

TARGETS = np.array([-28, -21, -21, -14] + [-11.5] * 19 + [-19], float)


def win_rms(x):
    w = x.reshape(2, 24, -1)
    return 10 * np.log10(np.mean(w ** 2, axis=(0, 2)) + 1e-12)


def main():
    bed, drums = build_music()
    fx = fxbus()
    # section gains (dB): [0], [1,2], [3], [4..22], [23]; iterate on section-mean error
    groups = [[0], [1, 2], [3], list(range(4, 23)), [23]]
    sg_db = np.zeros(len(groups))
    def expand(v):
        g = np.zeros(24)
        for gi, ws in enumerate(groups):
            g[ws] = v[gi]
        return g
    for it in range(12):
        out = master(bed, drums, fx, expand(sg_db))
        r = win_rms(out)
        err = np.array([np.mean((TARGETS - r)[ws]) for ws in groups])
        err[4] = 0
        sg_db = sg_db + .9 * err
    gains = expand(sg_db)
    out = master(bed, drums, fx, gains)
    out = out - out.mean(axis=1, keepdims=True) * 0  # no DC offset introduced (hp filter at 28 Hz)
    assert out.shape == (2, N)
    path = os.path.join(HERE, 'soundtrack.wav')
    with AudioFile(path, 'w', SR, 2, bit_depth=24) as f:
        f.write(out.astype(np.float32))
    np.save(os.path.join(HERE, '_gains.npy'), gains)
    print('wrote', path, 'peak dBFS', 20 * np.log10(np.abs(out).max()))
    print('gains dB', np.round(gains, 1))
    print('rms', np.round(win_rms(out), 1))

if __name__ == '__main__':
    main()
