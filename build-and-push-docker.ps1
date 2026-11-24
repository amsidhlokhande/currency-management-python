# ==============================================================================
# Docker Build, Push & Run Pipeline Orchestrator (PowerShell)
# Currency Management Microservices
# ==============================================================================

[CmdletBinding(DefaultParameterSetName = "Default")]
param (
    [Parameter(Position = 0)]
    [Alias("Action")]
    [ValidateSet("build", "pull", "BuildOnly", "BuildAndPush", "BuildPushRun", "PullAndRun", "Down")]
    [string]$Mode = "build",

    [Parameter(Position = 1)]
    [string]$Registry = $(if ($env:DOCKER_USERNAME) { $env:DOCKER_USERNAME } else { "amsidhlokhande" }),

    [Parameter(Position = 2)]
    [string]$Tag = $(if ($env:TAG) { $env:TAG } else { "latest" }),

    [string]$GithubToken = $(if ($env:READ_PACKAGES_TOKEN) { $env:READ_PACKAGES_TOKEN } elseif ($env:GITHUB_TOKEN) { $env:GITHUB_TOKEN } else { "" }),

    [switch]$Push,
    [switch]$Run,
    [switch]$Down
)

$ErrorActionPreference = "Stop"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  Currency Management Microservices - Docker Orchestrator" -ForegroundColor Cyan
Write-Host "  Mode     : $Mode" -ForegroundColor Yellow
Write-Host "  Registry : $Registry" -ForegroundColor Yellow
Write-Host "  Tag      : $Tag" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan

# ------------------------------------------------------------------------------
# Helper: Docker Daemon Health Check
# ------------------------------------------------------------------------------
Write-Host "`n[Check] Verifying Docker daemon status..." -ForegroundColor Green
try {
    $dockerVersion = & docker version --format '{{.Server.Version}}' 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($dockerVersion)) {
        throw "Docker engine is unreachable."
    }
    Write-Host "Docker daemon is operational (Engine version: $dockerVersion)." -ForegroundColor Green
} catch {
    Write-Error "Docker daemon is not running or not accessible in PATH. Please launch Docker Desktop."
    exit 1
}

# ------------------------------------------------------------------------------
# Helper: Docker Hub Authentication
# ------------------------------------------------------------------------------
function Invoke-DockerLogin {
    param (
        [string]$Username = $env:DOCKER_USERNAME,
        [string]$Password = $env:DOCKER_PASSWORD
    )
    if ($Username -and $Password) {
        Write-Host "`nAuthenticating to Docker Hub as '$Username'..." -ForegroundColor Cyan
        $Password | & docker login -u $Username --password-stdin
        if ($LASTEXITCODE -ne 0) {
            throw "Docker authentication failed! Please verify DOCKER_USERNAME and DOCKER_PASSWORD."
        }
        Write-Host "Successfully authenticated to Docker Hub." -ForegroundColor Green
    } else {
        Write-Host "`nDocker Hub credentials (DOCKER_USERNAME / DOCKER_PASSWORD) not provided in environment." -ForegroundColor Gray
        Write-Host "Proceeding with existing cached docker credentials if present." -ForegroundColor Gray
    }
}

# ------------------------------------------------------------------------------
# Teardown Handling (-Down)
# ------------------------------------------------------------------------------
if ($Down -or $Mode -eq "Down") {
    Write-Host "`n[Teardown] Stopping and removing containers and networks..." -ForegroundColor Yellow
    $env:DOCKER_USERNAME = $Registry
    $env:TAG = $Tag
    & docker compose -f docker-compose.build.yml down --remove-orphans
    & docker compose -f docker-compose.pull.yml down --remove-orphans
    Write-Host "All containers and networks stopped successfully." -ForegroundColor Green
    exit 0
}

# ------------------------------------------------------------------------------
# Normalize Execution Mode
# ------------------------------------------------------------------------------
$isPullMode = ($Mode -in @("pull", "PullAndRun"))
if ($Mode -in @("BuildAndPush", "BuildPushRun")) {
    $Push = $true
}
if ($Mode -in @("PullAndRun", "BuildPushRun")) {
    $Run = $true
}

# Export environment variables for Docker Compose file interpolation
$env:DOCKER_USERNAME = $Registry
$env:TAG = $Tag

# Token resolution
if (-not $GithubToken) {
    if ($env:READ_PACKAGES_TOKEN) {
        $GithubToken = $env:READ_PACKAGES_TOKEN
    } elseif ($env:GITHUB_TOKEN) {
        $GithubToken = $env:GITHUB_TOKEN
    }
}

if ($GithubToken) {
    $env:READ_PACKAGES_TOKEN = $GithubToken
    $env:GITHUB_TOKEN = $GithubToken
    Write-Host "`nGitHub Token resolved for dependency resolution inside Dockerfile." -ForegroundColor Cyan
} else {
    Write-Host "`nNo GitHub Token supplied. Public repository access will be used for enterprise-core-python." -ForegroundColor Gray
}

# ==============================================================================
# MODE 2: Pull & Run (docker-compose.pull.yml)
# ==============================================================================
if ($isPullMode) {
    Write-Host "`n-----------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "  MODE 2: Pull Images & Run Services" -ForegroundColor Cyan
    Write-Host "-----------------------------------------------------------------" -ForegroundColor Cyan

    # 1. Authenticate to Docker Hub if credentials provided
    Invoke-DockerLogin

    # 2. Pull images using docker-compose.pull.yml
    Write-Host "`n[Step 1/2] Pulling images via docker-compose.pull.yml..." -ForegroundColor Green
    & docker compose -f docker-compose.pull.yml pull
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to pull Docker images via docker-compose.pull.yml! Please ensure images exist on registry '$Registry'."
    }
    Write-Host "All images pulled successfully." -ForegroundColor Green

    # 3. Start containers
    Write-Host "`n[Step 2/2] Starting containers on Docker Desktop..." -ForegroundColor Green
    & docker compose -f docker-compose.pull.yml up -d
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start containers using docker-compose.pull.yml!"
    }

    Write-Host "`nService status:" -ForegroundColor Green
    & docker compose -f docker-compose.pull.yml ps

    Write-Host "`nDeployment verification endpoints:" -ForegroundColor Yellow
    Write-Host "  - Exchange Liveness   : http://localhost:8000/currency-exchange-service-python/health/liveness"
    Write-Host "  - Conversion Liveness : http://localhost:8100/currency-conversion-service-python/health/liveness"
    Write-Host "  - Sample Conversion   : http://localhost:8100/currency-conversion-service-python/currency-conversion/from/USD/to/INR/quantity/100"
    Write-Host "`nPull and run completed successfully!" -ForegroundColor Green
    exit 0
}

# ==============================================================================
# MODE 1: Build, Push & Run (docker-compose.build.yml)
# ==============================================================================
Write-Host "`n-----------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "  MODE 1: Build Multi-Stage Images" -ForegroundColor Cyan
Write-Host "-----------------------------------------------------------------" -ForegroundColor Cyan

# 1. Build images using docker-compose.build.yml
Write-Host "`n[Step 1/3] Building images via docker-compose.build.yml..." -ForegroundColor Green
$buildArgs = @("-f", "docker-compose.build.yml", "build")
if ($GithubToken) {
    $buildArgs += @("--build-arg", "GITHUB_TOKEN=$GithubToken")
}
& docker compose @buildArgs
if ($LASTEXITCODE -ne 0) {
    throw "Docker compose build failed! Please check Dockerfile or build logs above."
}
Write-Host "Images built successfully:" -ForegroundColor Green
Write-Host "  - $Registry/currency-exchange-service-python:$Tag" -ForegroundColor Cyan
Write-Host "  - $Registry/currency-conversion-service-python:$Tag" -ForegroundColor Cyan

# 2. Push to Docker Hub (if requested)
if ($Push) {
    Write-Host "`n[Step 2/3] Publishing images to registry ($Registry)..." -ForegroundColor Green
    Invoke-DockerLogin
    & docker compose -f docker-compose.build.yml push
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to push images to registry! Please check docker login and permissions for repository '$Registry'."
    }
    Write-Host "Images published successfully to $Registry." -ForegroundColor Green
} else {
    Write-Host "`n[Step 2/3] Push skipped. Use -Push to publish images to container registry." -ForegroundColor Gray
}

# 3. Run on Docker Desktop (if requested)
if ($Run) {
    Write-Host "`n[Step 3/3] Starting containers locally on Docker Desktop..." -ForegroundColor Green
    & docker compose -f docker-compose.build.yml up -d
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to launch containers using docker-compose.build.yml!"
    }

    Write-Host "`nService status:" -ForegroundColor Green
    & docker compose -f docker-compose.build.yml ps

    Write-Host "`nDeployment verification endpoints:" -ForegroundColor Yellow
    Write-Host "  - Exchange Liveness   : http://localhost:8000/currency-exchange-service-python/health/liveness"
    Write-Host "  - Conversion Liveness : http://localhost:8100/currency-conversion-service-python/health/liveness"
    Write-Host "  - Sample Conversion   : http://localhost:8100/currency-conversion-service-python/currency-conversion/from/USD/to/INR/quantity/100"
} else {
    Write-Host "`n[Step 3/3] Local run skipped. Use -Run to spin up services on Docker Desktop." -ForegroundColor Gray
}

Write-Host "`nAll operations completed successfully!" -ForegroundColor Green
