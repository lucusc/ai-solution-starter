# Optional AI services

Microsoft Foundry and Azure AI Document Intelligence are optional parts of the
base infrastructure deployment. Each service is selected independently with a
case-sensitive mode:

| Environment value | Values | Default |
| --- | --- | --- |
| `USE_FOUNDRY` | `new`, `existing`, `none` | `none` |
| `USE_DOCUMENT_INTELLIGENCE` | `new`, `existing`, `none` | `none` |

`new` creates the service, `existing` references an approved existing
resource, and `none` omits it. Run
`python scripts/validate_ai_service_config.py --from-azd --check-azure` before
provisioning. The preprovision hook runs the same validation.

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
system-assigned identities. Set `FOUNDRY_CONNECT_BASE_OPENAI=true` to create an
AAD connection from the project to the baseline Azure OpenAI account and grant
the project identity `Cognitive Services OpenAI User`. This connection requires
`OPENAI_HOST=azure`; custom and non-Azure endpoints are not accepted.

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

### Inspect and use the project

The deployment emits `AZURE_FOUNDRY_PROJECT_ID` and
`AZURE_FOUNDRY_PROJECT_ENDPOINT`. Inspect the management resource without
using keys:

```bash
az rest --method get \
  --url "https://management.azure.com${AZURE_FOUNDRY_PROJECT_ID}?api-version=2025-06-01"
```

Applications can use `DefaultAzureCredential` with the Foundry project SDK:

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

The module does not deploy agents, capability hosts, stores, or model
deployments.

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
