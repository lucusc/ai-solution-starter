# Optional AI services

Microsoft Foundry, standalone Azure OpenAI, and Azure AI Document Intelligence
are independently selected with case-sensitive modes:

| Environment value | Values | Default |
| --- | --- | --- |
| `USE_FOUNDRY` | `new`, `existing`, `none` | `new` |
| `USE_OPENAI` | `new`, `existing`, `none` | `none` |
| `USE_DOCUMENT_INTELLIGENCE` | `new`, `existing`, `none` | `none` |

`new` creates the service, `existing` references an approved existing
resource, and `none` omits it. Run
`python scripts/validate_ai_service_config.py --from-azd --check-azure` before
provisioning. The preprovision hook runs the same validation. Fresh setup
creates Foundry and its demo model deployment; no standalone Azure OpenAI
account is selected by default.

## Microsoft Foundry

### New account and project

Set:

```text
USE_FOUNDRY=new
AZURE_FOUNDRY_ACCOUNT=<globally-unique-name>
AZURE_FOUNDRY_PROJECT=starter
AZURE_FOUNDRY_LOCATION=<approved-region>
AZURE_FOUNDRY_SKU=S0
```

The deployment creates an `AIServices` account and project with
system-assigned identities, plus the `gpt-4o` model deployment
`starter-gpt-4o` by default. Model availability, capacity, quota, cost, and
region must be checked before provisioning. Configure
`AZURE_FOUNDRY_MODEL_DEPLOYMENT`, `AZURE_FOUNDRY_MODEL_NAME`,
`AZURE_FOUNDRY_MODEL_VERSION`, `AZURE_FOUNDRY_MODEL_SKU`, or
`AZURE_FOUNDRY_MODEL_CAPACITY` to override the model deployment.

The deployment emits `AZURE_FOUNDRY_INFERENCE_ENDPOINT` and
`AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME`. The inference endpoint is the Azure
OpenAI-compatible `/openai/v1/` endpoint for the Foundry account, not the
Foundry project management endpoint. The demo workflow authenticates with its
user-assigned managed identity, `https://ai.azure.com/.default`, and
`Cognitive Services OpenAI User`. The standalone Azure OpenAI account and
project connection are not used by this path.

To opt into a Foundry-project connection to a separate Azure OpenAI account,
set `FOUNDRY_CONNECT_BASE_OPENAI=true` and `USE_OPENAI=new` or `existing`.
This optional connection is not required for inference from the Foundry model
deployment.

### Existing account or project

Set `USE_FOUNDRY=existing` and provide either:

- `EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID` to create the configured project under
  an existing `AIServices` account; or
- `EXISTING_FOUNDRY_PROJECT_RESOURCE_ID` to reference an existing project.

If both IDs are supplied, the project must belong to the account. Existing
resources are not modified with diagnostics, private endpoints, or
operator-role assignments unless `CONFIGURE_EXISTING_AI_SERVICES=true`.
Creating a requested child project or OpenAI connection remains an explicit
deployment action. When creating a project under an existing account,
`AZURE_FOUNDRY_LOCATION` must match the account location; preprovision
validation checks this through Azure Resource Manager.

### Inspect the project

The deployment also emits `AZURE_FOUNDRY_PROJECT_ID` and
`AZURE_FOUNDRY_PROJECT_ENDPOINT` for project management operations. Inspect
the management resource without using keys:

```bash
az rest --method get \
  --url "https://management.azure.com${AZURE_FOUNDRY_PROJECT_ID}?api-version=2025-06-01"
```

For project management, applications can use `DefaultAzureCredential` with
the Foundry project SDK:

```python
import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project = AIProjectClient(
    endpoint=os.environ["AZURE_FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
for connection in project.connections.list():
    print(connection.name)
```

The module does not deploy agents, capability hosts, or stores.

## Standalone Azure OpenAI

Azure OpenAI is independent of Foundry and defaults to `USE_OPENAI=none`.
`none` creates or references no standalone OpenAI account and assigns no
OpenAI-specific roles, diagnostics, or private endpoints.

### Create a new account

Set `USE_OPENAI=new`. The deployment creates an Azure OpenAI account and its
configured model deployments. The `DEPLOY_AZURE_OPENAI` and
`DEPLOY_AZURE_OPEN_MODELS` variables are deprecated; use `USE_OPENAI` instead.

### Use an existing account

Set `USE_OPENAI=existing` and provide
`EXISTING_OPENAI_RESOURCE_ID=<full-resource-id>`. Preprovision validation
requires the account kind to be `OpenAI` or `AIServices`. Existing account
resources are not modified by default. Set
`DEPLOY_OPENAI_MODELS_EXISTING=true` only when explicitly authorizing model
deployment changes. `CONFIGURE_EXISTING_AI_SERVICES=true` separately controls
module-managed existing-resource RBAC, diagnostics, and networking.

### Migrate existing environments

Fresh environments resolve to `USE_FOUNDRY=new`, `USE_OPENAI=none`, and
`USE_DOCUMENT_INTELLIGENCE=none`. Existing environments that intentionally
used the legacy `DEPLOY_AZURE_OPENAI`, `DEPLOY_AZURE_OPEN_MODELS`, or
`OPENAI_HOST=azure` settings must select `USE_OPENAI` explicitly. Conflicting
legacy and new settings fail preprovision validation; they are not silently
translated. Remove obsolete settings after choosing the new selector.

## Azure AI Document Intelligence

### New resource

Set:

```text
USE_DOCUMENT_INTELLIGENCE=new
AZURE_DOCUMENT_INTELLIGENCE_ACCOUNT=<globally-unique-name>
AZURE_DOCUMENT_INTELLIGENCE_LOCATION=<approved-region>
AZURE_DOCUMENT_INTELLIGENCE_SKU=S0
```

The deployment creates a `FormRecognizer` account with managed identity and
local authentication disabled.

### Existing resource

Set:

```text
USE_DOCUMENT_INTELLIGENCE=existing
EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID=<full-resource-id>
```

The referenced account must have kind `FormRecognizer`. Existing resources are
not modified unless `CONFIGURE_EXISTING_AI_SERVICES=true`.

### Analyze a document with prebuilt Layout

Use the emitted `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` and token credentials:

```python
import os

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.identity import DefaultAzureCredential

client = DocumentIntelligenceClient(
    endpoint=os.environ["AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
with open("sample.pdf", "rb") as document:
    result = client.begin_analyze_document(
        "prebuilt-layout",
        body=document,
        content_type="application/pdf",
    ).result()

for page in result.pages:
    print(page.page_number, len(page.lines or []))
for table in result.tables or []:
    print(table.row_count, table.column_count)
```

Keep extracted text and tables tied to page and span metadata when normalizing
results. Do not log document content or return credentials in application
responses.

## Networking, diagnostics, and removal

New resources inherit the base public/restricted/private network selection.
Private mode uses:

| Service | Private-link group | Private DNS zone |
| --- | --- | --- |
| Foundry | `account` | `privatelink.services.ai.azure.com` |
| Document Intelligence | `account` | `privatelink.cognitiveservices.azure.com` |

When monitoring is enabled, new resources receive `allLogs` and `AllMetrics`
diagnostic settings. Existing resources receive those settings only when
`CONFIGURE_EXISTING_AI_SERVICES=true`.

To stop using a service, first set its mode to `none` and remove its existing
resource IDs. Resources created in `new` mode are Azure resources owned by the
deployment and must be reviewed individually before deletion. Resources
selected in `existing` mode are never deletion targets; remove only
module-owned child connections, assignments, diagnostics, or private endpoints
after inspecting their resource IDs.

## Azure AI Search

Azure AI Search is intentionally deferred. Phase 6 creates no Search service,
index, indexer, skillset, data source, role assignment, private endpoint, or
application dependency. A later reviewed increment must define index ownership,
schema, ingestion, retrieval, identity, networking, regional availability, and
cost before adding a conditional module.
