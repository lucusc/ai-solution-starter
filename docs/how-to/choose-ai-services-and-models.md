# Choose AI services and models

The template can create or reuse three AI services. Each one is controlled by
a `USE_*` setting with one of three lowercase values:

| Setting | `new` | `existing` | `none` | Default |
| --- | --- | --- | --- | --- |
| `USE_FOUNDRY` | Create a Foundry account, project and model | Reuse an account or project | Skip | `new` |
| `USE_DOCUMENT_INTELLIGENCE` | Create a Document Intelligence resource | Reuse one | Skip | `none` |
| `USE_OPENAI` | Create a standalone Azure OpenAI account | Reuse one | Skip | `none` |

**The sample workflow only uses Foundry.** Document Intelligence and
standalone Azure OpenAI are there for your own code to use.

Settings are checked before every `azd provision`. To check them yourself:

```bash
python3 scripts/validate_ai_service_config.py --from-azd --check-azure
```

To reuse existing resources, follow
[bring your own AI resources](../quickstarts/bring-your-own-ai.md).

## Change the model

The default is `gpt-4o` version `2024-11-20`, Standard deployment, capacity
30 (thousands of tokens per minute), deployed as `starter-gpt-4o`.

```bash
azd env set AZURE_FOUNDRY_MODEL_NAME "gpt-4o"
azd env set AZURE_FOUNDRY_MODEL_VERSION "2024-11-20"
azd env set AZURE_FOUNDRY_MODEL_SKU "GlobalStandard"
azd env set AZURE_FOUNDRY_MODEL_CAPACITY 10
azd env set AZURE_FOUNDRY_MODEL_DEPLOYMENT "starter-gpt-4o"
azd provision
```

The workflow sends the PDF to the model's **Responses API** as a file input
and asks for structured JSON output. Any replacement model must support all
three in your region. Check
[model availability](https://learn.microsoft.com/azure/ai-foundry/openai/concepts/models)
and your quota before changing it.

If you hit a quota error, lower `AZURE_FOUNDRY_MODEL_CAPACITY` or try
another region.

## How the workflow calls the model

- Endpoint: `AZURE_FOUNDRY_INFERENCE_ENDPOINT`, the account's
  OpenAI-compatible `/openai/v1/` URL. This is not the project endpoint.
- Deployment: `AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME`.
- Identity: the Logic App's user-assigned managed identity, token audience
  `https://ai.azure.com`, role **Cognitive Services OpenAI User**. No keys.
- Prompts: `app/agent/instructions/system.md` and `processing.md`, uploaded
  to the `instructions` Storage container on each deploy.

## Document Intelligence

```bash
azd env set USE_DOCUMENT_INTELLIGENCE new
azd provision
```

This creates a `FormRecognizer` account (SKU `S0`) with keys disabled and a
private endpoint when private endpoints are on. The endpoint is saved as
`AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`. Your code must sign in with
Microsoft Entra ID. For example, with `azure-ai-documentintelligence` and
`azure-identity`:

```python
import os

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.identity import DefaultAzureCredential

client = DocumentIntelligenceClient(
    endpoint=os.environ["AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
with open("tests/sample-data/generated/hello-world.pdf", "rb") as document:
    result = client.begin_analyze_document(
        "prebuilt-layout", body=document, content_type="application/pdf"
    ).result()

for page in result.pages:
    print(page.page_number, len(page.lines or []))
```

The caller needs **Cognitive Services User** on the account and a network
path to it. The template grants this to your account (`AZURE_PRINCIPAL_ID`).
To call it from the web app or Logic App, add a role assignment for that
identity. See [identity and access](../concepts/identity-and-access.md).

## Standalone Azure OpenAI

`USE_OPENAI=new` creates an Azure OpenAI account with chat, embedding and
optional vision and evaluation deployments. The model settings are listed
under *Standalone Azure OpenAI* in
[configuration](../reference/configuration.md#standalone-azure-openai).
Set `FOUNDRY_CONNECT_BASE_OPENAI=true` to also connect it to the Foundry
project.

Older environments that used `DEPLOY_AZURE_OPENAI`,
`DEPLOY_AZURE_OPEN_MODELS` or `OPENAI_HOST` must switch to `USE_OPENAI`.
Validation fails if the old and new settings conflict.

## Inspect the Foundry project

```bash
az rest --method get \
  --url "https://management.azure.com$(azd env get-value AZURE_FOUNDRY_PROJECT_ID)?api-version=2025-06-01"
```

The template creates the project only. It does not create agents,
connections (except the optional OpenAI one), or AI Search.

## Turn a service off

Set its mode to `none`, remove any `EXISTING_*_RESOURCE_ID` values, and run
`azd provision`. Provisioning does **not** delete resources that were already
created. Delete them yourself if you no longer need them.
