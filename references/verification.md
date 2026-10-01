# Verification

Nothing ships unchecked. Verification is a loop that runs throughout the build, not a step at the end.

## The loop

1. **Contact sheets after every scene build or change.** Render stills at the scene's key beats (entrances, holds, peaks, exits, first and last frame) and look at them. `scripts/contact_sheet.sh video.mp4 sheet.png 1.0 2.5 4.0 ...` — or render the stills straight from the framework (e.g. `remotion still`, Motion Canvas frame export, `manim -s`, Blender single frame) which is faster than a video render.
2. **Before/after comparisons** whenever a change substantially affects what's on screen. Render the *same frames* before and after; `scripts/compare_frames.sh before.png after.png cmp.png` gives side-by-side plus a difference image. Confirm the intended change happened and nothing else moved.
3. **Fix before moving on**: text overflow, overlaps, dead/empty frames, broken layouts, wrong numbers, missing fonts, wrong language strings.
4. **Sample before scaling**: before full narration, final renders, big generation batches or long 3D renders, run a small representative sample end to end. Then tell the user what you'll run, how long it'll take and what it'll produce; wait for their review when a mistake would waste real time.
5. **Low-res full pass** before the final render (e.g. half resolution, lower quality, fast preset) to catch crashes and timing errors across the whole piece.
6. **Final checks**: spot-check frames across the whole piece (a contact sheet of ~20 evenly spaced frames per variant), then `scripts/check_delivery.py final.mp4 --lufs -16 --srt final.srt`.

## Measure, don't hope

- Text fit: compute bounding boxes in code (canvas `measureText`, DOM `getBoundingClientRect`, Pillow `textbbox`) and assert they're inside the safe area. Title-safe ≈ 90% of frame; for vertical social formats, keep clear of the top ~14% and bottom ~20–25% plus the right-side button column.
- Numbers on screen: derive them from the same data file the narration was checked against; assert equality in the build.
- Sync: compare cue times in the timing file to the words in the STT alignment.

## Web pages and canvas renders

- Serve pages over http (pages that `fetch()` local JSON/audio fail on file://). `scripts/render_page.py` does this.
- Every page reports its loaded fonts; check the list (a missing family means a silent fallback), and add glyphs a
  font lacks (single-stroke fonts miss ⌀ – —; bitmap fonts need every character you use).
- Watch for global name clashes in library pages (`stroke`, `top`, `renderFrame` wrappers calling themselves) and
  non-integer indices into lookup tables (dither matrices, pattern grids).
- **Deterministic capture of a live page**: replace `performance.now` and `requestAnimationFrame` with a virtual
  clock you step once per output frame, script scroll/pointer/keys by time, screenshot, and log the page's state per
  frame. Real-time screen recording drops frames and can't be synced to sound
  (`assets/styles/12-coded-ascii/site_render.py`).
- Check every scroll/animation stop, at desktop and phone size, and with each theme.

## Debugging

When something breaks, find the **exact frame** and the **cause** — bisect the timeline, render single frames, log the props/state at that frame — reproduce it minimally, then fix. Don't guess-and-re-render the whole thing; that burns time and often hides the real bug.

## Classic traps

- **Conditional expressions rendering stray values** in UI code — e.g. JSX `{count && <X/>}` renders a literal `0`; `{items.length && ...}` likewise. Use explicit booleans/ternaries.
- **Animation indices out of range** before or after their cue — `words[i]` where `i` is −1 before the first cue or past the end after the last; interpolations without clamping that extrapolate beyond their range. Clamp everything.
- **Large media decoded inside headless browsers** — huge videos/PNGs in a Remotion/Puppeteer render cause timeouts, memory blowups and blank frames. Pre-transcode to proxy sizes/codecs, use image sequences, or composite in ffmpeg afterwards.
- **Assets overwritten while a render is reading them** — never regenerate into the path a running render uses; write to a new file and swap atomically after the render finishes (or version asset paths).
- Fonts silently falling back; wrong frame rate between assets and composition; audio sample-rate mismatches; off-by-one frames at scene boundaries; nondeterminism from unseeded randomness or `Date.now()`.
