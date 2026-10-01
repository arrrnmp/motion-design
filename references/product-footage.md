# Product footage: launch videos, demos, and anything that shows real software

Read at phase 2 whenever the video shows a product, app, site, CLI or UI that exists (or whose source is available), and again before building any scene that contains it.

## The rule

**If the product is on screen, the product is what's on screen.** Capture the real thing running. Do not redraw it, re-typeset it, or screenshot a hand-built approximation of it. A mockup written from memory of the codebase is always wrong in dozens of small ways (spacing, type, states, density, colour tokens, icon set, copy), and viewers who know the product spot it instantly. Full creative freedom applies to *everything around* the product (framing, camera, motion, sound, type, transitions); the UI itself is evidence and stays faithful.

Failure this prevents: having the whole codebase, then building "inspired by" mockups, screenshotting them into Remotion, and getting frames that look like a different product.

## Fidelity ladder (use the highest rung available; write down which one and why)

1. **Live capture of the real app** driving real interactions (recorded video or frame-exact captures).
2. **The real UI code rendered in the video pipeline** (import the app's components into Remotion/Canvas, feed them fixture data, drive them by frame). Best for React/web apps: pixel-true, resolution-independent, deterministic, and you can animate state.
3. **Real renderer output from a harness** (test renderer, Storybook, snapshot/render-check tool, design-system playground) saved as structured data or images.
4. **The project's own design source** (Figma export, `.html` design files, tokens) rendered as-is, never re-interpreted.
5. Hand-built recreation. **Last resort.** Only with the user's OK, built from extracted tokens and real assets (rung 4 inputs), and labelled as illustration in the report.

Never drop to a lower rung because it is quicker. Dropping is a checkpoint-worthy decision, not a silent one.

## Phase 0 for launch work: product recon (before direction, before storyboard)

Spend real time here; it is cheaper than redoing scenes.

1. **What surfaces exist?** Web app, desktop (Electron/Tauri/native), mobile, TUI, CLI, browser extension, docs site, marketing site. List each with how it is launched (`package.json` scripts, README, Makefile, `launch.json`, Docker).
2. **How can each run without production data?** Look for: dev servers, mock clients, seed/fixture files, Storybook, test/render harnesses, snapshot tools (an existing "render-check"/visual-test setup is gold), demo modes, design-preview pages. Run it. Look at it with your own eyes (screenshot, `read_page`) before planning.
3. **Extract the real look**: design tokens, CSS variables, theme files, fonts actually loaded (and their licenses), icon set, logo/wordmark files, existing brand or marketing assets, copy tone from README/landing page. Use those exact values; don't eyeball colours from a screenshot.
4. **Inventory the moments**: the 5-10 states or flows that actually sell the product (the "hero flow", the differentiating feature, the before/after). Verify each exists and works in the current build. Pull feature names and claims from the code and docs, not from memory.
5. **Data**: decide the story data (repo names, users, messages, numbers). Make it realistic, specific and on-brand, with no secrets, no real people, no third-party marks. Put it in one fixtures file that every capture reads, so all scenes tell one consistent story.

Write findings in a short `product-notes.md` in the project: surfaces, run commands, which fidelity rung each uses, tokens/fonts/assets, the moment list, fixtures location.

## Capture routes by surface

- **Web / Electron / Tauri UI**: Playwright or puppeteer against the dev server (or a static build) with fixture data or a mocked backend. Set `deviceScaleFactor` 2+ for crisp crops; fixed viewport; disable animations you don't want; freeze time/random (`page.clock`, seeded RNG). For motion, either record video (`recordVideo`, or screencast frames) of scripted interactions, or step the page and capture frames at a fixed rate. Scripted interactions (click, type at human speed, scroll) beat static shots: motion is what launch videos sell.
- **React/web components inside Remotion** (rung 2): alias the app's source into the Remotion bundler, mount the real components with fixture props/providers, drive state from `useCurrentFrame`. Stub network/router/native modules at the boundary. Check fonts and CSS are actually loaded.
- **iOS / Android**: simulator/emulator with a fixture build; `xcrun simctl io booted recordVideo` / `screenshot`, `adb shell screenrecord`. Set clean status bar (`simctl status_bar override`), demo mode on Android.
- **TUI / CLI**: prefer the app's own test/render harness dumping per-cell glyph + fg/bg (draw the cells yourself in the video, in the same monospace font, so it stays sharp and animatable), or record a real terminal (`vhs`, `asciinema` + `agg`, tmux + screenshots) at a fixed size with the user's actual theme. Do not type-set fake terminal output by hand.
- **Native desktop apps**: screen-record a real window (`screencapture -v`, ffmpeg avfoundation) on a clean account/desktop with fixture data; crop and scale in post.
- **Marketing site / docs**: browser capture with scroll scripting; never retype the copy.
- **Not runnable** (needs credentials, hardware, paid backend): say so, then choose between fixtures/mocks at the network boundary, the design source (rung 4), or asking the user for a screen recording. Don't quietly fall back to inventing UI.

Keep capture scripts in the repo (`capture/`), deterministic and re-runnable; commit outputs' provenance (script + fixtures + commit hash). When the product changes, re-run captures rather than editing frames.

## Fidelity gate (a checkpoint, before any scene is built around the footage)

Render a **footage proof**: 3-6 stills or 2-second clips of the real captures for the key moments, next to a screenshot of the actual running product for the same state (use `scripts/compare_frames.sh`). Check and state the result for: fonts, colour values, spacing/density, icons, copy, window chrome, state correctness, no placeholder or leaked data, sharpness at 1080p and at the crop/zoom scale you plan to use. Show it to the user with the moment list. Approve before storyboarding scenes around it.

A frame that a maintainer of the product would call "not quite ours" fails the gate, whatever it looks like otherwise.

## Composition around real footage

- The **direction** (medium, motion vocabulary, sound) governs the frame, transitions, typography and camera. The UI inside stays as captured; don't restyle it to match the direction. Let the direction show up in how the footage is presented (plates, masks, perspective, depth, cuts on the beat), and in the bridging scenes.
- **Show, don't tell**: each product beat is a real interaction playing out, with a short line of type naming the outcome. Avoid static screenshots sliding around; if a still is all you have, punch in and move within it purposefully, and know it's the weaker option.
- **Legibility**: UI is dense, video is small. Crop and zoom to the part that matters (the diff line, the button, the status chip) and hold it long enough to read. Check at phone size. One region of interest per shot.
- **Synthetic guidance is fine, synthetic UI is not**: cursor with easing and click ripple, highlight rings, zoom follow, callouts, speed ramps over waiting time. Keep them consistent.
- **Cuts that respect causality**: the click and its result appear in the same shot or a match cut; don't splice states that could not occur in sequence.
- **Continuity**: same fixture story, same window size and theme across scenes.
- **Claims match the product**: every feature named, number shown and command typed must be true in the current build. If narration says it, footage shows it.

## Launch-video shape (default beats; adapt to the direction)

Hook (the problem or the surprising result, within ~3 s) -> the product doing its hero flow, for real -> 2-3 differentiating moments, each a real capture -> proof/credibility beat if any (numbers, integrations, open source) -> call to action with the real install line / URL. Music and cuts locked to one timeline; see `SKILL.md` section 5. Length: 30-60 s for social/launch unless told otherwise.

## Anti-patterns (treat as ban-list items for launch work)

- Hand-writing HTML/SVG "mockups" of the product when the product can be run.
- Screenshots of those mockups as the hero footage.
- Approximate colours, generic system fonts, stock icon sets in place of the product's own.
- Lorem-ipsum-grade or generic data ("User 1", "Project Alpha") instead of a specific, believable story.
- Showing features from memory of the code without running them.
- Real secrets, emails, third-party repo/company names or personal data visible in captures.
- Restyling the product UI to fit the video's aesthetic.
- Declaring done without the fidelity gate.
