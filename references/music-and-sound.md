# Music and Sound

## Prefer composing in code

Strudel (the JavaScript port of TidalCycles) or real TidalCycles suit electronic, ambient, lo-fi, synthwave and experimental scores. Tempo and structure live in the code, so you get **exact beat and bar timestamps** for syncing visuals — no beat detection needed. Export those timestamps (e.g. a JSON of bar/beat/section times computed from cps/BPM and the arrangement) alongside the WAV.

Always produce the final WAV **locally**, and **verify which route works on this machine** with a 5-second test before relying on it.

### Strudel routes
- Run it in a headless browser (Playwright/Puppeteer with autoplay allowed) and capture the audio output — e.g. route the WebAudio graph into a `MediaRecorder`, or render through an `OfflineAudioContext` where possible.
- Or use Strudel's own export / offline rendering if the installed version supports it (check the version's docs first).

### TidalCycles route
- Run SuperCollider with SuperDirt headless via an `sclang` script.
- Drive the patterns from Tidal (GHCi with the Tidal boot file).
- Record the server's output to WAV using SuperCollider's own recording (`s.prepareForRecord(path); s.record; ... s.stopRecording`).

### For all routes
Render the exact target length with a clean start (no pre-roll junk) and a natural tail (let reverbs decay; fade if needed). Then check the WAV for: leading/trailing silence, unexpected dropouts (silencedetect), clipping, and exact duration.

### The numpy synth route (verified; no installs beyond numpy/scipy/soundfile)
`assets/lib/synth.py` renders scores and SFX directly: oscillators (pulse with duty + vibrato for 2A03-style
chiptune, triangle, sine with pitch sweeps, FM for e-piano/bells/kalimba/music box, Karplus-Strong plucks, stepped
"NES" noise), envelopes, filters (incl. a moving band-pass for scrapes and whooshes), a small stereo reverb, a
`Mix` bus with pan, a two-pass `loudnorm` master (-16 LUFS, TP -2) and `mux`. Every event is placed in seconds
computed from the visual's own frame schedule, so sync is exact and survives re-timing. Worked examples:
`assets/styles/{04,12,15,16,17}-*/sound.py` (chiptune + pick SFX; reactive lo-fi; carving foley → stamp → folk
groove; stitch foley + music box; nave pad following a light curve). You can't hear the result: verify by
measurement (below), not by trust.

### Scores that react to what's on screen
Log the visual's state per frame (chapter, progress, typed characters, theme, events) and drive the mix from it:
layer gains per section crossfaded with a one-pole smoother, a low-pass cutoff mapped to scroll/camera speed,
one-shot SFX on state changes. For a live web page, capture it deterministically first (virtual clock; see
`verification.md`) so the log and the video match frame for frame (`assets/styles/12-coded-ascii/`).

### Background music on a website
Autoplay is blocked until a user gesture: start on the first click/keypress, offer a visible toggle (and a key),
remember the choice, fade in/out with a gain node. For a gapless loop, render three cycles (so reverb tails wrap),
keep the middle cycle twice in the file, and loop a one-cycle window from inside it with WebAudio
`loopStart/loopEnd` (MP3 encoder padding then never lands in the loop). Master web loops quieter (~-20 LUFS).

### Other routes
- **Sonic Pi** — scriptable, good for melodic/structured pieces.
- **MIDI + soundfonts** (e.g. FluidSynth) — orchestral/acoustic sketches with exact timing from the MIDI.
- **Local music models** (MusicGen, Stable Audio Open, ACE-Step) — when the style is orchestral or realistic acoustic and code can't sound right. You lose exact beat times; detect onsets/beats afterwards (librosa, madmom) and verify them visually against the waveform.

## Licensing

Use synthesized sound, or sample packs / soundfonts whose licenses you've actually checked — especially for anything public or commercial. Record the license of every third-party asset in the project notes. Model outputs carry their model's license terms; check them for commercial use.

## Sound design and mix

Balancing several parts, keeping loudness even through the song, ducking under speech and the full mastering chain live in `mixing-and-mastering.md`. Render each part as a separate stem so that file's workflow is possible.

Add what the project calls for:
- A music bed, a full score, or per-section moods.
- Stings on reveals and logo moments.
- SFX on animation beats (whooshes on transitions, ticks on counters, pops on appearances) — placed from the same timing data as the visuals, so they stay in sync when timing changes.
- **Ducking** music under speech, driven by the narration's word timestamps (sidechain or computed gain automation with smooth attack/release), not by guesswork.

Master (platform targets; the chain and the checks are in `mixing-and-mastering.md`):
- Normalize to the platform target: around **−16 LUFS integrated** for most online video unless told otherwise (YouTube ~−14, podcasts ~−16, broadcast −23/−24), true peak ≤ −1 dBTP.
- Use two-pass `loudnorm` in ffmpeg or pyloudnorm, and re-measure the final file rather than trusting the filter.
- Check for clipping and look at a spectrogram of the final mix (muddy low-mids, harsh sibilance, music masking speech).

- Check band balance numerically, not just the spectrogram: mean level under 150 Hz vs an octave band around
  600-800 Hz vs above 3 kHz. Synth bass (triangle, sine kick, plucked bass) dominates after loudness
  normalisation; a 30-40 Hz high-pass and pulling the bass 4-6 dB fixed every score here. Look for dropouts
  where notes end abruptly (give plucks a release and let notes overlap).

Report the measured numbers to the user; they make the final taste calls.
