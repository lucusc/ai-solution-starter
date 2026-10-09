# Backend

Quart API for generic PDF work items.

## Setup

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r app/backend/requirements-dev.txt
```

## Development

Provide the Azure settings from an azd environment and a synthetic local
identity:

```bash
export LOCAL_AUTH_SUBJECT=local-developer
export AZURE_STORAGE_ACCOUNT=<storage-account>
export AZURE_STORAGE_CONTAINER=inputs
export AZURE_COSMOSDB_ACCOUNT=<cosmos-account>
export AZURE_COSMOSDB_DATABASE=starter
export AZURE_COSMOSDB_CONTAINER=inputs

PYTHONPATH=app/backend .venv/bin/hypercorn \
  --config app/backend/hypercorn.toml backend.main:app
```

`LOCAL_AUTH_SUBJECT` is rejected when `RUNNING_IN_PRODUCTION=true`.

## Validation

```bash
.venv/bin/python -m pytest
.venv/bin/python -m ruff check app/backend scripts/smoke_backend_azure.py
.venv/bin/python -m ruff format --check app/backend scripts/smoke_backend_azure.py
.venv/bin/python -m mypy app/backend/backend
cd app/frontend && npm ci && npm run build && cd ../..
docker build -f app/backend/Dockerfile app/backend
./scripts/verify_bicep_baseline.sh
```

The optional live-Azure smoke test requires an explicitly selected azd
environment and a matching confirmation:

```bash
.venv/bin/python scripts/smoke_backend_azure.py \
  --environment <environment-name> \
  --confirm-environment <environment-name>
```

It creates only synthetic PDF records, verifies idempotency, filtering, and
continuation paging, and removes the temporary Blob and Cosmos data.
