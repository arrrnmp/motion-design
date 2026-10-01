"""15 LINOCUT — foley + folk groove, synced to anim/15 (12 fps, 120 frames).
Act 1 CARVE (0-4 s): one gouge/chisel sound per cut, per frame, from the same STAGES schedule as
the page (different tool voices per stage), over lino-room tone. Beat of silence, then
Act 2 STAMP (4.0 s = frame 48): low thud + paper slap, and the groove starts on it.
Act 3 LIVING PRINT: 90 BPM, so a 16th note = 2 frames = one fresh impression. Muted-pluck
ostinato on 16ths, plucked bass on 1 & 3, kalimba melody, a print-press clack on 2 & 4,
steam hiss, and the cherry drop (whoosh f70 -> splash f84)."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent)); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'lib'))
from synth import *

FPS, DUR = 12, 10.0
fr = lambda f: f / FPS
mix = Mix(DUR); fol, mus = mix.bus(), mix.bus()
g = np.random.default_rng(15)

# ---- carving schedule (mirrors anim/15-linocut.html STAGES / upto)
STAGES = {'title': (0, 6, 17), 'sun': (6, 3, 1), 'rays': (9, 12, 36), 'ground': (21, 6, 70), 'halos': (27, 5, 7),
          'veins': (32, 5, 5), 'cherries': (37, 3, 8), 'cup': (40, 4, 11), 'steam': (44, 4, 15)}
def upto(name, f):
    s, d, n = STAGES[name]; p = max(0, min(1, (f - s + 1) / d)); return int(p * n + 1e-6)

def scrape(d, f0, f1, seed, grit=0.6):
    """a gouge pushing through lino: band-passed noise with a moving centre + chatter"""
    x = noise(d, seed) * (1 - grit + grit * (np.random.default_rng(seed).random(int(d * SR)) > 0.7))
    y = sweep_bp(x, f0, f1, q=3.0, blocks=12)
    e = adsr(len(y), 0.01, d * 0.3, 0.7, d * 0.35)
    return y * e
def chisel(seed):
    return bp(noise(0.05, seed), 2500, 7000) * expdec(int(0.05 * SR), 0.008) + 0.5 * sine(1300 + seed % 7 * 60, 0.05) * expdec(int(0.05 * SR), 0.006)

VOICE = {
    'title': lambda s: chisel(s),
    'sun': lambda s: scrape(0.55, 900, 1600, s),
    'rays': lambda s: scrape(0.22, 1400, 2600, s),
    'ground': lambda s: scrape(0.08, 2200, 3200, s, 0.3),
    'halos': lambda s: scrape(0.3, 1100, 1900, s),
    'veins': lambda s: scrape(0.12, 3000, 4500, s, 0.2),
    'cherries': lambda s: scrape(0.16, 700, 1300, s) + 0.6 * sine(300, 0.16, 180) * expdec(int(0.16 * SR), 0.05),
    'cup': lambda s: scrape(0.18, 1600, 2400, s),
    'steam': lambda s: scrape(0.14, 2600, 1800, s, 0.2),
}
GAIN = {'title': .35, 'sun': .45, 'rays': .22, 'ground': .12, 'halos': .3, 'veins': .2, 'cherries': .3, 'cup': .22, 'steam': .18}
for f in range(48):
    for name in STAGES:
        new = upto(name, f) - (upto(name, f - 1) if f else 0)
        for k in range(min(new, 4)):                                   # >4 cuts in one frame blur into a texture anyway
            fol.add(VOICE[name](f * 31 + k * 7 + list(STAGES).index(name) * 13), fr(f) + k * 0.02 + g.random() * 0.02, GAIN[name], pan=g.uniform(-0.5, 0.5))
# lino room tone (soft brown noise) through the carve, ducking out before the stamp
rt = bp(np.cumsum(noise(4.2, 3)) * 0.02, 80, 500); rt -= rt.mean()
fol.add(rt * np.concatenate([np.linspace(0, 1, int(0.3 * SR)), np.ones(int(3.4 * SR)), np.linspace(1, 0, int(0.5 * SR))])[:len(rt)], 0, 0.08)

# ---- STAMP at 4.0 s
T_STAMP = fr(48)
thud = sine(90, 0.7, 38) * expdec(int(0.7 * SR), 0.18) + 0.6 * lp(noise(0.7, 9), 300) * expdec(int(0.7 * SR), 0.05)
slap = hp(noise(0.12, 11), 1500) * expdec(int(0.12 * SR), 0.02)
fol.add(thud, T_STAMP, 1.1); fol.add(slap, T_STAMP, 0.4)
fol.add(lp(noise(0.5, 12), 3000) * adsr(int(0.5 * SR), 0.02, 0.1, 0.3, 0.3), T_STAMP + 0.12, 0.08)   # paper settles

# ---- GROOVE: 90 BPM from the stamp
B = 60 / 90; S16 = B / 4
CHORDS = [(T_STAMP, [52, 55, 59], 40), (T_STAMP + 4 * B, [48, 52, 55], 36), (T_STAMP + 8 * B, [55, 59, 62], 43)]
def chord_at(t): return [c for c in CHORDS if c[0] <= t + 1e-6][-1]
n16 = int((DUR - T_STAMP) / S16)
PAT = [0, 2, 1, 2, 0, 2, 1, 2, 0, 2, 1, 2, 0, 1, 2, 1]
for i in range(n16):
    t = T_STAMP + i * S16; _, notes, root = chord_at(t)
    m = notes[PAT[i % 16]] + 12
    s = pluck(mtof(m), 0.25, 0.985, 0.35, seed=i) * expdec(int(0.25 * SR), 0.06)        # palm-muted
    mus.add(lp(s, 3500), t, 0.22 if i % 4 == 0 else 0.13, pan=0.25)
    if i % 8 == 0:
        mus.add(lp(pluck(mtof(root), 1.7, 0.997, 0.7, seed=100 + i), 900) * adsr(int(1.7 * SR), 0.001, 0.01, 1.0, 0.45), t, 0.55)         # bass on 1 & 3
    if i % 8 == 4:                                                                          # press clack on 2 & 4
        clk = bp(noise(0.06, 200 + i), 1500, 3500) * expdec(int(0.06 * SR), 0.012) + 0.4 * sine(820, 0.06) * expdec(int(0.06 * SR), 0.01)
        mus.add(clk, t, 0.32, pan=-0.3)
# kalimba melody (FM bell), phrased around the drop
MEL = [(1.0, 71), (1.5, 67), (2.0, 76), (2.75, 74), (3.0, 71),          # Em  (beats from the stamp)
       (4.0, 72), (4.5, 76), (5.0, 79), (6.0, 76), (6.5, 74),          # C
       (8.0, 74)]                                                     # G, ring
for bt, m in MEL:
    d = 2.2 if bt >= 8 else 1.4
    mus.add(fm(mtof(m), d, ratio=3.0, index=1.6, idx_tau=0.05, amp_tau=0.6), T_STAMP + bt * B, 0.17, pan=-0.1)

# ---- cherry drop: whoosh f70 -> f84, splash at f84 + droplets
w0, w1 = fr(70), fr(84)
wh = sweep_bp(noise(w1 - w0 + 0.05, 21), 500, 2400, q=2.0) * np.linspace(0.1, 1, int((w1 - w0 + 0.05) * SR)) ** 2
fol.add(wh, w0, 0.35, pan=-0.2)
fol.add(sine(260, 0.18, 950) * adsr(int(0.18 * SR), 0.002, 0.05, 0.4, 0.1), w1, 0.6, pan=0.3)
fol.add(bp(noise(0.3, 22), 400, 2500) * expdec(int(0.3 * SR), 0.06), w1, 0.48, pan=0.3)
for k in range(9):                                                      # droplets falling back (12 frames)
    t = w1 + 0.25 + g.random() * 0.7
    fol.add(sine(1400 + g.random() * 1600, 0.05, 2600) * expdec(int(0.05 * SR), 0.012), t, 0.12, pan=g.uniform(-0.2, 0.7))
# steam hiss under the living print
hs = hp(noise(DUR - fr(56), 30), 5000) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t_(DUR - fr(56))))
fol.add(hs * np.minimum(1, t_(DUR - fr(56)) / 1.5), fr(56), 0.02, pan=0.4)

mix.add(reverb(fol.render(), 0.15, 0.5, 5000), 0, 1.0)
mix.add(reverb(mus.render(), 0.22, 0.9, 4000), 0, 1.0)
out = pathlib.Path(__file__).parent / '15_linocut.wav'
write_master(hp(mix.render(), 30), out, fade_out=1.2)
if len(sys.argv) > 1: mux(sys.argv[1], str(out), sys.argv[1].replace('.mp4', '.sound.mp4'))   # usage: sound.py <silent video.mp4>
print('ok')
