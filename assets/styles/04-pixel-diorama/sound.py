"""04 PIXEL DIORAMA — 2A03-style chiptune + SFX, synced to anim/04 (12 fps, 120 frames).
120 BPM => one beat = 6 frames, one bar = 24 frames; 10 s = 5 bars (D - Bm - G - A - D).
Channels like the NES: pulse 25% lead, pulse 12.5% arpeggio, triangle bass, noise drums.
SFX from the same frame schedule: picker's toss + plink (PICKS), title glint shimmer (f % 36),
steps on the walk cycle, crickets as the sun goes down."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent)); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'lib'))
from synth import *

FPS, BPM, DUR = 12, 120, 10.0
B = 60 / BPM
fr = lambda f: f / FPS
mix = Mix(DUR)
music, sfx = mix.bus(), mix.bus()

CH = [[62, 66, 69], [59, 62, 66], [55, 59, 62], [57, 61, 64], [62, 66, 69]]           # D Bm G A D
BASS = [38, 35, 31, 33, 38]
MEL = {1: [(0, 1, 78), (1, .5, 76), (1.5, .5, 74), (2, 1.5, 71), (3.5, .5, 74)],
       2: [(0, 1, 79), (1, .5, 78), (1.5, .5, 79), (2, 1, 83), (3, 1, 81)],
       3: [(0, 1.5, 81), (1.5, .5, 79), (2, .5, 78), (2.5, .5, 76), (3, 1, 73)],
       4: [(0, 3.5, 74)]}

for bar in range(5):
    t0 = bar * 4 * B
    # arpeggio: 16ths cycling chord tones an octave up (classic "fake chord")
    for i in range(16 if bar < 4 else 8):
        m = CH[bar][i % 3] + 12
        s = pulse(mtof(m), B / 4 * 0.9, 0.125) * adsr(int(B / 4 * 0.9 * SR), 0.002, 0.04, 0.35, 0.02)
        music.add(s, t0 + i * B / 4, 0.09, pan=0.35)
    # triangle bass: root on beats, octave on offbeats
    for i in range(8 if bar < 4 else 2):
        m = BASS[bar] + (12 if i % 2 else 0)
        music.add(tri(mtof(m), B / 2 * 0.85) * adsr(int(B / 2 * 0.85 * SR), 0.002, 0.02, 0.9, 0.02), t0 + i * B / 2, 0.15)
    # drums from bar 2: kick on 1 & 3 (triangle pitch-drop), noise snare on 2 & 4, soft hat 8ths
    if 1 <= bar < 4:
        for bt in (0, 2): music.add(sine(160, 0.12, 55) * expdec(int(0.12 * SR), 0.04), t0 + bt * B, 0.3)
        for bt in (1, 3): music.add(nes_noise(0.14, 6, bar * 7 + bt) * expdec(int(0.14 * SR), 0.05), t0 + bt * B, 0.16)
        for i in range(8): music.add(hp(nes_noise(0.03, 2, i), 6000) * expdec(int(0.03 * SR), 0.01), t0 + i * B / 2, 0.08, pan=-0.3)
    # lead melody with delayed vibrato
    for bt, d, m in MEL.get(bar, []):
        dd = d * B * 0.95; n = int(dd * SR)
        s = pulse(mtof(m), dd, 0.25, vib=0.006 if d >= 1 else 0.0) * adsr(n, 0.004, 0.08, 0.55, 0.05)
        music.add(s, t0 + bt * B, 0.16, pan=-0.15)
        music.add(s, t0 + bt * B + 0.19, 0.045, pan=0.4)      # echo channel, like NES "delay" tricks
music.add(tri(mtof(38), 2.0) * adsr(int(2.0 * SR), 0.01, 0.3, 0.5, 1.0), 4 * 4 * B, 0.14)   # final low D

# ---- SFX
PICKS, LEN = [28, 62, 96], 10
for s0 in PICKS:
    for k, m in enumerate([85, 88, 93]):                                             # toss: rising blip
        sfx.add(pulse(mtof(m), 0.035, 0.5) * adsr(int(0.035 * SR), 0.001, 0.01, 0.6, 0.01), fr(s0 + 1) + k * 0.035, 0.07, pan=0.1)
    sfx.add(tri(mtof(98), 0.22) * expdec(int(0.22 * SR), 0.06), fr(s0 + 6), 0.14, pan=0.1)      # plink into basket
    sfx.add(tri(mtof(105), 0.12) * expdec(int(0.12 * SR), 0.04), fr(s0 + 6) + 0.06, 0.08, pan=0.1)
# steps: the walk cycle advances every 2 walked frames (a foot lands on leg poses 1 and 3)
walked = 0
for f in range(120):
    if not any(s <= f < s + LEN for s in PICKS):
        if walked % 4 == 2: sfx.add(bp(nes_noise(0.03, 4, f), 800, 2500) * expdec(int(0.03 * SR), 0.01), fr(f), 0.05, pan=0.05)
        walked += 1
# title glint shimmer every 36 frames: quick descending sparkle
for f in (8, 44, 80, 116):
    for k, m in enumerate([100, 97, 93, 88]):
        sfx.add(pulse(mtof(m), 0.05, 0.125) * expdec(int(0.05 * SR), 0.03), fr(f) + k * 0.04, 0.035, pan=-0.6 + k * 0.1)
# crickets fade in as the sun sinks (bar 3 on): 4.4 kHz chirps gated at ~30 Hz, in pairs
for i in range(40):
    t = 5.0 + i * 0.125 + (i % 3) * 0.01
    if t > DUR - 0.2: break
    c = sine(4400, 0.05) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 32 * t_(0.05)))) * adsr(int(0.05 * SR), 0.005, 0.01, 0.8, 0.02)
    sfx.add(c, t, 0.012 * min(1, (t - 5) / 2), pan=0.7 if i % 2 else -0.7)

mix.add(reverb(music.render(), 0.12, 0.6), 0, 1.0)
mix.add(reverb(sfx.render(), 0.2, 0.7), 0, 1.0)
out = pathlib.Path(__file__).parent / '04_pixel.wav'
write_master(hp(mix.render(), 35), out, fade_out=0.6)
if len(sys.argv) > 1: mux(sys.argv[1], str(out), sys.argv[1].replace('.mp4', '.sound.mp4'))   # usage: sound.py <silent video.mp4>
print('ok')
