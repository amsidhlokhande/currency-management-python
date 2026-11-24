# 📋 Workflow 1: Requirements Analysis & Architectural Specification

## 1. Overview & Objective
Governed by **Agent 1 (Requirements & Architecture Specialist)**. This workflow defines the baseline requirements, service contracts, data models, technical stack guidelines (Python 3.15.2 + Flask), context path rules, error taxonomies, and non-functional requirements.

---

## 2. Step-by-Step Execution Sequence

### Step 1.1: Context Path & Service Partitioning
1. **`currency-exchange-service-python` Context Path**:
   - Standard Context Path: `/currency-exchange-service-python`
   - Authority for currency conversion rates.
   - Dual-mode ingestion: AWS S3 (`s3://...`) or local Windows filesystem (`C:\rates\exchange_rates.csv` / fallback `data/exchange_rates.csv`).
   - Default listening port: `8000`.
2. **`currency-conversion-service-python` Context Path**:
   - Standard Context Path: `/currency-conversion-service-python`
   - High-throughput conversion computation engine.
   - Issues resilient HTTP client calls to exchange service.
   - Calculates total conversion value (`quantity * conversionMultiple`).
   - Default listening port: `8100`.

### Step 1.2: Error Taxonomy & Generic Error Envelope Standards
- **Currency Exchange Service Prefix**: `CESP_xxx`
- **Currency Conversion Service Prefix**: `CCSP_xxx`
- Error response contains both functional `errorMessage` and technical `errorDetailMessage`.
- Error codes and messages are loaded from `.env` and driven via `constants.py`.

### Step 1.3: Layered Project Architecture Standard
Standardized modular layout: `app.py`, `constants.py`, `.env`, `e2e/config`, `e2e/route`, `e2e/modules`, `e2e/service`, `e2e/exception`, `e2e/utils`, `tests`.
