# Validation

## Repository-root commands

```bash
./scripts/validate.sh application
./scripts/validate.sh infrastructure
./scripts/validate.sh repository
./scripts/validate.sh all
```

`application` expects `.venv` to contain backend development dependencies. It
runs npm restore, frontend lint/types/tests/build, backend tests/lint/types,
the production container build, and probes `/` and `/healthz`.

`infrastructure` compiles Bicep, verifies the immutable checksum manifest, and
checks POSIX shell syntax. It does not authenticate to Azure or provision
resources.

`repository` validates required public files, relative Markdown links, tracked
artifact policy, the sample generator, and diff whitespace.

`all` runs all three areas.

## Individual commands

### Frontend

```bash
cd app/frontend
npm ci
npm run lint
npm run typecheck
npm test -- --run
npm run build
cd ../..
```

### Backend

```bash
.venv/bin/python -m pytest
.venv/bin/python -m ruff check \
  app/backend \
  scripts/generate_sample_pdf.py \
  scripts/smoke_backend_azure.py \
  scripts/validate_repository.py
.venv/bin/python -m ruff format --check \
  app/backend \
  scripts/generate_sample_pdf.py \
  scripts/smoke_backend_azure.py \
  scripts/validate_repository.py
.venv/bin/python -m mypy app/backend/backend
```

### Container

Build the frontend first, then:

```bash
docker build \
  -f app/backend/Dockerfile \
  -t ai-solution-starter:validation \
  app/backend
./scripts/probe_container.sh ai-solution-starter:validation
```

### Infrastructure

```bash
az bicep build --file infra/main.bicep --stdout > /dev/null
./scripts/verify_bicep_baseline.sh
bash -n scripts/*.sh
```

### Repository

```bash
.venv/bin/python scripts/validate_repository.py
git diff --check
```

## Logic App status

The Logic App business workflow is not implemented. Phase 4 will add package
validation, which must then become part of `validate.sh all` and Application
CI. Phase 5 does not report a skipped workflow check as a passed workflow.

## Generated files

These paths are expected to remain untracked:

- `app/backend/static/`
- `tests/sample-data/generated/*.pdf`
- `.venv/`
- `app/frontend/node_modules/`
- `.azure/`
- Python and tool caches
