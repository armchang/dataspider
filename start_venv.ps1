param(
    [switch]$Install,
    [switch]$NoShell
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$VenvDirectory = Join-Path $ProjectRoot ".venv"
$VenvPython = Join-Path $VenvDirectory "Scripts\python.exe"
$ActivateScript = Join-Path $VenvDirectory "Scripts\Activate.ps1"
$RequirementsFile = Join-Path $ProjectRoot "requirements.txt"

Set-Location $ProjectRoot

if (-not (Test-Path -LiteralPath $VenvPython)) {
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $Python) {
        throw "Python was not found on PATH. Install Python 3.11 or newer and try again."
    }

    Write-Host "Creating virtual environment in .venv..." -ForegroundColor Cyan
    & $Python.Source -m venv $VenvDirectory
    if ($LASTEXITCODE -ne 0) {
        throw "Python could not create the virtual environment."
    }

    $Install = $true
}

if ($Install) {
    Write-Host "Installing project dependencies..." -ForegroundColor Cyan
    & $VenvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        throw "pip could not be upgraded."
    }

    & $VenvPython -m pip install -r $RequirementsFile
    if ($LASTEXITCODE -ne 0) {
        throw "Project dependencies could not be installed."
    }
}

if ($NoShell) {
    Write-Host "Virtual environment is ready: $VenvDirectory" -ForegroundColor Green
    return
}

Write-Host "Opening an activated project shell..." -ForegroundColor Green
& powershell.exe -NoLogo -NoExit -ExecutionPolicy Bypass -Command `
    "& '$ActivateScript'; Set-Location '$ProjectRoot'; Write-Host 'Dataspider virtual environment activated.' -ForegroundColor Green"
