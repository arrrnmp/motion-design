#!/usr/bin/env bash

# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Aaron Mompié
# This file is part of motion-design (https://github.com/arrrnmp/motion-design).
# Licensed under the GNU Affero General Public License, version 3 or later.

# Side-by-side before | after | amplified difference, for checking a change did what you meant.
# Usage: compare_frames.sh <before.png> <after.png> <out.png>
set -euo pipefail
A="${1:?before image}"; B="${2:?after image}"; OUT="${3:?output image}"

ffmpeg -v error -y -i "$A" -i "$B" -filter_complex "
  [0:v]format=gbrp[a0]; [1:v]format=gbrp[b0];
  [b0][a0]scale2ref[b][a];
  [a]split[a1][a2]; [b]split[b1][b2];
  [a2][b2]blend=all_mode=difference,eq=contrast=4:brightness=0.05[d];
  [a1][b1][d]hstack=inputs=3,format=rgb24" -frames:v 1 "$OUT"

# Report how much changed (mean absolute difference, 0 = identical)
python3 - "$A" "$B" <<'PY' 2>/dev/null || true
import sys
from PIL import Image, ImageChops, ImageStat
a = Image.open(sys.argv[1]).convert("RGB")
b = Image.open(sys.argv[2]).convert("RGB").resize(a.size)
d = ImageChops.difference(a, b)
m = sum(ImageStat.Stat(d).mean) / 3
bbox = d.point(lambda v: 255 if v > 16 else 0).getbbox()
print(f"mean abs diff: {m:.2f}/255; changed region: {bbox or 'none'}")
PY
echo "wrote $OUT"
