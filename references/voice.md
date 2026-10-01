# Voice and Narration

## Choosing the source

| Source | When |
|---|---|
| User's own recordings | They want their voice and can record; best authenticity |
| Clone of the user's voice | They want their voice at scale / in other languages; needs clean reference audio (quiet room, no music, ideally 30 s+). Cloning a voice needs that person's consent — only clone the user's own voice or one they have rights to |
| Designed or stock TTS voice | Most explainers and ads |
| None | Music-led pieces, stings, many social clips |

Prefer local TTS. Cloud TTS means accounts, cost and the script leaving the machine — ask first.

## Generation workflow

1. Split the script into natural **paragraph-sized chunks** (a thought each). Too short sounds choppy; too long drifts.
2. Generate **several takes per chunk** (e.g. 3–5), with fixed seeds recorded so a chosen take is reproducible.
3. **Verify every take with speech-to-text** (e.g. Whisper / faster-whisper / whisper.cpp with word timestamps). Compute word error rate against the script, and check for dropped/repeated words, garbled names, clipped endings, long silences.
4. **Pick the best take automatically**: lowest WER, then no artifacts, then closest to target speaking rate and loudness.
5. If a word is wrong in **every** take, don't keep rolling the dice — **reword** (respell phonetically, rephrase, expand abbreviations/numbers, add punctuation for phrasing) and regenerate that chunk.
6. Keep the word timestamps from the chosen takes: they drive animation timing and captions.

## You can't hear — so measure

Report numbers to the user alongside auditions; the final taste calls are theirs.
- **Loudness**: integrated LUFS and true peak (`ffmpeg -af ebur128=peak=true` or pyloudnorm).
- **Pitch**: median F0 (e.g. librosa `pyin`, parselmouth/Praat) — especially when asked for a deeper or higher voice; report before/after.
- **Speaking rate**: words per minute from STT timestamps (typical narration 140–170 wpm; explainers for learners slower).
- **Similarity when cloning**: speaker-embedding cosine similarity (e.g. resemblyzer, SpeechBrain ECAPA) between reference and output.
- **Spectra and clipping when mixing**: spectrogram images you actually look at; count samples at/near full scale.

## Fixing pacing

Fix pacing with a **pitch-preserving time-stretch** (Rubber Band: `rubberband -T <ratio>` or `ffmpeg -af rubberband=tempo=<ratio>`; `atempo` as fallback) rather than regenerating — regeneration changes delivery and timing, stretching doesn't. Keep stretches modest (~0.9–1.1) to avoid artifacts; adjust pauses between chunks for larger changes. Re-run alignment after any stretch so timestamps stay correct.
