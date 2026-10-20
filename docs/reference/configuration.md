# Configuration reference

Every deployment setting, with its default. Set a value in the selected azd
environment, then provision:

```bash
azd env set NAME value
azd provision
```

[`infra/main.parameters.json`](../../infra/main.parameters.json) maps these
names to Bicep parameters. The mapping is the source of truth. A setting
written as `${NAME=default}` there uses that default when it isn't set.

> **Secrets.** `AZURE_SERVER_APP_SECRET`, `AZURE_CLIENT_APP_SECRET`,
> `AZURE_OPENAI_API_KEY` and `OPENAI_API_KEY` are secrets. Keep them in the
> azd environment or GitHub environment *secrets*. Never commit them or store
> them as GitHub *variables*.

For the backend and workflow runtime settings that the template writes into
the apps, see [app settings](app-settings.md).

## Most common settings

| Setting | Default | What it does |
| --- | --- | --- |
| `AZURE_ENV_NAME` | set by `azd env new` | Environment name, used in resource names |
| `AZURE_LOCATION` | prompted | Azure region |
| `AZURE_USE_AUTHENTICATION` | not set | `true` creates the sign-in apps during provisioning. Needed for a working site. |
| `AZURE_ALLOWED_IPS` | empty | Public IPs allowed through the firewalls, comma-separated |
| `AZURE_USE_PRIVATE_ENDPOINT` | `true` | Private endpoints and a VNet |
| `AZURE_PUBLIC_NETWORK_ACCESS` | `Disabled` | `Enabled` or `Disabled` |
| `USE_EXISTING_VNET` | `false` | Put private endpoints into your own VNet |
| `USE_FOUNDRY` | `new` | `new`, `existing` or `none` |
| `AZURE_FOUNDRY_MODEL_NAME` | `gpt-4o` | Model the workflow calls |
| `AZURE_FOUNDRY_MODEL_CAPACITY` | `30` | Model capacity, in thousands of tokens per minute |
| `USE_DOCUMENT_INTELLIGENCE` | `none` | `new`, `existing` or `none` |
| `USE_OPENAI` | `none` | Standalone Azure OpenAI: `new`, `existing` or `none` |
| `AZURE_APP_SERVICE_SKU` | `B1` | Web app plan size |
| `ASSIGN_ROLES` | `true` | Create the role assignments |
| `AZURE_USE_APPLICATION_INSIGHTS` | `true` | Monitoring |

Before provisioning, `scripts/validate_ai_service_config.py` checks the AI
settings. It runs automatically in the `preprovision` hook.

## Deployment

| Setting | Default | Description |
| --- | --- | --- |
| `AZURE_ENV_NAME` | required | Environment name and naming seed |
| `AZURE_LOCATION` | required | Primary region |
| `CREATE_RESOURCE_GROUP` | `true` | Create the primary resource group |
| `AZURE_RESOURCE_GROUP` | `rg-<env-name>` | Primary resource group name |

Most resource names include a token derived from the subscription,
environment name and region. Set the name settings below only to override
that token.

## Hosting

| Setting | Default | Description |
| --- | --- | --- |
| `AZURE_APP_SERVICE` | generated | Backend web app name |
| `AZURE_APP_SERVICE_PLAN` | generated | Backend plan name |
| `AZURE_APP_SERVICE_SKU` | `B1` | Backend plan SKU |
| `AZURE_APP_SERVICE_SKU_TIER` | `Basic` | Backend plan tier (must match the SKU) |
| `AZURE_APP_SERVICE_PLAN_ASE_ID` | empty | App Service Environment plan resource ID |
| `AZURE_LOGIC_APP_SERVICE` | generated | Logic App name |
| `AZURE_LOGIC_APP_SERVICE_PLAN` | generated | Logic App plan name |
| `AZURE_LOGIC_APP_SERVICE_SKU` | `WS1` | Logic App plan SKU |
| `AZURE_LOGIC_APP_SERVICE_SKU_TIER` | `WorkflowStandard` | Logic App plan tier |
| `AZURE_LOGIC_APP_SERVICE_ASE_ID` | empty | App Service Environment ID for the Logic App |
| `AZURE_CONTAINER_REGISTRY` | generated | Registry name. The SKU is always Premium. |
| `ALLOWED_ORIGIN` | empty | Extra CORS origins, `;`-separated, each `https://` with no trailing `/` |

## Storage

| Setting | Default | Description |
| --- | --- | --- |
| `AZURE_STORAGE_ACCOUNT` | generated | Account name |
| `AZURE_STORAGE_RESOURCE_GROUP` | primary group | Place Storage in another resource group |
| `AZURE_STORAGE_LOCATION` | primary region | Storage region |
| `AZURE_STORAGE_SKU` | `Standard_LRS` | Redundancy |
| `AZURE_STORAGE_CONTAINER_NAME` | `content` | General content container |
| `AZURE_STORAGE_TOKEN_CONTAINER_NAME` | `tokens` | Token container |
| `AZURE_STORAGE_INSTRUCTIONS_CONTAINER_NAME` | `instructions` | Workflow prompt container |
| `AZURE_STORAGE_INPUT_CONTAINER_NAME` | `inputs` | Uploaded PDF container |
| `AZURE_STORAGE_SYSTEM_INSTRUCTIONS_FILE` | `system.md` | System prompt file name |
| `AZURE_STORAGE_PROCESSING_INSTRUCTIONS_FILE` | `processing.md` | Processing prompt file name |
| `AZURE_STORAGE_EVALUATION_INSTRUCTIONS_FILE` | `evaluation.md` | Evaluation prompt file name (not used by the sample) |

## Cosmos DB

| Setting | Default | Description |
| --- | --- | --- |
| `AZURE_COSMOSDB_ACCOUNT` | generated | Account name |
| `AZURE_COSMOSDB_RESOURCE_GROUP` | primary group | Place Cosmos DB in another resource group |
| `AZURE_COSMOSDB_LOCATION` | primary region | Cosmos DB region |
| `AZURE_COSMOSDB_SKU` | `serverless` | `serverless`, `provisioned` or `free` |
| `AZURE_COSMOSDB_THROUGHPUT` | `400` | RU/s, for provisioned mode only |
| `AZURE_COSMOSDB_DATABASE` | `starter` | Database name |
| `AZURE_COSMOSDB_CONTAINER` | `inputs` | Work-item container (partition key `/created_at`) |
| `AZURE_COSMOSDB_API_VERSION` | `2023-10-15` | Data-plane API version used by the workflow |

## Foundry

The workflow calls the Foundry model deployment. See
[Choose AI services and models](../how-to/choose-ai-services-and-models.md).

| Setting | Default | Description |
| --- | --- | --- |
| `USE_FOUNDRY` | `new` | `new` creates an account, project and model deployment. `existing` reuses an account. `none` turns Foundry off, and the workflow can't process documents. |
| `AZURE_FOUNDRY_ACCOUNT` | generated | Account name (`new`) |
| `AZURE_FOUNDRY_RESOURCE_GROUP` | primary group | Account resource group (`new`) |
| `AZURE_FOUNDRY_LOCATION` | primary region | Account region (`new`). Choose a region with model quota. |
| `AZURE_FOUNDRY_SKU` | `S0` | Account SKU (`new`) |
| `AZURE_FOUNDRY_PROJECT` | `starter` | Project name |
| `EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID` | empty | Required for `existing` |
| `EXISTING_FOUNDRY_PROJECT_RESOURCE_ID` | empty | Optional for `existing`. Otherwise the project is found by name. |
| `AZURE_FOUNDRY_MODEL_DEPLOYMENT` | `starter-gpt-4o` | Deployment name. For `existing`, it must already exist unless `DEPLOY_FOUNDRY_MODEL_EXISTING=true`. |
| `AZURE_FOUNDRY_MODEL_NAME` | `gpt-4o` | Model. It must support the Responses API, PDF input and structured outputs. |
| `AZURE_FOUNDRY_MODEL_VERSION` | `2024-11-20` | Model version |
| `AZURE_FOUNDRY_MODEL_SKU` | `Standard` | Deployment type, for example `Standard` or `GlobalStandard` |
| `AZURE_FOUNDRY_MODEL_CAPACITY` | `30` | Capacity units. Subject to quota. |
| `DEPLOY_FOUNDRY_MODEL_EXISTING` | `false` | Allow creating or updating the model deployment in an existing account |
| `FOUNDRY_CONNECT_BASE_OPENAI` | `false` | Connect the project to standalone Azure OpenAI. Not needed by the sample. |

## Document Intelligence

| Setting | Default | Description |
| --- | --- | --- |
| `USE_DOCUMENT_INTELLIGENCE` | `none` | `new`, `existing` or `none` |
| `AZURE_DOCUMENT_INTELLIGENCE_ACCOUNT` | generated | Account name (`new`) |
| `AZURE_DOCUMENT_INTELLIGENCE_RESOURCE_GROUP` | primary group | Resource group (`new`) |
| `AZURE_DOCUMENT_INTELLIGENCE_LOCATION` | primary region | Region (`new`) |
| `AZURE_DOCUMENT_INTELLIGENCE_SKU` | `S0` | SKU (`new`) |
| `EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID` | empty | Required for `existing` |

## Existing AI services

| Setting | Default | Description |
| --- | --- | --- |
| `CONFIGURE_EXISTING_AI_SERVICES` | `false` | Let the template add role assignments, diagnostics and private endpoints to existing Foundry, Document Intelligence and OpenAI accounts. You need permission on those accounts. |

## Standalone Azure OpenAI

Optional and not used by the sample workflow. Most of these settings
come from the template this starter was based on. Leave them unset unless you
build features that call Azure OpenAI directly.

| Setting | Default | Description |
| --- | --- | --- |
| `USE_OPENAI` | `none` | `new`, `existing` or `none` |
| `EXISTING_OPENAI_RESOURCE_ID` | empty | Required for `existing` (an `OpenAI` or `AIServices` account) |
| `DEPLOY_OPENAI_MODELS_EXISTING` | `false` | Allow deploying models into an existing account |
| `OPENAI_HOST` | `azure` | `azure`, `azure_custom` or `openai` |
| `AZURE_OPENAI_SERVICE` | generated | Account name (`new`) |
| `AZURE_OPENAI_RESOURCE_GROUP` | primary group | Resource group (`new`) |
| `AZURE_OPENAI_LOCATION` | empty | Required for `new`. One of `canadaeast`, `eastus`, `eastus2`, `francecentral`, `switzerlandnorth`, `uksouth`, `japaneast`, `northcentralus`, `australiaeast` or `swedencentral`. |
| `AZURE_OPENAI_SERVICE_SKU` | `S0` | Account SKU |
| `AZURE_OPENAI_API_VERSION` | `2024-10-21` | API version |
| `AZURE_OPENAI_CUSTOM_URL` | empty | Required when `OPENAI_HOST=azure_custom` |
| `AZURE_OPENAI_DISABLE_KEYS` | `true` | Disable key authentication |
| `AZURE_OPENAI_API_KEY` | empty | **Secret.** Only for key authentication. |
| `OPENAI_API_KEY` | empty | **Secret.** Required when `OPENAI_HOST=openai`. |
| `OPENAI_API_ORGANIZATION` | empty | OpenAI organization |
| `AZURE_USE_GPT4V` | `true` | Create the vision deployment |
| `AZURE_USE_EVAL` | `false` | Create the evaluation deployment |

Model deployment overrides follow one pattern. Blank values use the template
defaults.

| Deployment | Model and name | Version, SKU and capacity |
| --- | --- | --- |
| Chat | `AZURE_OPENAI_CHATGPT_MODEL`, `AZURE_OPENAI_CHATGPT_DEPLOYMENT` | `AZURE_OPENAI_CHATGPT_DEPLOYMENT_VERSION`, `AZURE_OPENAI_CHATGPT_DEPLOYMENT_SKU`, `AZURE_OPENAI_CHATGPT_DEPLOYMENT_CAPACITY` |
| Embedding | `AZURE_OPENAI_EMB_MODEL_NAME`, `AZURE_OPENAI_EMB_DEPLOYMENT`, `AZURE_OPENAI_EMB_DIMENSIONS` | `AZURE_OPENAI_EMB_DEPLOYMENT_VERSION`, `AZURE_OPENAI_EMB_DEPLOYMENT_SKU`, `AZURE_OPENAI_EMB_DEPLOYMENT_CAPACITY` |
| Vision | `AZURE_OPENAI_GPT4V_MODEL_NAME`, `AZURE_OPENAI_GPT4V_DEPLOYMENT` | `AZURE_OPENAI_GPT4V_MODEL_VERSION`, `AZURE_OPENAI_GPT4V_DEPLOYMENT_SKU`, `AZURE_OPENAI_GPT4V_DEPLOYMENT_CAPACITY` |
| Evaluation | `AZURE_OPENAI_EVAL_MODEL_NAME`, `AZURE_OPENAI_EVAL_DEPLOYMENT` | `AZURE_OPENAI_EVAL_MODEL_VERSION`, `AZURE_OPENAI_EVAL_DEPLOYMENT_SKU`, `AZURE_OPENAI_EVAL_DEPLOYMENT_CAPACITY` |

## Sign-in and access

| Setting | Default | Description |
| --- | --- | --- |
| `AZURE_USE_AUTHENTICATION` | not set | `true` lets the hooks create and update the sign-in apps. Read by the hooks only. |
| `AZURE_BYPASS_AUTHENTICATION_SETUP` | not set | `true` skips the hooks. Supply the app IDs and secrets yourself. |
| `AZURE_AUTH_TENANT_ID` | subscription tenant | Tenant users sign in to |
| `AZURE_SERVER_APP_ID` | set by hook | API app registration ID |
| `AZURE_SERVER_APP_SECRET` | set by hook | **Secret.** API app secret. |
| `AZURE_CLIENT_APP_ID` | set by hook | Browser app registration ID |
| `AZURE_CLIENT_APP_SECRET` | set by hook | **Secret.** Browser app secret. |
| `AZURE_ENABLE_UNAUTHENTICATED_ACCESS` | `false` | Let anonymous users load pages. The API still requires sign-in. |
| `AZURE_DISABLE_APP_SERVICES_AUTHENTICATION` | `false` | Turn off App Service authentication. Unsafe with this backend. |
| `AZURE_ENFORCE_ACCESS_CONTROL` | not set | Legacy hook check. Has no effect on the deployment. |
| `ASSIGN_ROLES` | `true` | Create role assignments |
| `AZURE_PRINCIPAL_ID` | set by azd | Who gets the deployer roles |

See [Configure authentication](../how-to/configure-authentication.md) and
[Identity and access](../concepts/identity-and-access.md).

## Networking

See [Networking](../concepts/networking.md) for how these work together.

| Setting | Default | Description |
| --- | --- | --- |
| `AZURE_USE_PRIVATE_ENDPOINT` | `true` | Create the VNet, private endpoints and DNS |
| `AZURE_PUBLIC_NETWORK_ACCESS` | `Disabled` | Public access to services |
| `AZURE_ALLOWED_IPS` | empty | Comma-separated IPs or CIDRs. Non-empty values turn on restricted public access. |
| `AZURE_NETWORK_BYPASS` | `AzureServices` | Trusted-service bypass for Storage and Foundry |
| `AZURE_VNET_ADDRESS_PREFIX` | `10.0.0.0/16` | Generated VNet range |
| `AZURE_SUBNET_BACKEND_NAME` | `backend-subnet` | Generated private endpoint subnet |
| `AZURE_SUBNET_BACKEND_ADDRESS_PREFIX` | `10.0.1.0/24` | Its range |
| `AZURE_SUBNET_APP_INT_NAME` | `app-int-subnet` | Generated web app integration subnet |
| `AZURE_SUBNET_APP_INT_ADDRESS_PREFIX` | `10.0.2.0/24` | Its range |
| `AZURE_SUBNET_LOGIC_INT_NAME` | `logic-int-subnet` | Generated Logic App integration subnet |
| `AZURE_SUBNET_LOGIC_INT_ADDRESS_PREFIX` | `10.0.3.0/24` | Its range |
| `USE_EXISTING_VNET` | `false` | Use your own VNet |
| `EXISTING_VNET_SUBSCRIPTION_ID` | empty | Its subscription |
| `EXISTING_VNET_RESOURCE_GROUP_NAME` | empty | Its resource group |
| `EXISTING_VNET_NAME` | empty | Its name |
| `EXISTING_BACKEND_SUBNET_NAME` | empty | Private endpoint subnet |
| `EXISTING_APP_INT_SUBNET_NAME` | empty | Web app integration subnet (delegated to `Microsoft.Web/serverFarms`) |
| `EXISTING_LOGIC_INT_SUBNET_NAME` | empty | Logic App integration subnet (delegated to `Microsoft.Web/serverFarms`) |
| `USE_EXISTING_PRIVATE_DNS_ZONES` | `false` | Reuse central private DNS zones |
| `PRIVATE_DNS_ZONES_SUBSCRIPTION_ID` | empty | Their subscription |
| `PRIVATE_DNS_ZONES_RESOURCE_GROUP_NAME` | empty | Their resource group |
| `LINK_PRIVATE_ENDPOINT_TO_PRIVATE_DNS_ZONE` | `true` | Link reused zones to the VNet |
| `SKIP_PRIVATE_DNS_ZONES` | `false` | Don't create or link any zones |

## Monitoring

| Setting | Default | Description |
| --- | --- | --- |
| `AZURE_USE_APPLICATION_INSIGHTS` | `true` | Application Insights, Log Analytics and the dashboard |
| `AZURE_APPLICATION_INSIGHTS` | generated | Application Insights name |
| `AZURE_LOG_ANALYTICS` | generated | Log Analytics workspace name |

## Set automatically

| Setting | Set by | Effect |
| --- | --- | --- |
| `AZURE_SUBSCRIPTION_ID`, `AZURE_TENANT_ID` | azd | Target subscription and tenant |
| `GITHUB_ACTIONS`, `TF_BUILD` | CI runners | Deployer role assignments use principal type `ServicePrincipal` |

## Outputs

After provisioning, azd writes the template outputs into the environment.
Some examples are `BACKEND_URI`, `AZURE_RESOURCE_GROUP`,
`AZURE_BACKEND_SERVICE_NAME`, `AZURE_LOGICAPP_SERVICE_NAME`,
`AZURE_CONTAINER_REGISTRY_NAME`, `AZURE_STORAGE_ACCOUNT`,
`AZURE_COSMOSDB_ACCOUNT` and `AZURE_FOUNDRY_INFERENCE_ENDPOINT`. The deploy
scripts read these values. List them with:

```bash
azd env get-values
```

`azd env get-values` prints secrets too, so don't paste its output anywhere.
The [app settings reference](app-settings.md#deployment-outputs) maps each
output to the code that uses it.
