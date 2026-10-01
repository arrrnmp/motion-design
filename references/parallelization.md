# Parallelization and Utilization

Default failure: a render runs as **one process, mostly single-threaded Python, at low utilization**, e.g. 10-15% CPU and half the GPU, and finishes at a modest pace while the machine mostly sits idle. That's a bug in the pipeline, not a fact about the hardware. Treat idle capacity as something to fix.

## 1. Measure before and during every long job

- Sample utilization for ~10-20 seconds during a test render: per-core CPU (`top`/`htop`, Activity Monitor, Task Manager, `Get-Counter '\Processor(*)\% Processor Time'`), GPU (`nvidia-smi dmon`/`nvidia-smi -l 1`, `powermetrics`, Task Manager GPU engines), disk and RAM.
- Read the pattern:
  - **One core pegged, everything else idle** -> single-threaded stage (Python glue, scene setup, per-frame callbacks, image saving, encoding).
  - **GPU below ~80% with gaps** -> the GPU is waiting on the CPU: per-frame setup, file I/O, denoising handoff, synchronization.
  - **CPU and GPU both low** -> waiting on disk, network, or a serial pipeline (render, then encode, then next).
- Write down the numbers. After any change, measure again. Report utilization in the final notes.

## 2. Where the serial bottleneck usually hides

| Symptom | Common cause | Fix |
|---|---|---|
| Blender GPU busy in bursts, CPU ~10% | One Blender process; per-frame Python (`frame_change` handlers, driver expressions, scripted animation), scene sync between frames, PNG compression, denoise/save on one thread | Several Blender processes, each rendering a frame range; bake or keyframe motion instead of computing it in per-frame Python; lighter PNG compression; persistent data on |
| Headless-browser renders slow | One page rendering sequentially | N parallel pages/processes over frame ranges (bounded by cores and RAM); avoid huge media inside the page (see verification.md) |
| Python frame generation slow | Pure-Python loops over pixels/particles/points | Vectorize (numpy), move hot loops to GPU (moderngl, torch), or use `multiprocessing`/process pools over frame ranges |
| Encoding after all frames finish | Serial pipeline | Stream frames to ffmpeg as they render, or encode chunks in parallel and concatenate; use hardware encoders (`videotoolbox`, `nvenc`, `qsv`) for previews |
| GPU idle while CPU renders | Work isn't split by hardware | Put GPU-bound jobs (Cycles, EEVEE, models) and CPU-bound jobs (browser renders, encoding, TTS) on different devices and run them at the same time |
| Model inference underused | Batch size 1 | Raise batch size until VRAM (not shared memory) is the limit |

Python glue is fine for orchestration. Keep it out of the per-frame/per-pixel path, and never let it be the thing the expensive hardware waits on.

## 3. Split the work, then keep every device busy

1. **Split by frame range** (or by scene/variant). Frame-independent renders are embarrassingly parallel. Give each worker a disjoint range, write frames to unique paths, then concatenate.
2. **Pick worker count from measurements**, not guesses. Start at (physical cores / threads-per-worker) or (GPU count x 1-2), then add workers until utilization stops improving or memory becomes the limit. Two-to-four workers per GPU often saturates it when the per-frame CPU work is significant; one is enough when a frame is purely GPU-bound.
3. **Pin resources per worker**: threads (`--threads N` in Blender, ffmpeg `-threads`), GPU device (`CUDA_VISIBLE_DEVICES`, Blender device prefs), and separate output dirs. Oversubscribing threads slows everything. Keep the worker count inside the memory budget (section 4).
4. **Blender specifics** (headless, `--background`):
   - Each worker: `blender -b scene.blend -E CYCLES|BLENDER_EEVEE -s START -e END -a` with its own output path (or `-f` for single frames), and `--threads N`.
   - Set the compute device in a startup script; confirm it in the log (a silent CPU fallback is common).
   - Render an image sequence (PNG/EXR), never straight to video, so a crash keeps finished frames and a worker can resume.
   - Use `bpy.data` over `bpy.ops`; avoid per-frame Python handlers in the render path.
   - EEVEE/Cycles preview settings (fewer samples, half resolution, denoise) for review, full quality for finals.
5. **Overlap stages**: render workers write frames while ffmpeg encodes finished chunks; narration/music generation runs while visuals render.
6. **Resume, don't restart**: skip frames that already exist and are valid; make each worker idempotent.
7. **Scheduler**: a small script (Python `concurrent.futures`, `xargs -P`, GNU parallel, PowerShell jobs launched as files) that spawns workers, logs each worker's range and exit code, and checks that every expected frame exists at the end.

## 4. Memory and resource safety (a hard limit, not a suggestion)

More workers means more memory. Running out of RAM, VRAM or disk doesn't fail politely: it swaps until the machine is unusable, gets processes killed by the OS, or freezes the whole system. Stay well inside the limits.

1. **Measure per-worker peak before scaling.** Run one worker on a representative, heaviest-scene sample and record peak resident memory (`/usr/bin/time -l` on macOS, `/usr/bin/time -v` on Linux, Task Manager / `Get-Process` peak working set on Windows) and peak VRAM (`nvidia-smi`, or Activity Monitor's GPU memory). Pick the *heaviest* frames, not the first ones.
2. **Budget workers from that number:**
   `workers = floor((available RAM - reserve) / peak RAM per worker)`, further capped by cores and VRAM. Keep a **reserve of at least 20% of total RAM (never under ~4 GB)** for the OS, the browser and the user's other apps. Use only *currently available* memory, since other apps may already be using it. Apply the same rule to VRAM with a reserve of ~10-15%.
3. **Ramp up, don't slam.** Start one worker, add another only after memory has stabilized, and stop adding when the next one would cross the budget or throughput stops improving. Memory often grows over a worker's lifetime (leaks, caches, growing scene state), so re-check after a few minutes.
4. **Know the heavy hitters.** Headless-browser pages (hundreds of MB to over 1 GB each, more with video/large images), Blender scenes with big textures/volumes/high-poly geometry (RAM x workers, plus VRAM x workers), image/video models (VRAM, plus RAM for offloading), and large frame buffers (EXR, 4K+ sequences). Don't run a model and a multi-worker render together unless the summed budgets fit.
5. **Never let memory spill silently.** GPU shared-memory fallback, macOS swap pressure and Windows commit growth don't crash, they slow everything by 5-50x. Treat swap growth or "memory pressure" turning yellow/red as a failure and back off.
6. **Give the scheduler a watchdog.** Every few seconds check available RAM (and VRAM, disk). Below the reserve: stop launching workers; if it keeps dropping, pause or kill the newest worker and re-queue its frames at lower concurrency. Log every intervention. Workers must be resumable (see above) so this costs seconds, not a restart.
7. **Cap each worker where the OS allows**: lower priority (`nice`/`renice`, `Start-Process -Priority BelowNormal`) so the machine stays responsive, and hard limits where available (`ulimit -v`, cgroups/`systemd-run -p MemoryMax=`, Windows job objects). Reduce per-worker footprint first when possible: lower texture sizes for previews, tile sizes, `--threads`, adaptive sampling, proxy media.
8. **Disk is a resource too.** Estimate (frames x average frame size), confirm free space with margin before starting, and clean scratch/cached frames the user doesn't need. A full disk corrupts the last frames without warning.
9. **Don't cook the machine.** Sustained 100% loads on a laptop cause thermal throttling that erases the gain. Prefer a desktop/workstation for heavy runs (section 5), watch temperatures/throttling when the tools expose them, and leave headroom on portable machines.
10. **Tell the user the budget** in the plan: workers chosen, memory per worker measured, reserve kept, and the safety rules in effect.

## 5. Put heavy work on the right machine

- During inventory, note which machines are strongest, cooler, plugged in and always-on (desktop/workstation, render box) and which are portable (laptop). **Run long or heavy jobs on the strongest suitable machine; keep the portable one for editing, previews and light checks.** Laptops throttle, get hot, drain the battery and sleep. Do this whenever another machine is reachable, even if the user didn't ask, and say so in the plan. If the user names a machine for heavy work, use it.
- Still **benchmark the same few frames on each machine** (see hardware-and-shells.md). The winner depends on the stage: GPU-bound rendering favors the machine with the better discrete GPU; browser renders favor single-thread CPU speed and core count.
- Keep the project layout identical across machines and sync with rsync (or `robocopy`/`scp`). Send only what changed. Pull results back as image sequences or the final file.
- Launch remote jobs detached, write a done-marker and a log, and poll the marker (details in hardware-and-shells.md). Confirm the remote machine won't sleep, and that GPU drivers/tools are the expected versions, with an absolute path to each tool.
- On Windows remote machines, use `.ps1` files copied over and run with `-File`, not quoted one-liners.

## 6. Sanity checks before the full run

- Run 2-3 workers on ~20 frames first; verify utilization, output correctness, frame numbering and no collisions.
- Confirm memory: peak RAM/VRAM at the chosen worker count stays under the budget, with the reserve intact.
- Confirm total throughput scales (2 workers should be near 2x frames/min until a resource saturates). If it doesn't, find the bottleneck before launching everything.
- Estimate the full run from measured frames/min and tell the user the expected time.
- After the run: check the frame count, no gaps or zero-byte files, consistent resolution, then assemble.

## What to report

Machine used and why, worker count, per-worker peak RAM/VRAM and the reserve kept, measured utilization (CPU/GPU) before and after tuning, any watchdog interventions, frames per minute, and total render time.
