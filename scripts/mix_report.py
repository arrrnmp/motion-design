#!/usr/bin/env python3

# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Aaron Mompié
# This file is part of motion-design (https://github.com/arrrnmp/motion-design).
# Licensed under the GNU Affero General Public License, version 3 or later.

"""Measure a mix so you can judge it without hearing it.

Usage: mix_report.py --mix mix.wav [--stems drums.wav bass.wav lead.wav ...]
                     [--target -16] [--tol 1.5] [--json out.json]

Needs: ffmpeg on PATH, numpy, scipy. Decodes everything through ffmpeg (48 kHz),
so any format ffmpeg reads works.

Reports
  mix    integrated LUFS, LRA, true peak, PLR (peak-to-loudness), short-term (3 s)
         loudness timeline with the spans that stray from the target, mono
         fold-down loss, stereo correlation, low-end (<120 Hz) correlation
  stems  per stem: loudness, peak, crest, and its share of each frequency band
         (share = stem energy / sum of all stems' energy in that band)
  clash  band + stem pairs that sit within 6 dB of each other for much of the time
         both are present in that band: candidates for EQ carving, ducking or muting

Exit code is 0 unless the mix cannot be read; findings are printed, not enforced.
"""
import argparse, json, re, subprocess, sys
import numpy as np
from scipy.signal import stft

SR = 48000
BANDS = [("sub", 20, 60), ("bass", 60, 120), ("low", 120, 250), ("low-mid", 250, 500),
         ("mid", 500, 1000), ("upper-mid", 1000, 2000), ("presence", 2000, 4000),
         ("brilliance", 4000, 8000), ("air", 8000, 20000)]


def load(path):
    """Decode to float32 stereo at SR -> array (n, 2)."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                       capture_output=True)
    if r.returncode != 0 or not r.stdout:
        sys.exit(f"cannot read {path}: {r.stderr.decode()[:200]}")
    return np.frombuffer(r.stdout, dtype=np.float32).reshape(-1, 2)


def ebur128(path):
    """Integrated LUFS, LRA, true peak and the 3 s short-term series (0.1 s steps) via ffmpeg."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af",
                        "ebur128=peak=true:metadata=1,ametadata=print:key=lavfi.r128.S:file=-",
                        "-f", "null", "-"], capture_output=True, text=True)
    st = [float(x) for x in re.findall(r"lavfi\.r128\.S=(-?[\d.]+)", r.stdout)]
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    g = lambda pat: (lambda m: float(m[-1]) if m else None)(re.findall(pat, tail))
    return dict(I=g(r"I:\s+(-?[\d.]+) LUFS"), LRA=g(r"LRA:\s+(-?[\d.]+) LU"),
                TP=g(r"Peak:\s+(-?[\d.]+) dBFS"), S=[s for s in st if s > -70])


def db(x):
    return 20 * np.log10(max(float(x), 1e-9))


def band_energy(x):
    """Mono STFT -> (bands, frames) energy, using ~93 ms windows."""
    f, t, Z = stft(x, fs=SR, nperseg=4096, noverlap=2048)
    P = np.abs(Z) ** 2
    return np.array([P[(f >= lo) & (f < hi)].sum(axis=0) for _, lo, hi in BANDS])


def mix_stats(x, meas, target, tol):
    out = {}
    L, R = x[:, 0].astype(np.float64), x[:, 1].astype(np.float64)
    mono = (L + R) / 2
    out["integrated_lufs"], out["lra"], out["true_peak_dbtp"] = meas["I"], meas["LRA"], meas["TP"]
    if meas["I"] is not None and meas["TP"] is not None:
        out["plr_db"] = round(meas["TP"] - meas["I"], 1)
    rms = lambda a: np.sqrt(np.mean(a ** 2)) + 1e-12
    out["mono_fold_loss_db"] = round(db(rms(mono)) - db(rms(np.sqrt((L ** 2 + R ** 2) / 2))), 2)
    out["stereo_correlation"] = round(float(np.corrcoef(L, R)[0, 1]), 3) if rms(x) > 1e-6 else None
    from scipy.signal import butter, sosfilt
    sos = butter(4, 120, "low", fs=SR, output="sos")
    lo_l, lo_r = sosfilt(sos, L), sosfilt(sos, R)
    out["lowend_correlation_lt120hz"] = round(float(np.corrcoef(lo_l, lo_r)[0, 1]), 3) if rms(lo_l) > 1e-6 else None
    S = np.array(meas["S"])
    if len(S) > 30:
        ref = target if target is not None else meas["I"]
        out["short_term_min_max_lufs"] = [round(float(S.min()), 1), round(float(S.max()), 1)]
        bad, start = [], None
        for i, s in enumerate(S):  # 0.1 s per value; skip the first 3 s (window still filling)
            off = i >= 30 and abs(s - ref) > tol
            if off and start is None: start = i
            if not off and start is not None:
                if i - start >= 20: bad.append((start / 10, i / 10, round(float(S[start:i].mean() - ref), 1)))
                start = None
        if start is not None and len(S) - start >= 20: bad.append((start / 10, len(S) / 10, round(float(S[start:].mean() - ref), 1)))
        out["short_term_outside_tolerance"] = bad  # (from_s, to_s, mean_dev_LU)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mix", required=True)
    ap.add_argument("--stems", nargs="*", default=[])
    ap.add_argument("--target", type=float, help="target integrated LUFS (default: the mix's own)")
    ap.add_argument("--tol", type=float, default=1.5, help="short-term LU tolerance around the target")
    ap.add_argument("--json")
    a = ap.parse_args()

    mix = load(a.mix)
    meas = ebur128(a.mix)
    rep = {"mix": mix_stats(mix, meas, a.target, a.tol), "stems": {}, "clashes": []}
    m = rep["mix"]
    print(f"MIX  {a.mix}  ({len(mix) / SR:.1f}s)")
    print(f"  integrated {m['integrated_lufs']} LUFS   LRA {m['lra']} LU   true peak {m['true_peak_dbtp']} dBTP   PLR {m.get('plr_db')} dB")
    print(f"  mono fold-down {m['mono_fold_loss_db']} dB   L/R correlation {m['stereo_correlation']}   <120 Hz correlation {m['lowend_correlation_lt120hz']}")
    if "short_term_min_max_lufs" in m:
        print(f"  short-term (3 s) range {m['short_term_min_max_lufs'][0]} .. {m['short_term_min_max_lufs'][1]} LUFS")
        for s, e, d in m["short_term_outside_tolerance"]:
            print(f"    outside ±{a.tol} LU: {s:.1f}s–{e:.1f}s  ({d:+} LU vs target)")
    if m["lowend_correlation_lt120hz"] is not None and m["lowend_correlation_lt120hz"] < 0.9:
        print("  ! low end is not mono enough (<120 Hz correlation < 0.9)")
    if m["mono_fold_loss_db"] < -4:
        print("  ! mono fold-down loses more than 4 dB (uncorrelated stereo is about -3): phase cancellation")

    if a.stems:
        E, names = [], []
        for p in a.stems:
            x = load(p)
            mono = x.mean(axis=1)
            mm = ebur128(p)
            pk, r = db(np.abs(x).max()), db(np.sqrt(np.mean(mono ** 2)))
            rep["stems"][p] = dict(lufs=mm["I"], peak_dbfs=round(pk, 1), crest_db=round(pk - r, 1))
            E.append(band_energy(mono)); names.append(p.split("/")[-1])
        n = min(e.shape[1] for e in E)
        E = np.array([e[:, :n] for e in E])            # (stems, bands, frames)
        tot = E.sum(axis=0) + 1e-20                    # (bands, frames)
        print("\nSTEMS   (loudness solo | peak | crest | share of band energy across the stems)")
        print(f"  {'':18}{'LUFS':>7}{'peak':>7}{'crest':>7}   " + " ".join(f"{b[0][:6]:>7}" for b in BANDS))
        band_tot = E.sum(axis=(0, 2)) + 1e-20
        for i, nm in enumerate(names):
            sh = E[i].sum(axis=1) / band_tot
            s = rep["stems"][a.stems[i]]
            s["band_share"] = {b[0]: round(float(v), 2) for b, v in zip(BANDS, sh)}
            print(f"  {nm[:18]:18}{str(s['lufs']):>7}{s['peak_dbfs']:>7}{s['crest_db']:>7}   " + " ".join(f"{v * 100:6.0f}%" for v in sh))
        # clashes: per band and stem pair, look only at frames where BOTH are present in that
        # band (a transient kick vs a steady bass counts on the kick's frames), and ask how
        # often the weaker one is within 6 dB of the stronger one.
        gmax = E.max()
        for bi, (bn, lo, hi) in enumerate(BANDS):
            bmax = E[:, bi, :].max()
            if bmax < gmax * 1e-4: continue          # band is essentially empty in this song
            g = bmax * 1e-3                          # "present" = within 30 dB of the band's peak
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    x, y = E[i, bi], E[j, bi]
                    both = (x > g) & (y > g)
                    if both.sum() < 10: continue     # < ~0.4 s of shared time
                    close = both & (np.maximum(x, y) < 4 * np.minimum(x, y))
                    frac = close.sum() / both.sum()
                    if frac > 0.4:
                        rep["clashes"].append(dict(band=bn, hz=[lo, hi], stems=[names[i], names[j]],
                                                   fraction=round(float(frac), 2), seconds=round(float(close.sum() * 2048 / SR), 1)))
        rep["clashes"].sort(key=lambda c: -c["fraction"])
        print("\nCLASHES (same band, within 6 dB of each other, over the time both are present there)")
        if not rep["clashes"]:
            print("  none")
        for c in rep["clashes"][:12]:
            print(f"  {c['band']:>10} {c['hz'][0]}–{c['hz'][1]} Hz  {c['stems'][0]} vs {c['stems'][1]}  {c['fraction'] * 100:.0f}% of shared time ({c['seconds']}s)")
        if rep["clashes"]:
            print("  → pick an owner per clash: carve the other with EQ, duck it, move it in time, or mute it")

    if a.json:
        json.dump(rep, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
