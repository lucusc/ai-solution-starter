# Deployment configuration

## Configuration sources

Infrastructure values are defined by `infra/main.parameters.json` and supplied
through an Azure Developer CLI environment or GitHub environment variables.
Use the [parameter catalog](../infrastructure/PARAMETER_CATALOG.md) as the
authoritative inventory.

Application secrets must be stored as azd secrets or GitHub environment
secrets. Do not commit local environment files.

## Minimum environment choices

Before provisioning, decide:

- environment name and primary Azure region;
- resource-group creation or reuse;
- public, restricted-public, or private networking mode;
- generated or existing VNet and private DNS behavior;
- App Service and Logic Apps Standard SKUs;
- Cosmos DB free, provisioned, or serverless mode;
- Azure OpenAI account creation or approved existing account;
- optional Foundry and Document Intelligence `new`, `existing`, or `none`
  modes;
- model names, versions, capacity, and regional availability;
- monitoring enablement;
- role-assignment behavior; and
- authentication application setup.

## Authentication setup

The azd preprovision and postprovision hooks create or update server and SPA
Microsoft Entra application registrations unless
`AZURE_BYPASS_AUTHENTICATION_SETUP=true`.

Bypassing setup is explicit. When bypassed, provide compatible application IDs,
secrets, redirect URIs, and App Service authentication configuration through
the approved environment process.

## Networking

Select one documented mode from the
[networking matrix](../infrastructure/NETWORKING_MATRIX.md). Do not combine
settings based on assumptions about the Bicep implementation.

Restricted and private modes may require an operator IP allowlist, private DNS,
VPN, or access from an integrated network before data-plane validation works.

## GitHub deployment

The manual deployment workflow requires:

- GitHub OIDC federation;
- environment-scoped Azure subscription, tenant, and client IDs;
- environment variables matching the parameter catalog;
- required application-registration secrets when authentication setup uses
  them; and
- the management token used by the existing environment-variable action.

Review `.github/workflows/azure-dev.yml` before configuring an environment.
The workflow can provision infrastructure without deploying application
packages.

Before provisioning, validate optional AI service values:

```bash
python3 scripts/validate_ai_service_config.py --from-azd --check-azure
```

This rejects unsupported modes, conflicting new/existing inputs, malformed
resource IDs, and incompatible existing resource kinds. See
[optional AI services](../infrastructure/AI_SERVICES.md).

## Phase 4 boundary

The repository does not currently contain the deployable Logic App business
workflow. Do not enable application deployment expecting an AI processing flow
until Phase 4 is implemented and reviewed.
