# RBAC Matrix

Role assignment is controlled by `ASSIGN_ROLES`. User assignments additionally
require `AZURE_PRINCIPAL_ID`.

| Principal | Scope | Roles |
| --- | --- | --- |
| Operator or deployment principal | Azure OpenAI resource group | Cognitive Services OpenAI User |
| Operator or deployment principal | Primary resource group | Cognitive Services User |
| Operator or deployment principal | Storage resource group | Storage Blob Data Reader, Contributor, and Owner |
| Operator or deployment principal | Cosmos DB resource group/account | DocumentDB Account Contributor and Cosmos DB Built-in Data Contributor |
| Operator or deployment principal | Configured resource group scope | Storage queue reader, contributor, processor, and sender roles |
| Backend system identity | Azure OpenAI resource group | Cognitive Services OpenAI User |
| Backend system identity | Storage resource group | Blob reader, contributor, owner, and queue message sender |
| Backend system identity | Primary resource group | AcrPull |
| Backend system identity | Cosmos DB account | Cosmos DB Built-in Data Contributor |
| Logic App user-assigned identity | Azure OpenAI resource group | Cognitive Services OpenAI User |
| Logic App user-assigned identity | Storage resource group | Account, blob, table, queue, file, and message-processing roles |
| Logic App user-assigned identity | Primary resource group | AcrPull |
| Logic App user-assigned identity | Cosmos DB account | Cosmos DB Built-in Data Contributor |
| Logic App system identity | Azure OpenAI resource group | Cognitive Services OpenAI User |
| Logic App system identity | Storage resource group | Account, blob, table, queue, file, and message-processing roles |
| Logic App system identity | Primary resource group | AcrPull |
| Logic App system identity | Cosmos DB account | Cosmos DB Built-in Data Contributor |
| Azure OpenAI managed identity | Cosmos DB account | Cosmos DB Built-in Data Contributor |
| Operator or deployment principal | New Foundry or Document Intelligence account | Cognitive Services User |
| Operator or deployment principal | Selected existing Foundry or Document Intelligence account | Cognitive Services User only when `CONFIGURE_EXISTING_AI_SERVICES=true` |
| Foundry project system identity | Azure OpenAI resource group | Cognitive Services OpenAI User when `FOUNDRY_CONNECT_BASE_OPENAI=true` |
| Azure diagnostics service principal | Storage resource group | Storage Blob Data Contributor |

The template also creates Logic App connection access policies for the Logic
App system identity and user-assigned identity.

Role definition IDs in `infra/azure_roles.json` are Azure built-in role IDs.
Cosmos DB data-plane role assignments use the Azure built-in SQL Data
Contributor role definition.
