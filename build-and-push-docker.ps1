# ========================================================
# Agent 3: Docker Build & Push Automation Script (PowerShell)
# ========================================================

param (
    [string]$Registry = $(if ($env:DOCKER_USERNAME) { $env:DOCKER_USERNAME } else { "amsidhlokhande" }),
    [string]$Tag = "latest",
    [switch]$Push = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "  Agent 3: Multi-Stage Docker Build & Push Pipeline" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

# 0. Synchronize Centralized Constraints
Write-Host "`n[0/4] Synchronizing centralized dependency constraints (BOM)..." -ForegroundColor Green
$centralConstraints = Join-Path $PSScriptRoot "central-dependency-management\constraints.txt"
if (Test-Path $centralConstraints) {
    Copy-Item $centralConstraints -Destination "currency-exchange-service-python\constraints.txt" -Force
    Copy-Item $centralConstraints -Destination "currency-conversion-service-python\constraints.txt" -Force
    Write-Host "Enforced central constraints to microservices: $centralConstraints" -ForegroundColor Cyan
} else {
    Write-Warning "Central constraints file not found at $centralConstraints"
}

# 1. Build Currency Exchange Service
Write-Host "`n[1/4] Building Currency Exchange Service image..." -ForegroundColor Green
docker build -t "currency-exchange-service-python:$Tag" ./currency-exchange-service-python
if ($LASTEXITCODE -ne 0) { throw "Exchange service docker build failed!" }

# 2. Build Currency Conversion Service
Write-Host "`n[2/4] Building Currency Conversion Service image..." -ForegroundColor Green
docker build -t "currency-conversion-service-python:$Tag" ./currency-conversion-service-python
if ($LASTEXITCODE -ne 0) { throw "Conversion service docker build failed!" }

# 3. Tag images for target repository
$exchangeRemoteTag = "$Registry/currency-exchange-service-python:$Tag"
$conversionRemoteTag = "$Registry/currency-conversion-service-python:$Tag"

Write-Host "`n[3/4] Tagging images for remote registry ($Registry)..." -ForegroundColor Green
docker tag "currency-exchange-service-python:$Tag" $exchangeRemoteTag
if ($LASTEXITCODE -ne 0) { throw "Failed to tag $exchangeRemoteTag!" }
docker tag "currency-conversion-service-python:$Tag" $conversionRemoteTag
if ($LASTEXITCODE -ne 0) { throw "Failed to tag $conversionRemoteTag!" }

# 4. Optional Push
if ($Push) {
    if ($env:DOCKER_USERNAME -and $env:DOCKER_PASSWORD) {
        Write-Host "`nAuthenticating to Docker Hub with `$env:DOCKER_USERNAME..." -ForegroundColor Cyan
        $env:DOCKER_PASSWORD | docker login -u $env:DOCKER_USERNAME --password-stdin
        if ($LASTEXITCODE -ne 0) { throw "Docker authentication failed! Please check DOCKER_USERNAME and DOCKER_PASSWORD." }
    }

    Write-Host "`n[4/4] Pushing images to remote registry..." -ForegroundColor Green
    docker push $exchangeRemoteTag
    if ($LASTEXITCODE -ne 0) { throw "Failed to push $exchangeRemoteTag! Verify docker login and registry permissions." }
    docker push $conversionRemoteTag
    if ($LASTEXITCODE -ne 0) { throw "Failed to push $conversionRemoteTag! Verify docker login and registry permissions." }
    Write-Host "`nSuccessfully pushed images to $Registry" -ForegroundColor Green
} else {
    Write-Host "`n[4/4] Images built and tagged locally. Pass -Push to publish to remote registry." -ForegroundColor Yellow
}

Write-Host "`nAll container builds completed successfully!" -ForegroundColor Cyan
