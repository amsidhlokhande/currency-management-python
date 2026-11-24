#!/usr/bin/env bash
# ==============================================================================
# Agent 4: Google Cloud Run Dual-Service Automated Deployment Script (Bash)
# Target Environment: Google Cloud Run (Serverless Containers)
# Architecture: Zero-Trust IAM & Context Path Enforcement
# ==============================================================================

set -euo pipefail

PROJECT_ID="${1:-currency-microservices-prod}"
REGION="${2:-us-central1}"
ARTIFACT_REPO="${3:-currency-repo}"
TAG="${4:-latest}"
S3_RATE_URI="${5:-s3://currency-rates-bucket/exchange_rates.csv}"

echo "================================================================="
echo "  Agent 4: Google Cloud Run Deployment Pipeline Orchestrator"
echo "  Project ID : ${PROJECT_ID}"
echo "  Region     : ${REGION}"
echo "  Rate S3 URI: ${S3_RATE_URI}"
echo "================================================================="

# 1. Environment Verification
if ! command -v gcloud &> /dev/null; then
    echo "ERROR: gcloud CLI not found. Please install the Google Cloud SDK." >&2
    exit 1
fi

# 2. Configure GCP Context & Enable APIs
echo -e "\n[Step 2/7] Setting project & enabling APIs..."
gcloud config set project "${PROJECT_ID}"
gcloud config set run/region "${REGION}"

gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    storage.googleapis.com \
    iam.googleapis.com

# 3. Create Artifact Registry
echo -e "\n[Step 3/7] Setting up Artifact Registry..."
if ! gcloud artifacts repositories describe "${ARTIFACT_REPO}" --location="${REGION}" &> /dev/null; then
    gcloud artifacts repositories create "${ARTIFACT_REPO}" \
        --repository-format=docker \
        --location="${REGION}" \
        --description="Docker repository for Currency Microservices"
fi
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

# 4. Service Account Provisioning
echo -e "\n[Step 4/7] Provisioning IAM service accounts..."
SA_EXCHANGE="sa-currency-exchange"
SA_EXCHANGE_EMAIL="${SA_EXCHANGE}@${PROJECT_ID}.iam.gserviceaccount.com"
if ! gcloud iam service-accounts describe "${SA_EXCHANGE_EMAIL}" &> /dev/null; then
    gcloud iam service-accounts create "${SA_EXCHANGE}" --display-name="SA Currency Exchange"
fi

SA_CONVERSION="sa-currency-conversion"
SA_CONVERSION_EMAIL="${SA_CONVERSION}@${PROJECT_ID}.iam.gserviceaccount.com"
if ! gcloud iam service-accounts describe "${SA_CONVERSION_EMAIL}" &> /dev/null; then
    gcloud iam service-accounts create "${SA_CONVERSION}" --display-name="SA Currency Conversion"
fi

# 5. Build & Push Docker Images
echo -e "\n[Step 5/7] Building and pushing container images..."
EXCHANGE_IMG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/currency-exchange-service-python:${TAG}"
CONVERSION_IMG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/currency-conversion-service-python:${TAG}"

docker build -t "${EXCHANGE_IMG}" ./currency-exchange-service-python
docker push "${EXCHANGE_IMG}"

docker build -t "${CONVERSION_IMG}" ./currency-conversion-service-python
docker push "${CONVERSION_IMG}"

# 6. Deploy Private Exchange Service
echo -e "\n[Step 6/7] Deploying private currency-exchange-service-python..."
gcloud run deploy currency-exchange-service-python \
    --image="${EXCHANGE_IMG}" \
    --platform=managed \
    --region="${REGION}" \
    --service-account="${SA_EXCHANGE_EMAIL}" \
    --ingress=internal \
    --no-allow-unauthenticated \
    --port=8000 \
    --min-instances=1 \
    --max-instances=10 \
    --concurrency=80 \
    --cpu=1 \
    --memory=512Mi \
    --set-env-vars="ENV=production,LOG_LEVEL=INFO,PORT=8000,CONTEXT_PATH=/currency-exchange-service-python,RATES_CSV_PATH=${S3_RATE_URI}"

RAW_EXCHANGE_URL=$(gcloud run services describe currency-exchange-service-python --region="${REGION}" --format="value(status.url)")
EXCHANGE_URL="${RAW_EXCHANGE_URL}/currency-exchange-service-python"
echo "Currency Exchange internal URL: ${EXCHANGE_URL}"

# Bind IAM Invoker
gcloud run services add-iam-policy-binding currency-exchange-service-python \
    --region="${REGION}" \
    --member="serviceAccount:${SA_CONVERSION_EMAIL}" \
    --role="roles/run.invoker"

# 7. Deploy Public Conversion Service
echo -e "\n[Step 7/7] Deploying public currency-conversion-service-python..."
gcloud run deploy currency-conversion-service-python \
    --image="${CONVERSION_IMG}" \
    --platform=managed \
    --region="${REGION}" \
    --service-account="${SA_CONVERSION_EMAIL}" \
    --ingress=all \
    --allow-unauthenticated \
    --port=8100 \
    --min-instances=1 \
    --max-instances=10 \
    --concurrency=80 \
    --cpu=1 \
    --memory=512Mi \
    --set-env-vars="ENV=production,LOG_LEVEL=INFO,PORT=8100,CONTEXT_PATH=/currency-conversion-service-python,EXCHANGE_SERVICE_URL=${EXCHANGE_URL},GCP_OIDC_AUTH=true"

RAW_CONVERSION_URL=$(gcloud run services describe currency-conversion-service-python --region="${REGION}" --format="value(status.url)")
CONVERSION_BASE_URL="${RAW_CONVERSION_URL}/currency-conversion-service-python"

echo "================================================================="
echo "  DEPLOYMENT COMPLETE!"
echo "  Public Base URL: ${CONVERSION_BASE_URL}"
echo "  Test: curl ${CONVERSION_BASE_URL}/currency-conversion/from/USD/to/INR/quantity/100"
echo "================================================================="
