#!/usr/bin/env python3

# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Aaron Mompié
# This file is part of motion-design (https://github.com/arrrnmp/motion-design).
# Licensed under the GNU Affero General Public License, version 3 or later.

"""Pre-delivery checks for a rendered video.

Usage: check_delivery.py <video> [--lufs -16] [--tol 1.0] [--width 1920 --height 1080]
                         [--fps 30] [--duration 60.0] [--srt captions.srt]

Reports container/stream facts, integrated loudness + true peak, silence gaps,
black segments, and (optionally) caption sanity. Exits non-zero if any check fails.
"""
import argparse, json, re, subprocess, sys


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path])
    if r.returncode != 0:
        sys.exit(f"ffprobe failed: {r.stderr.strip()}")
    return json.loads(r.stdout)


def loudness(path):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"])
    txt = r.stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", txt)
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", txt)
    return (float(i[-1]) if i else None, float(tp[-1]) if tp else None)


def silences(path, noise="-50dB", d=1.0):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", f"silencedetect=noise={noise}:d={d}", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", r.stderr)]
    return list(zip(starts, ends + [None] * (len(starts) - len(ends))))


def blacks(path, d=0.5):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vf", f"blackdetect=d={d}:pix_th=0.05", "-an", "-f", "null", "-"])
    return re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", r.stderr)


def srt_check(path, duration):
    ts = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)")
    to_s = lambda h, m, s, ms: int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    cues, problems = [], []
    for line in open(path, encoding="utf-8"):
        m = ts.search(line)
        if m:
            g = m.groups()
            cues.append((to_s(*g[:4]), to_s(*g[4:])))
    prev_end = 0.0
    for n, (a, b) in enumerate(cues, 1):
        if b <= a:
            problems.append(f"cue {n}: end <= start")
        if a < prev_end - 0.001:
            problems.append(f"cue {n}: overlaps previous")
        if duration and b > duration + 0.05:
            problems.append(f"cue {n}: ends after video ({b:.2f}s > {duration:.2f}s)")
        prev_end = b
    return len(cues), problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--lufs", type=float, default=-16.0)
    ap.add_argument("--tol", type=float, default=1.0, help="LUFS tolerance")
    ap.add_argument("--max-tp", type=float, default=-1.0, help="max true peak dBTP")
    ap.add_argument("--width", type=int); ap.add_argument("--height", type=int)
    ap.add_argument("--fps", type=float); ap.add_argument("--duration", type=float)
    ap.add_argument("--srt")
    a = ap.parse_args()

    fails = []
    info = probe(a.video)
    dur = float(info["format"].get("duration", 0))
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    au = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)

    print(f"file: {a.video}")
    print(f"duration: {dur:.3f}s  size: {int(info['format'].get('size', 0)) / 1e6:.1f} MB")
    if v:
        num, den = (v.get("avg_frame_rate") or "0/1").split("/")
        fps = float(num) / float(den) if float(den) else 0
        print(f"video: {v['codec_name']} {v.get('profile','')} {v['width']}x{v['height']} {fps:.3f}fps {v.get('pix_fmt')}")
        if a.width and v["width"] != a.width: fails.append(f"width {v['width']} != {a.width}")
        if a.height and v["height"] != a.height: fails.append(f"height {v['height']} != {a.height}")
        if a.fps and abs(fps - a.fps) > 0.01: fails.append(f"fps {fps:.3f} != {a.fps}")
        if v.get("pix_fmt") not in ("yuv420p", "yuvj420p"): print("  note: pix_fmt is not yuv420p (may not play everywhere)")
        for s, e in blacks(a.video):
            print(f"  black segment: {s}s–{e}s")
    else:
        fails.append("no video stream")
    if a.duration and abs(dur - a.duration) > 0.1:
        fails.append(f"duration {dur:.2f}s != {a.duration}s")

    if au:
        print(f"audio: {au['codec_name']} {au.get('sample_rate')}Hz {au.get('channels')}ch")
        i, tp = loudness(a.video)
        print(f"loudness: {i} LUFS integrated, true peak {tp} dBTP (target {a.lufs}±{a.tol}, TP ≤ {a.max_tp})")
        if i is None or abs(i - a.lufs) > a.tol: fails.append(f"loudness {i} LUFS off target {a.lufs}")
        if tp is not None and tp > a.max_tp: fails.append(f"true peak {tp} > {a.max_tp}")
        for s, e in silences(a.video):
            print(f"  silence ≥1s: {s:.2f}s–{e if e is None else round(e, 2)}s")
    else:
        print("audio: none")

    if a.srt:
        n, probs = srt_check(a.srt, dur)
        print(f"captions: {n} cues")
        for p in probs:
            fails.append(f"srt {p}")

    print()
    if fails:
        print("FAIL:")
        for f in fails: print(f"  - {f}")
        sys.exit(1)
    print("OK: all checks passed")


if __name__ == "__main__":
    main()
