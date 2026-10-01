"""12 CODED ASCII — lo-fi café loop (84 BPM, 8 bars, Dmaj7-Bm7-Em9-A13 x2), rendered per layer so
the same music can be (a) a static seamless loop for the website and (b) a chapter-reactive score
for the demo video (layer gains + a filter that opens with scroll speed, driven by the page log).
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent)); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'lib'))
from synth import *

BPM = 84; B = 60 / BPM; BAR = 4 * B; LOOP = 8 * BAR
CHORDS = [[50, 54, 57, 61], [47, 50, 54, 57], [52, 55, 59, 62, 66], [45, 55, 61, 66]] * 2
ROOTS = [38, 35, 40, 33] * 2
BELL = [(1, 2.5, 78), (1, 3.0, 81), (3, 2.0, 83), (3, 2.5, 81), (3, 3.0, 78), (5, 1.5, 74), (5, 2.0, 76), (7, 2.5, 73), (7, 3.0, 76)]
SWING = 0.1
WEB_GAINS = {'keys': 2.2, 'bass': 0.45, 'kick': 0.38, 'snare': 0.8, 'hats': 4.5, 'crackle': 1.4, 'bell': 1.8}


def layers(dur, seed=0):
    """render every layer for `dur` seconds of the loop (repeating), each a stereo buffer"""
    L = {k: Mix(dur) for k in ('keys', 'bass', 'kick', 'snare', 'hats', 'crackle', 'bell')}
    g = np.random.default_rng(84 + seed)
    nb = int(np.ceil(dur / BAR)) + 1
    for bar in range(nb):
        t0 = bar * BAR; ch, root = CHORDS[bar % 8], ROOTS[bar % 8]
        # keys: FM e-piano, chord on 1 (long), stab on the and-of-2, slight per-note detune = tape wow
        for at, d, v in ((0, 3.4 * B, 0.12), (1.5 * B, 0.9 * B, 0.07), (3.5 * B, 0.4 * B, 0.05)):
            for i, m in enumerate(ch):
                f = mtof(m) * 2 ** (g.normal(0, 4) / 1200)
                s = fm(f, d + 0.6, ratio=1.0, index=1.3, idx_tau=0.25, amp_tau=0.9)
                s = s * adsr(len(s), 0.004, 0.1, 0.8, 0.35)
                L['keys'].add(s, t0 + at + i * 0.012, v, pan=-0.3 + 0.2 * i)
        # bass: root on 1, fifth on the and-of-3
        for at, m, d in ((0, root, 1.4 * B), (2.5 * B, root + 7, 0.9 * B)):
            s = (sine(mtof(m), d) + 0.25 * sine(mtof(m + 12), d)) * adsr(int(d * SR), 0.01, 0.1, 0.8, 0.12)
            L['bass'].add(s, t0 + at, 0.55)
        # drums (dusty): kick 1 & and-of-2, snare 2 & 4, swung hats
        for at in (0, 1.5 * B + SWING * B):
            L['kick'].add(sine(120, 0.35, 42) * expdec(int(0.35 * SR), 0.09), t0 + at, 0.9)
        for at in (B, 3 * B):
            sn = lp(bp(noise(0.25, bar * 3 + int(at)), 900, 6000) * expdec(int(0.25 * SR), 0.06), 5000) + 0.5 * sine(190, 0.25, 150) * expdec(int(0.25 * SR), 0.04)
            L['snare'].add(sn, t0 + at + g.normal(0, 0.004), 0.45)
        for i in range(8):
            at = i * B / 2 + (SWING * B if i % 2 else 0)
            L['hats'].add(hp(noise(0.05, bar * 8 + i), 7000) * expdec(int(0.05 * SR), 0.015), t0 + at, (0.14 if i % 2 else 0.09) * g.uniform(0.7, 1.1), pan=0.3)
        for b0, bt, m in BELL:
            if bar % 8 == b0:
                L['bell'].add(fm(mtof(m), 1.8, ratio=3.5, index=1.0, idx_tau=0.04, amp_tau=0.7), t0 + bt * B, 0.1, pan=0.2)
    # vinyl crackle: hiss + sparse clicks
    n = int(dur * SR); cr = hp(noise(dur, 5 + seed), 3000) * 0.015
    pos = np.random.default_rng(9 + seed).integers(0, n, int(dur * 18)); cr[pos] += np.random.default_rng(3).uniform(-0.6, 0.6, len(pos))
    L['crackle'].add(lp(cr, 9000), 0, 1.0)
    return {k: v.render() for k, v in L.items()}


def master_bus(mixed):
    return lp(reverb(mixed, 0.16, 0.8, 5000), 11000)


def web_loop(path):
    """3 cycles rendered so tails wrap; keep the middle cycle twice -> any LOOP-long window loops seamlessly"""
    Ls = layers(3 * LOOP)
    gains = WEB_GAINS
    mixed = sum(Ls[k] * v for k, v in gains.items())
    mixed = master_bus(mixed)
    i0, i1 = int(LOOP * SR), int(2 * LOOP * SR)
    cyc = mixed[i0:i1]
    two = np.concatenate([cyc, cyc])
    wav = str(pathlib.Path(__file__).parent / 'site_loop.wav')
    write_master(two, wav, lufs=-20.0, fade_out=0)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wav, '-c:a', 'libmp3lame', '-b:a', '160k', str(path)], check=True)
    return path


if __name__ == '__main__':
    out = pathlib.Path(__file__).resolve().parent / 'site' / 'audio'; out.mkdir(exist_ok=True)
    web_loop(out / 'loop.mp3'); print('wrote site/audio/loop.mp3', LOOP)
