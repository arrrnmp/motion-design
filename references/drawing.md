# Drawing and Illustration

Principle: **draw with code first.** Code-drawn art is editable, animatable, resolution-independent, deterministic and consistent in style. Reach for generative models only where code genuinely can't get there — and even then, keep control of the composition.

The medium comes from the direction spec (`direction.md`), not from whatever is easiest. Pixel art, cut-paper, cel and clay looks are first-class choices, not exotic ones: budget for them at planning time.

## Choosing the method

| Subject / style | Method |
|---|---|
| Flat, geometric, iconographic, isometric, diagrammatic | Hand-authored SVG |
| Pixel art, sprites | Explicit pixel grids + fixed palette; Aseprite Lua for real sprite work |
| Textures, noise, particles, generative patterns | Procedural canvas or shaders (GLSL/WGSL), seeded |
| Faces, anatomy, fur, painterly, complex characters | Local image model (FLUX, SDXL + style LoRAs) under ControlNet/img2img from your own layout |
| Same character/object from many angles | Model or pose in Blender; render flat, toon-shaded or pixelated |

## Hand-authored SVG

- Build it **parametric and layered**: named groups (`<g id="sky">`, `<g id="building-3">`), colors as variables/tokens, geometry driven by parameters. That lets one source produce variants — time of day, weather, UI states, brand recolors — and lets each layer animate independently.
- Keep a consistent stroke weight, corner radius and light direction across all pieces; that's most of what makes a set feel like one hand drew it.
- Isometric: work on a real isometric grid (30° axes), not eyeballed angles.
- Check drawings by rasterizing them (resvg, rsvg-convert, Inkscape CLI, or a headless browser) and looking at the PNG.

## Simulated physical processes (proven in the style library)

When the direction is a print or craft process, build the process: separate ink plates screened and misregistered
(`assets/lib/print.js`), carving with `destination-out` gouges then printing, pigment strokes with p5.brush (crayon,
G-pen, watercolour), stitches as lit floss strokes on woven cloth, dithered palette ramps for pixel art. See
`style-library.md` for working templates of each.

## Pixel art

- Author as explicit grids (arrays of palette indices) with a fixed, small palette.
- Sprite animation = frame edits on the grid (move a limb 1px, swap an eye state), not redrawing.
- Use Aseprite's Lua scripting (`aseprite -b --script`) when you need real sprite sheets, tags, onion-skinned animation or export.
- Scale up only by integer nearest-neighbor factors; never smooth-filter pixel art.

## Generative models, under control

For subjects code can't reach well:
1. Draw the layout yourself as a rough SVG (silhouettes, poses, horizon, focal placement).
2. Feed it through ControlNet (lineart/depth/pose) or img2img at moderate strength so the model adds detail but not composition.
3. Use a style LoRA or reference to keep a consistent look; fix the seed.
4. **Bring everything back into one style** with the rest of the piece: palette mapping, consistent grain, matching line weight, color grading.

Run models locally where possible. Cloud generation services need the user's permission first (accounts, cost, and their content leaving the machine).

### Post-processing generated images

- **Real pixel art**: generated "pixel art" is fake until quantized. Downscale to the exact target grid (nearest/box), map every pixel to the fixed palette, then clean stray/orphan pixels and fix outlines. Only then is it real pixel art.
- **Flat vector looks**: trace with `vtracer` (color) or `potrace` (monochrome) into SVG, then simplify paths and tidy layers so it animates like hand-drawn art.

## Anything that moves

Build characters and props as **separate parts, cut-out-rig style** — head, torso, upper/lower arms, hands, eyes, mouth shapes — with pivot points at joints. A single frozen image can only slide around; a rig can act. For generated characters, generate or paint the parts separately (or split them after), then rig.

## Consistency across angles

When a character or object must appear from many angles or poses, model or pose it in Blender (headless via Python) and render with a flat, toon (Freestyle/Grease Pencil or toon shader) or pixelated look. It stays on-model in a way independent image generations won't.
