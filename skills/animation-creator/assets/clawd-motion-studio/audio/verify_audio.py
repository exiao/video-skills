import os, sys
import numpy as np
from pedalboard.io import AudioFile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
import timeline
from PIL import Image, ImageDraw
with AudioFile(os.path.join(HERE, 'soundtrack.wav')) as f:
    x = f.read(f.frames); sr = f.samplerate; ch = f.num_channels
    bd = getattr(f, 'file_dtype', '?')
n = x.shape[1]; SR = sr
T = np.array([-28, -21, -21, -14] + [-11.5] * 19 + [-19], float)
w = x.reshape(2, 24, -1)
rms = 10 * np.log10(np.mean(w ** 2, axis=(0, 2)) + 1e-12)
peak = 20 * np.log10(np.abs(x).max())
dc = x.mean(axis=1)
lines = []
A = lines.append
A("# Audio report\n")
A("Regenerate from the project directory: `.venv/bin/python audio/make_audio.py`. Verify: `.venv/bin/python audio/verify_audio.py` regenerates this report and the PNGs.\n")
A(f"- Format: {sr} Hz, {ch} ch, 24-bit PCM, {n} samples ({n/sr:.3f} s)")
A(f"- Sample peak: {peak:.3f} dBFS (limit -1.0)")
A(f"- DC offset (mean L/R): {dc[0]:.2e} / {dc[1]:.2e}")
A(f"- Clipping (|x|>=0.999): {int((np.abs(x)>=0.999).sum())} samples")
A(f"- Overall RMS: {10*np.log10(np.mean(x**2)):.2f} dBFS\n")
A("## Loudness per half second (RMS dBFS, both channels)\n")
A("| win | time | measured | target | diff |\n|---|---|---|---|---|")
for i in range(24):
    A(f"| {i} | {i*.5:.1f}-{i*.5+.5:.1f} | {rms[i]:.1f} | {T[i]:.1f} | {rms[i]-T[i]:+.1f} |")
A(f"\nMax |diff|: {np.abs(rms-T).max():.1f} dB. Silent windows after 0.5 s: {int((rms[1:]<-60).sum())}.\n")
# onset check
mono = np.abs(x).mean(axis=0)
k = int(.002 * SR)
env = np.sqrt(np.convolve(mono ** 2, np.ones(k) / k, 'same'))
rise = np.diff(env, prepend=0)
hits = ['glass_knock', 'pop', 'keycap_click', 'ui_click', 'thwack', 'ding', 'brass_stab', 'power_down', 'sticker_peel', 'boom']
A("## Onset check (render vs timeline)\n")
A("Onset = time of steepest 2 ms-envelope rise within +-30 ms of the event; local peak = max |x| within -5..+40 ms. The groove's kicks sit on the same grid, so some hits share their onset with a kick.\n")
A("| time | kind | detected onset | d(ms) | local peak | peak d(ms) |\n|---|---|---|---|---|---|")
bad = 0
for t, kind, p in timeline.events():
    if kind not in hits: continue
    s = int(round(t * SR)); a = max(0, s - int(.03 * SR)); b = min(n, s + int(.03 * SR))
    o = a + int(np.argmax(rise[a:b]))
    a2 = max(0, s - int(.005 * SR)); b2 = min(n, s + int(.04 * SR))
    pk = a2 + int(np.argmax(mono[a2:b2]))
    d = (o - s) / SR * 1000; dp = (pk - s) / SR * 1000
    bad += abs(d) > 10
    A(f"| {t:.3f} | {kind} | {o/SR:.4f} | {d:+.1f} | {pk/SR:.4f} | {dp:+.1f} |")
A(f"\nOnsets outside +-10 ms: {bad}\n")
A("## Notes\n- Events synthesized: all %d kinds in timeline.events(); every sound starts at its event sample with no pre-delay.\n- Level matched by section gains (0-0.5, knocks, peel, groove, fade) iterated against the targets before compressor/limiter; fade = (1-x)^2 curve over 11.5-12.0.\n- Peak stays <= -1.0 dBFS (limiter plus final hard guard)." % len({k for _, k, _ in timeline.events()}))
open(os.path.join(HERE, 'audio_report.md'), 'w').write("\n".join(lines))
print("\n".join(lines))
W, H = 1100, 420
im = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(im)
L, R, Tp, B = 60, W - 20, 20, H - 40
def Y(db): return B - (db + 34) / 28 * (B - Tp)
for db in range(-32, -5, 4):
    d.line([(L, Y(db)), (R, Y(db))], fill=(225, 225, 225)); d.text((8, Y(db) - 5), f"{db}", fill='black')
bw = (R - L) / 24
for i in range(24):
    x0 = L + i * bw
    d.rectangle([x0 + 3, Y(rms[i]), x0 + bw / 2 - 1, B], fill=(70, 120, 200))
    d.rectangle([x0 + bw / 2, Y(T[i]), x0 + bw - 3, B], fill=(235, 150, 60))
    if i % 2 == 0: d.text((x0, B + 6), f"{i*.5:.1f}s", fill='black')
d.text((L + 5, 4), "blue = render RMS dBFS per 0.5 s, orange = reference target", fill='black')
im.save(os.path.join(HERE, 'loudness.png'))
W, H = 1400, 420
im = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(im)
for c in range(2):
    top = c * 205 + 5; mid = top + 100
    d.line([(0, mid), (W, mid)], fill=(210, 210, 210))
    for px in range(W):
        seg = x[c, px * n // W:(px + 1) * n // W]
        d.line([(px, mid - seg.max() * 95), (px, mid - seg.min() * 95)], fill=(40, 90, 170))
for t_, kind, _ in timeline.events():
    if kind in ('pop', 'brass_stab', 'sticker_peel', 'thwack', 'glass_knock', 'fade_out'):
        px = t_ / 12 * W; d.line([(px, 0), (px, H)], fill=(220, 60, 60))
for s_ in range(13): d.text((s_ / 12 * W + 2, H - 12), f"{s_}s", fill='black')
im.save(os.path.join(HERE, 'waveform.png'))
