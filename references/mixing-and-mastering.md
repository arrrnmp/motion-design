# Mixing and Mastering

Read when you are combining more than one sound (music parts, voice, SFX) or finishing any audio that will ship. `music-and-sound.md` covers how to *make* the sounds and the platform loudness targets; this file covers how they sit together and how the result is finished.

**You can't hear, so a mix here is a set of measured decisions.** Every rule below ends in a number you can compute. Run `scripts/mix_report.py` after each mix pass and treat its output as your ears. The user makes the final taste calls, so hand them the numbers and a short audition, not a claim that it "sounds great".

## The mental model

Each part (kick, bass, lead, pad, hats, a whoosh, the narrator) owns four things. Level alone never stops parts fighting, so assign all four:

1. **A level** relative to the section's hero (the one thing that should be most forward).
2. **A frequency home** where it is the loudest thing, and a filter that keeps it out of everyone else's.
3. **A stereo position** (centre for the low end and the hero; width for pads and air).
4. **A place in time**: when it plays, when it ducks, when it drops out.

"Overlap" is mostly **masking**: two parts loud in the same band at the same moment, so the quieter one disappears. Fixing it with volume alone makes the mix loud and thin. Carve frequency, then time, then level.

**Mixing vs mastering.** Mixing balances the parts (stems) against each other. Mastering treats the finished stereo mix: tonal balance, glue, limiting, loudness. Never use the master limiter to fix a balance problem; go back to the stems.

## Workflow

1. **Render every part as its own stem**, not just a stereo mix. Strudel: one orbit per role and record each solo (or mute all others per pass). SuperCollider: one bus per role. MIDI: one track per role. Same sample rate, same start, same length (pad with silence). Without stems you can only master, not mix.
2. **Gain-stage the stems.** Work in 32-bit float at 48 kHz (video standard); export 24-bit. Normalize sustained parts (bass, pads, leads, voice) by **loudness** and percussive or one-shot parts (kick, snare, hats, SFX) by **peak**, since the loudness of sparse hits is misleading. This gives every stem the same neutral starting point so the offsets in the next table mean something.
3. **Set the balance** with the role table, hero first, then the low end, then everything else in order of importance.
4. **Slot the frequencies** (next section), then the stereo field.
5. **Add space** (reverb/delay) on shared send buses, not per part.
6. **Bus and glue**: group buses (drums, bass, music, FX), light compression.
7. **Measure** with `mix_report.py --mix mix.wav --stems *.wav`. Fix what it flags at the stem, re-render, re-measure. Cap at about five passes, then report what remains.
8. **Master** the stereo mix (below), then run `scripts/check_delivery.py` on the final file.

Keep the mix bus peaking around **−6 dBFS or lower** before mastering. Headroom is what the master processing works with.

## Level budget

Starting points, not laws. Levels are relative to the hero at 0 dB (LU for sustained parts, dB of peak for percussive), ±3 dB depending on density. The measured band balance and the mix's short-term loudness decide the final numbers.

| Role | Frequency home | vs hero | Stereo |
|---|---|---|---|
| Lead, vocal, hook melody (hero) | 200 Hz–5 kHz | 0 | centre |
| Kick | 40–100 Hz thump, 2–5 kHz click | −3 to 0 | centre |
| Bass | 40–250 Hz | −3 to −1 | centre, mono below 120 Hz |
| Snare, clap | 150–250 Hz body, 2–5 kHz crack | −4 to −1 | centre; reverb wide |
| Chords, keys, guitars | 150 Hz–4 kHz | −8 to −4 | moderate width |
| Arps, plucks, counter-melody | 500 Hz–6 kHz | −8 to −5 | offset left/right |
| Pads, strings, atmosphere | 200 Hz–8 kHz | −14 to −8 | wide |
| Hats, shakers, top loops | 6–16 kHz | −14 to −8 | ±20–50% |
| SFX, risers, whooshes | broadband, transient | −10 to −4 at peak | matched to the on-screen motion |
| Reverb/delay returns | follows the send | tuck until the tail is felt but not heard | wide |

In a scored or narrated video the **voice is the hero** and the whole music bed sits under it (see "Music under speech").

## Slotting: frequency, stereo, time

**Frequency**
- **One owner per band at a time.** Assign each band to a part; carve the others. The 200–500 Hz range (mud) and 2–4 kHz (presence, where speech lives) are the usual battlegrounds.
- **High-pass everything that doesn't need lows.** Starting points: leads and vocals ~80–120 Hz, chords/guitars ~100–200 Hz, pads ~150–250 Hz, hats and tops ~300–500 Hz. Only kick, bass and deliberate sub parts go below 60 Hz.
- **Kick vs bass**: give them different jobs (kick at the transient and upper sub, bass sustaining below or above it) and duck the bass 3–6 dB from the kick (sidechain, attack 1–5 ms, release 80–150 ms, tuned to the tempo). Strudel's ducking (`duckorbit` and related) exists in recent versions; check the installed one.
- **Cut before you boost.** Prefer wide, small cuts (2–4 dB) on the competing part over boosting the one you want heard. Use narrow cuts only for a resonance you have measured.
- Low pass or shelf pads and reverb returns so they sit behind, not on top.

**Stereo**
- Centre: kick, bass, snare, lead/voice. Width: pads, ambience, reverbs, doubled parts.
- **Below ~120 Hz must be near-mono.** The report's `<120 Hz correlation` should be above ~0.9. Fix with a mono-ing filter on the bass bus, not by muting.
- Mono fold-down loss beyond ~4 dB means phase cancellation. Uncorrelated wide material folds down about −3 dB, which is normal.

**Time**
- The cheapest fix is arrangement: **not everything plays all the time.** If more than three or four sustained parts compete in the same section, mute one and re-measure before touching EQ.
- Stagger transients (kick, snare, bass note starts) by a few ms or a different envelope shape instead of stacking them on the same sample.
- Ride section levels (below) instead of leaving every part on all the way through.

## Consistent loudness across the whole song

Loudness that holds steady is measured with **short-term LUFS** (3 s window), not with integrated LUFS alone. `mix_report.py` prints the range and lists spans outside tolerance.

- **Body of the song**: short-term stays within about ±1.5 LU of the target. Intros, outros and breakdowns may differ by up to about 3 LU *on purpose*. Anything else outside tolerance is a bug to fix.
- **Section changes**: no step larger than ~2 LU unless it's an intended drop or hit. Some contrast is musical; a totally flat song feels lifeless, so don't flatten it beyond what the user asks for.
- **The usual cause in generated music is density**: more layers means a louder sum. Compensate at the **stem/section level**: measure each section's short-term loudness, apply a trim (smooth ramp over a bar, never a step) to the group that changed, re-measure. Don't fix it with a compressor or limiter on the whole mix.
- **Loudness range (LRA)** for music is typically about 3–6 LU; report it. A much bigger LRA means uneven sections, a much smaller one means it's squashed.
- Automate levels from the arrangement data (section and beat times already exist when music is composed in code), not by hand-placing values.

## Music under speech

- **Voice at the platform target, music beneath it.** Keep the music bed roughly 12–18 LU below the voice's short-term loudness while speaking. Measure the voice and music stems separately, then set the bed from those numbers.
- **Duck from the narration's word timestamps** (already used for timing): about 6–10 dB of gain reduction, attack 50–150 ms, release 300–800 ms, so the music breathes and doesn't pump.
- **Carve as well as duck**: a 2–4 dB wide dip at 1–4 kHz on the music bus during speech keeps consonants clear without lowering the whole bed. Then check the report for a clash between the music stem and the voice stem in the presence band.
- Music-only stretches (intro, outro, gaps) may rise a few LU above the ducked level, but never so far that the voice sections are perceived as quiet. Compare short-term loudness on both.

## Mastering the stereo mix

Order of operations on the final bus:

1. **Check the input**: peaks ≤ −6 dBFS, balanced left/right, mono-safe, no clipping, no DC offset.
2. **Corrective EQ**: a high-pass around 20–30 Hz; gentle tilts or shelves only; keep moves ≤ 2 dB.
3. **Glue compression** (optional): ratio 1.5:1–2:1, slow attack (~30 ms), auto or medium release, no more than ~2 dB of gain reduction.
4. **Limiter** (true-peak, at least 4× oversampling) as the last processor. Ceiling **−1 dBTP** (−2 dBTP for low-bitrate lossy delivery or when the platform re-encodes heavily). Drive it only far enough to reach the loudness target.
5. **Loudness**: hit the target from `music-and-sound.md` (−16 LUFS for most online video unless told otherwise). Use ffmpeg `loudnorm` two-pass with `linear=true` for the last few dB of gain. If it falls back to dynamic mode or the limiter is working hard, the problem is upstream.

Limits that tell you the master is being asked to do the mixer's job:
- **Limiter gain reduction** averaging more than ~3 dB, or peaks needing more than ~5 dB: fix the crest of the offending stem (a spiky kick, an over-hot transient) and re-mix.
- **PLR** (true peak minus integrated LUFS) below about 8–9 dB: the mix is over-compressed for its target. At −16 LUFS with a −1 dBTP ceiling PLR should be well above that.
- **Two-pass rule**: re-measure the final file. Don't trust the filter's report.

**Sample rate and format**: master at the delivery rate (48 kHz for video). Dither only when reducing to 16 bit. Leave headroom for AAC/MP3 encoding, which overshoots peaks slightly.

## Tools

`pedalboard` (EQ, compressor, limiter, gain, filters, reverb, all scriptable) for the processing; ffmpeg `ebur128`, `loudnorm`, `astats` for measurement; `pyloudnorm` and `librosa` for extra analysis. All are covered by `tools-and-installs.md`. `mix_report.py` needs only ffmpeg, numpy and scipy.

Optional: `matchering` can match a mix to a reference track's tonal balance and loudness; use it as a second opinion, not a replacement for the stem-level work.

## Checks before you report

Run these on the final mix and its stems, and report the numbers:

- `mix_report.py --mix final.wav --stems stems/*.wav --target <LUFS>`: no unexplained short-term spans outside tolerance; every listed clash resolved or deliberately accepted.
- Low end mono (`<120 Hz` correlation above ~0.9); mono fold-down loss not beyond ~4 dB.
- True peak ≤ the ceiling; PLR sane; no clipping; no unexpected silence or dropouts.
- **Spectrogram** of the final mix, looked at: mud between 200–500 Hz, harshness at 2–5 kHz, missing top end, music masking speech.
- If the user gave a reference track, run the same report on it and compare band balance and short-term range **loudness-matched** (raise or lower the reference to the same LUFS first). Otherwise the louder one always seems better.
- `scripts/check_delivery.py final.mp4 --lufs <target>` on the finished video.

Say in the report which parts were the hero in each section, which clashes you found and how you resolved them, and what you measured but couldn't judge by ear.
