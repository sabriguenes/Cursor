# Runs one read-only Codex CLI review with -Worktree as working root.
# Writes reviews\<Artifact>.json (schema-validated answer) and logs\stream-<Artifact>.jsonl, .err, exit-<Artifact>.txt under -RunDir.
param(
    [Parameter(Mandatory)][string]$RunDir,
    [Parameter(Mandatory)][string]$Worktree,
    [Parameter(Mandatory)][string]$PromptFile,
    [Parameter(Mandatory)][string]$Artifact,
    [Parameter(Mandatory)][string]$Schema
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue

$shim = Get-Command codex -ErrorAction SilentlyContinue
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $shim -or -not $node) { Write-Output "codex or node not found on PATH"; exit 10 }
$codexJs = Join-Path (Split-Path -Parent $shim.Source) "node_modules\@openai\codex\bin\codex.js"
if (-not (Test-Path -LiteralPath $codexJs)) { Write-Output "codex.js not found next to the npm shim"; exit 10 }

$logDir = Join-Path $RunDir "logs"
$reviewDir = Join-Path $RunDir "reviews"
New-Item -ItemType Directory -Force -Path $logDir, $reviewDir | Out-Null
$streamPath = Join-Path $logDir ("stream-{0}.jsonl" -f $Artifact)
$errPath = Join-Path $logDir ("stream-{0}.err" -f $Artifact)
$exitPath = Join-Path $logDir ("exit-{0}.txt" -f $Artifact)
$outPath = Join-Path $reviewDir ("{0}.json" -f $Artifact)
$prompt = Get-Content -Raw -Encoding utf8 -LiteralPath $PromptFile

& $node.Source $codexJs exec --json -s read-only -C $Worktree --output-schema $Schema -o $outPath $prompt 1> $streamPath 2> $errPath
$code = $LASTEXITCODE
Set-Content -LiteralPath $exitPath -Value $code -Encoding ascii
exit $code
