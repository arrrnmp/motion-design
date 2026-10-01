# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Aaron Mompié
# This file is part of motion-design (https://github.com/arrrnmp/motion-design).
# Licensed under the GNU Affero General Public License, version 3 or later.

# Inventory a Windows machine for motion-design work: hardware + relevant tools.
# Windows counterpart of inventory.sh. Compatible with Windows PowerShell 5.1 and PowerShell 7+.
# Kept ASCII-only on purpose: 5.1 reads BOM-less scripts in the ANSI code page.
#
# Local:   powershell -NoProfile -ExecutionPolicy Bypass -File inventory.ps1
# Remote:  scp inventory.ps1 host:inventory.ps1
#          ssh host powershell -NoProfile -ExecutionPolicy Bypass -File inventory.ps1
# (Copy-then-run avoids PowerShell's nested-quote mangling over SSH.)

# Native tools write version info to stderr; with 'Stop' that becomes a terminating error.
$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

function Section($name) { Write-Output ""; Write-Output "== $name ==" }

Section "System"
$os  = Get-CimInstance Win32_OperatingSystem
$cs  = Get-CimInstance Win32_ComputerSystem
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
Write-Output ("OS: {0} {1} (build {2}) {3}" -f $os.Caption, $os.Version, $os.BuildNumber, $os.OSArchitecture)
Write-Output ("CPU: {0} ({1} cores / {2} threads)" -f $cpu.Name.Trim(), $cpu.NumberOfCores, $cpu.NumberOfLogicalProcessors)
Write-Output ("RAM: {0} GB" -f [math]::Round($cs.TotalPhysicalMemory / 1GB))

$nvsmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($nvsmi) {
    # Win32_VideoController.AdapterRAM is a 32-bit field capped at 4 GB, so prefer nvidia-smi.
    & nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>$null |
        ForEach-Object { Write-Output "GPU: $_" }
} else {
    Get-CimInstance Win32_VideoController | ForEach-Object {
        Write-Output ("GPU: {0} (driver {1}; reported VRAM {2} GB, capped at 4)" -f $_.Name, $_.DriverVersion, [math]::Round($_.AdapterRAM / 1GB, 1))
    }
}
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
    Write-Output ("Disk {0} {1} GB free of {2} GB" -f $_.DeviceID, [math]::Round($_.FreeSpace / 1GB), [math]::Round($_.Size / 1GB))
}

Section "Tools"
# Returns the first line of a command's output (stdout+stderr), or $null.
function First-Line($exe, [string[]]$argv) {
    try {
        $out = & $exe @argv 2>&1 | ForEach-Object { "$_" } | Where-Object { $_.Trim() -ne "" } | Select-Object -First 1
        return $out
    } catch { return $null }
}

# Look on PATH first, then in common install folders (GUI apps often aren't on PATH).
function Find-Exe($names, $globs) {
    foreach ($n in $names) {
        $c = Get-Command $n -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($c) { return $c.Source }
    }
    foreach ($g in $globs) {
        $hit = Get-ChildItem -Path $g -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1
        if ($hit) { return $hit.FullName }
    }
    return $null
}

$pf   = $env:ProgramFiles
$pf86 = ${env:ProgramFiles(x86)}
$lad  = $env:LOCALAPPDATA

$tools = @(
    @{ n='ffmpeg';      exe=@('ffmpeg');  g=@();  a=@('-hide_banner','-version') },
    @{ n='ffprobe';     exe=@('ffprobe'); g=@();  a=@('-version') },
    @{ n='node';        exe=@('node');    g=@();  a=@('--version') },
    @{ n='npm';         exe=@('npm.cmd','npm'); g=@(); a=@('--version') },
    @{ n='bun';         exe=@('bun');     g=@();  a=@('--version') },
    @{ n='python';      exe=@('py','python','python3'); g=@(); a=@('--version') },
    @{ n='uv';          exe=@('uv');      g=@();  a=@('--version') },
    @{ n='blender';     exe=@('blender'); g=@("$pf\Blender Foundation\Blender*\blender.exe"); a=@('--version') },
    @{ n='manim';       exe=@('manim');   g=@();  a=@('--version') },
    @{ n='inkscape';    exe=@('inkscape'); g=@("$pf\Inkscape\bin\inkscape.exe"); a=@('--version') },
    @{ n='aseprite';    exe=@('aseprite'); g=@("$pf\Aseprite\Aseprite.exe", "$pf86\Steam\steamapps\common\Aseprite\Aseprite.exe"); a=@('--version') },
    @{ n='vtracer';     exe=@('vtracer'); g=@();  a=@('--version') },
    @{ n='potrace';     exe=@('potrace'); g=@();  a=@('--version') },
    @{ n='resvg';       exe=@('resvg');   g=@();  a=@('--version') },
    @{ n='magick';      exe=@('magick');  g=@("$pf\ImageMagick*\magick.exe"); a=@('--version') },
    @{ n='rubberband';  exe=@('rubberband','rubberband-r3'); g=@(); a=@('--version') },
    @{ n='sox';         exe=@('sox');     g=@("$pf86\sox-*\sox.exe"); a=@('--version') },
    @{ n='sclang';      exe=@('sclang');  g=@("$pf\SuperCollider*\sclang.exe"); a=$null },
    @{ n='ghci';        exe=@('ghci');    g=@();  a=@('--version') },
    @{ n='sonic-pi';    exe=@('sonic-pi'); g=@("$pf\Sonic Pi\app\gui\qt\build\Release\sonic-pi.exe", "$pf\Sonic Pi\*.exe"); a=$null },
    @{ n='fluidsynth';  exe=@('fluidsynth'); g=@(); a=@('--version') },
    @{ n='whisper-cpp'; exe=@('whisper-cli','whisper-cpp','whisper'); g=@(); a=$null },
    @{ n='reaper';      exe=@('reaper');  g=@("$pf\REAPER*\reaper.exe"); a=$null },
    @{ n='chrome';      exe=@('chrome');  g=@("$pf\Google\Chrome\Application\chrome.exe", "$pf86\Google\Chrome\Application\chrome.exe", "$lad\Google\Chrome\Application\chrome.exe"); a=$null },
    @{ n='edge';        exe=@('msedge');  g=@("$pf86\Microsoft\Edge\Application\msedge.exe"); a=$null },
    @{ n='ollama';      exe=@('ollama');  g=@("$lad\Programs\Ollama\ollama.exe"); a=@('--version') },
    @{ n='wsl';         exe=@('wsl');     g=@();  a=$null },
    @{ n='git-bash';    exe=@();          g=@("$pf\Git\bin\bash.exe"); a=$null }
)

$pythonExe = $null
foreach ($t in $tools) {
    $path = Find-Exe $t.exe $t.g
    if ($path) {
        if ($t.n -eq 'python') { $pythonExe = $path }
        $info = if ($t.a) { First-Line $path $t.a } else { $path }
        Write-Output ("  [x] {0,-12} {1}" -f $t.n, $info)
    } else {
        Write-Output ("  [ ] {0,-12}" -f $t.n)
    }
}

Section "Python packages"
if ($pythonExe) {
    # Written to a temp file rather than passed with -c: avoids PowerShell quote mangling.
    $py = @'
import importlib.util as u
pkgs = ["torch","diffusers","transformers","faster_whisper","whisper","whisperx","librosa",
        "pyloudnorm","pedalboard","soundfile","PIL","numpy","cv2","playwright","manim",
        "resemblyzer","audiocraft","TTS","kokoro","f5_tts"]
for p in pkgs:
    print("  [%s] %s" % ("x" if u.find_spec(p) else " ", p))
try:
    import torch
    print("  torch cuda:", torch.cuda.is_available(),
          "|", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "")
except Exception:
    pass
'@
    $tmp = Join-Path $env:TEMP "md_inventory_$PID.py"
    Set-Content -Path $tmp -Value $py -Encoding ASCII
    & $pythonExe $tmp 2>&1 | ForEach-Object { Write-Output "$_" }
    Remove-Item $tmp -ErrorAction SilentlyContinue
} else {
    Write-Output "  (no python found)"
}

Section "Node (global + cwd)"
$npm = Find-Exe @('npm.cmd','npm') @()
if ($npm) {
    & $npm ls -g --depth=0 2>$null | Select-String -Pattern 'remotion|motion-canvas|playwright|puppeteer|lottie|strudel' |
        ForEach-Object { Write-Output "  $($_.Line.Trim())" }
}
if (Test-Path package.json) {
    Select-String -Path package.json -Pattern '"(remotion|@remotion/[^"]+|@motion-canvas/[^"]+|three|lottie[^"]*|@strudel/[^"]+|playwright|puppeteer)"' |
        ForEach-Object { Write-Output "  $($_.Line.Trim())" }
}

Section "Agent skills (installed)"
foreach ($d in @("$env:USERPROFILE\.claude\skills", "$env:USERPROFILE\.agents\skills", ".\.claude\skills", ".\.agents\skills")) {
    if (Test-Path $d) { Write-Output ("  {0}: {1}" -f $d, ((Get-ChildItem $d -Name) -join ' ')) }
}
Write-Output "  Missing something relevant? npx skills find <query>   (Remotion: npx skills add remotion-dev/skills)"

Section "Fonts (count)"
$sysFonts  = (Get-ChildItem "$env:WINDIR\Fonts" -ErrorAction SilentlyContinue | Measure-Object).Count
$userFonts = (Get-ChildItem "$lad\Microsoft\Windows\Fonts" -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Output "  system: $sysFonts  user: $userFonts"

Section "Power"
# Long renders die when a machine sleeps; report the AC standby timeout.
$scheme = & powercfg /getactivescheme 2>$null
if ($scheme) { Write-Output "  $scheme" }
Write-Output "  (check sleep settings before long detached jobs: powercfg /query SCHEME_CURRENT SUB_SLEEP)"
