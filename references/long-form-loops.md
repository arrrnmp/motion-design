# Long-form ambient loops ("radio" pieces)

Hours-long, low-attention pieces: a lo-fi/ambient stream with a slow looping world, a character living in it, and a
"now playing" label. Reference in spirit: Claude FM (a 2 h stream: a pixel character wandering an ASCII-rendered world
on paper, occasionally a dark night scene, one small track label). **Don't copy that piece**: take its structure
(slow scene cycle + one character + a label + a gapless loop) and build it in a direction chosen for the job.

Worked example (a mix of two library styles, not a clone of either): `assets/patterns/ambient-loop/`
— riso print engine (01) + a character-in-a-world structure like the pixel diorama (04): a cherry lives through a day
in four printed vignettes, each its own ink pair; time of day = which ink drums are in the machine, never a dark
ground; a new sheet slides in over the last between scenes; the stamped label is the only UI.

## Rules
- **Structure:** a schedule of scenes (vignettes), each 20 s to several minutes, with a slow idle loop inside it
  (character action + ambient motion) and a signature transition between them. The last frame must equal the first
  (check the seam: pixel diff 0). For hours of runtime, lengthen the schedule and cycle scenes; don't render 2 h of
  unique frames unless it's needed.
- **Low-attention motion:** idles are gentle and cyclic (swinging legs, pedalling, rocking, rowing), nothing snaps
  except scene changes, no text beyond the label. A viewer glancing up at any moment should see a nice still.
- **Label:** one element, top-left or top-right, in the style's own idiom (stamped in riso, a pixel box in pixel
  art, a glyph line in ASCII). Track names can be invented if the music is.
- **Sound:** one track per scene (different key, tempo, colour), equal-power crossfades under the transitions (start
  the next track under the slide), the process's foley at low level (riso drum tick per re-print), per-scene ambience;
  wrap the tail around so the audio loops too. Master -16 LUFS for video.
- **Delivery:** full-frame grain re-rolled every frame barely compresses (the 96 s sample was 240 MB at CRF 22).
  Deliver a bitrate-capped share version too (8-10 Mb/s with `-tune grain`), and for multi-hour pieces render the
  loop once and loop it with ffmpeg (`-stream_loop`) rather than re-rendering.
