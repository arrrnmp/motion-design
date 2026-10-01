#!/usr/bin/env bash

# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Aaron Mompié
# This file is part of motion-design (https://github.com/arrrnmp/motion-design).
# Licensed under the GNU Affero General Public License, version 3 or later.

# Tile stills from a video into one labelled image for quick review.
# Usage: contact_sheet.sh <video> <out.png> [t1 t2 ...]   (seconds; default: 12 evenly spaced)
#        COLS=4 WIDTH=480 contact_sheet.sh ...
set -euo pipefail
VIDEO="${1:?video path required}"
OUT="${2:?output png required}"
shift 2
COLS="${COLS:-4}"
WIDTH="${WIDTH:-480}"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if [ "$#" -eq 0 ]; then
  DUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO")"
  set -- $(python3 -c "d=float('$DUR'); n=12; print(' '.join(f'{d*(i+0.5)/n:.3f}' for i in range(n)))")
fi

i=0
for t in "$@"; do
  f="$(printf '%s/%04d.png' "$TMP" "$i")"
  ffmpeg -v error -y -ss "$t" -i "$VIDEO" -frames:v 1 -vf "scale=${WIDTH}:-2" "$f"
  # Label with Pillow (many ffmpeg builds lack drawtext); unlabelled if Pillow is missing
  python3 -c '
import sys
from PIL import Image, ImageDraw, ImageFont
im = Image.open(sys.argv[1]).convert("RGB"); d = ImageDraw.Draw(im)
try: font = ImageFont.load_default(size=18)
except TypeError: font = ImageFont.load_default()
x0, y0, x1, y1 = d.textbbox((8, 6), sys.argv[2], font=font)
d.rectangle((x0 - 4, y0 - 3, x1 + 4, y1 + 3), fill=(0, 0, 0))
d.text((8, 6), sys.argv[2], fill=(255, 255, 255), font=font)
im.save(sys.argv[1])
' "$f" "t=${t}s" 2>/dev/null || true
  i=$((i+1))
done

N="$i"
[ "$N" -lt "$COLS" ] && COLS="$N"
ROWS=$(( (N + COLS - 1) / COLS ))
ffmpeg -v error -y -framerate 1 -i "$TMP/%04d.png" \
  -vf "tile=${COLS}x${ROWS}:padding=4:margin=4:color=0x202020" -frames:v 1 "$OUT"
[ -s "$OUT" ] && echo "wrote $OUT ($N frames)"
