# Phase 6 Implementation Report

## Outcome

Phase 6 is implemented locally and awaits review. Microsoft Foundry and Azure
AI Document Intelligence are conditional modules in the base infrastructure
deployment. Both default to `none`; Azure AI Search remains documentation-only.
No Azure deployment was run.

## Implemented infrastructure

- Added `infra/modules/ai/foundry.bicep`.
  - Creates or references an `AIServices` account.
  - Creates or references a Foundry project.
  - Supports managed identity, operator RBAC, diagnostics, and an optional AAD
    project connection to the baseline Azure OpenAI account.
- Added `infra/modules/ai/document-intelligence.bicep`.
  - Creates or references a `FormRecognizer` account.
  - Supports managed identity, operator RBAC, and diagnostics.
- Added minimal conditional composition to `infra/main.bicep`.
  - `USE_FOUNDRY=none|new|existing`
  - `USE_DOCUMENT_INTELLIGENCE=none|new|existing`
  - centralized private endpoints and DNS zones
  - Foundry project identity access to baseline Azure OpenAI
  - non-secret top-level outputs
- Added azd environment mappings to `infra/main.parameters.json`.

Existing resources are modified with module-owned RBAC, diagnostics, or private
endpoints only when `CONFIGURE_EXISTING_AI_SERVICES=true`. Explicitly requested
Foundry child-project and connection creation remains available in existing
mode.

## Configuration validation

`scripts/validate_ai_service_config.py` rejects:

- unsupported or incorrectly cased modes;
- existing-resource IDs in `new` or `none` mode;
- missing IDs in `existing` mode;
- malformed account and project IDs;
- mismatched Foundry account/project parents; and
- a Foundry OpenAI connection request while Foundry is disabled.

With `--check-azure`, it performs read-only Azure CLI lookups and verifies
Foundry account kind `AIServices` and Document Intelligence account kind
`FormRecognizer`. The azd preprovision hooks run this validation before
authentication setup or infrastructure provisioning.

## Compatibility evidence

The compiled pre-Phase-6 template contained 64 top-level resources. The
compiled Phase 6 template contains 67. No prior resource type/name pair was
removed. The only additions are conditional nested deployments:

| Deployment | Condition |
| --- | --- |
| `foundry` | Foundry mode is not `none` |
| `document-intelligence` | Document Intelligence mode is not `none` |
| `foundry-project-openai-role` | Foundry enabled, connection requested, `OPENAI_HOST=azure`, and role assignment enabled |

With both modes at their `none` defaults, all three additions evaluate false.
Existing baseline resources remain present with their original type/name
identity. Private endpoint additions are empty unless their corresponding
service is enabled.

## Documentation

Added `docs/infrastructure/AI_SERVICES.md` and updated the parameter, resource,
networking, RBAC, deployment, troubleshooting, cost, validation, replacement,
and repository guidance. The service guide includes:

- new/existing/none configuration;
- Foundry management inspection and SDK connection listing;
- Document Intelligence prebuilt Layout SDK usage;
- identity, diagnostics, and private networking behavior;
- safe removal boundaries; and
- explicit Azure AI Search deferral.

## Validation performed

- Foundry module Bicep compilation
- Document Intelligence module Bicep compilation
- integrated `infra/main.bicep` compilation
- parameter JSON parsing
- optional-service contract unit tests
- optional-service default validation
- shell syntax validation
- repository formatting and whitespace checks
- pre/post compiled resource graph comparison

Bicep compilation retains nullable conditional-resource warnings, including
warnings inherited from the protected baseline. It completes without errors.

## Deferred validation

Live `new` and `existing` deployments, private endpoint resolution, service
data-plane calls, quota checks, and regional availability checks require an
explicitly approved Azure environment. They were not run in this phase.

Azure AI Search implementation remains deferred to a separately reviewed
increment.
