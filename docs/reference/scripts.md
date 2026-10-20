# Scripts reference

Run these from the repository root.

Commands marked **Azure** change Azure resources. Run them only against the
environment you mean to change, and check which azd environment is selected
first with `azd env list`.

## Deploying

| Command | What it does |
| --- | --- |
| `./scripts/deploy_app.sh backend` | **Azure.** Builds the frontend, then builds the image in the registry and updates the web app. |
| `./scripts/deploy_app.sh agent` | **Azure.** Uploads the workflow prompts and zip-deploys the Logic App. |
| `./scripts/deploy_app.sh all` | **Azure.** Both of the above. |
| `./scripts/allow_my_ip_address.sh` | **Azure.** Allows your IP (and the Azure portal) through the Storage and Cosmos DB firewalls, and gives you data roles. The changes stay until you reverse them. |
| `./scripts/update_acr_network_access.sh <rg> <acr> [enabled\|disabled]` | **Azure.** Turns registry public access on or off. Defaults to `disabled`. |

`deploy_app.sh` needs Bash, the Azure CLI, Node.js, `zip` and GNU `mktemp`.
It reads resource names from the selected azd environment. There is no
automatic rollback.

See [Access a private deployment](../how-to/access-a-private-deployment.md)
for when to use the access scripts.

## azd hooks

`azd provision` runs these hooks automatically. You don't normally run them
yourself.

| Script | When | What it does |
| --- | --- | --- |
| `auth_init.sh` / `.ps1` → `auth_init.py` | Before provisioning | Validates the AI settings. If `AZURE_USE_AUTHENTICATION=true`, creates or reuses the sign-in app registrations and stores their IDs and secrets in the azd environment. |
| `auth_update.sh` / `.ps1` → `auth_update.py` | After provisioning | Adds the site and localhost redirect URIs to the sign-in apps |
| `auth_common.py` | — | Shared code for the hooks |
| `load_python_env.sh` / `.ps1` | Called by the hooks | Creates `.venv` and installs `scripts/requirements.txt` |
| `load_azd_env.py` | Called by the hooks | Loads the azd environment into a Python process |

Set `AZURE_BYPASS_AUTHENTICATION_SETUP=true` to skip the sign-in steps. See
[Configure authentication](../how-to/configure-authentication.md).

## Checking

| Command | What it checks | Needs |
| --- | --- | --- |
| `./scripts/validate.sh application` | Frontend lint, types, tests and build; backend, workflow and script tests; ruff; mypy; Docker build and probe | `.venv`, Node.js, Docker |
| `./scripts/validate.sh infrastructure` | AI settings, Bicep build, Bicep baseline checksums and shell syntax | Azure CLI with Bicep. Doesn't touch Azure resources. |
| `./scripts/validate.sh repository` | Required files and file policy, sample PDF generation, whitespace | `.venv` |
| `./scripts/validate.sh all` | All of the above | All of the above |
| `python3 scripts/validate_ai_service_config.py` | AI service settings. Add `--from-azd` to read the selected environment, and `--check-azure` to look up existing resources. | Azure sign-in with `--check-azure` |
| `python3 scripts/verify_logic_app_package.py` | Workflow package structure | — |
| `./scripts/verify_bicep_baseline.sh` | Bicep files match the protected checksum manifest | — |
| `./scripts/probe_container.sh [image]` | A built image serves `/healthz` and the frontend | Docker |

[Development](../contributing/development.md) explains when to run which
check.

## Test data and smoke tests

| Command | What it does |
| --- | --- |
| `.venv/bin/python scripts/generate_sample_pdf.py <out.pdf> [--overwrite]` | Writes a small synthetic PDF. See the [sample data guide](../../tests/sample-data/README.md). |
| `.venv/bin/python scripts/smoke_backend_azure.py --environment <name> --confirm-environment <name>` | **Azure.** Writes and then removes a test Blob and Cosmos DB record using the backend code. It doesn't test the web app or the model. |

## Used by GitHub Actions

| Script | What it does |
| --- | --- |
| `export_azd_values.ps1 -FilePath <path> [-Append]` | Writes **every** azd environment value, including secrets, to a file for the workflow. See [known limitations](../concepts/known-limitations.md#security). |

Never paste script output that contains environment values, secrets or
document text into issues or logs.
