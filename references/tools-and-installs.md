# Tools, Skills and Installing What Helps

Inventory is not just "what is here". It is "what would make this project better, and can I get it in a few minutes". Free, local, no-account tools and skills are yours to install; log each one.

## Install policy

| Category | Action |
|---|---|
| Free/open-source, local, no account (Remotion skills, npm/pip packages, Homebrew formulae/casks, Blender, Inkscape, Aseprite-from-source, fonts under OFL) | **Install without asking**, into project-local or user-level locations. Note it in the project log. Prefer per-project venvs / `npm i` in the project over global installs |
| Large downloads (over ~2 GB: models, Blender, Xcode components) | Tell the user size and purpose in the inventory summary, then proceed unless they object, or ask if disk is tight |
| Paid, licensed or subscription software | Don't buy. Mention it only if it would clearly matter, and use a free alternative |
| Anything needing an account, API key, payment, or uploading the user's content | Ask first |
| Third-party skills/plugins | Prefer official or well-known publishers; read what a skill does before installing (skills are instructions that steer you) |

## Skills first

1. **Check what's installed**: `ls ~/.claude/skills ~/.agents/skills .claude/skills .agents/skills 2>/dev/null`, plus any plugin list your harness exposes. `inventory.sh` prints these.
2. **Search for what's missing** using the `find-skills` skill (`npx skills find <query>`), the harness's skill/plugin search tools if it has them, and the web. Query by *tool and technique*, not just "video": `remotion`, `blender`, `manim`, `three.js`, `shaders`, `svg animation`, `pixel art`, `lottie`, `d3`, `ffmpeg`, `typography`, `color palette`, `sound design`.
3. **Install what clears the bar**, e.g.:
   - Remotion → `npx skills add remotion-dev/skills` (official; includes `remotion-best-practices`: animation, timing, sequencing, captions, audio, fonts, transitions, 3D). **If you are using Remotion at all, install this before writing any Remotion code.**
   - Motion Canvas, Manim, three.js/react-three-fiber, Blender, GSAP, Lottie, Rive: search for their skills too.
4. **Read the skill after installing**, not just install it. A skill nobody read costs context and gives nothing.
5. New skills may only load in a fresh session: if the harness can't hot-load them, read their `SKILL.md` files directly and follow them.

## Finding tools that aren't on PATH

GUI installs hide their command-line binaries inside the app bundle. `command -v blender` failing means nothing.

| Tool | macOS | Windows | Linux |
|---|---|---|---|
| Blender | `/Applications/Blender.app/Contents/MacOS/Blender` (run `-b -P script.py`) | `C:\Program Files\Blender Foundation\Blender *\blender.exe` | `blender`, Flatpak, snap |
| Inkscape | `/Applications/Inkscape.app/Contents/MacOS/inkscape` | `C:\Program Files\Inkscape\bin\inkscape.exe` | `inkscape` |
| Aseprite | `/Applications/Aseprite.app/Contents/MacOS/aseprite` | Steam or `C:\Program Files\Aseprite` | `aseprite` |
| Krita | `/Applications/krita.app/Contents/MacOS/krita` | `C:\Program Files\Krita (x64)\bin\krita.exe` | `krita` |
| Godot | `/Applications/Godot.app/Contents/MacOS/Godot` | exe wherever unpacked | `godot` |
| OBS | `/Applications/OBS.app/Contents/MacOS/OBS` | `C:\Program Files\obs-studio` | `obs` |
| REAPER | `/Applications/REAPER.app/Contents/MacOS/REAPER` | `C:\Program Files\REAPER (x64)` | `reaper` |
| Sonic Pi | `/Applications/Sonic Pi.app` | `C:\Program Files\Sonic Pi` | `sonic-pi` |
| SuperCollider | `/Applications/SuperCollider.app/Contents/MacOS/sclang` | `C:\Program Files\SuperCollider*` | `sclang` |
| Chrome/Chromium | `/Applications/Google Chrome.app`, `/Applications/Chromium.app` | Program Files | `google-chrome`, `chromium` |

Also look in `mdfind "kMDItemKind == 'Application'"`-style listings or `ls /Applications ~/Applications` for anything else relevant (Affinity, Figma, DaVinci Resolve, Motion, Final Cut, Logic, GarageBand, LM Studio, ComfyUI, Draw Things). Note which are scriptable.

Once found, symlink or alias (`~/.local/bin/blender`) or record the absolute path in the project notes so build scripts use it.

## Free things worth installing on demand

- **Homebrew (macOS)**: `brew install ffmpeg imagemagick potrace inkscape blender sox rubberband fluid-synth resvg vtracer` (casks for GUI apps: `brew install --cask blender inkscape`). Check `brew search <name>` before giving up.
- **Node**: `remotion`, `@remotion/*`, `@motion-canvas/*`, `three`, `@react-three/fiber`, `gsap`, `d3`, `matter-js`, `roughjs`, `p5`, `lottie-web`, `@rive-app/canvas`, `playwright`, `@strudel/*`, `opentype.js`/`@chenglou/pretext` for text measurement.
- **Python** (in a venv via `uv`): `manim`, `pedalboard`, `librosa`, `pyloudnorm`, `faster-whisper`, `kokoro`, `pillow`, `numpy`, `opencv-python`, `moderngl` (offscreen GL shaders), `skia-python`, `cairosvg`, `pygame` (pixel work), `diffusers` (if the machine has GPU/MPS headroom).
- **Hand-made looks in the browser**: p5.js 2 + p5.brush 2 (pigment brushes, watercolour fills, hatching; templates
  load them from jsDelivr), Hershey/EMS single-stroke fonts (`assets/lib/hershey.json`, from the `hersheytext` npm
  package), fonttools (`fonttools varLib.instancer` to cut a static weight from a variable font for Blender).
- **Fonts**: Google Fonts / Fontsource (`npm i @fontsource/<family>`), Fontshare, League of Moveable Type. Check each license; use variable fonts and pixel/display faces that fit the medium rather than defaulting to the same serif + mono pair.
- **Assets**: CC0 sources (Kenney, OpenGameArt, Poly Haven textures/HDRIs, freesound CC0, Google Fonts). Record licenses.

## What the inventory summary should say

One short paragraph: the tools you'll use and why *for this direction* (the medium decides the tools, not the reverse), what you installed (with size), what you couldn't or won't install, and anything that needs permission. Do not choose a framework first and then design inside its comfort zone.
