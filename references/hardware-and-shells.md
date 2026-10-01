# Hardware, Rendering and Shells

## Using the hardware well

See `parallelization.md` for measuring utilization, splitting work into worker processes, and choosing which machine runs heavy jobs. The notes below cover the multi-machine and remote-job mechanics.

- **Benchmark before assuming.** Render the same few frames on each machine and time them; the "fast" machine often isn't for this workload (browser renders are CPU/single-thread bound; Blender Cycles and models are GPU bound).
- **Parallelize**: run variants (languages, aspect ratios) on different machines, or split frame ranges and concatenate. Keep file layout identical across machines so the same build script runs everywhere; sync with rsync.
- **Keep GPUs busy** with generation or 3D while CPUs handle browser/motion renders and encoding.
- **Watch GPU memory spilling** into system memory (on Windows/NVIDIA, "shared GPU memory" fallback; on unified-memory Macs, swap pressure). It doesn't crash — it just gets silently many times slower. Monitor VRAM (`nvidia-smi`, Activity Monitor / `vm_stat`) and reduce batch size, resolution or model size if it spills.
- **Long remote jobs run detached** so they survive the user's laptop sleeping. Write a done-marker file (or exit-code file) at the end, and poll for that rather than keeping a live SSH session.
  - macOS/Linux: `tmux new -d -s render '...'`, or `nohup ... > log 2>&1 &`.
  - Windows: processes started from an OpenSSH session (including `Start-Process` and `Start-Job`) are usually killed when the session closes. Use a scheduled task instead — `Register-ScheduledTask` with a one-off trigger, then `Start-ScheduledTask` — or launch through `Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine='powershell -NoProfile -File C:\jobs\render.ps1'}`, which runs outside the session. Redirect output to a log file inside the script, since there's no console.
  - Make sure the remote machine itself won't sleep mid-job (`powercfg`, `pmset`, `systemd-inhibit`).
- **Log watching**: logs often contain ANSI color codes, so a grep for `"Done"` can miss `\x1b[32mDone`. Strip codes (`sed 's/\x1b\[[0-9;]*m//g'`), disable color (`NO_COLOR=1`, `--no-color`), or better, check marker files and exit codes.

- **Remote Blender stills**: `assets/blender/remote.sh <scene> [samples] [res%]` copies `blender/<scene>.py`, the shared
  `common.py`, fonts and any `assets/blender/<scene>/*.png` textures to a Windows GPU box (`GPU_HOST=user@host`), runs
  it headless via `run.ps1` (OptiX device selected in `common.setup_render`), and pulls the PNG back. Preview at
  32-64 spp and 50%, final at 256-512 spp: most library plates rendered in 4-20 s on an RTX 5070 Ti.

## Shells bite on every platform

Use small script files (`.sh`, `.py`, `.ps1`) instead of fragile one-liners, quote and guard variables, and check outputs instead of assuming success.

**PowerShell** (assume it on Windows; don't assume Git Bash or WSL)
- Mangles nested quotes when passing arguments to native programs (especially over SSH) — put the command in a `.ps1` file, `scp` it over, run it with `powershell -NoProfile -ExecutionPolicy Bypass -File x.ps1`.
- Target Windows PowerShell 5.1 unless you've confirmed `pwsh` (7+) is installed: no `?:`, `??`, `&&`/`||` pipeline chains or `-Parallel`. Keep `.ps1` files ASCII (5.1 reads BOM-less files in the ANSI code page, so non-ASCII text gets garbled) or save them as UTF-8 *with* BOM.
- The SSH default shell on Windows is usually `cmd.exe`, so a bare `ssh host 'Get-Process'` fails — prefix with `powershell -NoProfile -Command` or, better, use a script file.
- Paths: use `Join-Path` and quote everything; `Program Files` has a space, and `$env:ProgramFiles(x86)` must be written `${env:ProgramFiles(x86)}`.
- Uses localized names for system things (group names, folder names, "Administrators" etc. differ by OS language) — don't hard-code them.
- Treats native stderr output as errors in some modes (`$ErrorActionPreference = 'Stop'` + stderr = spurious failure) — check `$LASTEXITCODE` instead.

**zsh** (macOS default)
- Globs that match nothing abort the command (`no matches found`) — use `setopt null_glob` in scripts, quote patterns, or use `find`.
- `$var:x` is parsed as a history modifier (`$host:8080` → broken) — write `${var}:x`.
- Unset variables in paths expand to empty, so `rm -rf "$DIR/"*` becomes `rm -rf /*`-style disasters — use `set -u` / `${DIR:?}` and double-check before any delete.

**Everywhere**
- Check exit codes and verify outputs exist and are non-empty (and have the right duration/size) after every step.
- Prefer absolute paths in build scripts.
