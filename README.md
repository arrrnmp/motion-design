# motion-design

An agent skill for making motion graphics and video with code — explainers, ads,
product launch videos, social clips, title sequences, logo stings, data
visualizations, music visualizers, UI animation and 3D — plus the still images
that go with them (posters, thumbnails, key art, cover art, style frames).

The skill covers the whole job: briefing, tool inventory, art direction that
avoids the generic house look, planning with approval checkpoints, code-drawn
illustration, narration, code-composed music, data-driven timing, multi-variant
builds, verification, parallel rendering and delivery.

## What's in it

| Path | What it is |
|---|---|
| `SKILL.md` | The skill itself — eight phases from brief to deliver |
| `references/` | Deep-dives read on demand: direction, style library, drawing, voice, music, mixing, verification, parallelization, product footage, hardware |
| `references/styles/` | 12 reviewed style guides |
| `assets/styles/<id>/` | For each style: a reference still, a still page, and where useful a template with animation and sound |
| `assets/patterns/ambient-loop/` | Template for hours-long ambient / lo-fi looping pieces |
| `assets/lib/` | Engines: `print.js` spot-ink print simulator, `hershey.js` single-stroke fonts, `font5x7.js` bitmap font, `synth.py` numpy synth + mixer + loudness master + mux |
| `assets/blender/` | Blender helpers and a remote-GPU render script |
| `scripts/` | Bundled tools: machine inventory (sh + ps1), contact sheets, before/after frame compare, mix measurement, delivery checks, page renderer, stills grid |

## Install

Copy or symlink the repository into your skills directory:

```sh
git clone https://github.com/arrrnmp/motion-design.git ~/.claude/skills/motion-design
```

The skill is then picked up by any agent that reads skills, and triggers on
requests like "make a short clip", "animate this logo", "turn this script into a
video", "add voiceover", "make a Remotion/Manim/Blender scene" or "do a vertical
version for TikTok".

## Quick start

```sh
bash scripts/inventory.sh                                   # what's on this machine
python3 scripts/render_page.py assets/styles/01-riso-zine/still.html out.png
python3 scripts/stills_grid.py assets/styles out.jpg        # compare all 12 at once
```

Each style page exposes `window.renderFrame(f)`, `FRAMES` and `FPS`, so the same
file also renders to an MP4 across parallel workers.

## License

Copyright (C) 2026 Aaron Mompié. Licensed under the **GNU Affero General Public
License, version 3 or later** — see [LICENSE](LICENSE) and [NOTICE](NOTICE).

The AGPL's section 13 network clause is satisfied by publishing the corresponding
source in this public repository: <https://github.com/arrrnmp/motion-design>.
Contributions and pull requests are welcome; contributions are accepted under the
same AGPL-3.0-or-later terms.
