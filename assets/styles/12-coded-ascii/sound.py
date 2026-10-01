"""12 CODED ASCII — reactive score + SFX for the demo video, driven by site/_render/log.json.
Music: the lo-fi loop's layers, re-mixed per frame: each chapter adds/removes layers (hero: filtered
keys + crackle; cherry: + bass/bell; seed: + hats; roast: + drums, crackle up; grind: full; cup: drums
drop, warm resolve), and a low-pass opens with scroll speed and closes when the reader stops.
SFX from the same log: typed characters, the bean stamp click, dither dissolves between chapters,
theme switches, the cherry splitting, the rake, roaster rumble + first-crack pops (same burst
schedule as the page), grinder, and the pour."""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent)); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'lib'))
from synth import *
from lofi import layers, master_bus, WEB_GAINS

ROOT = pathlib.Path(__file__).resolve().parent          # run site_render.py first: it writes site/_render/log.json + site/demo.mp4
LOG = json.loads((ROOT / 'site/_render/log.json').read_text())
FPS, FR = LOG['fps'], LOG['frames']; DUR = LOG['dur']
T = np.array([f['t'] for f in FR]); K = np.array([f.get('k', 0) for f in FR]); Qv = np.array([f.get('q', 0) for f in FR])
MIX = np.array([f.get('mix', 0) for f in FR]); Pv = np.array([f.get('p', 0) for f in FR])
CH = np.array([f.get('chars', 0) for f in FR]); TH = np.array([f.get('theme', 0) for f in FR])
n = int(DUR * SR); ts = np.arange(n) / SR
fidx = np.minimum(len(FR) - 1, (ts * FPS).astype(int))

def per_sample(v, tau=0.25):
    """frame values -> smoothed per-sample curve (one-pole, time constant tau)"""
    x = np.asarray(v, float)[fidx]; a = 1 - np.exp(-1 / (tau * SR))
    return lfilter([a], [1, a - 1], x, zi=[x[0] * (1 - a)])[0].astype(np.float32)

# chapter presence: w[c] = how much chapter c is on screen (current fades out as the dither mix rises)
W = np.zeros((6, len(FR)))
for i, (k, m) in enumerate(zip(K, MIX)):
    W[k, i] += 1 - m
    if k < 5: W[k + 1, i] += m

# ---------------------------------------------------------------- music (layer gains per chapter)
LAYER = {  # chapter:  0    1    2    3    4    5
    'keys':    [0.7, 1.0, 1.0, 1.0, 1.0, 1.1],
    'bass':    [0.0, 0.8, 0.9, 1.0, 1.0, 0.7],
    'bell':    [0.0, 0.6, 0.6, 0.4, 0.5, 1.2],
    'hats':    [0.0, 0.0, 1.0, 1.0, 1.0, 0.4],
    'kick':    [0.0, 0.0, 0.0, 1.0, 1.0, 0.25],
    'snare':   [0.0, 0.0, 0.0, 1.0, 1.0, 0.0],
    'crackle': [1.0, 0.8, 0.8, 1.8, 1.0, 0.8],
}
Ls = layers(DUR + 1.0)
music = np.zeros((n, 2), np.float32)
for name, row in LAYER.items():
    g = per_sample((np.array(row)[:, None] * W).sum(0), 0.35)
    music += Ls[name][:n] * (g * WEB_GAINS[name])[:, None]
# filter: chapter base cutoff, opened by scroll speed
speed = np.abs(np.gradient(Pv) * FPS)                               # chapters per second
base = (np.array([900, 2200, 3200, 5500, 6500, 4200])[:, None] * W).sum(0)
cut = per_sample(base + 5000 * np.minimum(1, speed / 0.8), 0.18)
out = np.zeros_like(music); zi = None; blk = 1024
for i in range(0, n, blk):
    sos = butter(2, float(np.clip(cut[i], 300, 16000)), 'low', fs=SR, output='sos')
    if zi is None: zi = np.zeros((sos.shape[0], 2, 2))
    y, zi = sosfilt(sos, music[i:i + blk], axis=0, zi=zi); out[i:i + blk] = y
music = master_bus(out)

# ---------------------------------------------------------------- SFX
mix = Mix(DUR); sfx = mix.bus(); g = np.random.default_rng(12)
fr = lambda f: f / FPS
def key_click(seed):
    return hp(noise(0.025, seed), 2500) * expdec(int(0.025 * SR), 0.004) + 0.3 * sine(900 + seed % 5 * 70, 0.025) * expdec(int(0.025 * SR), 0.003)

# typing: every newly revealed character
for i in range(1, len(FR)):
    d = CH[i] - CH[i - 1]
    if K[i] != K[i - 1] or d <= 0: continue
    for j in range(min(d, 4)):
        sfx.add(key_click(i * 5 + j), fr(i) + j / (FPS * max(1, d)) + g.uniform(0, 0.006), 0.45 * g.uniform(0.7, 1.0), pan=g.uniform(-0.3, 0.3))
# bean stamp (click)
tc = LOG['click']
sfx.add(sine(150, 0.3, 60) * expdec(int(0.3 * SR), 0.07) + 0.4 * bp(noise(0.3, 7), 200, 1500) * expdec(int(0.3 * SR), 0.02), tc, 0.8)
for k2, m in enumerate([84, 88, 91, 96]):
    sfx.add(fm(mtof(m), 0.4, 3.0, 0.8, 0.03, 0.2), tc + 0.05 + k2 * 0.06, 0.08, pan=0.3)
# dither dissolves: a filtered noise swell shaped by mix*(1-mix), plus a soft digital sweep down
env = per_sample(4 * MIX * (1 - MIX), 0.05)
swell = sweep_bp(noise(DUR, 44), 6000, 2500, q=1.5, blocks=200)[:n] * env
sfx.add(swell, 0, 0.35)
# theme switches: relay "chunk" (two clicks + thump)
for i in range(1, len(FR)):
    if TH[i] != TH[i - 1]:
        for dt, fq in ((0, 3000), (0.03, 1800)):
            sfx.add(bp(noise(0.03, i + int(dt * 100)), fq * 0.6, fq * 1.6) * expdec(int(0.03 * SR), 0.005), fr(i) + dt, 0.5)
        sfx.add(sine(90, 0.15, 60) * expdec(int(0.15 * SR), 0.04), fr(i), 0.5)
# cherry split (ch1 split passes halfway): wet snap
sp = [i for i in range(1, len(FR)) if K[i] == 1 and Qv[i - 1] < 0.45 <= Qv[i]]
for i in sp:
    sfx.add(bp(noise(0.25, 70), 300, 2500) * expdec(int(0.25 * SR), 0.05), fr(i), 0.6)
    sfx.add(pluck(mtof(64), 0.4, 0.99, 0.3, seed=71) * expdec(int(0.4 * SR), 0.08), fr(i), 0.25)
# rake on the drying bed (ch2): scrape proportional to scroll speed in ch2
rake = bp(noise(DUR, 80), 900, 2600)[:n] * per_sample(W[2] * np.minimum(1, speed / 0.5), 0.08) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 7 * ts)))
sfx.add(rake, 0, 0.25)
# roaster: drum rumble while ch3 is on screen
rum = (lp(noise(DUR, 90), 180) * 3 + 0.3 * sine(52, DUR)[:n] * (0.5 + 0.5 * np.sin(2 * np.pi * 1.1 * ts))) * per_sample(W[3], 0.3)
sfx.add(rum, 0, 0.15)
# first-crack pops: same burst schedule as the page (crackParticles: 7 bursts, period 1.4 s, q >= 0.45)
Pg = []; s = 21
for _ in range(512): s = (s * 16807) % 2147483647; Pg.append(s / 2147483647)
hash1 = lambda i: Pg[(i * 97 + 13) & 511]
for i in range(1, len(FR)):
    if K[i] != 3 or Qv[i] < 0.45: continue
    t0, t1 = FR[i - 1]['t'], FR[i]['t']
    for b in range(7):
        off = hash1(b + 70) * 1.4
        if int((t1 + off) // 1.4) != int((t0 + off) // 1.4):
            for j in range(3):
                sfx.add(bp(noise(0.02, i * 7 + b * 3 + j), 1500, 7000) * expdec(int(0.02 * SR), 0.003), fr(i) + j * g.uniform(0.01, 0.04), 0.35 * g.uniform(0.5, 1), pan=g.uniform(-0.6, 0.6))
# grinder: motor + burr noise while ch4 is on screen, grounds hiss
motor = (0.4 * pulse(110, DUR, 0.3)[:n] + bp(noise(DUR, 91), 1200, 4200)[:n] * (0.7 + 0.3 * np.sin(2 * np.pi * 17 * ts)))
sfx.add(lp(motor, 5000) * per_sample(W[4], 0.25), 0, 0.12)
# pour: liquid stream while ch5 fills (q < 0.85)
pour_on = per_sample(W[5] * ((Qv < 0.85) & (K == 5)), 0.15)
stream = bp(noise(DUR, 95), 500, 2800)[:n] * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 9 * ts + np.sin(2 * np.pi * 1.3 * ts))))
sfx.add(stream * pour_on, 0, 0.22, pan=-0.1)

final = music[:n] * 0.9 + reverb(sfx.render(), 0.12, 0.6)[:n]
wav = ROOT / '12_site.wav'
write_master(hp(final, 30), wav, fade_in=0.05, fade_out=1.0)
if len(sys.argv) > 1: mux(sys.argv[1], str(wav), sys.argv[1].replace('.mp4', '.sound.mp4'))   # usage: sound.py <silent video.mp4>
print('ok', DUR)
