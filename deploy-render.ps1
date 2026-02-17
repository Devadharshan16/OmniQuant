#!/usr/bin/env pwsh
# Quick deployment script for Render

Write-Host "🚀 OmniQuant Render Deployment Preparation" -ForegroundColor Cyan
Write-Host "=" * 60

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "❌ Git not initialized. Run:" -ForegroundColor Red
    Write-Host "   git init" -ForegroundColor Yellow
    Write-Host "   git add ." -ForegroundColor Yellow
    Write-Host "   git commit -m 'Initial commit'" -ForegroundColor Yellow
    exit 1
}

# Check for uncommitted changes
$status = git status --porcelain
if ($status) {
    Write-Host "⚠️  Uncommitted changes detected" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Committing changes..." -ForegroundColor Cyan
    git add .
    git commit -m "Prepare for Render deployment - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}

Write-Host ""
Write-Host "✅ Ready for deployment!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Push to GitHub:" -ForegroundColor White
Write-Host "   git push origin main" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Go to Render Dashboard:" -ForegroundColor White
Write-Host "   https://dashboard.render.com" -ForegroundColor Blue
Write-Host ""
Write-Host "3. Create services using render.yaml (Blueprint)" -ForegroundColor White
Write-Host "   OR follow RENDER_DEPLOYMENT.md for manual setup" -ForegroundColor White
Write-Host ""
Write-Host "📖 Full guide: RENDER_DEPLOYMENT.md" -ForegroundColor Cyan
Write-Host "=" * 60
