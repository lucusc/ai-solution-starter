# Backend

Quart API for generic PDF work items.

## Setup

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r app/backend/requirements-dev.txt
```

## Development

Copy the local backend environment template and fill in values from the
approved azd development environment:

```bash
cp app/backend/.env.example app/backend/.env
```

Then run the backend:

```bash
PYTHONPATH=app/backend .venv/bin/hypercorn \
  --config app/backend/hypercorn.toml backend.main:app
```

The backend loads `app/backend/.env` (or a repository-root `.env`) only when
`RUNNING_IN_PRODUCTION` is not true. Exported environment variables always
take precedence over values in `.env`.

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
