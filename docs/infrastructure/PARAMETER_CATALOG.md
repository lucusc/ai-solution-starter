# Infrastructure Parameter Catalog

`infra/main.parameters.json` is the executable parameter catalog. Values use
Azure Developer CLI substitution and can be supplied through an azd
environment or GitHub environment variables.

## Core deployment

| Environment value | Purpose | Default |
| --- | --- | --- |
| `AZURE_ENV_NAME` | Environment identifier and naming seed | Required |
| `AZURE_LOCATION` | Primary Azure location | Required |
| `AZURE_RESOURCE_GROUP` | Primary resource group name | Generated |
| `CREATE_RESOURCE_GROUP` | Create or reuse the primary resource group | `true` |
| `ASSIGN_ROLES` | Create user and service identity role assignments | `true` |
| `AZURE_PRINCIPAL_ID` | User or deployment principal receiving roles | Empty |

## Hosting and registry

| Environment value group | Purpose |
| --- | --- |
| `AZURE_APP_SERVICE*` | Backend Web App, plan, ASE, and SKU configuration |
| `AZURE_LOGIC_APP_SERVICE*` | Logic App, plan, ASE, and SKU configuration |
| `AZURE_CONTAINER_REGISTRY` | Optional explicit registry name |
| `ALLOWED_ORIGIN` | Additional CORS origins |

## Storage and database

| Environment value group | Purpose |
| --- | --- |
| `AZURE_STORAGE_ACCOUNT`, `AZURE_STORAGE_RESOURCE_GROUP`, `AZURE_STORAGE_LOCATION`, `AZURE_STORAGE_SKU` | Primary Storage placement and SKU |
| `AZURE_STORAGE_CONTAINER_NAME` | General content container; default `content` |
| `AZURE_STORAGE_TOKEN_CONTAINER_NAME` | Token container; default `tokens` |
| `AZURE_STORAGE_INSTRUCTIONS_CONTAINER_NAME` | Instruction container; default `instructions` |
| `AZURE_STORAGE_INPUT_CONTAINER_NAME` | Input container; default `inputs` |
| `AZURE_STORAGE_SYSTEM_INSTRUCTIONS_FILE` | System instruction filename; default `system.md` |
| `AZURE_STORAGE_PROCESSING_INSTRUCTIONS_FILE` | Processing instruction filename; default `processing.md` |
| `AZURE_STORAGE_EVALUATION_INSTRUCTIONS_FILE` | Evaluation instruction filename; default `evaluation.md` |
| `AZURE_COSMOSDB_ACCOUNT`, `AZURE_COSMOSDB_RESOURCE_GROUP`, `AZURE_COSMOSDB_LOCATION` | Cosmos DB placement |
| `AZURE_COSMOSDB_DATABASE` | Database name; default `starter` |
| `AZURE_COSMOSDB_CONTAINER` | Container name; default `inputs` |
| `AZURE_COSMOSDB_SKU` | `free`, `provisioned`, or `serverless`; default `serverless` |
| `AZURE_COSMOSDB_THROUGHPUT` | Provisioned throughput; default `400` |
| `AZURE_COSMOSDB_API_VERSION` | Application-facing API version; default `2023-10-15` |

## Azure OpenAI

| Environment value group | Purpose |
| --- | --- |
| `OPENAI_HOST` | `azure`, `azure_custom`, or `openai` |
| `DEPLOY_AZURE_OPENAI` | Create a new Azure OpenAI account |
| `DEPLOY_AZURE_OPEN_MODELS` | Deploy models into an approved existing account |
| `AZURE_OPENAI_SERVICE`, `AZURE_OPENAI_RESOURCE_GROUP`, `AZURE_OPENAI_LOCATION`, `AZURE_OPENAI_SERVICE_SKU` | Azure OpenAI account placement and SKU |
| `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_CUSTOM_URL`, `AZURE_OPENAI_API_KEY` | Azure OpenAI client overrides |
| `AZURE_OPENAI_CHATGPT_*` | Chat model, deployment, version, SKU, and capacity |
| `AZURE_OPENAI_EMB_*` | Embedding model, dimensions, deployment, version, SKU, and capacity |
| `AZURE_OPENAI_GPT4V_*` | Vision model, deployment, version, SKU, and capacity |
| `AZURE_OPENAI_EVAL_*` | Optional evaluation model, deployment, version, SKU, and capacity |
| `AZURE_USE_GPT4V`, `AZURE_USE_EVAL` | Enable optional deployments |
| `OPENAI_API_KEY`, `OPENAI_API_ORGANIZATION` | Non-Azure OpenAI configuration |

## Optional AI services

Both services default to `none`. Values are case-sensitive.

| Environment value | Purpose | Default |
| --- | --- | --- |
| `USE_FOUNDRY` | `new`, `existing`, or `none` Foundry selection | `none` |
| `AZURE_FOUNDRY_ACCOUNT` | New Foundry account name; generated when empty | Empty |
| `AZURE_FOUNDRY_PROJECT` | Project to create or resolve | `starter` |
| `AZURE_FOUNDRY_RESOURCE_GROUP` | New or existing account resource group | Primary resource group |
| `AZURE_FOUNDRY_LOCATION` | New account/project location | Primary location |
| `AZURE_FOUNDRY_SKU` | New Foundry account SKU | `S0` |
| `EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID` | Full existing `AIServices` account ID | Empty |
| `EXISTING_FOUNDRY_PROJECT_RESOURCE_ID` | Optional full existing project ID | Empty |
| `FOUNDRY_CONNECT_BASE_OPENAI` | Add an AAD project connection to baseline Azure OpenAI | `false` |
| `USE_DOCUMENT_INTELLIGENCE` | `new`, `existing`, or `none` selection | `none` |
| `AZURE_DOCUMENT_INTELLIGENCE_ACCOUNT` | New account name; generated when empty | Empty |
| `AZURE_DOCUMENT_INTELLIGENCE_RESOURCE_GROUP` | New or existing account resource group | Primary resource group |
| `AZURE_DOCUMENT_INTELLIGENCE_LOCATION` | New account location | Primary location |
| `AZURE_DOCUMENT_INTELLIGENCE_SKU` | New account SKU | `S0` |
| `EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID` | Full existing `FormRecognizer` account ID | Empty |
| `CONFIGURE_EXISTING_AI_SERVICES` | Permit module-owned RBAC, diagnostics, and private endpoints on selected existing accounts | `false` |

See [optional AI services](AI_SERVICES.md) for mode validation, existing
resource behavior, and usage examples.

## Authentication

| Environment value | Purpose |
| --- | --- |
| `AZURE_AUTH_TENANT_ID` | Optional authentication tenant override |
| `AZURE_SERVER_APP_ID`, `AZURE_SERVER_APP_SECRET` | Server application registration |
| `AZURE_CLIENT_APP_ID`, `AZURE_CLIENT_APP_SECRET` | SPA application registration |
| `AZURE_DISABLE_APP_SERVICES_AUTHENTICATION` | Force application-managed authentication |
| `AZURE_ENABLE_UNAUTHENTICATED_ACCESS` | Allow anonymous App Service access |
| `AZURE_BYPASS_AUTHENTICATION_SETUP` | Skip application registration hooks |

## Networking

| Environment value group | Purpose |
| --- | --- |
| `AZURE_PUBLIC_NETWORK_ACCESS` | Default public access state; default `Disabled` |
| `AZURE_ALLOWED_IPS` | Comma-separated public IP allowlist |
| `AZURE_NETWORK_BYPASS` | Trusted Azure service bypass |
| `AZURE_USE_PRIVATE_ENDPOINT` | Enable private networking |
| `AZURE_VNET_ADDRESS_PREFIX` | Generated VNet address range |
| `AZURE_SUBNET_*` | Backend, application-integration, and Logic App subnet names and ranges |
| `USE_EXISTING_VNET`, `EXISTING_VNET_*` | Integrate with an existing VNet |
| `USE_EXISTING_PRIVATE_DNS_ZONES`, `PRIVATE_DNS_ZONES_*` | Reuse central private DNS zones |
| `LINK_PRIVATE_ENDPOINT_TO_PRIVATE_DNS_ZONE` | Link reused zones to the selected VNet |
| `SKIP_PRIVATE_DNS_ZONES` | Skip private DNS creation and linking |

## Monitoring and pipeline context

| Environment value group | Purpose |
| --- | --- |
| `AZURE_USE_APPLICATION_INSIGHTS` | Enable monitoring resources |
| `AZURE_APPLICATION_INSIGHTS`, `AZURE_LOG_ANALYTICS` | Optional explicit resource names |
| `GITHUB_ACTIONS`, `TF_BUILD` | Select user or service-principal role assignment type |

Secure parameters must be stored as azd secrets or GitHub environment secrets,
not committed values.
