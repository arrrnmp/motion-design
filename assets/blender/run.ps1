param([string]$Name, [int]$Samples = 256, [int]$Pct = 100)
# Runs one Blender still headless on this GPU box. ASCII only (PowerShell 5.1 safe).
$dir = Join-Path $env:USERPROFILE 'mds'
$bl = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$log = Join-Path $dir ($Name + '.log')
$sw = [Diagnostics.Stopwatch]::StartNew()
& $bl -b --factory-startup -P (Join-Path $dir ($Name + '.py')) -- $dir $Samples $Pct *> $log
$code = $LASTEXITCODE
Select-String -Path $log -Pattern 'Error|Traceback|DEVICES|DONE|line [0-9]+' | ForEach-Object { $_.Line }
Write-Output ('exit=' + $code + ' seconds=' + [int]$sw.Elapsed.TotalSeconds)
