# ae_run.ps1 <script.jsx> [--timeout seconds] [--set name=value]...
# The Windows twin of ae_run.sh: the only way to run a script in After Effects on Windows. Errors come back here as text,
# never as a dialog someone has to click.
#   powershell -ExecutionPolicy Bypass -File ae_run.ps1 <script.jsx> [--timeout seconds] [--set name=value]
# Exit codes: 0 finished, 1 the script reported an error (printed), 2 refused or not found, 3 AE isn't open or an earlier
# script is still running, 4 AE didn't finish in time.
# On 3 or 4 AE is most likely showing a dialog or stuck on a render: stop and ask the person, don't wait or retry.
# ae_safe.jsx writes the log, so AE's "Allow Scripts to Write Files and Access Network" preference must be on (Preferences >
# Scripting & Expressions); with it off, every run ends in AE_TIMEOUT with an empty log.

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($args.Count -lt 1) { Write-Output 'usage: ae_run.ps1 <script.jsx> [--timeout seconds] [--set name=value]'; exit 2 }
$jsx = $args[0]; $timeout = 120; $sets = @()
for ($i = 1; $i -lt $args.Count; $i += 2) {
  switch ($args[$i]) {
    '--timeout' { $timeout = [int]$args[$i + 1] }
    '--set'     { $sets += [string]$args[$i + 1] }
    default     { Write-Output "unknown option $($args[$i])"; exit 2 }
  }
}
if (-not (Test-Path -LiteralPath $jsx -PathType Leaf)) { Write-Output "no such script: $jsx"; exit 2 }
$jsx = (Resolve-Path -LiteralPath $jsx).Path
$lines = Get-Content -LiteralPath $jsx -Encoding UTF8

# alert(), confirm() and prompt() always stop AE for a click, whatever else is suppressed: refuse them unless a quiet flag guards them
function Show-Hits($hits) { foreach ($h in $hits) { $t = "$($h.LineNumber):$($h.Line)"; Write-Output $t.Substring(0, [Math]::Min(140, $t.Length)) } }
$bad = @($lines | Select-String -Pattern '(^|[^.A-Za-z_$])(alert|confirm|prompt)\s*\(' |
         Where-Object { $_.Line -notmatch '__AE_QUIET|__MAPS_QUIET|^\s*//' })
if ($bad.Count) { Write-Output 'REFUSED: this script would stop AE on a dialog:'; Show-Hits $bad; exit 2 }
# app.newProject() on unsaved work opens a Save box: use $.global.__AE_NEW_PROJECT() from ae_safe.jsx, or check P.dirty on that line
$raw = @($lines | Select-String -SimpleMatch 'app.newProject' | Where-Object { $_.Line -notmatch 'dirty|^\s*//' })
if ($raw.Count) { Write-Output 'REFUSED: use $.global.__AE_NEW_PROJECT() instead, it can''t open a Save box:'; Show-Hits $raw; exit 2 }

$app = Get-ChildItem -Path "$env:ProgramFiles\Adobe\Adobe After Effects 20*\Support Files\AfterFX.com" -ErrorAction SilentlyContinue |
       Sort-Object FullName | Select-Object -Last 1
if (-not $app) { Write-Output "After Effects isn't installed here"; exit 2 }

$work = Join-Path $env:TEMP ("ae_run." + [IO.Path]::GetRandomFileName()); New-Item -ItemType Directory -Path $work | Out-Null
$log = Join-Path $work 'log.txt'; $boot = Join-Path $work 'boot.jsx'; New-Item -ItemType File -Path $log | Out-Null

# Never ping AE with a script: a second script while one is waiting raises its own warning dialog. A lock says one is still running.
$proc = Get-Process -Name AfterFX -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $proc) { Write-Output "AE_NOT_OPEN: After Effects isn't running. Ask the person to open it."; exit 3 }
$lock = Join-Path $env:TEMP 'ae_run.lock'
if (Test-Path -LiteralPath $lock) {
  $held = (Get-Content -LiteralPath $lock -Raw) -split ' ', 2
  if ($held[0] -eq "$($proc.Id)") {
    Write-Output "AE_BUSY: an earlier script hasn't finished ($($held[1].Trim())). AE may be waiting on a dialog. Nothing was sent. Ask the person to check it."
    exit 3
  }
}
$utf8 = New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText($lock, "$($proc.Id) $jsx", $utf8)

# ExtendScript takes forward slashes
function Js($p) { '"' + ($p -replace '\\', '/') + '"' }
$b = @()
foreach ($s in $sets) { $kv = $s -split '=', 2; $b += "`$.global.$($kv[0]) = $($kv[1]);" }
$b += "`$.global.__AE_TARGET = $(Js $jsx); `$.global.__AE_LOG = $(Js $log); `$.global.__AE_LOCK = $(Js $lock);"
$b += "`$.evalFile(new File($(Js (Join-Path $here 'ae_safe.jsx'))));"
[IO.File]::WriteAllText($boot, ($b -join "`n") + "`n", $utf8)

# -r hands the script to the running AE and returns before it finishes, so the finish is read from the log
Start-Process -FilePath $app.FullName -ArgumentList @('-r', "`"$boot`"") -WindowStyle Hidden | Out-Null
$until = (Get-Date).AddSeconds($timeout); $done = $false
while ((Get-Date) -lt $until) {
  if (Select-String -LiteralPath $log -Pattern '^(FINISHED|ERROR )' -Quiet) { $done = $true; break }
  Start-Sleep -Milliseconds 300
}
Get-Content -LiteralPath $log -Encoding UTF8
if (-not $done) { Write-Output "AE_TIMEOUT: the script didn't finish within $timeout s. AE is probably showing a dialog or stuck on a render. Stop and ask the person."; exit 4 }
if (Select-String -LiteralPath $log -Pattern '^ERROR ' -Quiet) { exit 1 }
exit 0
