---
name: motion-design
description: End-to-end approach for producing motion graphics and video with code — explainers, ads, product videos, social clips, title sequences, logo stings, data visualizations, music visualizers, UI animations, 3D renders, and anything in that world, including launch videos and demos of real software (capturing the actual product instead of mocking it up) — plus the still images that go with them (posters, thumbnails, key art, style frames, cover art). Starts art direction from a bundled library of 12 reviewed styles (riso, engraving, pixel diorama, linocut, cross-stitch, stained glass, coded ASCII and more) with stills, templates, animation and code-composed sound. Covers briefing, tool/skill inventory and installing what helps, art direction that avoids the generic house style, planning with approval checkpoints, design quality, code-drawn illustration, narration, code-composed music, data-driven timing, multi-variant builds, verification, rendering and delivery. Use this skill whenever the user wants to make, animate, render, edit or localize any video or animation — even if they only say "make a short clip", "animate this logo", "turn this script into a video", "add voiceover", "make a Remotion/Manim/Blender scene", or "do a vertical version for TikTok" — or design a still image in the same media (poster, thumbnail, cover, key art, style frame).
---

# Motion Design

The user's request (whatever follows this skill being invoked) is the actual job. This skill is about *how* to approach it: like a small studio that happens to work in code — careful about taste, rigorous about correctness, and economical with the user's time and attention.

**Start from the style library.** `references/style-library.md` holds 12 directions that a human art director reviewed and kept (riso, engraving, pixel diorama, brutal editorial, Space Age print, naive crayon, tactile macro, coded ASCII, printed manga, linocut, cross-stitch, stained glass), each with a guide, a reference still and working templates (most with animation and sound), plus the taste rules learned from what was rejected. Read it at phase 3. It is a **foundation, not a catalogue**: adapt a style, mix two or three, or invent a new one with the same taste rules; never ship a clone of a clone (see its "clone test").

**Stills are in scope, not just video.** Posters, thumbnails, key art, cover images and style frames are built
with the same direction, engines and taste rules as video — a still is a direction rendered once, at full
resolution, through `scripts/render_page.py`. When the job is stills-only, run the same phases scaled down:
brief the use (print vs screen, sizes), pick a direction, render options, verify at full resolution, deliver
PNG/JPG (plus source). Don't treat a still as a video frame-grab; compose it as its own piece.

**The failure this skill guards against most is sameness.** Process rigor (verification, timing from data, no overflow) is the easy half and is well covered below. The hard half is that code-built motion work drifts to one template — dark gradient ground, glow, mono eyebrow labels, glass cards, tiny objects in an empty frame — whatever the topic. Phase 3 (Direction) exists to break that; don't skip it, and don't treat the quality bullets in Build as a substitute for it.

**The second failure it guards against is faking the product.** When a video shows software that exists or whose source is available, the UI on screen must be the real thing, captured or rendered from the real code, never a hand-built mockup or screenshots of one. See `references/product-footage.md`.

The work moves through eight phases. Scale each phase to the project: a 5-second logo sting shouldn't get the ceremony of a 5-minute bilingual explainer, but it still gets briefed, given a direction, checked and delivered properly.

1. Brief — pin down the essentials
2. Inventory — machines, tools, skills; install what helps
3. Direction — choose a medium and a look that isn't the default
4. Plan — concept, shots, audio, timing, rendering, checkpoints
5. Build — distinctive, correct, data-driven
6. Verify — in a loop, nothing ships unchecked
7. Render — use the hardware well
8. Deliver — files plus an honest report

Deep-dive references (read when the project touches that area):

| File | Read when |
|---|---|
| `references/product-footage.md` | **Any launch video, demo, walkthrough or ad that shows a real product/app/site/CLI/TUI**, at phases 1-2, before storyboarding, and at the fidelity gate |
| `references/style-tactile-editorial.md` | Phase 3, when considering a photographic / scanned / physical-material direction (launches, brand films, title sequences, essays): what it looks like and how to build it |
| `references/direction.md` | **Always, at phase 3**, and again before the final render (its audit) |
| `references/long-form-loops.md` | Hours-long ambient/lo-fi "radio" pieces, looping worlds with a character and a now-playing label (template in `assets/patterns/ambient-loop/`) |
| `references/style-library.md` | **Always, at phase 3**: the 12 proven directions (guides in `references/styles/`, stills + templates in `assets/styles/<id>/`), the review-derived taste rules, and the dropped directions not to re-propose |
| `references/tools-and-installs.md` | Phase 2: install policy, finding tools inside app bundles, which skills to fetch |
| `references/drawing.md` | Any illustration, characters, icons, pixel art, textures, AI imagery |
| `references/voice.md` | Any narration, voiceover, TTS or voice cloning |
| `references/music-and-sound.md` | Any music, score or SFX: how to make it, licensing, platform loudness targets |
| `references/mixing-and-mastering.md` | Any time more than one sound plays together (music parts, voice, SFX) or audio is finished: per-part levels, frequency/stereo/time slotting, consistent loudness, ducking, mastering |
| `references/verification.md` | Before first render; whenever something looks wrong |
| `references/parallelization.md` | **Before any render or generation job longer than a minute or two**: measuring utilization, splitting work across processes/machines, choosing where heavy jobs run |
| `references/hardware-and-shells.md` | Multi-machine rendering, GPU jobs, remote/long jobs, shell scripting |

Bundled scripts (run them rather than rewriting them):

- `scripts/inventory.sh` (macOS/Linux) and `scripts/inventory.ps1` (Windows) — print OS/CPU/RAM/GPU/disk and which relevant tools are installed.
- `scripts/contact_sheet.sh <video> <out.png> [times...]` — tiled stills at given timestamps (or evenly spaced) for fast visual review.
- `scripts/compare_frames.sh <before> <after> <out.png>` — side-by-side plus a difference image of two stills.
- `scripts/mix_report.py --mix mix.wav [--stems a.wav b.wav ...] [--target -16]` — measures a mix: integrated/short-term loudness and the spans that stray from target, true peak, PLR, mono compatibility, low-end phase, per-stem levels and band shares, and frequency clashes between stems. Your ears for phase 6 on any audio work.
- `scripts/check_delivery.py <video> [--lufs -16] [--srt captions.srt]` — reports duration, resolution, fps, codec, integrated loudness, true peak, silence and caption timing sanity.
- `scripts/render_page.py <page.html> <out.png|out.mp4>` — renders an HTML/canvas page to a still, or (if it exposes `window.renderFrame(f)`, `FRAMES`, `FPS`) to frames + MP4 across parallel workers; serves over http, waits for `window.__ready`, reports fonts and page errors. All style templates use it.
- `scripts/stills_grid.py <folder> <out.jpg>` — labelled grid of direction stills for side-by-side review (`assets/styles/library-sheet.jpg` is the library's).

Bundled engines (`assets/lib/`): `print.js` (spot-ink print simulator: plates, halftone, misregistration, paper), `hershey.js`/`hershey.json` (single-stroke fonts for drawn lettering), `font5x7.js` (bitmap font), `synth.py` (numpy synth, mixer, loudness master, mux). `assets/blender/` has Blender helpers and a remote-GPU render script.

---

## 1. Brief

Establish: format and platform, aspect ratio, resolution and frame rate, length, audience and tone, whether there's voice / music / SFX / subtitles / multiple languages, available brand assets, references and constraints, deliverables and deadline.

**Stills-only jobs:** establish use instead of timeline — print vs screen, exact sizes (e.g. poster 24×36" 300 dpi, thumbnail 1280×720, cover 1600×1600), where the image will be seen (phone-size legibility still applies), and how many options to show. Reuse the same direction process; a still gets composed as its own piece, not grabbed from a video render.

**Infer defaults wherever you sensibly can** (e.g. YouTube explainer → 16:9 1920×1080 30fps H.264, −14 to −16 LUFS; Reels/TikTok/Shorts → 9:16 1080×1920 with platform UI safe zones; logo sting → 3–6 s, no voice). Only ask about things that are genuinely the user's to decide *and* would change the plan. Put all questions into one grouped message, each with your recommendation, so the user can reply "all defaults" in one line. Don't ask about things you can look up or measure.

**Launch or product videos:** also establish what the product is, where its source lives, which surfaces (web, desktop, mobile, TUI, CLI) and which 3-6 flows to show, and whether it can run locally. Answer these from the repo yourself where possible rather than asking. Then follow `references/product-footage.md`.

**References deserve real study.** If the user shares links, screenshots, videos or frames, analyze them: pacing (cut rhythm, shot lengths, hold times), typography (families, weights, scale contrast, tracking, case), color (palette, contrast, saturation), transitions, camera work, and sound. For video references, pull frames with ffmpeg and look at them; measure shot lengths with scene detection. Write a short "what makes this work" note and match that *taste*, not just the subject matter.

## 2. Inventory

Before building anything, take stock. Run the inventory script for this machine, and do the same over SSH for any other machines the user mentions or that are clearly reachable. Note which machines can do GPU work (3D, AI models, hardware encoding) and which could render in parallel.

Pick the script by the machine's OS, not by assuming bash exists. Detect it first: `ssh host uname -s` answers on macOS/Linux; if that fails, `ssh host ver` answers on Windows (whose OpenSSH default shell is usually cmd, sometimes PowerShell).
- macOS / Linux: `ssh host 'bash -s' < scripts/inventory.sh`
- Windows: PowerShell is always there (Git Bash and WSL often aren't), so copy the script and run it — copying avoids PowerShell's quote mangling over SSH:
  `scp scripts/inventory.ps1 host:inventory.ps1` then `ssh host powershell -NoProfile -ExecutionPolicy Bypass -File inventory.ps1`

The same rule applies to everything you run on a remote Windows machine later: write a `.ps1` file, copy it over, run it with `-File`. See `references/hardware-and-shells.md`.

**Product recon (launch/demo videos):** if the product's code is available, this is the most important inventory item. Find how each surface runs, what fixtures, mock clients, render harnesses, Storybook or design files exist, and the real tokens, fonts and assets. Run it and look at it. Choose the highest rung of the fidelity ladder in `references/product-footage.md` for every surface; write the result in `product-notes.md`.

Check which relevant tools are installed or cheap to install — motion frameworks (Remotion, Motion Canvas, Manim), Blender (headless via Python), three.js/shaders, Lottie, ffmpeg, headless browsers, local image/video/TTS/music/STT models, audio tooling (pedalboard, Reaper, Rubber Band), live-coding music (Strudel, TidalCycles/SuperCollider, Sonic Pi), drawing tools (Aseprite, Inkscape, vtracer, potrace) and font sources. **A tool missing from PATH is not a missing tool**: GUI apps hide their CLI inside the app bundle (e.g. `/Applications/Blender.app/Contents/MacOS/Blender`); the script and `references/tools-and-installs.md` cover where to look.

**Skills are tools too — look for them and install them.** Check which skills and plugins are already installed (the script lists them), then search for any that match the tools or techniques you're likely to use (`find-skills`, `npx skills find <query>`, your harness's skill/plugin search, the web). If you're going to use Remotion, install its official skills (`npx skills add remotion-dev/skills`) *before* writing Remotion code, and read them. The default failure is to scan the machine, see what's there, and quietly build with whatever you already had.

For each candidate, write one sentence: what it would concretely save or improve on *this* project. **Free, local, no-account software and skills clear the bar by default: install them and log what you installed.** Weigh only paid software, big downloads, and anything touching accounts or the user's content.

Ground rules:
- **Never** set up anything requiring accounts, credentials, payment, or uploading the user's content to the cloud without asking first. The user's material is theirs; cloud services leak it and cost money. Don't buy software; use a free equivalent.
- Prefer scriptable, headless, deterministic tools over driving GUIs — they're reproducible and re-runnable. Use computer use only when no scriptable route exists, and say when you do.
- **Let the direction pick the tools, not the other way round.** Don't choose Remotion (or any single framework) by default and design inside its comfort zone. Pick per shot: code-driven motion graphics as a backbone where it fits, Blender for real 3D or tactile looks, Manim for math, canvas/shaders for texture and pixel work, physics engines for simulated things, generative models for textures or plates.

Finish with a **short** summary to the user (what you found, what you'll use, anything you'll need their permission for) and keep going — this isn't a checkpoint unless something needs their approval.

## 3. Direction

Read `references/direction.md`. Short version:

1. **Name the default** — the look you'd build if nobody were watching — then write a project **ban list** of those habits. Naming specific patterns to avoid steers you far better than "be original".
2. **Pick a medium, not a theme.** Pixel art, cut-paper, cel/hand-drawn, risograph, blueprint, clay/toy 3D, isometric dioramas, Swiss typographic, chalkboard, comic panels, physical "charts made of things"… Choose what the subject is made of and what the audience associates with it. A palette or font swap is not a different style.
3. **Write a one-page direction spec**: shape language, line/texture, light and depth, palette roles, type, *motion vocabulary* (cadence, easing, entrances), camera, transitions, sound, bans.
4. **Render three genuinely different directions as stills of the same real moment** and show them with a recommendation (skip the three-way only if the user already specified a style; then render one plus a riskier variation). If the three look like siblings, redo two.
5. Style references: **`references/style-library.md` first** (shortlist 2-3 directions whose *process* fits the subject, including at least one mix of library styles or a new idea; reuse the engines, not the layouts; run the clone test), and `references/style-tactile-editorial.md` (physical, photographic, restrained).
6. Apply the library's taste rules to anything new: a real process with its flaws, light grounds, one title face and at most one line of copy, derived effects derived from their source, no metadata rows / mono labels / glows.
7. Use references: if the user gave none, look up real work in the space (studios, series, films, games, print traditions) and write down what makes it distinctive.

For product videos the direction governs everything *around* the product (frame, camera, transitions, type, sound, bridging scenes); the product UI itself stays true to the real thing. Render the direction stills with real captured footage in them, not placeholder boxes.

This is the highest-leverage step in the project. The direction is the first checkpoint on any substantial job (see Plan).

## 4. Plan

Write a plan covering: concept and structure; shot/scene list; visual language per section; audio approach; how timing is driven; how rendering splits across machines; deliverables; rough time estimate.

**Checkpoints go where mistakes are expensive**, scaled to project size:

- **Substantial projects** (roughly: >30 s, narration, multiple scenes, or multiple variants) get four pauses:
  1. Direction — the three rendered style options from phase 3, with your recommendation. Approve before designing anything else.
  1b. **Footage proof (product videos)** — real captures of the key moments beside the running product (fidelity gate in `references/product-footage.md`). Approve before building scenes around them.
  2. Script / storyboard / shot list — approve before building visuals. Storyboards describe *what is seen and what moves* (metaphors, camera, scale changes), not just captions.
  3. Voice and/or music — short auditions (a paragraph, a 15-s loop) before generating everything.
  4. Style frames — rendered stills of each distinct scene type in the chosen direction, before building every scene in it.
- **Small projects** fold these into one quick check (e.g. plan + the three direction stills), or skip them if the request is fully specified.

Between checkpoints work autonomously and post short progress updates (a line or two: what's done, what's next, anything surprising). Don't ask for permission for things the plan already covers.

## 5. Build

### Make it distinctive, then make it polished

The bullets below are craft basics; they are necessary and not sufficient. Following them inside the default look yields a clean, generic video. Apply them *inside the direction spec from phase 3*.

- **Use the whole frame.** One dominant subject at real scale, foreground/midground/background depth, shot-scale variety, camera moves, objects that interact. Tiny centered objects in empty space, tiny labels and UI-mockup diagrams are the tell.
- **Product on screen is real.** Capture or render the actual app (see `references/product-footage.md`); crop, zoom, frame and time it, but don't redraw it.
- **Metaphor before diagram.** Animate the tangible thing a concept behaves like; use boxes and arrows only when the idea really is boxes and arrows.
- **Motion vocabulary comes from the medium** (stepped for pixel art, snapping for cut-paper, squashing for clay, drawing-on for blueprint), not from one global ease-out fade.
- **Vary the structure.** Chapter cards, section labels and transitions change design as the story changes; a repeated template is a house style leaking back in.

- **Hierarchy**: one focal point per moment. Size, weight, contrast and motion all point at it.
- **Typography**: few families, strong scale contrast, deliberate weights and tracking, good line lengths, real typographic quotes and dashes. Load fonts properly and confirm they rendered (fallback fonts are a classic silent failure).
- **Color**: a small deliberate palette with defined roles (background, ink, accent, data series). Check contrast.
- **Spacing**: generous, on a consistent grid. Crowded frames read as cheap.
- **Easing**: designed, not default. Use custom curves/springs; asymmetric in/out; overshoot sparingly; stagger groups.
- **Transitions**: varied and motivated — match cuts, morphs, pushes, masks — not the same crossfade everywhere.
- **Motion has a job**: every animation explains, emphasizes or guides the eye. If it only decorates, cut it or calm it.
- **One coherent identity within the medium**; vary the look per section only when it serves the story, and by changing method and composition, not just palette. Recurring motifs, examples or characters give continuity.
- **Pacing** for the audience and platform: hooks early on social; room to breathe after dense ideas; hold important frames long enough to read (rough rule: ~3 words/second of on-screen text reading time, plus a beat).

### Correctness is part of quality

- Verify every fact, number, label and translation that appears on screen or in narration. Cite sources for facts in your notes. Have translations checked back (back-translate or cross-check) rather than trusting a single pass.
- Visuals and audio must agree exactly — if the narrator says "three steps", three steps appear.
- Keep all text inside safe areas, **measured, not hoped** — compute text bounds in code (or measure rendered frames) and assert they fit, especially with translations (German/Spanish run long), dynamic data, and vertical formats with platform UI overlays.

### Drawing and illustration

Draw with code first (parametric, layered SVG; pixel grids; procedural shaders), and bring in local image models only for organic/detailed subjects, under compositional control. Build anything that moves as separate parts. Read `references/drawing.md` for the full approach.

### Audio

Choose the voice source to fit the project (user recordings, a clone of the user's voice, designed/stock TTS, or none). Generate in paragraph chunks with several takes, verify each with speech-to-text, pick automatically. You can't hear, so measure and report. Prefer composing music in code (Strudel/TidalCycles) so beat times are exact, and render each part as its own stem so the mix can be balanced and measured rather than guessed. Read `references/voice.md`, `references/music-and-sound.md` and `references/mixing-and-mastering.md`.

### Timing from data, one codebase for all variants

Drive timing from data, never hand-placed frame numbers:
- **Voice**: word timestamps from speech-to-text, plus cue markers in the script (e.g. `[[chart-in]]`) resolved to times.
- **Music**: beat/bar times from the music code (or detected onsets for external music).
- **Data viz**: the data itself determines durations and order.

That way changing voice, music, language or data never means re-timing by hand.

Architecture:
- One codebase for every variant (languages, voices, aspect ratios, cut-downs), with per-variant text, audio and timing files.
- Scenes as separate components; layout responsive to aspect ratio rather than duplicated.
- Deterministic: seeded randomness, no wall-clock or network dependencies at render time.
- Build scripts (Makefile or a `build` script) so the whole pipeline — narration → alignment → timing → render → mix → encode → checks — re-runs end to end. Cache every expensive step keyed on its inputs and only regenerate what changed.

## 6. Verify

Nothing ships unchecked. The loop, in short (details and trap list in `references/verification.md`):

- After building or changing a scene, render a **contact sheet** of stills at its key beats and actually look at it.
- When a change substantially affects what's on screen, render the **same frames before and after** and compare side by side: confirm what you meant to change changed and nothing else broke.
- **Product fidelity check**: compare every product frame against the real running app for the same state (fonts, colours, density, copy, icons). "Not quite ours" is a fail.
- Fix overflow, overlaps, dead frames, broken layouts and wrong numbers before moving on.
- Run the **direction audit** from `references/direction.md` on the contact sheet: ban-list scan, squint test against the default look, phone-size legibility. Correct but generic is a fail.
- Before any big or slow job (full narration, final renders, big generation batches, long 3D renders): run a **small representative sample** end to end first. Then tell the user what you're about to run, how long it'll take and what it'll produce — and get their review when a mistake would waste real time.
- Before the final render, do a **quick low-res full pass** to catch crashes end to end.
- When something breaks, find the exact frame and cause, reproduce it minimally, then fix — don't guess and re-render.
- After final renders, spot-check frames across the whole piece and run `scripts/check_delivery.py` (duration, resolution, loudness, captions).

Answer questions with stills or partial renders instead of full renders whenever possible.

## 7. Render

Read `references/parallelization.md` before any long render. Short version:

- **Idle hardware is a bug.** Sample CPU and GPU utilization during a test render. One pegged core or a half-idle GPU means a serial bottleneck (usually Python glue, per-frame callbacks, or a single render process), so fix it before the full run.
- **Never overload memory.** Measure one worker's peak RAM/VRAM on the heaviest frames, size the worker count to leave a reserve (at least 20% of RAM, never under ~4 GB), ramp workers up gradually, and run a watchdog that stops launching or kills workers when available memory drops. Check disk space too. A swapping or frozen machine is a failed job.
- **Split by frame range or variant across several worker processes**, sized from measurements; pin threads and GPU per worker; render image sequences and resume rather than restart; encode while rendering.
- **Run heavy jobs on the strongest, coolest machine available and keep portable machines for editing and previews**, even if not asked; say so in the plan. Benchmark the same frames on each machine first.
- Launch long remote jobs detached with done-markers, and use small script files instead of fragile shell one-liners. See `references/hardware-and-shells.md` for details.

## 8. Deliver

Deliver in the agreed formats — by default MP4, H.264 (yuv420p, `+faststart`), AAC audio, at the agreed resolution and frame rate — plus captions (SRT/VTT, generated from the verified word timestamps), scripts, and any source assets the user would reasonably want (project source, stems, style frames, SVGs). For stills deliverables: PNG (or JPG for photographic work) at full resolution plus web-sized exports, with source (HTML/SVG/scene) included.

Close with a short, honest report:
- **What you made** (files, lengths, variants).
- **How it rendered** (machine, workers, measured utilization, frames/min, total time).
- **How you verified it** (checks run, measured loudness/duration, what you looked at).
- **Direction**: the medium you chose, what you rejected, and which ban-list items you had to break and why.
- **Known weaknesses** — be specific and candid; the user will find them anyway.
- **What you'd improve next** with more time.

## Where to spend effort

Quality is decided by the concept, the direction (medium and motion vocabulary), the script/storyboard, the first scene of each style, and debugging — spend there. Be efficient on mechanical parts: localization, plumbing, variants, re-renders. Cache everything.

## License

Copyright (C) 2026 Aaron Mompié. This skill — `SKILL.md`, everything under `references/`, `assets/` and `scripts/` — is free software under the **GNU Affero General Public License, version 3 or later**: <https://github.com/arrrnmp/motion-design> (see `LICENSE` and `NOTICE`). You may use, copy, modify and redistribute it under those terms; derivatives must stay AGPL-3.0-or-later and keep the notices intact.

If you modify this skill, keep the SPDX and copyright headers and say what you changed; if you make it reachable over a network, offer its corresponding source (publishing it in a public repo, as upstream does, satisfies section 13). Third-party assets a project pulls in keep their own licenses — record them, as `references/music-and-sound.md` and `references/drawing.md` require. The skill's own third-party audit is `THIRD_PARTY.md`; keep it current when you add a bundled asset, web font or dependency.
