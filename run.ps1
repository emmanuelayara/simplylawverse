# Simply Law - Development Server Launcher
# This script properly sets up and runs the Flask development server

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Simply Law - Dev Server" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (!(Test-Path "myenv")) {
    Write-Host "Virtual environment not found. Creating it now..." -ForegroundColor Yellow
    python -m venv myenv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\myenv\Scripts\Activate.ps1"

# Check if packages are installed
Write-Host "Verifying packages..." -ForegroundColor Yellow
python -m pip install -q -r requirements.txt

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "✓ Environment Ready!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Starting Flask development server..." -ForegroundColor Cyan
Write-Host "Open your browser and go to: http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run Flask in debug mode
python -m flask run --debug
