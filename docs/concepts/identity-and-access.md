# Identity and access

The starter uses no passwords or keys between Azure services. Three kinds of
identity are involved:

| Identity | Who or what | Used for |
| --- | --- | --- |
| **User** | A person signed in with Microsoft Entra ID | Using the web app; each user sees only their own work items |
| **Managed identities** | Identities Azure creates for the web app and the Logic App | Reaching Storage, Cosmos DB, the registry and the model |
| **Deployer** | You (`AZURE_PRINCIPAL_ID`) or the GitHub workflow's service principal | Provisioning, deploying and inspecting data |

## User sign-in

- App Service authentication (Easy Auth) signs users in with two Entra app
  registrations: an API app and a browser app.
- App Service then adds an `X-MS-CLIENT-PRINCIPAL` header to each request. The
  backend uses that header to identify the owner.
- The backend returns 401 if the header is missing. A deployment without sign-in
  therefore doesn't work.
- Easy Auth must stay on. It is the only thing that stops a caller from
  forging the header.

Setup, custom tenants and bring-your-own registrations are covered in
[Configure authentication](../how-to/configure-authentication.md).

## Managed identities

| Identity | Uses it to |
| --- | --- |
| Web app (system-assigned) | Read and write Blob Storage and Cosmos DB, and pull images from the registry |
| Logic App (system-assigned) | Watch Blob Storage and read PDFs and prompts with the built-in Blob connector |
| Logic App (user-assigned) | Read and update Cosmos DB and call the Foundry model |

Shared-key access on Storage and the registry admin user are disabled, so
these identities and Azure RBAC are the only way in.

## Role assignments

With `ASSIGN_ROLES=true` (the default), the template assigns roles to the
identities above. The deployer gets data roles only when `AZURE_PRINCIPAL_ID`
is set; azd sets it to your signed-in identity. To assign roles outside the
template, set `ASSIGN_ROLES=false` and use the
[Assign RBAC workflow](../reference/github-workflows.md#assign-rbac) or your
own process.

Role assignments can take a few minutes to take effect after provisioning.

### Full role inventory

| Principal | Scope | Roles |
| --- | --- | --- |
| Deployer | Azure OpenAI resource group | Cognitive Services OpenAI User |
| Deployer | Primary resource group | Cognitive Services User |
| Deployer | Storage resource group | Storage Blob Data Reader, Contributor and Owner |
| Deployer | Cosmos DB account or resource group | DocumentDB Account Contributor and Cosmos DB Built-in Data Contributor |
| Deployer | Cosmos DB resource group | Storage Queue Data Reader, Contributor, Message Processor and Message Sender |
| Deployer | New Foundry or Document Intelligence account | Cognitive Services User |
| Deployer | Existing Foundry or Document Intelligence account | Cognitive Services User, only with `CONFIGURE_EXISTING_AI_SERVICES=true` |
| Web app identity | Azure OpenAI resource group | Cognitive Services OpenAI User |
| Web app identity | Storage resource group | Storage Blob Data Reader, Contributor and Owner, plus Storage Queue Data Message Sender |
| Web app identity | Primary resource group | AcrPull |
| Web app identity | Cosmos DB account | Cosmos DB Built-in Data Contributor |
| Logic App identities (system and user) | Azure OpenAI resource group | Cognitive Services OpenAI User |
| Logic App identities (system and user) | Storage resource group | Storage account, blob, table, queue and file roles |
| Logic App identities (system and user) | Primary resource group | AcrPull |
| Logic App identities (system and user) | Cosmos DB account | Cosmos DB Built-in Data Contributor |
| Logic App user identity | Foundry resource group | Cognitive Services OpenAI User, when Foundry is `new` or `CONFIGURE_EXISTING_AI_SERVICES=true` |
| Foundry project identity | Azure OpenAI resource group | Cognitive Services OpenAI User, when `FOUNDRY_CONNECT_BASE_OPENAI=true` and standalone OpenAI is enabled |
| Azure OpenAI identity | Cosmos DB account | Cosmos DB Built-in Data Contributor |
| Azure diagnostics service | Storage resource group | Storage Blob Data Contributor |

Conditions:

- Azure OpenAI rows apply only when standalone OpenAI is enabled: `USE_OPENAI`
  is `new`, or `existing` with `CONFIGURE_EXISTING_AI_SERVICES=true`.
- **Reusing an existing Foundry account?** Without
  `CONFIGURE_EXISTING_AI_SERVICES=true`, the Logic App doesn't get permission
  to call the model. Have the account owner grant **Cognitive Services OpenAI
  User** to the Logic App's user-assigned identity.
- The deployer's principal type is `ServicePrincipal` when the deployment runs
  in GitHub Actions or Azure Pipelines, and `User` otherwise.
- The table lists what the template assigns. It is not a least-privilege
  recommendation.

Role IDs are in [`infra/azure_roles.json`](../../infra/azure_roles.json).
