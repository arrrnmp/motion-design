#!/bin/bash
# Render a Blender still on the Windows GPU box and pull the PNG back.
# usage: blender/remote.sh <scene-name> [samples] [res-percent]
set -euo pipefail
NAME=${1:?scene name}; SAMPLES=${2:-256}; PCT=${3:-100}
HOST=${GPU_HOST:?set GPU_HOST=user@host (a Windows box with Blender; see run.ps1)}
ROOT=${PROJECT_ROOT:-$(pwd)}   # expects blender/<scene>.py, assets/fonts/, stills/ in the project
scp -q "$ROOT/blender/common.py" "$ROOT/blender/$NAME.py" "$ROOT/blender/run.ps1" "$ROOT"/assets/fonts/*.ttf "$HOST:mds/"
[ -d "$ROOT/assets/blender/$NAME" ] && scp -q "$ROOT/assets/blender/$NAME"/*.png "$HOST:mds/"
ssh "$HOST" powershell -NoProfile -ExecutionPolicy Bypass -File mds/run.ps1 -Name "$NAME" -Samples "$SAMPLES" -Pct "$PCT" | sed 's/\x1b\[[0-9;]*m//g'
scp -q "$HOST:mds/$NAME.png" "$ROOT/stills/$NAME.png"
echo "pulled stills/$NAME.png"
