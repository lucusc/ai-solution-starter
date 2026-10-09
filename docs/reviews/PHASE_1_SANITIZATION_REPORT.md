# Phase 1 Sanitization Report

## Scope

Phase 1 introduced the infrastructure and deployment baseline only:

- Bicep entry points and modules
- azd parameter mapping and hooks
- authentication and deployment scripts
- reusable GitHub composite actions
- infrastructure deployment and RBAC workflows
- infrastructure contract documentation

No backend, frontend, Logic App business workflow, prompts, sample documents,
database records, or generated assets were introduced.

## Generalization performed

- Replaced solution-specific project and application registration names.
- Replaced domain-specific database, container, field, and instruction names
  with generic work-item terminology.
- Replaced generated permission and dashboard identifiers that were not Azure
  platform constants.
- Removed application-specific document upload steps.
- Removed application test automation until application phases provide code.
- Reduced the Azure role catalog to built-in roles referenced by the template.
- Added a generic infrastructure-validation workflow.
- Added independent script dependencies for authentication hooks.

## Behavior preserved

- Subscription-scoped resource deployment
- Resource graph and resource-type counts
- Module boundaries and API versions
- Resource conditions, loops, dependencies, and outputs
- Azure OpenAI deployment options
- identity and RBAC behavior
- network isolation, existing-network, and private DNS options
- App Service and Logic Apps Standard hosting
- monitoring and diagnostics
- azd authentication hook sequence
- GitHub OIDC provisioning and application deployment sequence

## Validation evidence

- Original and generalized templates each compile to:
  - 111 parameters
  - 31 outputs
  - 341 expanded resources
- Compiled resource-type counts are identical.
- Bicep compilation succeeds with the inherited warning baseline.
- JSON, YAML, Bash, Python, and PowerShell syntax validation succeeds.
- Scans found no private repository name, source commit, organization name,
  domain-specific business term, email address, subscription resource ID, or
  credential value.
- URLs are limited to public product documentation, Microsoft and GitHub APIs,
  Azure endpoints, and localhost development callbacks.
- IP addresses are limited to generic private network defaults, Azure portal
  middleware access, and the Azure Cosmos DB service bypass value.

## Deployment validation

A temporary clean environment was provisioned in Sweden Central with the full
private-network defaults and authentication app-registration setup bypassed.

The deployment successfully created or validated:

- the isolated resource group
- primary and Logic App Storage accounts
- Premium Azure Container Registry
- Azure OpenAI and the chat, embedding, and vision deployments
- Log Analytics and Application Insights
- the monitoring dashboard
- Azure Cosmos DB
- the backend App Service plan on the retry

The Logic Apps Standard plan could not be allocated because Azure reported no
available regional instances. An idempotent retry produced the same regional
capacity response. This was accepted as an external capacity result rather
than a template defect; no infrastructure changes were made to work around it.

The complete temporary resource group was then deleted. The Log Analytics
workspace and Azure OpenAI account were purged, and Azure Developer CLI
reported successful removal of the application resources.
