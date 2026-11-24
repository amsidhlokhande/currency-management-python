# ☁️ Agent 4: Google Cloud Run Deployment & Architecture Playbook

## 1. Agent Persona & Mandate

- **Role**: Staff Site Reliability Engineer (SRE) & Google Cloud Solutions Architect
- **Primary Mission**:
  1. Author and maintain the production-ready step-by-step deployment architecture and runbooks for Google Cloud Run.
  2. Implement declarative Cloud Run service specifications (`service.yaml`), Google Cloud IAM zero-trust authentication, and networking topology.
  3. Formulate Secret Manager integration and Google Cloud Storage / S3 rate data storage mechanisms.
  4. Continuously monitor Agent 1, 2, and 3 changes (ports, environment variables, health endpoints, image tags) and reconcile deployment plans to maintain zero configuration drift.

---

## 2. Cloud Run Architecture & Zero-Trust Service-to-Service Mesh

```mermaid
graph TB
    subgraph PublicInternet ["🌐 External World"]
        User([Client Application])
    end

    subgraph GoogleCloud ["☁️ Google Cloud Platform Project"]
        subgraph CloudRun_Ingress ["Edge & Conversion Service"]
            ConvRun["🚀 Cloud Run: currency-conversion-service-python<br/>• Ingress: all (Public / Authenticated)<br/>• Min: 1 | Max: 10<br/>• Concurrency: 80<br/>• Service Account: sa-conversion@project.iam.gserviceaccount.com"]
        end

        subgraph IAM_Auth ["🔐 Zero-Trust IAM & OIDC"]
            MetadataSvc["GCP Metadata Server<br/>http://metadata.google.internal/...<br/>Generates OIDC Identity Token"]
            IAM_Invoker["Cloud Run Invoker Role<br/>roles/run.invoker"]
        end

        subgraph CloudRun_Private ["Internal Exchange Authority"]
            ExchRun["🚀 Cloud Run: currency-exchange-service-python<br/>• Ingress: internal (Private)<br/>• Min: 1 | Max: 10<br/>• Concurrency: 80<br/>• Service Account: sa-exchange@project.iam.gserviceaccount.com"]
        end

        subgraph CloudStorage ["💾 Rate Data Authority"]
            GCS_Bucket[("🪣 Cloud Storage / S3 Bucket<br/>gs://currency-rates-data/exchange_rates.csv")]
            SecretMgr[("🔑 Google Secret Manager<br/>AWS_SECRET_ACCESS_KEY, API_KEY")]
        end
    end

    User -->|1. HTTPS Request<br/>X-Correlation-ID| ConvRun
    ConvRun -->|2. Request OIDC Token for ExchRun Audience| MetadataSvc
    MetadataSvc -->>|3. Return Bearer OIDC Token| ConvRun
    ConvRun -->|4. Authenticated Request<br/>Authorization: Bearer <ID_TOKEN><br/>X-Correlation-ID: xyz| ExchRun
    IAM_Invoker -.->|Enforce IAM Policy| ExchRun
    ExchRun -->|5. Load CSV at Boot| GCS_Bucket
    ExchRun -.->|Fetch Credentials if S3| SecretMgr
    ExchRun -->>|6. Rate Response JSON| ConvRun
    ConvRun -->>|7. Final Conversion JSON| User
```

---

## 3. Step-by-Step Google Cloud Run Deployment Plan

### Step 1: GCP Project & Infrastructure Prerequisites
```powershell
# Set GCP Project and Region
$PROJECT_ID = "your-gcp-project-id"
$REGION = "us-central1"
$ARTIFACT_REPO = "currency-repo"

# Authenticate & set default project
gcloud auth login
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

# Enable required Google APIs
gcloud services enable `
    run.googleapis.com `
    artifactregistry.googleapis.com `
    secretmanager.googleapis.com `
    storage.googleapis.com `
    iam.googleapis.com
```

### Step 2: Create Artifact Registry for Docker Images
```powershell
gcloud artifacts repositories create $ARTIFACT_REPO `
    --repository-format=docker `
    --location=$REGION `
    --description="Docker repository for Currency Microservices"

# Configure Docker local authentication
gcloud auth configure-docker "$REGION-docker.pkg.dev"
```

### Step 3: Configure Dedicated Least-Privilege IAM Service Accounts
```powershell
# 1. Service Account for Currency Exchange Service
gcloud iam service-accounts create sa-currency-exchange `
    --description="Runtime identity for Currency Exchange Service" `
    --display-name="SA Currency Exchange"

# Grant storage.objectViewer to read CSV rate files
gcloud projects add-iam-policy-binding $PROJECT_ID `
    --member="serviceAccount:sa-currency-exchange@$PROJECT_ID.iam.gserviceaccount.com" `
    --role="roles/storage.objectViewer"

# 2. Service Account for Currency Conversion Service
gcloud iam service-accounts create sa-currency-conversion `
    --description="Runtime identity for Currency Conversion Service" `
    --display-name="SA Currency Conversion"
```

### Step 4: Build & Push Images to Google Artifact Registry
```powershell
# Build and Push Currency Exchange Service
docker build -t "$REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REPO/currency-exchange-service-python:v1" ./currency-exchange-service-python
docker push "$REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REPO/currency-exchange-service-python:v1"

# Build and Push Currency Conversion Service
docker build -t "$REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REPO/currency-conversion-service-python:v1" ./currency-conversion-service-python
docker push "$REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REPO/currency-conversion-service-python:v1"
```

### Step 5: Deploy Private `currency-exchange-service-python`
```powershell
gcloud run deploy currency-exchange-service-python `
    --image="$REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REPO/currency-exchange-service-python:v1" `
    --platform=managed `
    --region=$REGION `
    --service-account="sa-currency-exchange@$PROJECT_ID.iam.gserviceaccount.com" `
    --ingress=internal `
    --no-allow-unauthenticated `
    --port=8000 `
    --min-instances=1 `
    --max-instances=10 `
    --concurrency=80 `
    --cpu=1 `
    --memory=512Mi `
    --set-env-vars="LOG_LEVEL=INFO,RATES_CSV_PATH=gs://$PROJECT_ID-currency-rates/exchange_rates.csv"
```

### Step 6: Bind IAM Invoker Permissions (Conversion ➔ Exchange)
```powershell
# Allow Conversion Service Account to invoke Exchange Service via OIDC token
gcloud run services add-iam-policy-binding currency-exchange-service-python `
    --region=$REGION `
    --member="serviceAccount:sa-currency-conversion@$PROJECT_ID.iam.gserviceaccount.com" `
    --role="roles/run.invoker"
```

### Step 7: Deploy Public `currency-conversion-service-python`
```powershell
# Retrieve URL of the exchange service
$EXCHANGE_URL = (gcloud run services describe currency-exchange-service-python --region=$REGION --format="value(status.url)")

# Deploy conversion service
gcloud run deploy currency-conversion-service-python `
    --image="$REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REPO/currency-conversion-service-python:v1" `
    --platform=managed `
    --region=$REGION `
    --service-account="sa-currency-conversion@$PROJECT_ID.iam.gserviceaccount.com" `
    --ingress=all `
    --allow-unauthenticated `
    --port=8100 `
    --min-instances=1 `
    --max-instances=10 `
    --concurrency=80 `
    --cpu=1 `
    --memory=512Mi `
    --set-env-vars="LOG_LEVEL=INFO,EXCHANGE_SERVICE_URL=$EXCHANGE_URL,GCP_OIDC_AUTH=true"
```

---

## 4. Declarative YAML Manifest (`service.yaml`)

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: currency-conversion-service-python
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/launch-stage: GA
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/execution-environment: gen2
        run.googleapis.com/cpu-throttling: "false"
    spec:
      serviceAccountName: sa-currency-conversion@PROJECT_ID.iam.gserviceaccount.com
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
      - image: REGION-docker.pkg.dev/PROJECT_ID/currency-repo/currency-conversion-service-python:v1
        ports:
        - name: http1
          containerPort: 8100
        resources:
          limits:
            cpu: 1000m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health/liveness
            port: 8100
          initialDelaySeconds: 5
          periodSeconds: 15
        startupProbe:
          httpGet:
            path: /health/readiness
            port: 8100
          initialDelaySeconds: 2
          periodSeconds: 5
          failureThreshold: 10
        env:
        - name: LOG_LEVEL
          value: "INFO"
        - name: PORT
          value: "8100"
        - name: GCP_OIDC_AUTH
          value: "true"
```

---

## 5. Continuous Synchronization & Drift Management

Agent 4 continuously listens to Agent 5 broadcasts:
- **Port Alterations**: If Agent 2 updates service ports, Agent 4 automatically updates `containerPort` and `--port` flags in scripts and YAML manifests.
- **Environment Variable Additions**: If new configuration keys are declared in `AGENT1_REQUIREMENTS_SPEC.md`, Agent 4 maps them as either plain-text environment variables or Secret Manager bindings.
- **Image Digest Updates**: Recompiles deployment manifests with latest SHA256 immutable digests after Agent 3 pushes new images.
