# Local setup

## Clone

```bash
git clone https://github.com/lucusc/ai-solution-starter.git
cd ai-solution-starter
```

## Install backend dependencies

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r app/backend/requirements-dev.txt
```

## Install frontend dependencies

```bash
cd app/frontend
npm ci
cd ../..
```

## Generate a synthetic PDF

```bash
.venv/bin/python scripts/generate_sample_pdf.py \
  tests/sample-data/generated/hello-world.pdf
```

Use `--overwrite` only when intentionally replacing the generated file. The
generator prints the byte size and SHA-256. Its output is ignored by Git.

## Frontend development

Copy the safe example configuration:

```bash
cp app/frontend/.env.example app/frontend/.env.local
```

Start Vite:

```bash
cd app/frontend
npm run dev
```

Vite proxies API calls to `VITE_PROXY_TARGET`. The frontend test suite uses
test-only request fixtures and does not call Azure.

## Backend development

The real backend persistence adapters require Azure Storage and Cosmos DB.
Export values from an explicitly selected development environment before
starting the server. Never use a production environment for local experiments.

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

`LOCAL_AUTH_SUBJECT` is for local development only and is rejected when
`RUNNING_IN_PRODUCTION=true`.

## Default local workflow

The default no-Azure workflow is:

1. generate the synthetic PDF;
2. run backend tests with mocked Azure boundaries;
3. run frontend tests with request fixtures;
4. build frontend assets;
5. build the production container; and
6. run repository and infrastructure validation.

Use [validation](VALIDATION.md) for the complete command list.
