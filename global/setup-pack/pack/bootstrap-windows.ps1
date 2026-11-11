# Claude setup pack: first step on Windows. Checks winget, then every tool the pack needs, and installs what's
# missing. Windows PowerShell 5.1 or PowerShell 7; no Python needed: run it before sync.py.
#
#   powershell -ExecutionPolicy Bypass -File bootstrap-windows.ps1            # check only: lists what is missing
#   powershell -ExecutionPolicy Bypass -File bootstrap-windows.ps1 -Install   # also install the missing tools with winget
#
# Exit codes: 0 = everything ready, 1 = tools missing (run with -Install), 2 = winget missing (only the user can add it).
param([switch]$Install)

function Say($t) { Write-Output $t }
function Ok($n, $w) { Write-Output ("  [ok] {0,-34} {1}" -f $n, $w) }
function No($n, $w) { Write-Output ("  [--] {0,-34} {1}" -f $n, $w) }
function Refresh-Path {   # pick up PATH changes from installers without opening a new terminal
  $m = [Environment]::GetEnvironmentVariable("Path", "Machine"); $u = [Environment]::GetEnvironmentVariable("Path", "User")
  $env:Path = "$m;$u"
}
function Has($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

Say ("Claude setup pack: Windows bootstrap ({0}, {1})" -f [Environment]::OSVersion.VersionString, $env:PROCESSOR_ARCHITECTURE)
Say ""
Refresh-Path

# ---------------------------------------------------------------- 1. winget (everything else comes from it)
if (-not (Has "winget")) {
  Say "WINGET IS NOT INSTALLED. Only the user can add it."
  Say ""
  Say "Ask the user to do this:"
  Say "  1. Open the Microsoft Store, search for 'App Installer' (by Microsoft) and click Get or Update."
  Say "     (Or download it from https://aka.ms/getwinget and open the file.)"
  Say "  2. Close and reopen PowerShell, then say 'done' and run this script again."
  exit 2
}
Ok "winget" ((winget --version) -join " ")

# ---------------------------------------------------------------- 2. the tools
function PyOk {
  if (Has "py") { & py -3.12 -c "import sys" 2>$null; if ($LASTEXITCODE -eq 0) { return $true } }
  if (Has "python") { $v = & python -c "import sys; print(sys.version_info >= (3, 10))" 2>$null; if ($v -eq "True") { return $true } }
  return $false
}
function FfmpegFullOk {
  if (-not (Has "ffmpeg") -or -not (Has "ffprobe")) { return $false }
  $f = (& ffmpeg -hide_banner -filters 2>$null) -join "`n"
  return ($f -match "drawtext") -and ($f -match "subtitles")
}
function ChromeOk {
  foreach ($p in @("$env:ProgramFiles\Google\Chrome\Application\chrome.exe", "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
                   "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe")) { if (Test-Path $p) { return $true } }
  return $false
}
$tools = @(
  @{ n = "git (+ Git Bash)";            t = { Has "git" };                         id = "Git.Git";            why = "video-use clone; Claude Code's Bash tool" },
  @{ n = "Python 3.12";                 t = { PyOk };                              id = "Python.Python.3.12"; why = "sync.py, every skill script, venvs" },
  @{ n = "node + npx";                  t = { (Has "node") -and (Has "npx") };    id = "OpenJS.NodeJS.LTS";  why = "hyperframes, markroom, explainers" },
  @{ n = "uv + uvx";                    t = { (Has "uv") -and (Has "uvx") };      id = "astral-sh.uv";       why = "venvs (cut-out, video-use), the Fetch MCP" },
  @{ n = "ffmpeg full build";           t = { FfmpegFullOk };                      id = "Gyan.FFmpeg";        why = "renders, drawtext + subtitles, transcription audio" },
  @{ n = "yt-dlp";                      t = { Has "yt-dlp" };                      id = "yt-dlp.yt-dlp";      why = "watch skill: downloading videos"; skipDeps = $true },  # its package pulls a second FFmpeg; the full build above serves it
  @{ n = "deno";                        t = { Has "deno" };                        id = "DenoLand.Deno";      why = "yt-dlp's JavaScript runtime for YouTube" },
  @{ n = "Google Chrome";               t = { ChromeOk };                          id = "Google.Chrome";      why = "headless stills, logo PNGs" }
)
Say ""
Say "TOOLS"
$missing = @()
foreach ($x in $tools) {
  if (& $x.t) { Ok $x.n $x.why } else { No $x.n ("winget install --id {0} -e{2}   ({1})" -f $x.id, $x.why, $(if ($x.skipDeps) { " --skip-dependencies" } else { "" })); $missing += $x }
}

# Bonjour's name-lookup add-in (mdnsNSP.dll) with Windows' LSA protection on: a Bonjour older than 3.1.0.1 (3.0.0.10,
# from 2011, still comes with some installers) is blocked inside lsass, and Windows shows a "Local Security Authority"
# pop-up at start-up and during some downloads. Updating Bonjour to 3.1.0.1 stopped it on a Windows 11 PC (no lsass
# blocks over three start-ups; other protected services still skip the add-in, silently and harmlessly). Setup's own
# downloads avoid the pop-up (git uses OpenSSL here). A note, never a blocker: Claude offers the update and runs it on
# the user's yes. $Dlls: the add-in's copies to read the version from (Bonjour's usual folders).
function BonjourNote([string[]]$Dlls = @("$env:ProgramFiles\Bonjour\mdnsNSP.dll", "${env:ProgramFiles(x86)}\Bonjour\mdnsNSP.dll")) {
  $lsa = Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -Name RunAsPPL -ErrorAction SilentlyContinue
  if (-not $lsa -or ($lsa.RunAsPPL -ne 1 -and $lsa.RunAsPPL -ne 2)) { return }
  $cat = (& netsh winsock show catalog 2>$null) -join "`n"
  if ($cat -notmatch "mdnsNSP") { return }
  $vers = @($Dlls | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | ForEach-Object {
    $v = (Get-Item -LiteralPath $_).VersionInfo; [version]::new($v.FileMajorPart, $v.FileMinorPart, $v.FileBuildPart, $v.FilePrivatePart) })
  $old = @($vers | Where-Object { $_ -lt [version]"3.1.0.1" } | Sort-Object)
  if ($vers.Count -and -not $old.Count) { return }          # 3.1.0.1 or newer everywhere: no pop-up to stop
  $which = if ($old.Count) { "Bonjour $($old[0])" } else { "A Bonjour of unknown version" }
  Say ""
  Say "BONJOUR NOTE (nothing stops; offer the user this update):"
  Say "  $which is installed and Windows' LSA protection is on, so Windows blocks Bonjour's name-lookup add-in and"
  Say "  shows a 'Local Security Authority' pop-up at start-up and during some downloads. Updating Bonjour to 3.1.0.1 stops"
  Say "  it. On the user's yes, run this (Windows asks for administrator rights; the user clicks Yes):"
  Say "    winget upgrade --id Apple.Bonjour -e --accept-source-agreements --accept-package-agreements"
  Say "  (if winget finds no installed package to upgrade, use  winget install --id Apple.Bonjour -e  instead)."
  Say "  If the pop-up still comes after a restart, the user can run these two lines in PowerShell opened as administrator;"
  Say "  they remove only Bonjour's name-lookup add-in, and the Bonjour service keeps running:"
  Say '    regsvr32 /u "C:\Program Files\Bonjour\mdnsNSP.dll"'
  Say '    C:\Windows\SysWOW64\regsvr32.exe /u "C:\Program Files (x86)\Bonjour\mdnsNSP.dll"'
  Say "  Or uninstall Bonjour if nothing on the computer needs it. Keep LSA protection on."
}
BonjourNote

if ($missing.Count -eq 0) {
  Say ""; Say "READY: winget and every tool are installed. Next: ask which languages to transcribe, then py -3.12 sync.py install (SETUP.md steps 3-4)"
  exit 0
}
Say ""
if (-not $Install) {
  Say ("MISSING: " + (($missing | ForEach-Object { $_.id }) -join " "))
  Say "Run  powershell -ExecutionPolicy Bypass -File bootstrap-windows.ps1 -Install  to install them with winget (a few"
  Say "minutes; Windows may show a permission prompt for some of them, which the user clicks Yes on)."
  exit 1
}

# ---------------------------------------------------------------- 3. install
foreach ($x in $missing) {
  Say ("Installing {0} ({1})" -f $x.n, $x.id)
  $extra = @(); if ($x.skipDeps) { $extra = @("--skip-dependencies") }
  winget install --id $x.id -e --silent --accept-source-agreements --accept-package-agreements @extra
  if ($LASTEXITCODE -ne 0) { Say ("  winget reported an error for {0}; the user may need to run the same command in their own PowerShell." -f $x.id) }
}
Refresh-Path
Say ""
Say "Re-checking... (if something still shows as missing, close and reopen PowerShell once so PATH updates, then re-run)"
& powershell -NoProfile -ExecutionPolicy Bypass -File $PSCommandPath
exit $LASTEXITCODE
