"""16 CROSS-STITCH — needlework foley + a music-box waltz, synced to anim/16 (12 fps, 120 frames).
From audio/16_events.json (stitches added per frame): a needle pierce (tiny fabric pop) and a thread
pull (soft swish) at a steady hand rhythm while stitching is active, busier when more stitches land;
backstitch gets a longer pull. Colour changes = a scissors snip in the pauses between motifs
(frames 33, 59, 91); frame 107 the needle is laid down. Music box in D, 3/4 at 108 BPM."""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent)); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'lib'))
from synth import *

FPS, DUR = 12, 10.0
EV = json.loads((pathlib.Path(__file__).parent / '16_events.json').read_text())
fr = lambda f: f / FPS
mix = Mix(DUR); fol, mus = mix.bus(), mix.bus()
g = np.random.default_rng(16)

def pierce(seed):
    return bp(noise(0.03, seed), 2500, 7500) * expdec(int(0.03 * SR), 0.006) + 0.35 * sine(420, 0.03, 260) * expdec(int(0.03 * SR), 0.008)
def pull(d, seed, f0=1400, f1=900):
    x = sweep_bp(noise(d, seed), f0, f1, q=2.0, blocks=8)
    return x * adsr(len(x), 0.02, d * 0.3, 0.6, d * 0.4)
def snip(seed):
    s = np.zeros(int(0.12 * SR), np.float32)
    for dt in (0, 0.045):
        c = bp(noise(0.02, seed + int(dt * 100)), 3000, 9000) * expdec(int(0.02 * SR), 0.004) + 0.4 * sine(2600, 0.02) * expdec(int(0.02 * SR), 0.003)
        i = int(dt * SR); s[i:i + len(c)] += c
    return s

# stitching rhythm: one pierce+pull per 1/6 s ("hand speed") while active; extra quiet pierces when dense
hand = 1 / 6
t = 0.0
while t < DUR:
    f = int(t * FPS)
    if f < len(EV) and EV[f]['x'] + EV[f]['b'] > 0:
        dens = min(1.0, (EV[f]['x'] + EV[f]['b']) / 20)
        fol.add(pierce(int(t * 1000)), t + g.uniform(-0.01, 0.01), 0.5 * (0.6 + 0.4 * dens), pan=g.uniform(-0.2, 0.3))
        long = EV[f]['b'] > 0
        fol.add(pull(0.22 if long else 0.12, int(t * 997)), t + 0.05, 0.22 if long else 0.14, pan=0.2)
        if dens > 0.5:
            fol.add(pierce(int(t * 1000) + 5), t + hand / 2 + g.uniform(-0.01, 0.01), 0.22, pan=g.uniform(-0.3, 0.3))
    t += hand
for f in (33, 59, 91):
    fol.add(snip(f), fr(f) + 0.02, 0.45, pan=-0.3)
fol.add(bp(noise(0.08, 107), 1500, 5000) * expdec(int(0.08 * SR), 0.02), fr(107), 0.35, pan=0.4); fol.add(sine(1800, 0.25) * expdec(int(0.25 * SR), 0.06), fr(107), 0.17, pan=0.4)  # needle laid down: a small metal tick
# cloth room tone
fol.add(lp(noise(DUR, 3), 900) * 0.04, 0, 1.0)

# music box waltz, D major, 108 BPM 3/4
B = 60 / 108
MEL = [(0, 74), (1, 78), (2, 81), (3, 83), (4, 81), (5, 78),  (6, 76), (7, 79), (8, 83), (9, 81), (10, 79), (11, 76),
       (12, 74), (13, 78), (14, 81), (15, 86), (16, 85), (17, 83), (18, 81), (21, 74)]
BASS = [50, 55, 50, 57, 50, 50, 50]
for bt, m in MEL:
    mus.add(fm(mtof(m), 1.6, ratio=4.0, index=1.2, idx_tau=0.02, amp_tau=0.55), 0.35 + bt * B, 0.16, pan=0.15)
for bar, m in enumerate(BASS):
    mus.add(fm(mtof(m), 2.0, ratio=2.0, index=0.8, idx_tau=0.05, amp_tau=0.8), 0.35 + bar * 3 * B, 0.1, pan=-0.2)
    for k in (1, 2):
        for dm in (4, 7):
            mus.add(fm(mtof(m + 12 + dm), 0.8, ratio=4.0, index=0.6, idx_tau=0.02, amp_tau=0.3), 0.35 + (bar * 3 + k) * B, 0.035, pan=-0.1)

mix.add(reverb(fol.render(), 0.1, 0.4, 6000), 0, 1.0)
mix.add(reverb(mus.render(), 0.28, 0.8, 5000), 0, 1.0)
out = pathlib.Path(__file__).parent / '16_stitch.wav'
write_master(hp(mix.render(), 40), out, fade_out=0.8)
if len(sys.argv) > 1: mux(sys.argv[1], str(out), sys.argv[1].replace('.mp4', '.sound.mp4'))   # usage: sound.py <silent video.mp4>
print('ok')
