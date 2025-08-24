# AI Bootcamp Windows Runner Script

# Set environment variable
$env:PYTHONPATH = "D:\Zdata-20240805\ai-bootcamp-template\src;$env:PYTHONPATH"

# Get command from arguments
$Command = $args[0]
if (-not $Command) { $Command = "help" }

function Show-Help {
    Write-Host "AI Bootcamp Windows Runner" -ForegroundColor Green
    Write-Host "Usage: .\run.ps1 [command]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Available commands:" -ForegroundColor Cyan
    Write-Host "  api     - Start FastAPI server (port 8000)" -ForegroundColor White
    Write-Host "  setup   - Install dependencies" -ForegroundColor White
    Write-Host "  test    - Run tests" -ForegroundColor White
    Write-Host "  lint    - Code linting" -ForegroundColor White
    Write-Host "  fmt     - Code formatting" -ForegroundColor White
    Write-Host "  help    - Show this help" -ForegroundColor White
}

function Start-API {
    Write-Host "Starting FastAPI server..." -ForegroundColor Green
    Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "Health Check: http://localhost:8000/health" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
    python -m uvicorn ai_bootcamp.app.api:app --host 0.0.0.0 --port 8000 --reload
}

function Install-Dependencies {
    Write-Host "Installing dependencies..." -ForegroundColor Green
    python -m pip install fastapi uvicorn python-dotenv pydantic hydra-core mlflow
    python -m pip install ruff black isort pytest pytest-cov mypy pre-commit jupytext ipykernel
}

function Run-Tests {
    Write-Host "Running tests..." -ForegroundColor Green
    python -m pytest
}

function Run-Lint {
    Write-Host "Running code linting..." -ForegroundColor Green
    python -m ruff check .
    python -m mypy src
}

function Run-Format {
    Write-Host "Formatting code..." -ForegroundColor Green
    python -m black .
    python -m isort .
}

# Execute command
switch ($Command.ToLower()) {
    "api" { Start-API }
    "setup" { Install-Dependencies }
    "test" { Run-Tests }
    "lint" { Run-Lint }
    "fmt" { Run-Format }
    "help" { Show-Help }
    default { 
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Help
    }
} 