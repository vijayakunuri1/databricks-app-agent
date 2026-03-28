# Databricks App Agent

A FastAPI REST API service deployed on Databricks Apps, exposing Databricks Unity Catalog over HTTP.

## Overview

This project provides a structured API layer on top of Databricks Unity Catalog, deployable as a [Databricks App](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html) using [Databricks Asset Bundles](https://docs.databricks.com/en/dev-tools/bundles/index.html).

## Endpoints

All routes are prefixed with `/api` (required for Databricks Apps OAuth2 protection).

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health/live` | Liveness check |
| GET | `/api/v1/health/ready` | Readiness check (verifies Databricks connectivity) |
| GET | `/api/v1/catalogs/` | List all catalogs |
| GET | `/api/v1/catalogs/{catalog}` | Get catalog details |
| GET | `/api/v1/catalogs/{catalog}/schemas/` | List schemas in a catalog |
| GET | `/api/v1/catalogs/{catalog}/schemas/{schema}` | Get schema details |
| GET | `/api/v1/catalogs/{catalog}/schemas/{schema}/tables/` | List tables in a schema |
| GET | `/api/v1/catalogs/{catalog}/schemas/{schema}/tables/{table}` | Get table details |
| POST | `/api/v1/query/` | Execute a SQL statement |

## Project Structure

```
├── app.py                  # FastAPI application entrypoint
├── app.yaml                # Databricks Apps runtime configuration
├── databricks.yml          # Databricks Asset Bundle (DAB) configuration
├── requirements.txt        # Runtime dependencies
├── api/
│   ├── router.py
│   └── v1/                 # Versioned route handlers
│       ├── health.py
│       ├── catalogs.py
│       ├── schemas.py
│       ├── tables.py
│       └── query.py
├── core/
│   ├── config.py           # Pydantic settings (env-var driven)
│   └── dependencies.py     # WorkspaceClient dependency injection
├── services/
│   ├── catalog_service.py  # Unity Catalog SDK wrapper
│   └── query_service.py    # SQL statement execution
└── tests/
    └── conftest.py
```

## Local Development

### Prerequisites

- Python 3.11+
- [Databricks CLI](https://docs.databricks.com/en/dev-tools/cli/index.html) v0.239+
- Access to a Databricks workspace with Unity Catalog enabled

### Option 1: Dev Container (recommended)

Requires [VS Code](https://code.visualstudio.com/) with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers), or [GitHub Codespaces](https://github.com/features/codespaces).

1. Open the repo in VS Code
2. Click **Reopen in Container** when prompted (or run `Dev Containers: Reopen in Container` from the command palette)
3. Fill in your credentials in the auto-generated `.env` file
4. Run the API: `uvicorn app:app --reload`

The container includes Python 3.11, all dependencies, and the Databricks VS Code extension pre-installed.

### Option 2: Virtual Environment

```bash
# Create venv, install all dependencies, and copy .env.example
bash scripts/setup_venv.sh

# Activate
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows

# Edit .env with your credentials, then run
uvicorn app:app --reload
```

The interactive API docs will be available at `http://localhost:8000/docs`.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABRICKS_HOST` | Workspace URL (e.g. `https://adb-xxx.azuredatabricks.net`) |
| `DATABRICKS_CLIENT_ID` | Service principal client ID |
| `DATABRICKS_CLIENT_SECRET` | Service principal client secret |
| `DATABRICKS_TOKEN` | Personal access token (alternative to SP credentials) |
| `DATABRICKS_WAREHOUSE_ID` | SQL Warehouse ID for query execution |
| `UC_CATALOG_NAME` | Default Unity Catalog name |

> When running on Databricks Apps, `DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`, and `DATABRICKS_CLIENT_SECRET` are injected automatically.

## Deployment

### Configure `databricks.yml`

Update the workspace hosts and warehouse IDs in `databricks.yml` for each target environment.

### Deploy via Asset Bundle

```bash
# Validate configuration
databricks bundle validate

# Deploy to dev (default)
databricks bundle deploy -t dev

# Deploy to production
databricks bundle deploy -t prod

# Or use the deploy script
bash scripts/deploy.sh dev
```

### Unity Catalog Permissions

The app's service principal requires the following grants on the target catalog:

```sql
GRANT USE CATALOG ON CATALOG <catalog> TO `<service-principal>`;
GRANT USE SCHEMA ON SCHEMA <catalog>.<schema> TO `<service-principal>`;
GRANT SELECT ON TABLE <catalog>.<schema>.<table> TO `<service-principal>`;
```

## Branch Protection

The `master` branch is protected with the following rules:

| Rule | Setting |
|------|---------|
| Required status checks | Lint & Format, Type Check, Tests |
| Require branches up to date | Yes |
| Required PR approvals | 1 |
| Dismiss stale reviews | Yes |
| Require conversation resolution | Yes |
| Enforce for admins | Yes |
| Allow force pushes | No |
| Allow deletions | No |
| Require linear history | Yes |

### Applying the rules

**Option A — GitHub Actions (recommended):**
Go to **Actions → Apply Branch Protection → Run workflow**.

**Option B — Script:**
```bash
export GITHUB_TOKEN=<your-pat-with-repo-scope>
bash scripts/setup_branch_protection.sh
```

## CI/CD

GitHub Actions workflows run automatically on push and pull requests.

### CI (`ci.yml`) — triggers on every PR and push to `master`

| Job | Tool | What it checks |
|-----|------|----------------|
| Lint & Format | `ruff` | Code style and import ordering |
| Type Check | `mypy` | Static type correctness |
| Tests | `pytest` | Unit tests with coverage report |

### CD (`cd.yml`) — triggers on push to `master`

| Stage | Trigger | Environment approval |
|-------|---------|----------------------|
| Dev | Automatic on push | None |
| Staging | After dev succeeds | Optional (configure in GitHub) |
| Prod | Manual via `workflow_dispatch` | Required (configure in GitHub) |

### Required GitHub Secrets

Configure these in **Settings → Secrets and variables → Actions**:

| Secret | Description |
|--------|-------------|
| `DATABRICKS_HOST_DEV` | Dev workspace URL |
| `DATABRICKS_HOST_STAGING` | Staging workspace URL |
| `DATABRICKS_HOST_PROD` | Prod workspace URL |
| `DATABRICKS_CLIENT_ID` | Service principal client ID (shared) |
| `DATABRICKS_CLIENT_SECRET` | Service principal client secret (shared) |

### Manual deployment to a specific target

You can trigger the CD workflow manually from the GitHub Actions tab and select `dev`, `staging`, or `prod` as the target.

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/) — REST API framework
- [Databricks SDK for Python](https://databricks-sdk-py.readthedocs.io/) — Unity Catalog & SQL execution
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) — Environment-based configuration
- [Uvicorn](https://www.uvicorn.org/) — ASGI server
