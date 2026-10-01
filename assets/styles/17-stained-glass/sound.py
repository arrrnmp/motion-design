"""17 STAINED GLASS — a nave in daylight, synced to anim/17 (24 fps, 10 s).
Same light curve as the page: sun rises 0.2-2.2 s, a cloud dims it 5.9-7.9 s. An organ-like pad
(additive partials, slow tremolo) swells with the light and closes its filter under the cloud; a
tubular bell when the light arrives (2.2 s) and when it returns (7.9 s); faint glass chimes on the
half-beat flickers; a breath of wind with the cloud; big room reverb throughout."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent)); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'lib'))
from synth import *

DUR = 10.0
n = int(DUR * SR); ts = np.arange(n) / SR
sm = lambda a, b, v: (lambda t: t * t * (3 - 2 * t))(np.clip((v - a) / (b - a), 0, 1))
sun = sm(0.2, 2.2, ts) * (1 - 0.62 * sm(5.9, 6.5, ts) * (1 - sm(7.2, 7.9, ts)))
mix = Mix(DUR); g = np.random.default_rng(17)

# ---- pad: D (0-4 s) -> G/D (4-7) -> A/D (7-10), additive organ-ish voices, crossfaded
CH = [(0.0, [50, 57, 62, 66, 69]), (4.0, [50, 55, 59, 62, 67]), (7.0, [50, 57, 61, 64, 69])]
pad = np.zeros(n, np.float32)
for k, (t0, notes) in enumerate(CH):
    t1 = CH[k + 1][0] if k + 1 < len(CH) else DUR + 1
    env = sm(t0 - 0.6, t0 + 0.6, ts) * (1 - sm(t1 - 0.6, t1 + 0.6, ts)) if k else (1 - sm(t1 - 0.6, t1 + 0.6, ts))
    for m in notes:
        f = mtof(m) * (1 + g.normal(0, 0.0015))
        v = sum(a * np.sin(2 * np.pi * f * p * ts + g.uniform(0, 6)) for p, a in ((1, 1), (2, .45), (3, .22), (4, .12), (6, .05)))
        pad += (v * env * (0.85 + 0.15 * np.sin(2 * np.pi * 5.2 * ts + m))).astype(np.float32) * 0.05
# the light opens the filter; cloud closes it
cut = 350 + 3800 * sun
out = np.zeros_like(pad); zi = None
for i in range(0, n, 1024):
    sos = butter(2, float(cut[i]), 'low', fs=SR, output='sos')
    if zi is None: zi = np.zeros((sos.shape[0], 2))
    out[i:i + 1024], zi = sosfilt(sos, pad[i:i + 1024], zi=zi)
mix.add(out * (0.35 + 0.65 * sun), 0, 1.0)

# ---- bells when the light arrives / returns
def bell(f, d=6.0):
    return sum(fm(f * r, d, ratio=1.4, index=0.9, idx_tau=0.2, amp_tau=a) * w for r, w, a in ((1, 1, 2.2), (2.76, .5, 1.2), (5.4, .25, .6)))
mix.add(bell(mtof(62)), 2.2, 0.22, pan=-0.2); mix.add(bell(mtof(69)), 2.2 + 0.9, 0.12, pan=0.25)
mix.add(bell(mtof(64)), 7.9, 0.18, pan=0.15)

# ---- glass chimes on the half-beat flicker (quiet, high, scaled by light)
for k in range(1, 20):
    t = k * 0.5
    s_ = float(np.interp(t, ts[::480], sun[::480]))
    for j in range(2):
        mix.add(fm(mtof(g.choice([86, 88, 90, 93, 95])), 1.2, ratio=3.1, index=0.4, idx_tau=0.02, amp_tau=0.35), t + j * 0.07, 0.03 * s_, pan=g.uniform(-0.7, 0.7))

# ---- wind with the cloud, room tone always
wind = sweep_bp(noise(DUR, 5), 300, 900, q=1.2, blocks=60)[:n] * (sm(5.6, 6.6, ts) * (1 - sm(7.2, 8.3, ts)))
mix.add(wind, 0, 0.18)
mix.add(lp(noise(DUR, 6), 500) * 0.05, 0, 1.0)

wet = reverb(mix.render(), 0.5, 2.6, 4500)
path = pathlib.Path(__file__).parent / '17_glass.wav'
write_master(hp(wet, 35), path, fade_in=0.3, fade_out=1.2)
if len(sys.argv) > 1: mux(sys.argv[1], str(path), sys.argv[1].replace('.mp4', '.sound.mp4'))   # usage: sound.py <silent video.mp4>
print('ok')
