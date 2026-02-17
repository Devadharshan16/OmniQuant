#!/usr/bin/env pwsh
# Test deployed OmniQuant API

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiUrl
)

Write-Host "🧪 Testing OmniQuant API: $ApiUrl" -ForegroundColor Cyan
Write-Host "=" * 60

# Test 1: Health Check
Write-Host "`n1️⃣  Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$ApiUrl/health" -Method Get
    Write-Host "   ✅ Status: $($health.status)" -ForegroundColor Green
    Write-Host "   ✅ Timestamp: $($health.timestamp)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Root Endpoint
Write-Host "`n2️⃣  API Root..." -ForegroundColor Yellow
try {
    $root = Invoke-RestMethod -Uri "$ApiUrl/" -Method Get
    Write-Host "   ✅ Name: $($root.name)" -ForegroundColor Green
    Write-Host "   ✅ Version: $($root.version)" -ForegroundColor Green
    Write-Host "   ✅ Status: $($root.status)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Root endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Metrics
Write-Host "`n3️⃣  Metrics Endpoint..." -ForegroundColor Yellow
try {
    $metrics = Invoke-RestMethod -Uri "$ApiUrl/metrics" -Method Get
    Write-Host "   ✅ Success: $($metrics.success)" -ForegroundColor Green
    if ($metrics.total_scans) {
        Write-Host "   ✅ Total Scans: $($metrics.total_scans)" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Metrics failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Quick Scan
Write-Host "`n4️⃣  Quick Scan (Simulated Data)..." -ForegroundColor Yellow
try {
    $scan = Invoke-RestMethod -Uri "$ApiUrl/quick_scan?use_real_data=false" -Method Post -ContentType "application/json"
    Write-Host "   ✅ Success: $($scan.success)" -ForegroundColor Green
    Write-Host "   ✅ Opportunities Found: $($scan.opportunities_found)" -ForegroundColor Green
    Write-Host "   ✅ Data Source: $($scan.data_source)" -ForegroundColor Green
    Write-Host "   ✅ Detection Time: $($scan.detection_time_ms) ms" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Quick scan failed: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "   (This is okay if backend is still warming up)" -ForegroundColor Gray
}

Write-Host "`n" + "=" * 60
Write-Host "✅ API Tests Complete!" -ForegroundColor Green
Write-Host "`n📊 API is accessible at: $ApiUrl" -ForegroundColor Cyan
Write-Host "📖 API Docs (if enabled): $ApiUrl/docs" -ForegroundColor Cyan
Write-Host ""
