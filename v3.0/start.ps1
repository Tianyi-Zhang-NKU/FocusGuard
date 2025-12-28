$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Starting FocusGuard v2.0..." -ForegroundColor Green

# Start Backend
Write-Host "Launching Backend..."
$BackendPath = Join-Path $ScriptDir "backend"
# Check if venv exists to determine activation method, fallback to standard python if needed, 
# but assuming standard venv structure from previous 'ls'
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$BackendPath'; if (Test-Path '.\venv\Scripts\Activate.ps1') { .\venv\Scripts\Activate.ps1 } else { Write-Warning 'Venv not found, trying global python...' }; python app.py"

# Start Frontend
Write-Host "Launching Frontend..."
$FrontendPath = Join-Path $ScriptDir "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$FrontendPath'; npm run dev"

Write-Host "Services are starting in separate windows..." -ForegroundColor Cyan
