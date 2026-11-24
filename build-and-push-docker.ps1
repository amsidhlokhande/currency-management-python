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

# 0. Build & Distribute Shared Enterprise Core Library Wheel
Write-Host "`n[0/4] Packaging enterprise-core-python shared library into wheel..." -ForegroundColor Green
$coreDist = Join-Path $PSScriptRoot "enterprise-core-python\dist"
if (-not (Test-Path $coreDist)) { New-Item -ItemType Directory -Path $coreDist -Force | Out-Null }
pip wheel "$PSScriptRoot\enterprise-core-python" --no-deps -w $coreDist --quiet
if ($LASTEXITCODE -ne 0) { throw "enterprise-core-python wheel packaging failed!" }

# Distribute wheel to service contexts for local monorepo container builds
Copy-Item "$coreDist\*.whl" "$PSScriptRoot\currency-exchange-service-python\" -Force
Copy-Item "$coreDist\*.whl" "$PSScriptRoot\currency-conversion-service-python\" -Force
Write-Host "Successfully packaged and distributed enterprise-core-python wheel." -ForegroundColor Cyan

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
