# Runs one Claude Code CLI call (Opus) inside -Worktree.
# Writes logs\stream-<Artifact>.jsonl, logs\stream-<Artifact>.err, logs\exit-<Artifact>.txt and logs\answer-<Artifact>.md under -RunDir.
# git push and git commit are always denied: the orchestrator owns every commit.
param(
    [Parameter(Mandatory)][string]$RunDir,
    [Parameter(Mandatory)][string]$Worktree,
    [Parameter(Mandatory)][string]$PromptFile,
    [Parameter(Mandatory)][string]$Artifact,
    [ValidateSet("plan", "acceptEdits", "dontAsk")][string]$PermissionMode = "plan",
    [string]$SessionId = "",
    [string]$Resume = "",
    [string]$AllowedTools = ""
)

$ErrorActionPreference = "Continue"
Set-Location -LiteralPath $Worktree
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
Remove-Item Env:ANTHROPIC_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:ANTHROPIC_AUTH_TOKEN -ErrorAction SilentlyContinue

# The npm shim passes arguments through a batch file and can cut a multi-line prompt, so claude.exe is started directly.
$shim = Get-Command claude -ErrorAction SilentlyContinue
if (-not $shim) { Write-Output "claude not found on PATH"; exit 10 }
$claude = Join-Path (Split-Path -Parent $shim.Source) "node_modules\@anthropic-ai\claude-code\bin\claude.exe"
if (-not (Test-Path -LiteralPath $claude)) { Write-Output "claude.exe not found next to the npm shim"; exit 10 }

$logDir = Join-Path $RunDir "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$streamPath = Join-Path $logDir ("stream-{0}.jsonl" -f $Artifact)
$errPath = Join-Path $logDir ("stream-{0}.err" -f $Artifact)
$exitPath = Join-Path $logDir ("exit-{0}.txt" -f $Artifact)
$prompt = Get-Content -Raw -Encoding utf8 -LiteralPath $PromptFile

# Windows names the shell tool PowerShell, so every pattern is listed for Bash and PowerShell.
$denied = "Bash(git push *),PowerShell(git push *),Bash(git push),PowerShell(git push),Bash(git commit *),PowerShell(git commit *),Bash(git commit),PowerShell(git commit)"

$claudeArgs = @(
    "-p", $prompt,
    "--permission-mode", $PermissionMode,
    "--output-format", "stream-json",
    "--verbose",
    "--add-dir", $RunDir,
    "--disallowedTools", $denied
)
if ($AllowedTools) { $claudeArgs += @("--allowedTools", $AllowedTools) }
if ($Resume) { $claudeArgs += @("--resume", $Resume) }
elseif ($SessionId) { $claudeArgs += @("--session-id", $SessionId) }

& $claude @claudeArgs 1> $streamPath 2> $errPath
$code = $LASTEXITCODE
Set-Content -LiteralPath $exitPath -Value $code -Encoding ascii

# Plan mode cannot write files, so the final answer text is saved as logs\answer-<Artifact>.md.
$answer = $null
foreach ($line in (Get-Content -LiteralPath $streamPath -ErrorAction SilentlyContinue)) {
    if ($line -notmatch '"type"\s*:\s*"result"') { continue }
    try { $evt = $line | ConvertFrom-Json } catch { continue }
    if ($evt.type -eq "result" -and $evt.result) { $answer = [string]$evt.result }
}
if ($null -ne $answer) {
    [IO.File]::WriteAllText((Join-Path $logDir ("answer-{0}.md" -f $Artifact)), $answer, [Text.UTF8Encoding]::new($false))
}
exit $code
