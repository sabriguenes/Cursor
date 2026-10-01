# Ends a CLI process tree on stall (stream file does not grow for -StallSec) or at the cap (-CapSec).
# Exit codes: 0 process exited, 1 bad arguments or self-test failure, 2 no process at start, 3 cap, 4 stall.
param(
    [int]$TargetPid = 0,
    [string]$Stream = "",
    [int]$StallSec = 900,
    [int]$CapSec = 3600,
    [int]$PollSec = 2,
    [switch]$SelfTest,
    [switch]$LiveTest
)

function Get-WatchdogTrigger {
    param([double]$ElapsedSec, [double]$QuietSec, [int]$StallSec, [int]$CapSec)
    if ($ElapsedSec -ge $CapSec) { return "cap" }
    if ($QuietSec -ge $StallSec) { return "stall" }
    return "run"
}

if ($SelfTest) {
    $fails = @()
    if ((Get-WatchdogTrigger -ElapsedSec 0 -QuietSec 0 -StallSec 900 -CapSec 3600) -ne "run") { $fails += "fresh" }
    if ((Get-WatchdogTrigger -ElapsedSec 899 -QuietSec 899 -StallSec 900 -CapSec 3600) -ne "run") { $fails += "just-under" }
    if ((Get-WatchdogTrigger -ElapsedSec 100 -QuietSec 900 -StallSec 900 -CapSec 3600) -ne "stall") { $fails += "stall-900" }
    if ((Get-WatchdogTrigger -ElapsedSec 3600 -QuietSec 0 -StallSec 900 -CapSec 3600) -ne "cap") { $fails += "cap-3600" }
    if ((Get-WatchdogTrigger -ElapsedSec 3600 -QuietSec 900 -StallSec 900 -CapSec 3600) -ne "cap") { $fails += "cap-over-stall" }
    if ($fails.Count -gt 0) { Write-Output ("self-test fail: " + ($fails -join ",")); exit 1 }
    Write-Output "self-test ok stall=900 cap=3600"
    exit 0
}

if ($LiveTest) {
    $liveStream = Join-Path $env:TEMP ("watchdog-live-{0}.txt" -f [guid]::NewGuid())
    Set-Content -Path $liveStream -Value "start" -Encoding ascii
    $sleeper = Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile", "-Command", "Start-Sleep -Seconds 120") -PassThru -WindowStyle Hidden
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $MyInvocation.MyCommand.Path -TargetPid $sleeper.Id -Stream $liveStream -StallSec 8 -CapSec 60 -PollSec 2
    $code = $LASTEXITCODE
    $still = Get-Process -Id $sleeper.Id -ErrorAction SilentlyContinue
    if ($still) { Stop-Process -Id $sleeper.Id -Force -ErrorAction SilentlyContinue }
    Remove-Item -LiteralPath $liveStream -ErrorAction SilentlyContinue
    Write-Output "live-exit=$code still=$(if ($still) { 'yes' } else { 'no' })"
    exit $code
}

if ($TargetPid -eq 0 -or $Stream -eq "") { Write-Output "need -TargetPid and -Stream"; exit 1 }
if (-not (Get-Process -Id $TargetPid -ErrorAction SilentlyContinue)) { Write-Output "no-process"; exit 2 }

$start = Get-Date
$lastSize = -1
$lastChange = Get-Date
while ($true) {
    if (-not (Get-Process -Id $TargetPid -ErrorAction SilentlyContinue)) { Write-Output "exited"; exit 0 }
    $size = 0
    if (Test-Path -LiteralPath $Stream) { $size = (Get-Item -LiteralPath $Stream).Length }
    if ($size -ne $lastSize) { $lastSize = $size; $lastChange = Get-Date }
    $now = Get-Date
    $trigger = Get-WatchdogTrigger -ElapsedSec ($now - $start).TotalSeconds -QuietSec ($now - $lastChange).TotalSeconds -StallSec $StallSec -CapSec $CapSec
    if ($trigger -ne "run") {
        & taskkill.exe /PID $TargetPid /T /F | Out-Null
        Write-Output $trigger
        if ($trigger -eq "cap") { exit 3 }
        exit 4
    }
    Start-Sleep -Seconds $PollSec
}
