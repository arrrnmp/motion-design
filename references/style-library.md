# Style library: 12 proven directions

A library of art directions that were built, rendered, reviewed by a human art director over several rounds and
**kept**. Each has a guide in `references/styles/`, a reference still, and working templates (still, and for most
an animation and a code-composed sound score) in `assets/styles/<id>/`. It is a **foundation, not a catalogue**: the point is to
start from proven processes and taste, not to hand out clones. Sometimes a library style adapted to the subject is
exactly right; often the better answer is a **mix** of two (a world from one, a character or print treatment from
another) or a **new direction** built the same way. Videos made from this library must not become clones of clones.

Every reference still shows the same subject ("From cherry to cup", a coffee explainer beat) so the styles
compare on style alone. Look at the still first (`assets/styles/<id>/still.jpg`), then read the guide.

| id | Direction | The process it simulates | Ground | Motion (cadence) | Anim + sound template |
|---|---|---|---|---|---|
| 01 | [Riso zine](styles/01-riso-zine.md) | 2-ink risograph: halftone screens, overprint, misregistration | off-white paper | stepped 12 fps, reprint jitter | still only |
| 02 | [Engraved plate](styles/02-engraved-plate.md) | line engraving printed in black + one spot colour | cream paper | burin draws lines on | still only |
| 04 | [Pixel diorama](styles/04-pixel-diorama.md) | 16-bit pixel art, fixed palette, Bayer dither, rim light | dusk sky | stepped 12 fps, whole-pixel parallax | yes + chiptune |
| 07 | [Brutal editorial](styles/07-brutal-editorial.md) | magazine-cover collage: raw HTML, OS chrome, xerox, marker | safety yellow | paste-in cuts, cursor clicks | still only |
| 09 | [Space Age](styles/09-space-age.md) | 1958 magazine ad, 4 spot inks on aged newsprint | yellowed paper | limited animation, UPA holds | still only |
| 10 | [Naive doodle](styles/10-naive-doodle.md) | a real child's crayon drawing (p5.brush pigment) | white paper | boiling line on 2s | still only |
| 11 | [Tactile editorial](styles/11-tactile-editorial.md) | macro photograph (Blender) + quiet serif | photo | light + slow push | still only |
| 12 | [Coded ASCII](styles/12-coded-ascii.md) | the frame is one character grid of shaded fields | paper | fields evolve, glyphs flip | website + reactive score |
| 14 | [Printed manga](styles/14-printed-manga.md) | G-pen ink plate + screentone + vermilion spot, printed | cream stock | panel pushes, smash cuts | still only |
| 15 | [Linocut](styles/15-linocut.md) | carved relief block, two inks, rough transfer | paper | carve → stamp → living print, 12 fps | yes + foley/folk |
| 16 | [Cross-stitch](styles/16-cross-stitch.md) | sampler on Aida, lit twisted floss, stitched wreath | linen | stitches itself in, 12 fps | yes + foley/music box |
| 17 | [Stained glass](styles/17-stained-glass.md) | Richter-square glass, Sagrada gradient, projected cast | pale stone | sun moves, cloud passes, 24 fps | yes + nave pad/bells |

## What the reviews taught (apply to every new direction, not just these)

These are the art director's verdicts, generalised. They are the difference between "kept" and "AI slop".

1. **Simulate a real process, including its flaws.** Every kept style is a physical or historical process with its
   imperfections built in: ink that misregisters and speckles, gouges that taper, crayon that misses the line,
   dither between palette steps, floss with sheen and twist. Everything dropped was clean vector or clean 3D
   perfection ("too perfect", "like my toddler is an AI", "bland"). Build the *process* (separate ink plates,
   screen them, offset them, multiply onto paper), not an image that looks like the process.
2. **Light grounds.** Paper, linen, stone, newsprint. The dark versions (black engraving ground, dark nave with
   glow) read as the generic AI house style every time. A dark ground needs a medium that is dark by nature
   (night pixel sky, a photograph).
3. **Typography: one title face, at most one line of copy.** Pick a face that belongs to the process (Caslon for
   engraving, a slab for lino, bitmap for pixel, crayon strokes for naive). No metadata rows, mono eyebrow labels,
   "PLATE I · 01/06" headers, crop-mark grids, leader-line annotations, palette strips, stats, glows. "Too much
   subtitles and too dense" is the most common failure of a technically good render.
4. **Derived things must be derived.** A shadow or cast light comes from the actual source layer (project the
   glass layer, don't redraw an approximation); rim light faces the actual sun; a bean's crease is in the bean.
   A cast with blocky edges under smooth glass reads as fake instantly.
5. **Generic trend looks don't survive.** Swiss grid, bento neo-brutalism, Y2K chrome, museum flat-lay and clean
   clay toy were all dropped as "generic". A trend is a reference, not a direction; push it to an artefact
   (a 1958 ad, a Businessweek cover, a sampler) or drop it.
6. **Frames stay uncluttered and the subject is big.** One focal image, one title. Props earn their place
   (bobbins and needle tell "handmade"; three unlabelled blobs don't).
7. **Motion is the process happening.** Carve then print; stitch in X by X; the sun moves and the cast follows;
   the pixel world steps in whole pixels. Use the medium's cadence: 12 fps stepped for print/craft/pixel,
   24 fps smooth only for light and camera.
8. **Sound is the process's foley plus a small score in the medium's idiom**, placed from the same frame data as
   the visuals (see `music-and-sound.md`): gouges per cut, a thud on the stamp, needle pierces, chiptune for pixel,
   a nave pad that follows the light curve.

## Dropped directions (don't re-propose without a new angle)

Clay toy 3D (bland), Y2K chrome ident (dropped), Swiss typographic grid (generic), specimen flat-lay grid (no
vision), blueprint/cyanotype sheet (never read as a real blueprint), 3D paper-cut shadowbox (dropped), watercolour
cartoon (dropped). Also rejected: the dark-ground versions of 02 and 17.

## Shared engines (assets/lib)

- `print.js` — spot-ink print simulator: plates are canvases whose alpha is ink density; each gets a halftone angle
  and cell, speckle voids, roller unevenness, a register offset, and multiplies onto paper (optionally aged).
  Used by 02, 09 (and the approach of 01, 14, 15).
- `hershey.js` + `hershey.json` — single-stroke fonts (Hershey + EMS) as polylines, for lettering that is *drawn*
  (crayon letters, pen-plotter, blueprint Leroy lettering). Glyphs it lacks (⌀ – —) must be added by hand.
- `font5x7.js` — 5×7 bitmap font for pixel/ASCII work.
- `synth.py` — numpy/scipy synth + mixer + two-pass loudnorm master + mux (see `music-and-sound.md`).

## Tools

- `scripts/render_page.py page.html out.png|out.mp4` — renders any template (serves over http so pages can fetch
  local files; waits for `window.__ready`; animations via `window.renderFrame(f)`, native fps encoded at 24).
- `scripts/stills_grid.py` — labelled contact sheet of a folder of stills, for side-by-side review.
- `assets/styles/12-coded-ascii/site_render.py` — deterministic capture of a live web page (virtual clock).
- `assets/blender/` — `common.py` helpers (GPU setup, clay/stone materials, text meshes, cove), and
  `remote.sh` + `run.ps1` to render on a Windows GPU box over SSH (`GPU_HOST=user@host`).

## Foundation, not a template: mixing and inventing

- **Three moves, in order of ambition:** *adapt* one style to the subject (change content, composition, palette
  derived from the subject, motion beats); *mix* two or three (keep each one's strongest idea, drop the rest); or
  *invent* a new process using the taste rules above. Offer at least one mix or new idea among the direction stills
  unless the brief clearly calls for a library style as-is.
- **Good mixes combine different axes**, not two looks: a world-rendering method + a character medium (ASCII
  landscape + pixel sprite), a making process + a print process (linocut carving printed as riso overprint), a
  light behaviour + a material (stained-glass cast on an engraved plate), a structure + a texture (manga panels in
  cross-stitch).
- **Clone test (before showing any direction):** put the new still next to its closest library still. If it reads
  as the same piece with new nouns (same composition, same palette, same type, same props), push it until at least
  the composition, palette and one signature element are its own. Also compare against the last piece made with
  the skill: two jobs in a row should not look like siblings.
- **Keep the process, change everything else.** What transfers is the engine (plates, carving, stitch rendering,
  glyph shading) and the taste rules. What must not transfer unchanged: the reference layout, the coffee motifs, the
  exact palette, the title treatment.
- **Sometimes the foundation is enough.** If the user picks a library style by name, or it genuinely fits, adapt it
  well rather than forcing novelty; the clone test still applies to layout and content.

## How to use it on a job

1. Brief as usual. At Direction, shortlist 2-3 directions: library styles whose *process* fits the subject and audience,
   at least one mix or new idea
   (e.g. linocut for craft/food/origin stories; ASCII for developer/infra; stained glass for anything about light,
   transformation or ritual; cross-stitch for home, care, heritage; pixel for games or playful systems).
2. Copy the relevant template folders into the project as engines; build the real subject's composition, palette
   and motifs on top (and combine engines for a mix).
3. Render stills of the same real moment in each, run the clone test, show them together, recommend one.
4. When approved, animate with the style's motion rule and build its sound from the same frame schedule.
5. If none fits, invent a new direction the same way (a real process with its flaws) and, when it's approved,
   add it to this library: guide + still + templates.
