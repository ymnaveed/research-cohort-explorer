# Research Cohort Explorer

A full-stack research cohort exploration application built with PostgreSQL, FastAPI, React, and Python.

Research Cohort Explorer demonstrates how structured clinical data can be modeled, validated, queried, and exposed through a controlled cohort-building workflow. The project uses a fully synthetic clinical dataset and provides a reusable cohort engine for defining patient populations using demographic and clinical criteria.

> **Important:** All patient and clinical data used by this project is synthetic. The repository does not contain real patient information or protected health information (PHI).

## Overview

The project was designed as an end-to-end data engineering and analytics application covering:

- synthetic clinical data generation
- relational database design
- data validation and quality assurance
- analytical SQL views
- metadata-driven cohort criteria
- controlled dynamic SQL generation
- cohort execution and membership persistence
- REST API development
- automated regression testing
- React-based cohort management and exploration

The application separates the data, cohort engine, API, and user interface into independent layers.

## Architecture

```text
┌─────────────────────────────┐
│       React Frontend        │
│ Cohorts • Criteria • Results│
│ Members • API Status        │
└──────────────┬──────────────┘
               │ HTTP / JSON
               ▼
┌─────────────────────────────┐
│        FastAPI Backend      │
│ Validation • API • Execution│
└──────────────┬──────────────┘
               │ psycopg
               ▼
┌─────────────────────────────┐
│       PostgreSQL 16         │
│                             │
│ Core Clinical Tables        │
│ Analytical Views            │
│ Cohort Definitions          │
│ Criteria Whitelist          │
│ Cohort Engine               │
│ Membership + Audit Log      │
└─────────────────────────────┘
               ▲
               │
┌──────────────┴──────────────┐
│ Synthetic Data Generators   │
│          Python             │
└─────────────────────────────┘
```

## Technology Stack

### Database

- PostgreSQL 16
- Docker / Docker Compose
- relational clinical data model
- analytical SQL views
- PL/pgSQL cohort execution
- database constraints and validation
- controlled dynamic SQL

### Backend

- Python 3.11
- FastAPI
- psycopg
- Uvicorn
- pytest
- HTTPX

### Frontend

- React
- Vite
- JavaScript
- CSS
- Fetch API

## Synthetic Clinical Dataset

The development database contains **100,000 synthetic patients** and more than **4.46 million total synthetic records** across the core clinical domains.

| Dataset | Records |
|---|---:|
| Patients | 100,000 |
| Encounters | 1,151,313 |
| Diagnoses | 56,531 |
| Laboratory Results | 1,408,495 |
| Medication Orders | 114,123 |
| Procedures | 211,638 |
| Clinical Notes | 1,401,000 |
| **Total** | **4,463,110** |

The synthetic study period spans:

**January 1, 2015 – December 31, 2025**

Synthetic data generators are located in:

```text
synthetic-data/
```

The generated CSV output is intentionally excluded from Git.

## Clinical Data Model

The database includes core tables for:

- patients
- encounters
- diagnoses
- laboratory results
- medication orders
- procedures
- clinical notes

Reference tables provide controlled values for:

- diagnosis codes
- laboratory tests
- medication codes
- procedure codes
- encounter types
- facilities
- providers
- note types

Database constraints and validation logic help enforce referential and temporal integrity.

## Analytical Views

Seven analytical views provide consistent query interfaces over the underlying clinical tables:

```text
vw_patient_demographics
vw_encounters
vw_diagnoses
vw_lab_results
vw_medication_orders
vw_procedures
vw_clinical_notes
```

These views isolate cohort logic from the physical source tables and provide a reusable analytical layer.

## Cohort Engine v1

The project includes a metadata-driven cohort engine that converts stored cohort criteria into controlled SQL.

Supported inclusion domains are:

- demographics
- diagnosis
- laboratory
- medication
- procedure
- encounter

Diagnosis criteria additionally support exclusions.

### Supported Criteria

The current whitelist supports:

| Domain | Field | Operators |
|---|---|---|
| Demographics | `age_at_study_end` | `>=` |
| Diagnosis | `diagnosis_code` | `=` |
| Diagnosis | `recorded_date` | `>=`, `<=` |
| Laboratory | `test_code` | `=` |
| Laboratory | `result_numeric` | `>=`, `<=` |
| Medication | `medication_code` | `=` |
| Procedure | `procedure_code` | `=` |
| Encounter | `encounter_type_code` | `=` |

Only combinations explicitly defined in the criterion whitelist can be used by the SQL generator.

### Cohort Safety Controls

The cohort engine includes several controls to prevent arbitrary SQL construction:

- domain, field, and operator whitelist validation
- criterion value type validation
- safe PostgreSQL identifier and literal formatting
- validation before SQL generation
- validation before cohort execution
- inclusion criteria required before execution
- unsupported exclusion domains rejected
- controlled cohort membership persistence
- cohort execution audit logging

## Example Cohort

The development database includes an example cohort:

**Adult Type 2 Diabetes**

Criteria:

```text
Diagnosis code = E11.9
Age at study end >= 18
Diagnosis recorded date >= 2015-01-01
Diagnosis recorded date <= 2025-12-31
```

The validated synthetic dataset produces:

**6,620 cohort members**

This result is also checked by the database regression suite.

## Backend API

The FastAPI backend exposes endpoints for health monitoring, cohort management, criteria management, execution, results, and member exploration.

### Health

```text
GET /health
GET /health/database
```

### Cohorts

```text
GET  /cohorts
GET  /cohorts/{cohort_id}
POST /cohorts
```

### Criteria

```text
GET    /cohorts/{cohort_id}/criteria
POST   /cohorts/{cohort_id}/criteria
DELETE /cohorts/{cohort_id}/criteria/{criterion_id}
```

### Execution and Results

```text
POST /cohorts/{cohort_id}/execute
GET  /cohorts/{cohort_id}/results
```

### Cohort Members

```text
GET /cohorts/{cohort_id}/members
```

Member retrieval supports pagination using:

```text
limit
offset
```

The API returns research identifiers and analytical demographics rather than exposing the internal patient primary key.

FastAPI's interactive API documentation is available while the backend is running at:

```text
http://127.0.0.1:8000/docs
```

## Frontend Application

The React frontend provides a user interface for the complete cohort workflow.

Current functionality includes:

- view available cohorts
- create a cohort
- inspect cohort criteria
- add supported criteria
- delete criteria
- execute a cohort
- display cohort member counts
- browse cohort members
- paginate through cohort membership
- display backend/database connection status
- responsive layout

The API status indicator uses the database health endpoint rather than displaying a hardcoded connection state.

## Project Structure

```text
research-cohort-explorer/
│
├── backend/
│   └── app/
│       ├── database.py
│       └── main.py
│
├── database/
│   ├── cohort_engine/
│   ├── queries/
│   ├── schema/
│   ├── seed/
│   ├── views/
│   └── init.sql
│
├── docs/
│   ├── database-validation.md
│   └── week-1-summary.md
│
├── frontend/
│   ├── public/
│   └── src/
│
├── synthetic-data/
│
├── tests/
│   ├── test_api.py
│   └── test_cohort_engine.sql
│
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

## Local Development Setup

### Prerequisites

Install:

- Git
- Python 3.11+
- Docker Desktop
- Node.js / npm

### 1. Clone the Repository

```powershell
git clone <repository-url>
cd research-cohort-explorer
```

### 2. Start PostgreSQL

```powershell
docker compose up -d
```

Docker Compose creates the PostgreSQL container and initializes the database schema, reference data, analytical views, cohort tables, whitelist, audit infrastructure, and cohort execution function.

The development database uses:

```text
Database: research_cohort
User: research_admin
Port: 5432
```

### 3. Configure the Backend Environment

Create the local environment file from the provided template:

```powershell
Copy-Item .env.example .env
```

The development connection string is:

```text
DATABASE_URL=postgresql://research_admin:research_dev_password@localhost:5432/research_cohort
```

The `.env` file is excluded from Git.

### 4. Create the Python Environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install backend dependencies:

```powershell
pip install -r backend\requirements.txt
```

### 5. Synthetic Data

Synthetic-data generation scripts are organized by clinical domain under:

```text
synthetic-data/
```

Generated output is written under:

```text
synthetic-data/output/
```

and is excluded from version control.

The repository separates schema initialization from large synthetic dataset generation/loading so database infrastructure can be developed independently from generated test data.

### 6. Start the Backend

```powershell
python -m uvicorn backend.app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### 7. Install Frontend Dependencies

```powershell
npm --prefix frontend install
```

### 8. Start the Frontend

```powershell
npm --prefix frontend run dev
```

Frontend:

```text
http://localhost:5173
```

## Testing

### Backend API Tests

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_api.py -q
```

Current regression suite:

```text
24 passed
```

### Cohort Engine Database Tests

Run:

```powershell
Get-Content tests\test_cohort_engine.sql -Raw |
    docker exec -i research-cohort-postgres `
    psql -U research_admin -d research_cohort
```

The database regression suite validates:

1. expected Adult Type 2 Diabetes cohort membership
2. absence of duplicate cohort members
3. valid patient references
4. whitelist support for all stored criteria

### Frontend Lint

```powershell
npm --prefix frontend run lint
```

### Frontend Production Build

```powershell
npm --prefix frontend run build
```

## Data Quality and Validation

The project includes validation across multiple layers:

**Database integrity**

- primary and foreign key validation
- controlled reference codes
- temporal integrity checks
- unique membership constraints

**Synthetic data validation**

- unique research identifiers
- required demographic fields
- valid reference values
- cross-table patient references
- study-period validation

**Cohort validation**

- criterion whitelist validation
- value type validation
- supported exclusion validation
- execution readiness validation

**API validation**

- invalid cohort handling
- invalid criterion handling
- duplicate criterion-order handling
- pagination validation
- invalid date handling

Additional database validation details are documented in:

```text
docs/database-validation.md
```

## Design Principles

The project follows several design principles:

**Separation of concerns**  
Clinical storage, analytical views, cohort logic, API behavior, and frontend presentation are maintained as separate layers.

**Controlled query generation**  
User-configurable cohort criteria are translated into SQL only through explicitly supported metadata.

**Reproducibility**  
Synthetic data generation, database initialization, cohort execution, and regression testing are designed to produce repeatable development results.

**Data quality first**  
Validation occurs at the database, cohort-engine, API, and test layers rather than relying only on frontend checks.

**Synthetic by design**  
The application demonstrates clinical data engineering patterns without requiring real patient data.

## Current Scope

Cohort Engine v1 intentionally supports a controlled set of cohort operations rather than unrestricted query construction.

Current limitations include:

- no arbitrary Boolean grouping
- no user-defined SQL
- exclusions limited to diagnosis criteria
- no timestamp-based laboratory/procedure/encounter date criteria
- supported fields and operators limited to the whitelist
- local development authentication only; production authentication and authorization are outside the current scope

These constraints keep cohort execution predictable, testable, and safe while providing a foundation for future expansion.

## Future Enhancements

Potential future extensions include:

- richer Boolean cohort logic
- additional exclusion domains
- cohort version management
- additional clinical criteria
- cohort export
- saved cohort comparison
- execution history visualization
- authentication and authorization
- containerized backend/frontend deployment
- CI/CD regression testing

## Documentation

Additional project documentation is available in:

```text
docs/database-validation.md
docs/week-1-summary.md
```

## License

No license has currently been assigned to this project.
