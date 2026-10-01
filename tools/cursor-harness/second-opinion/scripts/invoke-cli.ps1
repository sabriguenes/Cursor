# Starts runner-claude.ps1 or runner-codex.ps1 in a child process and guards it with watchdog.ps1.
# Exit code: the watchdog's (0 exited, 2 no process, 3 cap, 4 stall). The runner's own exit code is in logs\exit-<Artifact>.txt.
param(
    [Parameter(Mandatory)][ValidateSet("claude", "codex")][string]$Cli,
    [Parameter(Mandatory)][string]$RunDir,
    [Parameter(Mandatory)][string]$Worktree,
    [Parameter(Mandatory)][string]$PromptFile,
    [Parameter(Mandatory)][string]$Artifact,
    [string]$PermissionMode = "plan",
    [string]$SessionId = "",
    [string]$Resume = "",
    [string]$AllowedTools = "",
    [string]$Schema = "",
    [int]$StallSec = 900,
    [int]$CapSec = 3600,
    [int]$PollSec = 2
)

function Quote([string]$Value) { '"' + $Value.Replace('"', '\"') + '"' }

$runner = Join-Path $PSScriptRoot ("runner-{0}.ps1" -f $Cli)
$watchdog = Join-Path $PSScriptRoot "watchdog.ps1"
$parts = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Quote $runner),
    "-RunDir", (Quote $RunDir), "-Worktree", (Quote $Worktree),
    "-PromptFile", (Quote $PromptFile), "-Artifact", (Quote $Artifact))
if ($Cli -eq "claude") {
    $parts += @("-PermissionMode", (Quote $PermissionMode))
    if ($SessionId) { $parts += @("-SessionId", (Quote $SessionId)) }
    if ($Resume) { $parts += @("-Resume", (Quote $Resume)) }
    if ($AllowedTools) { $parts += @("-AllowedTools", (Quote $AllowedTools)) }
} else {
    if (-not $Schema) { Write-Output "codex needs -Schema"; exit 10 }
    $parts += @("-Schema", (Quote $Schema))
}

$stream = Join-Path (Join-Path $RunDir "logs") ("stream-{0}.jsonl" -f $Artifact)
$proc = Start-Process -FilePath "powershell.exe" -ArgumentList ($parts -join " ") -PassThru -WindowStyle Hidden
Write-Output "runner-pid=$($proc.Id)"
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $watchdog -TargetPid $proc.Id -Stream $stream -StallSec $StallSec -CapSec $CapSec -PollSec $PollSec
$code = $LASTEXITCODE
Write-Output "watchdog-exit=$code"
exit $code
