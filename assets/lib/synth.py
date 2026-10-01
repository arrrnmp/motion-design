"""Tiny deterministic synth + mixer for the style clips (numpy/scipy). 48 kHz stereo float32.

Everything is placed by time in seconds, computed from the same frame schedules as the visuals,
so sound stays in sync when timing changes.
"""
import numpy as np, subprocess, json, re, soundfile as sf
from scipy.signal import butter, sosfilt, lfilter

SR = 48000
rng = np.random.default_rng(7)


def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def t_(d): return np.arange(int(d * SR)) / SR


class Mix:
    def __init__(self, dur):
        self.buf = np.zeros((int(dur * SR) + SR, 2), np.float32)
        self.dur = dur

    def add(self, sig, at, gain=1.0, pan=0.0):
        if sig.ndim == 1:
            l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
            sig = np.stack([sig * l * 1.414, sig * r * 1.414], 1)
        i = int(at * SR)
        if i >= len(self.buf) or i + len(sig) <= 0: return
        if i < 0: sig, i = sig[-i:], 0
        n = min(len(sig), len(self.buf) - i)
        self.buf[i:i + n] += sig[:n] * gain

    def bus(self):
        return Mix(self.dur)

    def render(self):
        return self.buf[:int(self.dur * SR)]


# ---------------------------------------------------------------- envelopes & oscillators
def adsr(n, a=0.005, d=0.05, s=0.6, r=0.05):
    e = np.ones(n, np.float32) * s
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    A = min(A, n); e[:A] = np.linspace(0, 1, A, endpoint=False)
    D = min(D, max(0, n - A)); e[A:A + D] = np.linspace(1, s, D, endpoint=False)
    if R and n > R: e[-R:] *= np.linspace(1, 0, R)
    return e


def expdec(n, tau): return np.exp(-np.arange(n) / (tau * SR)).astype(np.float32)


def pulse(f, d, duty=0.5, vib=0.0, vibf=5.5):
    t = t_(d); ph = np.cumsum(np.full(len(t), f) * (1 + vib * np.sin(2 * np.pi * vibf * t)) / SR)
    return np.where((ph % 1) < duty, 1.0, -1.0).astype(np.float32)


def tri(f, d):
    ph = (t_(d) * f) % 1
    return (4 * np.abs(ph - 0.5) - 1).astype(np.float32)


def sine(f, d, f_end=None):
    t = t_(d); fr = np.full(len(t), f) if f_end is None else f * (f_end / f) ** (t / d)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR).astype(np.float32)


def noise(d, seed=None):
    g = np.random.default_rng(seed) if seed is not None else rng
    return g.uniform(-1, 1, int(d * SR)).astype(np.float32)


def nes_noise(d, period=8, seed=1):
    """stepped (sample-and-hold) noise like a 2A03 noise channel"""
    n = noise(d, seed); return np.repeat(n[::period], period)[:len(n)]


def fm(f, d, ratio=1.0, index=2.0, idx_tau=0.3, amp_tau=1.2):
    t = t_(d); idx = index * np.exp(-t / idx_tau)
    return (np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * ratio * t)) * np.exp(-t / amp_tau)).astype(np.float32)


def pluck(f, d, decay=0.996, bright=0.5, seed=None):
    """Karplus-Strong"""
    N = max(2, int(SR / f)); n = int(d * SR)
    g = np.random.default_rng(seed if seed is not None else int(f * 13))
    buf = g.uniform(-1, 1, N) * 1.0
    buf = lfilter([bright, 1 - bright], [1], buf)
    out = np.zeros(n, np.float32)
    for i in range(0, n, N):
        seg = buf[:min(N, n - i)]; out[i:i + len(seg)] = seg
        buf = decay * 0.5 * (buf + np.roll(buf, -1))
    return out


# ---------------------------------------------------------------- filters & fx
def lp(x, fc, order=2): return sosfilt(butter(order, min(fc, SR * 0.45), 'low', fs=SR, output='sos'), x, axis=0).astype(np.float32)
def hp(x, fc, order=2): return sosfilt(butter(order, fc, 'high', fs=SR, output='sos'), x, axis=0).astype(np.float32)
def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo, min(hi, SR * 0.45)], 'band', fs=SR, output='sos'), x, axis=0).astype(np.float32)


def sweep_bp(x, f0, f1, q=4.0, blocks=24):
    """band-pass whose centre moves f0 -> f1 (piecewise), for scrapes and whooshes"""
    out = np.zeros_like(x); n = len(x); step = max(1, n // blocks)
    for i in range(0, n, step):
        c = f0 * (f1 / f0) ** (i / n); seg = x[max(0, i - 512):i + step]
        y = bp(seg, c / (1 + 1 / q), c * (1 + 1 / q)); out[i:i + step] = y[-len(out[i:i + step]):] if len(y) >= len(out[i:i + step]) else 0
    return out


def reverb(x, mix=0.25, size=1.0, damp=3500):
    """small Freeverb-ish: 6 parallel combs + 2 allpasses, per channel"""
    if x.ndim == 1: x = np.stack([x, x], 1)
    out = np.zeros_like(x)
    for ch, off in ((0, 0), (1, 23)):
        s = x[:, ch]; acc = np.zeros_like(s)
        for d, g in ((1116, .84), (1188, .83), (1277, .82), (1356, .81), (1422, .8), (1491, .79)):
            D = int((d + off) * size * SR / 44100); a = np.zeros(D + 1); a[0] = 1; a[D] = -g
            acc += lfilter([1], a, lp(s, damp, 1))
        for d in (556, 441):
            D = int((d + off) * SR / 44100); b = np.zeros(D + 1); b[0] = -0.5; b[D] = 1; a = np.zeros(D + 1); a[0] = 1; a[D] = -0.5
            acc = lfilter(b, a, acc)
        out[:, ch] = acc / 6
    return (x * (1 - mix) + out * mix).astype(np.float32)


def softclip(x, drive=1.0): return np.tanh(x * drive) / np.tanh(drive)


# ---------------------------------------------------------------- master + mux
def write_master(buf, path, lufs=-16.0, tp=-2.0, fade_in=0.0, fade_out=0.3):
    x = buf.copy()
    if fade_in: n = int(fade_in * SR); x[:n] *= np.linspace(0, 1, n)[:, None]
    if fade_out: n = int(fade_out * SR); x[-n:] *= np.linspace(1, 0, n)[:, None]
    x = softclip(x / (np.abs(x).max() + 1e-9) * 0.9, 1.2)
    raw = str(path).replace('.wav', '.raw.wav'); sf.write(raw, x, SR, subtype='FLOAT')
    # two-pass loudnorm
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', raw, '-af', f'loudnorm=I={lufs}:TP={tp}:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    m = json.loads(re.findall(r'\{[^{}]+\}', r.stderr)[-1])
    af = (f"loudnorm=I={lufs}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', af, '-ar', str(SR), str(path)], check=True)
    return path


def mux(video, wav, out):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], check=True)
