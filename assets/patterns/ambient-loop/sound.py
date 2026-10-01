"""18 RISO RADIO — the station: one lo-fi track per scene (different key, tempo, instrument colour), crossfaded
under each 1.5 s sheet slide, plus the riso drum's soft paper-feed tick on every re-print (2 frames = 6 Hz),
a paper swish on each slide, and per-scene ambience (birds / road / crickets / water). Loop-safe: the tail wraps
into the start. usage: 18_radio.py <silent video.mp4>"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent)); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "lib"))
from synth import *

FPS, SCENE, SLIDE, N = 12, 24.0, 1.5, 4
DUR = N * SCENE
g = np.random.default_rng(18)

def track(dur, bpm, root, prog, keys_ratio, lead, swing=0.12, seed=0):
    """a small lo-fi loop: FM keys chords, sine bass, dusty kick/snare/hats, a sparse lead"""
    m = Mix(dur); B = 60 / bpm; r = np.random.default_rng(seed)
    for bar in range(int(dur / (4 * B)) + 1):
        t0 = bar * 4 * B; ch = prog[bar % len(prog)]
        for i, n in enumerate(ch):
            s = fm(mtof(root + n), 4 * B + 0.8, ratio=keys_ratio, index=1.1, idx_tau=0.3, amp_tau=1.4)
            m.add(s * adsr(len(s), 0.01, 0.2, 0.8, 0.5), t0 + i * 0.015, 0.16, pan=-0.3 + 0.2 * i)
        for at, dn in ((0, 0), (2.5 * B, 7)):
            b = (sine(mtof(root + ch[0] - 12 + dn), 1.2 * B)) * adsr(int(1.2 * B * SR), 0.01, 0.1, 0.8, 0.15)
            m.add(b, t0 + at, 0.16)
        for at in (0, 1.5 * B + swing * B): m.add(sine(110, 0.3, 55) * expdec(int(0.3 * SR), 0.08), t0 + at, 0.28)
        for at in (B, 3 * B): m.add(lp(bp(noise(0.2, bar * 7 + seed), 800, 5000) * expdec(int(0.2 * SR), 0.05), 4500), t0 + at, 0.3)
        for i in range(8): m.add(hp(noise(0.04, bar * 8 + i + seed), 7000) * expdec(int(0.04 * SR), 0.012), t0 + i * B / 2 + (swing * B if i % 2 else 0), 0.35 * r.uniform(0.6, 1), pan=0.3)
        if bar % 2 == 1:
            for k, (bt, n) in enumerate(lead):
                m.add(fm(mtof(root + n), 1.4, ratio=lead_ratio, index=0.9, idx_tau=0.04, amp_tau=0.6), t0 + bt * B, 0.12, pan=0.2)
    cr = hp(noise(dur, seed + 5), 3000) * 0.012; pos = r.integers(0, len(cr), int(dur * 15)); cr[pos] += r.uniform(-0.5, 0.5, len(pos))
    m.add(lp(cr, 9000), 0, 1.0)
    return lp(m.render(), 10000)

# scene tracks: dawn (F, 76 bpm, soft e-piano), day (A, 92, bright), dusk (D, 70, warm), night (Bb, 64, bell-like)
SPECS = [
    (76, 53, [[0, 4, 7, 11], [5, 9, 12, 16], [2, 5, 9, 12], [7, 11, 14, 17]], 1.0, [(0, 16), (1, 19), (2, 21), (3, 19)], 3.5),
    (92, 57, [[0, 4, 7, 11], [-3, 0, 4, 7], [5, 9, 12, 16], [7, 11, 14, 17]], 2.0, [(0, 19), (0.5, 16), (1.5, 14), (2, 12), (3, 14)], 3.0),
    (70, 50, [[0, 3, 7, 10], [5, 8, 12, 15], [-2, 2, 5, 9], [3, 7, 10, 14]], 1.0, [(0, 15), (2, 12), (3, 10)], 4.0),
    (64, 46, [[0, 4, 7, 11], [2, 5, 9, 12], [-3, 0, 4, 7], [5, 9, 12, 16]], 3.5, [(0, 24), (1, 23), (2, 19), (3, 16)], 5.0),
]
full = np.zeros((int(DUR * SR), 2), np.float32)
L = int((SCENE + SLIDE) * SR)
for k, (bpm, root, prog, kr, lead, lr) in enumerate(SPECS):
    lead_ratio = lr
    x = track(SCENE + SLIDE + 0.5, bpm, root, prog, kr, lead, seed=k * 11)[:L]
    env = np.ones(L, np.float32); fi = int(SLIDE * SR)
    env[:fi] = np.sqrt(np.linspace(0, 1, fi)); env[-fi:] = np.sqrt(np.linspace(1, 0, fi))
    start = int((k * SCENE - SLIDE) * SR)                          # starts under the incoming slide
    idx = (np.arange(L) + start) % len(full)                        # wrap: scene 0's fade-in sits under scene 3's slide
    np.add.at(full, idx, x * env[:, None])
mix = Mix(DUR); mix.add(full, 0, 0.9)
# riso drum: a soft tick every re-print (every 2 frames) and a slow drum hum
for i in range(int(DUR * FPS / 2)):
    mix.add(bp(noise(0.012, i), 2000, 6000) * expdec(int(0.012 * SR), 0.003), i * 2 / FPS, 0.05 * g.uniform(0.6, 1), pan=-0.4)
ts = np.arange(int(DUR * SR)) / SR
mix.add(bp(noise(DUR, 7), 150, 400) * (0.8 + 0.2 * np.sin(2 * np.pi * 6 * ts)), 0, 0.03)
# paper swish on every sheet slide
for k in range(N):
    t = (k + 1) * SCENE - SLIDE
    mix.add(sweep_bp(noise(SLIDE, 30 + k), 3000, 900, q=1.5, blocks=12) * adsr(int(SLIDE * SR), 0.2, 0.4, 0.5, 0.8), t % DUR, 0.22, pan=0.5)
# ambience per scene
amb = [lambda t0: [mix.add(sine(g.uniform(2800, 4200), 0.12, g.uniform(3000, 5000)) * expdec(int(0.12 * SR), 0.04), t0 + g.uniform(0, SCENE), 0.03, pan=g.uniform(-.8, .8)) for _ in range(18)],
       lambda t0: mix.add(lp(noise(SCENE, 41), 700) * 0.6, t0, 0.08),
       lambda t0: [mix.add(sine(4400, 0.05) * adsr(int(0.05 * SR), 0.005, 0.01, 0.8, 0.02), t0 + i * 0.13, 0.01, pan=0.7 if i % 2 else -0.7) for i in range(int(SCENE / 0.13))],
       lambda t0: [mix.add(bp(noise(0.5, 60 + i), 300, 1200) * adsr(int(0.5 * SR), 0.1, 0.1, 0.5, 0.3), t0 + 1 + i * 2, 0.05) for i in range(11)]]
for k in range(N): amb[k](k * SCENE)
out = pathlib.Path(__file__).parent / '18_radio.wav'
write_master(hp(reverb(mix.render(), 0.12, 0.8), 35), out, fade_out=0)
if len(sys.argv) > 1: mux(sys.argv[1], str(out), sys.argv[1].replace('.mp4', '.sound.mp4'))
print('ok')
