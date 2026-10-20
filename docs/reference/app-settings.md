# App settings reference

Settings that the backend, the workflow and the frontend read at runtime.
In Azure, the template sets them as app settings. Locally, you put them in
`.env` files. Deployment settings are in the
[configuration reference](configuration.md).

## Backend

Source: [`Settings.from_environment`](../../app/backend/backend/config.py).
The backend fails at startup if a required value is blank.

| Setting | Default | Meaning |
| --- | --- | --- |
| `AZURE_STORAGE_ACCOUNT` | required | Storage account name |
| `AZURE_STORAGE_CONTAINER` | required | Container for uploaded PDFs, normally `inputs` |
| `AZURE_COSMOSDB_ACCOUNT` | required | Cosmos DB account name |
| `AZURE_COSMOSDB_DATABASE` | required | Database, normally `starter` |
| `AZURE_COSMOSDB_CONTAINER` | required | Work-item container, normally `inputs` |
| `AZURE_STORAGE_ENDPOINT` | derived from the account | Blob endpoint override |
| `AZURE_COSMOSDB_ENDPOINT` | derived from the account | Cosmos DB endpoint override |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | unset | Telemetry. Treat it as sensitive. |
| `RUNNING_IN_PRODUCTION` | `false` | `true` disables `.env` loading and rejects `LOCAL_AUTH_SUBJECT` |
| `LOCAL_AUTH_SUBJECT` | unset | Local development only: act as this fixed user |
| `MAX_PDF_SIZE_MB` | `20` (1–100) | Upload limit in MiB. The request limit adds 1 MiB for form overhead. |
| `DEFAULT_PAGE_SIZE` | `20` (1–100) | Default list page size. It can't exceed `MAX_PAGE_SIZE`. |
| `MAX_PAGE_SIZE` | `100` (1–1000) | Largest page size a caller can request |
| `READINESS_CACHE_SECONDS` | `30` (1–300) | How long `/readyz` caches its result |
| `LOG_LEVEL` | `INFO` | Logging level |

- Booleans accept `1/true/yes/on` and `0/false/no/off`, in any case.
- The backend signs in to Azure with `DefaultAzureCredential`: its managed
  identity in Azure, and your `az login` session locally.
- It never calls the model itself.
- Raising `MAX_PDF_SIZE_MB` doesn't raise any limit in the workflow or the
  model.

### Which `.env` file is used

Unless `RUNNING_IN_PRODUCTION=true`, the backend loads the **first** of these
files that exists. Files are not merged:

1. `.env` in the current directory
2. `app/backend/.env`
3. `.env` at the repository root

Variables already set in the shell take priority. Start from
[`app/backend/.env.example`](../../app/backend/.env.example). Never commit a
`.env` file.

## Workflow (Logic App)

Source: [`app/agent/workflows/azure.parameters.json`](../../app/agent/workflows/azure.parameters.json).
The template sets these settings on the Logic App.

| App setting | Meaning |
| --- | --- |
| `AZURE_STORAGE_ACCOUNT` | Storage account |
| `AZURE_STORAGE_INPUT_CONTAINER` | Container watched for new PDFs |
| `AZURE_STORAGE_INSTRUCTIONS_CONTAINER` | Container with the prompts |
| `AZURE_STORAGE_SYSTEM_INSTRUCTIONS_FILE` | System prompt blob name |
| `AZURE_STORAGE_PROCESSING_INSTRUCTIONS_FILE` | Processing prompt blob name |
| `AZURE_COSMOS_ACCOUNT_NAME`, `AZURE_COSMOS_ACCOUNT_URI` | Cosmos DB account |
| `AZURE_COSMOS_DATABASE`, `AZURE_COSMOS_CONTAINER` | Work-item database and container |
| `AZURE_FOUNDRY_INFERENCE_ENDPOINT` | Foundry endpoint the workflow calls |
| `AZURE_FOUNDRY_DEPLOYMENT_NAME` | Model deployment the workflow calls |
| `WORKFLOWS_IDENTITY_RESOURCE_ID` | User-assigned identity for Cosmos DB and Foundry calls |

## Frontend

| Setting | Default | Meaning |
| --- | --- | --- |
| `VITE_LOCAL_AUTH_DISPLAY_NAME` | see [`app/frontend/.env.example`](../../app/frontend/.env.example) | Name shown for the local development user. Display only. |
| `VITE_PROXY_TARGET` | `http://127.0.0.1:8000` | Where the Vite dev server forwards `/api` calls. Export it in the shell; Vite doesn't read it from `.env`. |

Anything in a frontend build becomes public. Never put a secret in a `VITE_`
variable.

## Deployment outputs

Similar names are **not** interchangeable. This table shows how one value flows
from the deployment settings to each app.

| Deployment setting or resource | Backend setting / azd output | Logic App setting |
| --- | --- | --- |
| `AZURE_STORAGE_ACCOUNT` | `AZURE_STORAGE_ACCOUNT` | `AZURE_STORAGE_ACCOUNT` |
| `AZURE_STORAGE_INPUT_CONTAINER_NAME` | `AZURE_STORAGE_CONTAINER` | `AZURE_STORAGE_INPUT_CONTAINER` |
| `AZURE_STORAGE_INSTRUCTIONS_CONTAINER_NAME` | output `AZURE_STORAGE_INSTRUCTIONS_CONTAINER` | `AZURE_STORAGE_INSTRUCTIONS_CONTAINER` |
| `AZURE_STORAGE_SYSTEM_INSTRUCTIONS_FILE` | used by the deploy script | `AZURE_STORAGE_SYSTEM_INSTRUCTIONS_FILE` |
| `AZURE_STORAGE_PROCESSING_INSTRUCTIONS_FILE` | used by the deploy script | `AZURE_STORAGE_PROCESSING_INSTRUCTIONS_FILE` |
| Cosmos DB account | `AZURE_COSMOSDB_ACCOUNT` | `AZURE_COSMOS_ACCOUNT_NAME`, `AZURE_COSMOS_ACCOUNT_URI` |
| `AZURE_COSMOSDB_DATABASE` | `AZURE_COSMOSDB_DATABASE` | `AZURE_COSMOS_DATABASE` |
| `AZURE_COSMOSDB_CONTAINER` | `AZURE_COSMOSDB_CONTAINER` | `AZURE_COSMOS_CONTAINER` |
| Foundry endpoint | output `AZURE_FOUNDRY_INFERENCE_ENDPOINT` | `AZURE_FOUNDRY_INFERENCE_ENDPOINT` |
| `AZURE_FOUNDRY_MODEL_DEPLOYMENT` | output `AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME` | `AZURE_FOUNDRY_DEPLOYMENT_NAME` |

The deploy scripts also use `BACKEND_URI`, `AZURE_RESOURCE_GROUP`,
`AZURE_BACKEND_SERVICE_NAME`, `AZURE_LOGICAPP_SERVICE_NAME`,
`AZURE_CONTAINER_REGISTRY_NAME` and `AZURE_CONTAINER_REGISTRY_ENDPOINT`.

The template also sets some older OpenAI app settings on the backend. The
backend doesn't use them.
