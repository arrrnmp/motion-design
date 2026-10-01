#!/usr/bin/env bash

# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Aaron Mompié
# This file is part of motion-design (https://github.com/arrrnmp/motion-design).
# Licensed under the GNU Affero General Public License, version 3 or later.

# Inventory this machine for motion-design work: hardware + relevant tools.
# Usage: inventory.sh            (run locally)
#        ssh host 'bash -s' < inventory.sh   (run on a remote Unix machine)
set -u

section() { printf '\n== %s ==\n' "$1"; }

section "System"
OS="$(uname -s)"
echo "OS: $OS $(uname -r) $(uname -m)"
case "$OS" in
  Darwin)
    sw_vers 2>/dev/null | tr '\n' ' '; echo
    echo "CPU: $(sysctl -n machdep.cpu.brand_string 2>/dev/null) ($(sysctl -n hw.ncpu) threads)"
    echo "RAM: $(( $(sysctl -n hw.memsize) / 1073741824 )) GB"
    system_profiler SPDisplaysDataType 2>/dev/null | grep -E 'Chipset Model|Total Number of Cores|VRAM' | sed 's/^ */GPU: /'
    ;;
  Linux)
    grep -m1 'model name' /proc/cpuinfo | sed 's/.*: /CPU: /'; echo "Threads: $(nproc)"
    free -g | awk '/Mem:/ {print "RAM: " $2 " GB"}'
    if command -v nvidia-smi >/dev/null; then
      nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader | sed 's/^/GPU: /'
    else
      lspci 2>/dev/null | grep -iE 'vga|3d' | sed 's/^/GPU: /'
    fi
    ;;
esac
echo "Disk (cwd): $(df -h . | awk 'NR==2 {print $4 " free of " $2}')"

section "Tools"
check() {  # name, command...
  local name="$1"; shift
  if out="$("$@" 2>&1 | head -n1)" && [ -n "$out" ]; then
    printf '  [x] %-16s %s\n' "$name" "$out"
  else
    printf '  [ ] %-16s\n' "$name"
  fi
}
has() { command -v "$1" >/dev/null 2>&1; }
ver() { has "$1" && "$@"; }

check ffmpeg        ver ffmpeg -hide_banner -version
check ffprobe       ver ffprobe -version
check node          ver node --version
check npm           ver npm --version
check bun           ver bun --version
check python3       ver python3 --version
check uv            ver uv --version
# GUI installs often hide their CLI inside the app bundle (macOS) -- look there too.
app_bin() {  # name, bundle path, binary relative path, version flag
  local name="$1" bin="$2/Contents/MacOS/$3"; shift 3
  if has "$name"; then "$name" "$@" 2>&1 | head -n1
  elif [ -x "$bin" ]; then echo "$bin (not on PATH: symlink or use absolute path) $("$bin" "$@" 2>&1 | head -n1)"
  fi
}
check blender       app_bin blender /Applications/Blender.app Blender --version
check manim         ver manim --version
check inkscape      app_bin inkscape /Applications/Inkscape.app inkscape --version
check aseprite      app_bin aseprite /Applications/Aseprite.app aseprite --version
check krita         sh -c 'command -v krita || ls -d /Applications/krita.app 2>/dev/null'
check godot         sh -c 'command -v godot || ls -d /Applications/Godot.app 2>/dev/null'
check obs           sh -c 'command -v obs || ls -d /Applications/OBS.app 2>/dev/null'
check comfyui       sh -c 'ls -d /Applications/ComfyUI.app ~/ComfyUI 2>/dev/null | head -n1'
check brew          ver brew --version
check gh            ver gh --version
check vtracer       ver vtracer --version
check potrace       ver potrace --version
check resvg         ver resvg --version
check rsvg-convert  ver rsvg-convert --version
check magick        ver magick --version
check rubberband    ver rubberband --version
check sox           ver sox --version
check sclang        sh -c 'command -v sclang'
check ghci          ver ghci --version
check sonic-pi      sh -c 'command -v sonic-pi || ls -d /Applications/Sonic\ Pi.app 2>/dev/null'
check fluidsynth    ver fluidsynth --version
check whisper-cpp   sh -c 'command -v whisper-cli || command -v whisper-cpp || command -v whisper'
check reaper        sh -c 'command -v reaper || ls -d /Applications/REAPER.app 2>/dev/null'
check chrome        sh -c 'ls -d "/Applications/Google Chrome.app" 2>/dev/null || command -v google-chrome || command -v chromium'
check ollama        ver ollama --version

section "Python packages"
if has python3; then
python3 - <<'PY'
import importlib.util as u
pkgs = ["torch","diffusers","transformers","faster_whisper","whisper","whisperx","librosa",
        "pyloudnorm","pedalboard","soundfile","PIL","numpy","cv2","playwright","manim",
        "resemblyzer","audiocraft","TTS","kokoro","f5_tts"]
for p in pkgs:
    print(f"  [{'x' if u.find_spec(p) else ' '}] {p}")
try:
    import torch
    print("  torch cuda:", torch.cuda.is_available(), "| mps:", getattr(torch.backends, "mps", None) and torch.backends.mps.is_available())
except Exception:
    pass
PY
fi

section "Node (global + cwd)"
has npm && npm ls -g --depth=0 2>/dev/null | grep -iE 'remotion|motion-canvas|playwright|puppeteer|lottie|strudel' || true
[ -f package.json ] && grep -iE '"(remotion|@remotion/[^"]+|@motion-canvas/[^"]+|three|lottie[^"]*|@strudel/[^"]+|playwright|puppeteer)"' package.json || true

section "Agent skills (installed)"
for d in "$HOME/.claude/skills" "$HOME/.agents/skills" ./.claude/skills ./.agents/skills; do
  [ -d "$d" ] && printf '  %s: %s\n' "$d" "$(ls "$d" 2>/dev/null | tr '\n' ' ')"
done
echo "  Look here for: remotion-best-practices, blender, manim, threejs, shader, svg, pixel-art, lottie, typography."
echo "  Missing something relevant? Search: npx skills find <query>   (Remotion: npx skills add remotion-dev/skills)"

section "Other apps worth knowing about (/Applications)"
ls /Applications ~/Applications 2>/dev/null | grep -iE 'blender|inkscape|aseprite|krita|godot|obs|resolve|final cut|motion|logic|garageband|figma|affinity|pixelmator|comfy|draw things|lm studio|davinci|cavalry|rive|unity|unreal' | sed 's/^/  /' || true

section "Fonts (count)"
case "$OS" in
  Darwin) ls ~/Library/Fonts /Library/Fonts /System/Library/Fonts 2>/dev/null | wc -l | sed 's/^ */  files: /' ;;
  Linux)  has fc-list && fc-list | wc -l | sed 's/^/  fonts: /' ;;
esac
