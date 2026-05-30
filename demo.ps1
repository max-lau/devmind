# DevMind Live Demo
# Hits every endpoint and shows the system working end to end.
# Usage: .\demo.ps1
#        .\demo.ps1 -BaseUrl https://devmind-production-c756.up.railway.app -ApiKey your-key

param(
    [string]$BaseUrl = "http://localhost:8000",
    [string]$ApiKey  = "dev-local-key"
)

$Headers = @{"X-API-Key" = $ApiKey; "Content-Type" = "application/json"}

function Show-Section($title) {
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "  $title" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
}

function Call-Endpoint($label, $uri, $body) {
    Write-Host ""
    Write-Host ">> $label" -ForegroundColor Yellow
    try {
        $result = Invoke-RestMethod -Uri "$BaseUrl$uri" -Method POST -Headers $Headers -Body $body
        $result | ConvertTo-Json -Depth 4
    } catch {
        Write-Host "ERROR: $_" -ForegroundColor Red
    }
}

# ── Health check ──────────────────────────────────────────
Show-Section "0. Health Check"
Write-Host ""
Write-Host ">> GET /health" -ForegroundColor Yellow
Invoke-RestMethod -Uri "$BaseUrl/health" -Headers $Headers | ConvertTo-Json

# ── Code Review ───────────────────────────────────────────
Show-Section "1. Code Review"
$body = @{code = "def divide(a, b):`n    return a / b"} | ConvertTo-Json
Call-Endpoint "POST /review/code" "/review/code" $body

# ── Bug Analysis ──────────────────────────────────────────
Show-Section "2. Bug Analysis"
$body = @{title = "Login crashes when email is empty"; description = "Users see a 500 error when submitting the login form with a blank email field."} | ConvertTo-Json
Call-Endpoint "POST /bugs/analyze" "/bugs/analyze" $body

# ── Agile Stand-up ────────────────────────────────────────
Show-Section "3. Agile — Daily Stand-up"
$body = @{tasks = @("DONE: fixed login bug", "IN PROGRESS: building dashboard", "BLOCKED: waiting for API keys")} | ConvertTo-Json
Call-Endpoint "POST /agile/standup" "/agile/standup" $body

# ── Sprint Planning ───────────────────────────────────────
Show-Section "4. Agile — Sprint Planning"
$body = @{backlog = @("Add user authentication", "Build dashboard UI", "Fix payment bug", "Write API docs", "Add email notifications", "Deploy to staging")} | ConvertTo-Json
Call-Endpoint "POST /agile/sprint-plan" "/agile/sprint-plan" $body

# ── Retrospective ─────────────────────────────────────────
Show-Section "5. Agile — Retrospective"
$body = @{observations = @("Shipped login feature on time", "Daily standups were too long", "No staging environment caused prod bugs", "Good team communication")} | ConvertTo-Json
Call-Endpoint "POST /agile/retro" "/agile/retro" $body

# ── Eval Harness ──────────────────────────────────────────
Show-Section "6. Eval Harness — Quality Gate"
Write-Host ""
python evals/run_evals.py --url $BaseUrl --key $ApiKey

# ── Summary ───────────────────────────────────────────────
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "  DevMind demo complete." -ForegroundColor Green
Write-Host "  Live API: https://devmind-production-c756.up.railway.app" -ForegroundColor Green
Write-Host "  Repo:     https://github.com/max-lau/devmind" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
