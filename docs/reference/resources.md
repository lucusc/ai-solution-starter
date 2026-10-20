# Azure resources reference

What [`infra/main.bicep`](../../infra/main.bicep) creates. It deploys at
subscription scope and creates `rg-<environment-name>`, or uses an existing
resource group. Storage, Cosmos DB and the AI services can be placed in other
resource groups.

Resource names include a token derived from the subscription, environment name
and region, unless you override them. See the
[configuration reference](configuration.md).

## Resources

| Purpose | Resource | Notes |
| --- | --- | --- |
| Web app hosting | Linux App Service plan and web app | Runs the backend container, which also serves the frontend. System-assigned identity. Easy Auth when sign-in apps are configured. |
| Container images | Azure Container Registry (Premium) | Admin user disabled. The apps pull with managed identity. |
| App data | Storage account | Containers `content`, `tokens`, `instructions` and `inputs`. Shared keys and public Blob access are disabled. The firewall denies by default. |
| Workflow runtime storage | Second Storage account | Used by Logic Apps Standard, with managed identity |
| Database | Cosmos DB for NoSQL | Database `starter`, container `inputs`, partition key `/created_at`. Serverless by default. |
| Document workflow | Logic Apps Standard plan and app | System- and user-assigned identities, VNet integration in private mode |
| Model | Foundry account, project and model deployment | `gpt-4o` by default. Can be `existing` or `none`. |
| Optional | Document Intelligence account | Off by default |
| Optional | Azure OpenAI account | Off by default. Not used by the sample. |
| Monitoring | Log Analytics, Application Insights and a dashboard | On by default |
| Networking | VNet, subnets, private endpoints, private DNS zones and a Monitor private link scope | Private mode (default). See [Networking](../concepts/networking.md). |
| Access | Azure role assignments, including Cosmos DB data-plane roles | See [Identity and access](../concepts/identity-and-access.md) |

The Entra app registrations used for sign-in are created by the azd hooks,
not by Bicep. See [Configure authentication](../how-to/configure-authentication.md).

## Cosmos DB container

| Property | Value |
| --- | --- |
| Database | `starter` (`AZURE_COSMOSDB_DATABASE`) |
| Container | `inputs` (`AZURE_COSMOSDB_CONTAINER`) |
| Partition key | `/created_at` |
| Indexed paths | `/created_at/?` and `/source_name/?` |

The app is written for this container shape. Changing it requires an
infrastructure change. See
[infrastructure change control](../contributing/infra-change-control.md).

## Outputs

Provisioning writes the following outputs into the azd environment:

- resource group and region
- sign-in tenant
- backend URL and name
- Logic App name
- registry name and endpoint
- Storage and Cosmos DB names
- Foundry, Document Intelligence and Azure OpenAI identifiers and endpoints

Outputs for services set to `none` are empty. No output contains a
credential. The azd environment as a whole can still hold secrets, such as
the sign-in app secrets.

[App settings](app-settings.md#deployment-outputs) shows how the outputs map
to the backend and workflow settings.
