# Infrastructure Resource Contract

## Deployment scope

`infra/main.bicep` deploys at subscription scope. It can create the primary
resource group or target an existing resource group. Storage, Cosmos DB, and
Azure OpenAI may be placed in separately named existing resource groups.

All generated resource names use a deterministic token derived from the
subscription, environment name, and primary location. Resources receive the
`azd-env-name` tag.

## Resource graph

| Capability | Azure resource | Contract |
| --- | --- | --- |
| Application hosting | Linux App Service plan and container Web App | Hosts the backend and built frontend; system-assigned identity; optional App Service authentication |
| Container images | Premium Azure Container Registry | Admin access disabled; backend and Logic App identities receive pull access when role assignment is enabled |
| Object storage | General-purpose Storage account | Private containers for content, tokens, instructions, and inputs; shared-key and public blob access disabled |
| Workflow runtime storage | Separate Storage account | Supports Logic Apps Standard runtime storage with managed identity |
| Database | Azure Cosmos DB for NoSQL | Supports free, provisioned, and serverless modes; creates the starter database and work-item container |
| Workflow hosting | Logic Apps Standard plan and workflow app | Uses system- and user-assigned identities, VNet integration, diagnostics, and managed-identity storage authentication |
| AI | Azure OpenAI account or approved existing account | Supports chat, embedding, vision, and optional evaluation deployments |
| Optional AI | Microsoft Foundry account and project | `new`, `existing`, or disabled; optional managed-identity connection to baseline Azure OpenAI |
| Optional document analysis | Azure AI Document Intelligence account | `new`, `existing`, or disabled; intended for prebuilt Layout usage |
| Monitoring | Log Analytics and Application Insights | Optional monitoring, diagnostics, linked storage, and portal dashboard |
| Networking | VNet, integration subnets, private endpoints, and private DNS | Supports generated or existing VNets and generated or existing private DNS zones |
| Authentication | Microsoft Entra application registrations | Optional server and SPA registrations configured through azd hooks |
| Authorization | Azure RBAC and Cosmos DB data-plane roles | Optional user, backend, workflow, AI, and diagnostic assignments |

## Storage contract

The primary account creates:

| Parameter | Default | Purpose |
| --- | --- | --- |
| `storageContainerName` | `content` | General application content |
| `storageTokenContainerName` | `tokens` | Token or transient application artifacts |
| `storageInstructionsContainerName` | `instructions` | Generic AI instruction assets |
| `storageInputContainerName` | `inputs` | User-provided work-item inputs |

Blob public access and shared-key access are disabled. Network ACLs default to
deny. Allowed IPs can temporarily enable restricted public access.

## Database contract

The Cosmos DB account creates one SQL database and one container.

- Default database: `starter`
- Default container: `inputs`
- Partition key: `/created_at`
- Indexed fields: `/created_at/?` and `/source_name/?`
- Throughput: serverless, free-tier, or provisioned according to parameters

Later application phases must adapt to this contract rather than changing the
infrastructure baseline.

## Azure OpenAI contract

The deployment supports:

- a chat deployment
- an embedding deployment
- an optional vision deployment
- an optional evaluation deployment
- creation of a new Azure OpenAI account
- use of an approved existing Azure OpenAI account
- optional deployment of models into the existing account
- optional non-Azure OpenAI endpoint configuration

Model name, version, SKU, and capacity remain environment-configurable.

## Application configuration outputs

The template emits:

- resource group and location
- authentication tenant information
- backend URI and service name
- Logic App service name
- container registry name and endpoint
- Storage account, input container, instructions container, and resource group
- Cosmos DB account, resource group, database, container, and API version
- Azure OpenAI account, resource group, model names, and deployment names
- Foundry mode, account/project IDs and names, resource group, location,
  endpoints, and managed identity principal IDs
- Document Intelligence mode, account ID and name, resource group, location,
  endpoint, and managed identity principal ID

These outputs form the stable deployment and application configuration
contract for later phases.

When an optional service mode is `none`, its identifiers, endpoints,
locations, resource groups, and principal IDs are emitted as empty strings.
No credentials or shared output JSON are emitted.
