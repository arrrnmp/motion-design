# Art Direction: escaping the house style

## The problem this file exists to fix

Left alone, code-built motion work converges on one look, whatever the topic. Recognise it so you can refuse it:

- A near-black navy/indigo/purple background with a soft radial vignette, faint grid or bokeh dust
- Neon glow on everything; cyan + magenta + amber accents on dark
- Small monospace labels, "01 — SECTION NAME" eyebrows, pill-shaped tags, glassy rounded cards with 1px borders
- A serif display headline with one colored accent word
- Chapter cards that are all the same template (label, title, progress dots)
- Tiny objects floating in the middle of a mostly empty frame; diagrams that are boxes, arrows and labels; "UI mockup" energy
- Every scene fades in with the same ease-out and a slight upward drift
- Palette swaps between scenes standing in for actual variety

Changing the palette or the font does **not** change the style. Two videos that differ only in color and typeface are the same video. Style is decided by *how things are made*: shape language, line, texture, light, depth, camera, and how things move.

## Step 1: name the default, then ban it

Before choosing a direction, write down (in the project notes) the look you would have built if nobody asked: background, type, accents, layout, motion, transition. That is the default. Then write the project **ban list**: the specific habits you will not use unless you can justify them in one sentence for this subject. Naming concrete patterns to avoid works far better than telling yourself to "be original".

Start from the list above, then add anything else you catch yourself reaching for. From the style-library reviews
(`style-library.md`), these also read as "AI slop" even under good art:
- metadata furniture: "PLATE I · 01/06" header rows, mono location labels, stats lines ("983 SQUARES · 112 COLOURS"),
  palette strips, crop-mark grids, leader-line annotations everywhere;
- more than one line of copy under the title; decorative second and third typefaces;
- glowing type; dark grounds for media that aren't dark by nature;
- clean vector or clean 3D standing in for a physical process ("too perfect");
- recognisable web/design trends taken at face value (bento neo-brutalism, Swiss grid, Y2K chrome, museum flat-lay).

## Step 2: pick a medium, not a theme

**Check the style library first** (`style-library.md`): directions already built, reviewed and kept, with guides
and templates. Treat it as a foundation: adapt one, mix two or three (different axes: world + character medium,
making process + print process, light + material), or invent with the same rules; the menu below widens the search.
Whatever you pick must pass the library's clone test.

A style is a *made thing*. Ask: what would this look like if it were physically or historically produced by a particular craft? Choose one primary medium per project (or per chapter, when the story earns a shift) and let its constraints drive every decision.

Menu, to widen the search (not exhaustive, and mix rarely):

| Medium | What it implies | Route |
|---|---|---|
| Pixel art / 8-bit / 16-bit | Fixed grid and palette, integer scaling, stepped motion, dithering, tile worlds, sprite characters | Pixel grids, canvas with `image-rendering: pixelated`, Aseprite Lua |
| Paper cut-out / collage | Layered flat shapes, drop shadows between layers, torn edges, parallax, stop-motion cadence (8-12 fps) | SVG + filters, Blender, three.js |
| Cel animation / hand-drawn | Wobbling outlines, held poses on twos, squash and stretch, smear frames | Rough.js-style jitter, SVG path morphs, Manim |
| Risograph / screenprint / halftone | Two or three spot inks, misregistration, grain, overprint blending, big flat shapes | Canvas/shader with multiply blending and halftone shader |
| Blueprint / technical drawing / patent plate | Cyanotype or paper ground, dimension lines, hatching, drafting-pen line draw-on | SVG stroke animation |
| Vintage scientific / encyclopedia plate | Engraved linework, cream plates, specimen labels, cross-hatch | Only with justification (cream is on the ban list) |
| Woodcut / linocut / stamp | Chunky carved edges, limited inks, ink spread, print-on-paper reveals | Displacement + threshold shaders |
| Isometric / dioramas / tiny worlds | Real 30 degree grid, tilt-shift depth, little machines doing the work | SVG, three.js orthographic, Blender |
| Clay / plasticine / toy / tactile 3D | Soft lighting, fingerprints, imperfect forms, physical bounce | Blender (headless), three.js |
| Low-poly / wireframe / vector-monitor / CRT | Vertex-level geometry, scanlines, phosphor bloom (earned here, banned elsewhere) | three.js, shaders |
| Swiss / International typographic | Grid, huge type, flat color fields, asymmetric layout, hard cuts | HTML/CSS in Remotion |
| Kinetic typography as the whole visual | Words *are* the objects: they collide, stack, break, get measured | Remotion + text-measure |
| Bold-flat editorial infographics | Big shapes, thick outlines, character-driven metaphors, saturated palettes on *light* or mid-tone grounds | SVG |
| Chalkboard / whiteboard / paper notebook | Hand-drawing action, erasing, arrows drawn on, smudges | Stroke animation, path-following hand |
| Comic panels / manga | Panel layouts, speed lines, onomatopoeia, camera cuts between panels | SVG/CSS grid |
| Data-physical / "charts made of things" | Bars are stacked objects, populations are crowds, quantities are real volumes | Physics sim (matter.js), instancing |
| Live-action-feeling 3D scenes | Camera moves through real space, depth of field, materials | Blender, three.js |
| Tactile editorial (photographic / scanned material) | Full-bleed real or procedural texture, macro crops, quiet serif type, slow light and grade changes, grain, bookended openings and endings | See `style-tactile-editorial.md` |
| Mixed-media (photo texture + flat vector) | Scanned textures under vector shapes, cut-paper on photographic ground | Compositing in ffmpeg or shader |

When you invent one, **simulate the process, flaws included**: separate ink plates screened and misregistered,
carved blocks, pigment brush strokes that miss the lines, stitches with thread sheen, dither between palette steps.
That, not the palette, is what made every kept direction work.

Choose by **fit to the subject and audience**: what the topic *is made of*, and what the viewer already associates with it. Vaccines and immune cells: a soft painted/paper-cell look or a tactile diorama; a machine-learning explainer: physical machinery, printed matrices, punched cards, or a pixel world, not floating glowing UI. Deliberately pick a medium that surprises you.

## Step 3: write the direction spec (one page, in the plan)

- **Medium and the one-sentence reason it fits**
- **Shape language** (round, angular, blocky, organic; corner and stroke rules)
- **Line and texture** (outline weights, grain, paper, halftone, none)
- **Light and depth** (flat, layered parallax, lit 3D; where shadows fall)
- **Palette with roles** (ground, ink, 1-3 accents, data series). State the ground color and confirm it isn't the default
- **Type system** (max two families, sizes as a scale, where type lives in the frame)
- **Motion vocabulary**: frame cadence (smooth 60/30, stepped on twos or fours), easing family, how things enter and exit, what a "hit" feels like. Different media move differently: pixel art steps, cut-paper snaps and slides, clay squashes, blueprints draw on
- **Camera**: static, slow push, parallax pan, orbit, whip; how it cuts between scenes
- **Transition set**: 3-5 named transitions used with intent
- **Sound**: the sonic equivalent (foley for paper, chiptune for pixel, room tone for 3D)
- **Bans**: this project's ban list

## Step 4: show three real directions before committing

For anything with a storyboard, produce **three genuinely different directions** as **rendered stills of the same key moment** (not descriptions, not palette swaps), each in a different medium from the menu. Give the user your recommendation and why. Rules:

- The three must differ in medium and composition, and at least one should be a bold choice you think might work but aren't sure of.
- Each still must show real content from the piece (real label, real diagram beat), not lorem ipsum.
- Pixel-different is not different: place all three in a contact sheet, blur your eyes; if the three look like siblings, redo two of them.

If the user has already named a style or provided references, skip the three-way choice and instead render one still plus one riskier variation.

## Composition: use the whole frame

- One dominant subject at real scale. If the hero occupies under a third of the frame, justify it or scale up.
- Build **foreground / midground / background**; move them at different rates.
- Vary shot scale within a sequence (wide, medium, tight, macro), like an editor would. Cut or camera-move between scales rather than fading in place.
- Let objects **do** things to each other (collide, carry, chase, pour, connect) rather than appearing labelled next to each other.
- Metaphor before diagram: for every concept ask "what tangible thing does this behave like?" and animate that thing. Use boxes and arrows only when the abstraction *is* boxes and arrows.
- Text is a supporting actor: label sparingly, big enough to read on a phone (body text at least ~4% of frame height on 16:9), and prefer showing to captioning. Tiny monospace annotations are a tell.
- Section and chapter markers should differ in *design* as the story changes mood, not repeat one template.

## Motion craft beyond default easing

- Anticipation, follow-through, overlap, settle. Things with mass should feel like it.
- Ease curves per medium (see motion vocabulary), never one global ease.
- Stagger with purpose, not uniform 60ms offsets.
- Use holds and stillness. Constant motion reads as noise.
- Match cuts and shape/scale continuity across scene changes, not just dissolves.
- Add small imperfection where the medium calls for it (jitter, misregistration, grain), seeded so renders are deterministic.

## The audit (run before the final render)

1. **Ban-list check**: scan the contact sheet against the ban list. Any hit needs a written reason.
2. **Squint test**: could this contact sheet be mistaken for the default described at the top of this file? If yes, it's not done.
3. **Family resemblance across your own work**: if you've built a previous piece in this project or session, put the two contact sheets side by side. If only color and type differ, change the medium.
4. **Silent test**: mute the audio and watch stills: does each frame carry one clear idea?
5. **Phone test**: view a still at ~400 px wide. Can you read the labels and see the subject?
6. **Furniture test**: count type elements. More than a title, one line and one small functional label (a stamp,
   a chapter number) needs a reason. Delete metadata rows, stats, palette strips and decorative annotations.
7. **Clone test**: next to its closest library still and the last piece made with this skill, does it read as the
   same piece with new nouns? If so, change composition, palette and at least one signature element.
8. **Derivation test**: every shadow, cast, reflection and rim light must come from its source (same layer,
   same light direction). Mismatched edges or rims on the wrong side read as fake at a glance.
