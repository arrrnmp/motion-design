#!/usr/bin/env python3

# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Aaron Mompié
# This file is part of motion-design (https://github.com/arrrnmp/motion-design).
# Licensed under the GNU Affero General Public License, version 3 or later.

"""Labelled contact sheet of every PNG/JPG in a folder (sorted by name), for comparing direction stills side by side.

  stills_grid.py <folder> <out.jpg> [--cols 3] [--width 960]
Squint at the result: if two directions look like siblings, redo one (see references/direction.md).
"""
import argparse, pathlib
from PIL import Image, ImageDraw, ImageFont
ap = argparse.ArgumentParser(); ap.add_argument("folder"); ap.add_argument("out"); ap.add_argument("--cols", type=int, default=3); ap.add_argument("--width", type=int, default=960)
A = ap.parse_args()
files = sorted(p for p in pathlib.Path(A.folder).iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg"))
tw = A.width; th = tw * 9 // 16; lab, pad = 56, 24
rows = -(-len(files) // A.cols)
sheet = Image.new("RGB", (pad + A.cols * (tw + pad), pad + rows * (th + lab + pad)), "#e9e6df")
d = ImageDraw.Draw(sheet)
font = None
for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"):
    try: font = ImageFont.truetype(f, 30); break
    except OSError: pass
font = font or ImageFont.load_default()
for i, p in enumerate(files):
    x, y = pad + (i % A.cols) * (tw + pad), pad + (i // A.cols) * (th + lab + pad)
    sheet.paste(Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS), (x, y))
    d.text((x + 4, y + th + 12), p.stem.upper().replace("-", "  ", 1).replace("-", " "), fill="#1c1a17", font=font)
sheet.save(A.out, quality=88); print(A.out, sheet.size, len(files))
