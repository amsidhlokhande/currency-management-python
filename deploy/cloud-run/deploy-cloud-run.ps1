# ==============================================================================
# Agent 4: Google Cloud Run Dual-Service Automated Deployment Script (PowerShell)
# Target Environment: Google Cloud Run (Serverless Containers)
# Architecture: Zero-Trust IAM & Context Path Enforcement
# ==============================================================================

param (
    [string]$ProjectId = "currency-microservices-prod",
    [string]$Region = "us-central1",
    [string]$ArtifactRepo = "currency-repo",
    [string]$Tag = "latest",
    [string]$S3RateUri = "s3://currency-rates-bucket/exchange_rates.csv",
    [string]$GithubToken = $(if ($env:READ_PACKAGES_TOKEN) { $env:READ_PACKAGES_TOKEN } elseif ($env:GITHUB_TOKEN) { $env:GITHUB_TOKEN } else { "" })
)

$ErrorActionPreference = "Stop"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  Agent 4: Google Cloud Run Deployment Pipeline Orchestrator" -ForegroundColor Cyan
Write-Host "  Project ID : $ProjectId" -ForegroundColor Yellow
Write-Host "  Region     : $Region" -ForegroundColor Yellow
Write-Host "  Rate S3 URI: $S3RateUri" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Environment Verification
Write-Host "`n[Step 1/7] Verifying CLI prerequisites..." -ForegroundColor Green
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Warning "gcloud CLI is not found in PATH."
    Write-Host "Please install Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    Write-Host "Or execute this script inside Google Cloud Shell."
    exit 1
}

# 2. Configure GCP Context & Enable APIs
Write-Host "`n[Step 2/7] Setting GCP project and enabling required APIs..." -ForegroundColor Green
gcloud config set project $ProjectId
gcloud config set run/region $Region

gcloud services enable `
    run.googleapis.com `
    artifactregistry.googleapis.com `
    secretmanager.googleapis.com `
    storage.googleapis.com `
    iam.googleapis.com

# 3. Create Artifact Registry Repository & Configure Docker Auth
Write-Host "`n[Step 3/7] Setting up Artifact Registry repository ($ArtifactRepo)..." -ForegroundColor Green
$repoExists = gcloud artifacts repositories describe $ArtifactRepo --location=$Region --format="value(name)" 2>$null
if (-not $repoExists) {
    gcloud artifacts repositories create $ArtifactRepo `
        --repository-format=docker `
        --location=$Region `
        --description="Docker repository for Currency Microservices"
}
gcloud auth configure-docker "$Region-docker.pkg.dev" --quiet

# 4. Service Account Provisioning
Write-Host "`n[Step 4/7] Provisioning least-privilege IAM service accounts..." -ForegroundColor Green

# Exchange Service SA
$saExchange = "sa-currency-exchange"
$saExchangeEmail = "$saExchange@$ProjectId.iam.gserviceaccount.com"
$saExExists = gcloud iam service-accounts describe $saExchangeEmail 2>$null
if (-not $saExExists) {
    gcloud iam service-accounts create $saExchange --display-name="SA Currency Exchange"
}

# Conversion Service SA
$saConversion = "sa-currency-conversion"
$saConversionEmail = "$saConversion@$ProjectId.iam.gserviceaccount.com"
$saCvExists = gcloud iam service-accounts describe $saConversionEmail 2>$null
if (-not $saCvExists) {
    gcloud iam service-accounts create $saConversion --display-name="SA Currency Conversion"
}

# 5. Build & Push Docker Images to Google Artifact Registry
Write-Host "`n[Step 5/7] Building and pushing Docker images to Artifact Registry..." -ForegroundColor Green
$exchangeImage = "$Region-docker.pkg.dev/$ProjectId/$ArtifactRepo/currency-exchange-service-python:$Tag"
$conversionImage = "$Region-docker.pkg.dev/$ProjectId/$ArtifactRepo/currency-conversion-service-python:$Tag"

$dockerBuildArgs = @()
if ($GithubToken) {
    $dockerBuildArgs += @("--build-arg", "GITHUB_TOKEN=$GithubToken")
}

# Build & push Exchange
docker build @dockerBuildArgs -t $exchangeImage ./currency-exchange-service-python
if ($LASTEXITCODE -ne 0) { throw "Exchange service docker build failed!" }
docker push $exchangeImage
if ($LASTEXITCODE -ne 0) { throw "Exchange service docker push failed!" }

# Build & push Conversion
docker build @dockerBuildArgs -t $conversionImage ./currency-conversion-service-python
if ($LASTEXITCODE -ne 0) { throw "Conversion service docker build failed!" }
docker push $conversionImage
if ($LASTEXITCODE -ne 0) { throw "Conversion service docker push failed!" }

# 6. Deploy Private Currency Exchange Service
Write-Host "`n[Step 6/7] Deploying private currency-exchange-service-python (internal ingress)..." -ForegroundColor Green
gcloud run deploy currency-exchange-service-python `
    --image=$exchangeImage `
    --platform=managed `
    --region=$Region `
    --service-account=$saExchangeEmail `
    --ingress=internal `
    --no-allow-unauthenticated `
    --port=8000 `
    --min-instances=1 `
    --max-instances=10 `
    --concurrency=80 `
    --cpu=1 `
    --memory=512Mi `
    --set-env-vars="ENV=production,LOG_LEVEL=INFO,PORT=8000,CONTEXT_PATH=/currency-exchange-service-python,RATES_CSV_PATH=$S3RateUri"

# Retrieve private URL of the exchange service
$rawExchangeUrl = (gcloud run services describe currency-exchange-service-python --region=$Region --format="value(status.url)")
$exchangeUrl = "$rawExchangeUrl/currency-exchange-service-python"
Write-Host "Currency Exchange Service internal base URL: $exchangeUrl" -ForegroundColor Cyan

# Grant Conversion Service Account permission to invoke Exchange Service (Zero-Trust IAM)
Write-Host "Binding Cloud Run Invoker role (Conversion SA -> Exchange Service)..." -ForegroundColor Yellow
gcloud run services add-iam-policy-binding currency-exchange-service-python `
    --region=$Region `
    --member="serviceAccount:$saConversionEmail" `
    --role="roles/run.invoker"

# 7. Deploy Public Currency Conversion Service
Write-Host "`n[Step 7/7] Deploying public currency-conversion-service-python..." -ForegroundColor Green
gcloud run deploy currency-conversion-service-python `
    --image=$conversionImage `
    --platform=managed `
    --region=$Region `
    --service-account=$saConversionEmail `
    --ingress=all `
    --allow-unauthenticated `
    --port=8100 `
    --min-instances=1 `
    --max-instances=10 `
    --concurrency=80 `
    --cpu=1 `
    --memory=512Mi `
    --set-env-vars="ENV=production,LOG_LEVEL=INFO,PORT=8100,CONTEXT_PATH=/currency-conversion-service-python,EXCHANGE_SERVICE_URL=$exchangeUrl,GCP_OIDC_AUTH=true"

$rawConversionUrl = (gcloud run services describe currency-conversion-service-python --region=$Region --format="value(status.url)")
$conversionBaseUrl = "$rawConversionUrl/currency-conversion-service-python"

Write-Host "`n=================================================================" -ForegroundColor Green
Write-Host "  DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "  Public Conversion Service Context URL: $conversionBaseUrl" -ForegroundColor Cyan
Write-Host "  Try: curl $conversionBaseUrl/currency-conversion/from/USD/to/INR/quantity/100" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Green
