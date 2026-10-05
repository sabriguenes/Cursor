# One guarded CLI call for the Foreman: Opus through claude.exe, a read-only Codex review through node codex.js,
# or -Cli selftest, which starts a sleeping child so the watchdog can be tested without a CLI.
# The script starts itself again as a hidden child (-Inner) that makes the call, and watches that child's stream:
# no growth for -StallSeconds ends the whole process tree with exit 4, more than -CapSeconds in total with exit 3.
# Exit codes: 0 the child ended on its own (the CLI's code is in logs\exit-<Artifact>.txt), 3 cap, 4 stall, 10 bad arguments or setup.
param(
    [Parameter(Mandatory)][ValidateSet("claude", "codex", "selftest")][string]$Cli,
    [Parameter(Mandatory)][string]$RunDir,
    [string]$Worktree = "",
    [string]$PromptFile = "",
    [string]$Artifact = "selftest",
    [ValidateSet("plan", "acceptEdits")][string]$PermissionMode = "plan",
    [string]$SessionId = "",
    [string]$Resume = "",
    [string]$AllowedTools = "",
    [int]$StallSeconds = 900,
    [int]$CapSeconds = 3600,
    [switch]$Inner
)

$ErrorActionPreference = "Continue"
$PollSeconds = 1
$SchemaTag = "review-schema-instructions"
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
Remove-Item Env:ANTHROPIC_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:ANTHROPIC_AUTH_TOKEN -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue

$RunDir = [IO.Path]::GetFullPath($RunDir)
$logDir = Join-Path $RunDir "logs"
$streamPath = Join-Path $logDir ("stream-{0}.jsonl" -f $Artifact)
$errPath = Join-Path $logDir ("stream-{0}.err" -f $Artifact)
$exitPath = Join-Path $logDir ("exit-{0}.txt" -f $Artifact)
$schemaPath = Join-Path (Join-Path $RunDir "scripts") "review.schema.json"
# Windows PowerShell 5 redirects native output as UTF-16.
$streamEncoding = if ($PSVersionTable.PSVersion.Major -lt 6) { "Unicode" } else { "UTF8" }

function Fail([string]$Message) {
    # The hidden child has no visible console, so its setup failures go to the exit file.
    if ($Inner) { Set-Content -LiteralPath $exitPath -Value "10 $Message" -Encoding ascii }
    Write-Output $Message
    exit 10
}

# Windows command-line quoting: backslashes before a quote are doubled, so a path ending in \ survives.
function Quote([string]$Value) {
    $escaped = [regex]::Replace($Value, '(\\*)"', { param($m) $m.Groups[1].Value * 2 + '\"' })
    '"' + [regex]::Replace($escaped, '(\\+)$', '$1$1') + '"'
}

function Get-StreamSize {
    # Read through a handle: a directory entry can lag behind a file another process still holds open.
    try {
        $fs = [IO.File]::Open($streamPath, "Open", "Read", "ReadWrite, Delete")
        try { return $fs.Length } finally { $fs.Dispose() }
    } catch { return 0 }
}

function Export-Schema {
    $source = Join-Path (Split-Path -Parent $PSScriptRoot) "foreman.md"
    if (-not (Test-Path -LiteralPath $source)) { Fail "foreman.md not found next to scripts\" }
    $lines = [IO.File]::ReadAllLines($source, [Text.UTF8Encoding]::new($false))
    $open = @(for ($i = 0; $i -lt $lines.Count; $i++) { if ($lines[$i] -ceq "<$SchemaTag>") { $i } })
    $close = @(for ($i = 0; $i -lt $lines.Count; $i++) { if ($lines[$i] -ceq "</$SchemaTag>") { $i } })
    if ($open.Count -ne 1 -or $close.Count -ne 1 -or $open[0] -ge $close[0]) { Fail "$SchemaTag block not found exactly once" }
    $inner = @($lines[($open[0] + 1)..($close[0] - 1)])
    $first = 0; $last = $inner.Count - 1
    while ($first -le $last -and -not $inner[$first].Trim()) { $first++ }
    while ($last -ge $first -and -not $inner[$last].Trim()) { $last-- }
    if ($first -gt $last) { Fail "$SchemaTag block is empty" }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $schemaPath) | Out-Null
    $text = ($inner[$first..$last] -join "`n") + "`n"
    [IO.File]::WriteAllText($schemaPath, $text, [Text.UTF8Encoding]::new($false))
}

function Invoke-Claude {
    # The npm shim passes arguments through a batch file and can cut a multi-line prompt, so claude.exe is started directly.
    $shim = Get-Command claude -ErrorAction SilentlyContinue
    if (-not $shim) { Fail "claude not found on PATH" }
    $claude = Join-Path (Split-Path -Parent $shim.Source) "node_modules\@anthropic-ai\claude-code\bin\claude.exe"
    if (-not (Test-Path -LiteralPath $claude)) { Fail "claude.exe not found next to the npm shim" }
    # Windows names the shell tool PowerShell, so every pattern is listed for Bash and PowerShell.
    $denied = "Bash(git push *),PowerShell(git push *),Bash(git push),PowerShell(git push),Bash(git commit *),PowerShell(git commit *),Bash(git commit),PowerShell(git commit)"
    $prompt = Get-Content -Raw -Encoding utf8 -LiteralPath $PromptFile
    $claudeArgs = @("-p", $prompt, "--permission-mode", $PermissionMode, "--output-format", "stream-json",
        "--verbose", "--add-dir", $RunDir, "--disallowedTools", $denied)
    if ($AllowedTools) { $claudeArgs += @("--allowedTools", $AllowedTools) }
    if ($Resume) { $claudeArgs += @("--resume", $Resume) } elseif ($SessionId) { $claudeArgs += @("--session-id", $SessionId) }
    & $claude @claudeArgs 1> $streamPath 2> $errPath
    $code = $LASTEXITCODE
    Set-Content -LiteralPath $exitPath -Value $code -Encoding ascii
    # Plan mode cannot write files, so the answer is taken from the stream.
    $answer = $null
    foreach ($line in (Get-Content -Encoding $streamEncoding -LiteralPath $streamPath -ErrorAction SilentlyContinue)) {
        if ($line -notmatch '"type"\s*:\s*"result"') { continue }
        try { $evt = $line | ConvertFrom-Json } catch { continue }
        if ($evt.type -eq "result" -and $evt.result) { $answer = [string]$evt.result }
    }
    if ($null -ne $answer) {
        [IO.File]::WriteAllText((Join-Path $logDir ("answer-{0}.md" -f $Artifact)), $answer, [Text.UTF8Encoding]::new($false))
    }
    exit $code
}

function Invoke-Codex {
    $shim = Get-Command codex -ErrorAction SilentlyContinue
    $node = Get-Command node -ErrorAction SilentlyContinue
    if (-not $shim -or -not $node) { Fail "codex or node not found on PATH" }
    $codexJs = Join-Path (Split-Path -Parent $shim.Source) "node_modules\@openai\codex\bin\codex.js"
    if (-not (Test-Path -LiteralPath $codexJs)) { Fail "codex.js not found next to the npm shim" }
    $reviewDir = Join-Path $RunDir "reviews"
    New-Item -ItemType Directory -Force -Path $reviewDir | Out-Null
    $outPath = Join-Path $reviewDir ("{0}.json" -f $Artifact)
    $prompt = Get-Content -Raw -Encoding utf8 -LiteralPath $PromptFile
    & $node.Source $codexJs exec --json -s read-only -C $Worktree --output-schema $schemaPath -o $outPath $prompt 1> $streamPath 2> $errPath
    $code = $LASTEXITCODE
    Set-Content -LiteralPath $exitPath -Value $code -Encoding ascii
    # The stream names no model; the session file named by the thread.started thread id does. Nothing is written when either is missing.
    $thread = Select-String -LiteralPath $streamPath -Encoding $streamEncoding -List `
        -Pattern '^\{"type":"thread\.started","thread_id":"([0-9A-Za-z-]+)"' -ErrorAction SilentlyContinue
    if ($thread) {
        $codexDir = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
        $session = Get-ChildItem -LiteralPath (Join-Path $codexDir "sessions") -Recurse -File -ErrorAction SilentlyContinue `
            -Filter ("rollout-*-{0}.jsonl" -f $thread.Matches[0].Groups[1].Value) | Select-Object -First 1
        $model = if ($session) { Select-String -LiteralPath $session.FullName -Encoding utf8 -List -Pattern '"model":"([^"]+)"' }
        if ($model) {
            Set-Content -LiteralPath (Join-Path $logDir ("model-{0}.txt" -f $Artifact)) -Value $model.Matches[0].Groups[1].Value -Encoding ascii
        }
    }
    exit $code
}

function Invoke-SelfTest {
    # A sleeping grandchild proves the whole tree ends; with -PromptFile the child also writes a line every second.
    $sleep = "-NoProfile -Command Start-Sleep -Seconds {0}" -f ($CapSeconds * 10)
    $sleeper = Start-Process -FilePath "powershell.exe" -ArgumentList $sleep -PassThru -WindowStyle Hidden
    if ($PromptFile) {
        while ($true) { Add-Content -LiteralPath $streamPath -Value "tick" -Encoding ascii; Start-Sleep -Seconds 1 }
    }
    $sleeper.WaitForExit()
    exit 0
}

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

if ($Inner) {
    if ($Cli -eq "claude") { Set-Location -LiteralPath $Worktree; Invoke-Claude }
    if ($Cli -eq "codex") { Invoke-Codex }
    Invoke-SelfTest
}

if ($Cli -eq "codex") { Export-Schema }
if ($Cli -ne "selftest") {
    if (-not $Worktree -or -not (Test-Path -LiteralPath $Worktree -PathType Container)) { Fail "-Worktree must be an existing directory" }
    if (-not $PromptFile -or -not (Test-Path -LiteralPath $PromptFile -PathType Leaf)) { Fail "-PromptFile must be an existing file" }
    if ($Artifact -eq "selftest") { Fail "-Artifact is required" }
    $Worktree = [IO.Path]::GetFullPath($Worktree)
    $PromptFile = [IO.Path]::GetFullPath($PromptFile)
}
if ($SessionId -and $Resume) { Fail "pass -SessionId or -Resume, not both" }
if ($StallSeconds -lt 1 -or $CapSeconds -lt 1) { Fail "-StallSeconds and -CapSeconds must be positive" }

$parts = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Quote $PSCommandPath), "-Inner",
    "-Cli", $Cli, "-RunDir", (Quote $RunDir), "-Artifact", (Quote $Artifact),
    "-PermissionMode", $PermissionMode, "-StallSeconds", $StallSeconds, "-CapSeconds", $CapSeconds)
foreach ($pair in @(@("-Worktree", $Worktree), @("-PromptFile", $PromptFile), @("-SessionId", $SessionId),
        @("-Resume", $Resume), @("-AllowedTools", $AllowedTools))) {
    if ($pair[1]) { $parts += @($pair[0], (Quote $pair[1])) }
}

$proc = Start-Process -FilePath "powershell.exe" -ArgumentList ($parts -join " ") -PassThru -WindowStyle Hidden
$null = $proc.Handle
Write-Output "runner-pid=$($proc.Id)"

$start = Get-Date
$lastSize = -1
$lastChange = $start
while (-not $proc.HasExited) {
    $size = Get-StreamSize
    if ($size -ne $lastSize) { $lastSize = $size; $lastChange = Get-Date }
    $now = Get-Date
    $trigger = ""
    if (($now - $start).TotalSeconds -ge $CapSeconds) { $trigger = "cap" }
    elseif (($now - $lastChange).TotalSeconds -ge $StallSeconds) { $trigger = "stall" }
    if ($trigger) {
        # Partial stream, error and review files stay; only the process tree ends.
        & taskkill.exe /PID $proc.Id /T /F | Out-Null
        $killCode = $LASTEXITCODE
        # taskkill exits 128 when the child ended between the poll and the kill; any other failure may leave the tree running.
        $record = if ($killCode -eq 0 -or $killCode -eq 128) { $trigger } else { "$trigger taskkill-failed=$killCode" }
        Set-Content -LiteralPath $exitPath -Value $record -Encoding ascii
        Write-Output "watchdog=$record"
        if ($trigger -eq "cap") { exit 3 }
        exit 4
    }
    Start-Sleep -Seconds $PollSeconds
}
Write-Output "exited child-exit=$($proc.ExitCode)"
exit 0
