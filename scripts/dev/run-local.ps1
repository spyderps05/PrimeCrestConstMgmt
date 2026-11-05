<#
.SYNOPSIS
  Start a local PrimeCrest dev stack on non-default ports (backend :8810, frontend :5810).

.DESCRIPTION
  - Ensures a throwaway PostgreSQL 16 container (primecrest-qa-pg on host port 55432) is running.
  - Starts the FastAPI backend (uvicorn app.main:create_app --factory) on 127.0.0.1:8810.
    Tables are created by the backend on first boot (create_all + alembic stamp); demo
    accounts/projects are seeded on first boot when SEED_DEMO=true.
  - Starts the Vite dev server on 127.0.0.1:5810 with its /api proxy pointed at :8810
    (VITE_API_TARGET).
  Logs go to scripts/dev/.local/logs/ (gitignored). Stop with: .\scripts\dev\run-local.ps1 -Stop

  Demo login: demo@openconstructionerp.com / DemoPass1234!  (set via DEMO_USER_PASSWORD)

.PARAMETER Python
  Python interpreter with backend deps installed. Default: H:/PrimeCrestConstMgmt/backend/.venv/Scripts/python.exe
#>
param(
  [int]$BackendPort = 8810,
  [int]$FrontendPort = 5810,
  [int]$PgPort = 55432,
  [string]$PgContainer = 'primecrest-qa-pg',
  [string]$Python = 'H:/PrimeCrestConstMgmt/backend/.venv/Scripts/python.exe',
  [switch]$NoFrontend,
  [switch]$Stop
)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$LogDir = Join-Path $PSScriptRoot '.local/logs'
$PidFile = Join-Path $LogDir 'pids.txt'
New-Item -ItemType Directory -Force $LogDir | Out-Null

if ($Stop) {
  if (Test-Path $PidFile) {
    foreach ($p in Get-Content $PidFile) {
      try { & taskkill /PID $p /T /F | Out-Null } catch {}
    }
    Remove-Item $PidFile -Force
  }
  Write-Host "Stopped dev servers (postgres container '$PgContainer' left running)."
  return
}

# --- PostgreSQL ---------------------------------------------------------------
$state = (& docker ps -a --filter "name=^$PgContainer$" --format '{{.State}}') 2>$null
if (-not $state) {
  & docker run -d --name $PgContainer -e POSTGRES_USER=primecrest -e POSTGRES_PASSWORD=primecrest `
    -e POSTGRES_DB=primecrest -p "${PgPort}:5432" postgres:16 | Out-Null
} elseif ($state -ne 'running') {
  & docker start $PgContainer | Out-Null
}
for ($i = 0; $i -lt 30; $i++) {
  & docker exec $PgContainer pg_isready -U primecrest 2>$null | Out-Null
  if ($LASTEXITCODE -eq 0) { break }
  Start-Sleep -Seconds 1
}

# --- Backend ------------------------------------------------------------------
$env:DATABASE_URL = "postgresql+asyncpg://primecrest:primecrest@127.0.0.1:$PgPort/primecrest"
$env:DATABASE_SYNC_URL = "postgresql://primecrest:primecrest@127.0.0.1:$PgPort/primecrest"
$env:SEED_DEMO = 'true'
$env:DEMO_USER_PASSWORD = 'DemoPass1234!'
$env:DEMO_ESTIMATOR_PASSWORD = 'DemoPass1234!'
$env:DEMO_MANAGER_PASSWORD = 'DemoPass1234!'
$env:OE_DATA_DIR = Join-Path $PSScriptRoot '.local/data'
# Keep demo/partner-pack markers per stack. Without this the backend reads ~/.openestimate,
# and a marker left there by any earlier install makes a FRESH database skip demo projects.
$env:OE_CLI_DATA_DIR = $env:OE_DATA_DIR
$env:PYTHONPATH = '.'
$env:PYTHONIOENCODING = 'utf-8'
$env:ALLOWED_ORIGINS = "http://127.0.0.1:$FrontendPort,http://localhost:$FrontendPort"

$be = Start-Process -FilePath $Python -WorkingDirectory (Join-Path $Root 'backend') -PassThru -WindowStyle Hidden `
  -ArgumentList @('-m', 'uvicorn', 'app.main:create_app', '--factory', '--host', '127.0.0.1', '--port', "$BackendPort") `
  -RedirectStandardOutput (Join-Path $LogDir 'backend.out.log') -RedirectStandardError (Join-Path $LogDir 'backend.err.log')
Set-Content $PidFile $be.Id

# --- Frontend -----------------------------------------------------------------
if (-not $NoFrontend) {
  $env:VITE_API_TARGET = "http://127.0.0.1:$BackendPort"
  $fe = Start-Process -FilePath 'cmd.exe' -WorkingDirectory (Join-Path $Root 'frontend') -PassThru -WindowStyle Hidden `
    -ArgumentList @('/c', 'npx', 'vite', '--port', "$FrontendPort", '--strictPort', '--host', '127.0.0.1') `
    -RedirectStandardOutput (Join-Path $LogDir 'frontend.out.log') -RedirectStandardError (Join-Path $LogDir 'frontend.err.log')
  Add-Content $PidFile $fe.Id
}

Write-Host "Waiting for backend on :$BackendPort (first boot creates schema + seeds demo data; can take minutes)..."
for ($i = 0; $i -lt 600; $i++) {
  try { Invoke-WebRequest "http://127.0.0.1:$BackendPort/api/health" -UseBasicParsing -TimeoutSec 3 | Out-Null; break } catch { Start-Sleep -Seconds 2 }
}
Write-Host "Backend : http://127.0.0.1:$BackendPort  (docs: /api/docs)"
if (-not $NoFrontend) { Write-Host "Frontend: http://127.0.0.1:$FrontendPort" }
Write-Host "Login   : demo@openconstructionerp.com / DemoPass1234!"
Write-Host "Logs    : $LogDir   Stop: .\scripts\dev\run-local.ps1 -Stop"
