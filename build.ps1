# Setup pybind11 as git submodule
New-Item -ItemType Directory -Force -Path "external" | Out-Null

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "OmniQuant v2 - Windows Build Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚠️  MANDATORY DISCLAIMER:" -ForegroundColor Yellow
Write-Host "OmniQuant is a research and educational arbitrage detection simulator."
Write-Host "All opportunities shown are theoretical."
Write-Host "No trades are executed. Not financial advice."
Write-Host ""

# Check for Python
Write-Host "Checking Python..." -ForegroundColor Green
try {
    $pythonVersion = python --version
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check for Node.js
Write-Host "Checking Node.js..." -ForegroundColor Green
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found! Please install Node.js 16+" -ForegroundColor Red
    exit 1
}

# Install Python dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Green
pip install -r requirements.txt

# Check for CMake (optional for C++ build)
Write-Host ""
Write-Host "Checking CMake..." -ForegroundColor Green
try {
    $cmakeVersion = cmake --version
    Write-Host "✓ CMake found" -ForegroundColor Green
    $buildCpp = $true
} catch {
    Write-Host "⚠️  CMake not found - skipping C++ build (Python fallback will be used)" -ForegroundColor Yellow
    $buildCpp = $false
}

# Build C++ engine if CMake available
if ($buildCpp) {
    Write-Host ""
    Write-Host "Building C++ engine..." -ForegroundColor Green
    
    if (-not (Test-Path "external/pybind11")) {
        Write-Host "Downloading pybind11..." -ForegroundColor Green
        git clone https://github.com/pybind/pybind11.git external/pybind11
    }
    
    New-Item -ItemType Directory -Force -Path "build" | Out-Null
    Set-Location build
    
    try {
        cmake ..
        cmake --build . --config Release
        Write-Host "✓ C++ engine built successfully!" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  C++ build failed - Python fallback will be used" -ForegroundColor Yellow
    }
    
    Set-Location ..
}

# Setup frontend
Write-Host ""
Write-Host "Setting up frontend..." -ForegroundColor Green
Set-Location frontend
npm install
Set-Location ..

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "✓ Setup Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start OmniQuant:" -ForegroundColor Cyan
Write-Host "  1. Start backend:  python api/main.py" -ForegroundColor White
Write-Host "  2. Start frontend: cd frontend; npm start" -ForegroundColor White
Write-Host ""
Write-Host "Access dashboard at: http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
