# Style direction: Tactile editorial

A direction to pick at phase 3, not a category of video. Full-bleed photographic, scanned or procedurally textured material, hard macro crops, quiet serif type, light and time as the motion. It suits anything where the visuals should feel *made and physical*: launches and announcements, brand films, title sequences, essays, product stories. It is a poor fit for diagrams, data-dense explainers, or playful/cartoon subjects. Each project chooses its own material so the art is evidence of the subject.

A built, reviewed example with its Blender scene and composite lives in the style library:
`styles/11-tactile-editorial.md` (`assets/styles/11-tactile-editorial/`).

## What it looks like

- **Full-bleed, material imagery** as hero and bookend: sky and clouds, macro photographs of natural or mechanical things (a leaf edge, dial numerals, rock, glass), scanned paper and collage panels, graphite and ink textures. Real grain, real imperfection.
- **Hard, macro crops.** Subjects run off the frame edge; a corner of a branch, a fraction of a dial. It should feel photographed, not composed from icons.
- **Quiet type over the image.** One serif (or one strong face), cream or ink on image, small uppercase metadata, hairline rules or dotted-leader lists. The art sets the mood; type never competes.
- **Light and time as the motion vocabulary.** Slow re-grades (morning / noon / night), slow camera drift, fade-from-black openings, grain that breathes. Nothing bounces or pops.
- **One scene, several grades.** A single build shipped in 2-3 lightings or palettes gives hero options and social variants cheaply.
- **Bookends.** The opening material comes back, transformed, at the end (a texture that dissolves into the closing card, a crop that widens into the outro) instead of a generic end slate.
- **Credited authorship.** When the product genuinely made or helped make the art, say so in a small corner credit ("Made with <product>"). It turns the art into a demonstration.

## Choosing the material

Ask what the release *is* and what it feels like, then pick material accordingly: an archival, layered, capable release suggests scanned paper and collage; a precise, fast one suggests mechanism macros; an expansive, narrative one suggests sky, landscape, weather. Avoid material that only signals "tech" (grids, glow, circuits). One medium per release; vary crop, scale and grade across scenes, not the material.

## How to make it

Pick the route by what you can honestly produce; combine freely.

1. **Photographic / scanned plates**
   - *Sources:* the user's own photography or scans; the product itself if it generates imagery (then the credit is true); licensed or public-domain archives with recorded licenses; local image models for textures and backgrounds. Log provenance for every plate.
   - *Build:* work at 2x+ the delivery resolution so slow pushes and crops stay sharp. Plates larger than the frame allow parallax and drift.
2. **Procedural / code-made material** (when there's no source imagery)
   - Noise-based skies and gradients with banding-free dithering, grain and paper textures from noise + blur + threshold, halftone and displacement shaders, generated collage panels (torn-edge masks, misregistered ink layers). Seeded, so renders are deterministic. See `drawing.md`.
3. **3D macros**: Blender or three.js close-ups of a real-feeling object (dial, dial-plate, glass, fabric) with shallow depth of field, a slow dolly, and physical materials. Use one lens and one light story per shot.
4. **Compositing**: layer plates in a shader or compositor (WebGL canvas, Remotion + canvas, ffmpeg): multiply/overlay grain, vignette kept subtle, slow parallax between depth layers, gentle displacement for atmosphere.
5. **Grade**: one look per scene (lift the blacks slightly, warm highlights, limited palette); build the alternates as grade changes, then check each for contrast against the type.

## Motion recipe

- Camera: slow push or drift, 1-3% scale change per second, eased at both ends; no shake.
- Opening: from black or from a blurred/out-of-focus state; a skippable feel (short, under ~4 s of pre-title).
- Type: fades or tracks in on the beat with the image, holds, leaves the same way. No bounce, no glow.
- Transitions: dissolves through grain, wipes along a panel edge, match-cuts on shape (a dial hole to a moon). Cut on music bars.
- Grain and light shifts are the only "ambient" motion.

## With product footage

- Frame real product footage with this art (see `product-footage.md`): the art owns the title, bridges and end card; the captured UI stays untouched. A shared grain/light treatment belongs on the frame, never on the UI.
- Place the credit and provenance in the end card or a corner, and list models/tools used for imagery, music or voice when it is true and adds to the story.
- Never claim the product made something it didn't.

## Verify

- Stills at hero, mid and end frames at delivery resolution: check sharpness at the deepest crop, banding in gradients, type contrast on every grade, safe areas.
- Run the direction audit (`direction.md`): the frame should not read as gradient-and-glow at squint size.
