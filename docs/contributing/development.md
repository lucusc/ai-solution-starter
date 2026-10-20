# Development

How to set up a machine for working on the code, and which checks to run
before a pull request. To deploy, use the
[quick starts](../quickstarts/README.md) instead.

## Tools

| Tool | Version | Needed for |
| --- | --- | --- |
| Git | Any current version | Everything |
| Python | 3.12 (the CI version) | Backend, workflow and script tests |
| Node.js and npm | 20.19 or later | Frontend |
| Docker | Any current engine | Building and probing the production container |
| Azure CLI | Current, with Bicep | Compiling Bicep locally (no sign-in needed) |
| Azure Developer CLI (azd) | Current | Deploying only |

Newer Python versions may work but aren't what CI tests. On Windows, use the
PowerShell versions of the scripts where they exist, and
`.venv\Scripts\python` instead of `.venv/bin/python`.

## Set up

```bash
git clone https://github.com/<owner>/<repo>.git
cd <repo>

python3 -m venv .venv
.venv/bin/python -m pip install -r app/backend/requirements-dev.txt

cd app/frontend
npm ci
cd ../..
```

The backend development requirements also install the authentication-hook
dependencies from `scripts/requirements.txt`, including the Microsoft Graph SDK.

None of the tests need Azure, an azd environment or real documents. To run
the app locally against a deployed environment, see
[develop against Azure](../quickstarts/develop-against-azure.md).

## Run the checks

`scripts/validate.sh` runs the same checks as CI:

```bash
./scripts/validate.sh application     # frontend, backend, workflow, container
./scripts/validate.sh infrastructure  # Bicep build, baseline checksum, shell syntax
./scripts/validate.sh repository      # tracked-file policy, sample PDF, whitespace
./scripts/validate.sh all             # all three
```

| Mode | What it runs | Needs |
| --- | --- | --- |
| `application` | `npm ci`; frontend lint, type check, tests and build; backend, workflow and script tests; ruff and mypy; workflow package check; builds the container and probes `/` and `/healthz` | `.venv`, Node.js, Docker |
| `infrastructure` | `az bicep build`, `verify_bicep_baseline.sh`, `bash -n scripts/*.sh` | Azure CLI with Bicep; internet access to restore modules |
| `repository` | `validate_repository.py`, writes `tests/sample-data/generated/hello-world.pdf`, `git diff --check` | `.venv` |

None of the modes sign in to Azure or change Azure resources. `application`
and `all` do install packages, write build output and build a container.

Run only what covers your change:

- **Frontend only:** `application`, or the frontend commands below.
- **Backend or workflow:** `application`.
- **Bicep or `azure.yaml`:** `infrastructure`, and follow
  [infrastructure change control](infra-change-control.md).
- **Shared contract** (API, work-item shape, settings): `all`.
- **Documentation only:** no checks needed. Preview the Markdown and check
  your links by hand.

### Individual commands

Frontend:

```bash
cd app/frontend
npm run lint
npm run typecheck
npm test -- --run
npm run build
cd ../..
```

Backend, workflow and scripts:

```bash
.venv/bin/python -m pytest app/backend/tests app/agent/tests scripts/tests
.venv/bin/python scripts/verify_logic_app_package.py
LINT_PATHS="app/backend scripts/generate_sample_pdf.py scripts/smoke_backend_azure.py
  scripts/validate_ai_service_config.py scripts/validate_repository.py scripts/tests"
.venv/bin/python -m ruff check $LINT_PATHS
.venv/bin/python -m ruff format --check $LINT_PATHS
.venv/bin/python -m mypy app/backend/backend
```

Container (build the frontend first):

```bash
docker build -f app/backend/Dockerfile -t ai-solution-starter:local app/backend
./scripts/probe_container.sh ai-solution-starter:local
```

Infrastructure:

```bash
python3 scripts/validate_ai_service_config.py
az bicep build --file infra/main.bicep --stdout > /dev/null
./scripts/verify_bicep_baseline.sh
```

### What the tests don't cover

The workflow tests check the Logic App package and its contract, but they
don't run the Logic Apps runtime. Connector sign-in, Cosmos DB ETag behavior,
model responses and real request size limits are only proven by deploying.
See [known limitations](../concepts/known-limitations.md#testing).

## Generated files

Keep these out of Git (they're already in `.gitignore`):

- `app/backend/static/` (frontend build output)
- `tests/sample-data/generated/*.pdf`
- `.venv/`, `app/frontend/node_modules/`
- `.azure/` (azd environments, which can contain secrets)
- Python and tool caches

## Common problems

| Problem | Fix |
| --- | --- |
| `ModuleNotFoundError` | Install and run with `.venv/bin/python`, not the system Python. |
| `/` returns 404 from the local backend | Build the frontend; the backend serves `app/backend/static/`. |
| Port 8000 or 5173 already in use | Stop the other server, or choose a different port and update `VITE_PROXY_TARGET`. |
| `verify_bicep_baseline.sh` fails | A protected Bicep file changed. See [infrastructure change control](infra-change-control.md). |
