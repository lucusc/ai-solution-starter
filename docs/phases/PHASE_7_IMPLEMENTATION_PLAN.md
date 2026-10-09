# Phase 7 Implementation Plan

## Status

**Proposed requirements; awaiting implementation approval.** This phase plans
optional Azure OpenAI selection and a Foundry-first solution. It does not
authorize implementation, Azure deployment, a baseline-manifest update, a
commit, or a push.

Earlier phases retain their historical contracts and review gates. Their
defaults and preservation requirements are not changed by the behavior
proposed here. Phase 4 currently defines an Azure OpenAI workflow; its
implementation and review must be complete before migrating that workflow. If
Phase 4 is still unimplemented, review a Foundry-aligned revision of that plan
explicitly rather than claiming an existing workflow has been migrated.

## Objective

1. Give Azure OpenAI the same independent `new`, `existing`, and `none` modes
   as Foundry and Document Intelligence.
2. Default fresh solution setup to Foundry `new`, OpenAI `none`, and Document
   Intelligence `none`.
3. Make the demo application and Logic App use Foundry-hosted model inference
   without requiring a standalone Azure OpenAI account.
4. Preserve the PDF vertical slice, managed identity, structured response,
   work-item lifecycle, and operational error contracts.

Using an OpenAI-compatible API or SDK to call a Foundry-hosted model does not
make standalone Azure OpenAI a deployment dependency. Document the selected
Foundry endpoint and API explicitly; do not substitute the Foundry project
management endpoint for an inference endpoint.

## Proposed Service Contract

| Selector | Allowed values | Fresh-environment default |
| --- | --- | --- |
| `USE_FOUNDRY` | `new`, `existing`, `none` | `new` |
| `USE_OPENAI` | `new`, `existing`, `none` | `none` |
| `USE_DOCUMENT_INTELLIGENCE` | `new`, `existing`, `none` | `none` |

Selectors remain case-sensitive and independent. An explicit selection must
take precedence over a default consistently across every configuration path.
Invalid or conflicting inputs must fail with actionable errors.

### OpenAI modes

- **`new`:** Create a standalone Azure OpenAI account and explicitly selected
  model deployments. Reject existing-account IDs. Preserve supported account
  placement, SKU, identity, network, diagnostic, and model settings.
- **`existing`:** Reference a compatible existing Azure OpenAI account through
  a validated full resource ID. Confirm resource kind, scope, location, and
  required model availability before use. Do not recreate or implicitly
  modify the account. Apply `CONFIGURE_EXISTING_AI_SERVICES` consistently for
  optional RBAC, networking, and diagnostics. Creating or updating models
  requires an explicit model-deployment opt-in, distinct from account reuse.
- **`none`:** Omit standalone OpenAI account creation and lookup, child model
  deployments, OpenAI-specific RBAC, diagnostics, private endpoints, and
  Foundry-to-OpenAI connections. Emit no usable standalone OpenAI endpoint or
  resource ID and require no OpenAI keys, account, location, or model settings.
  Reject supplied existing-resource IDs and explicitly enabled dependent
  actions rather than silently ignoring them.

Existing resources are never deletion targets. Switching modes does not
authorize deletion of previously created accounts or model deployments.
Document ownership and inspect module-owned child resources before removal.

### Legacy configuration migration

Inventory `DEPLOY_AZURE_OPENAI`, `DEPLOY_AZURE_OPENAI_MODELS`, `OPENAI_HOST`,
existing account name/resource-group inputs, model settings, custom endpoints,
and API-key overrides. Define a reviewed mapping or explicit deprecation path
for every current input rather than adding a competing selector.

- Unconfigured fresh environments receive the new defaults.
- Explicit legacy account/provider choices must not silently become `none` or
  switch the application to Foundry.
- Conflicting legacy and new selectors must produce explicit errors.
- Document how existing azd and GitHub environments adopt Foundry, retain
  optional standalone OpenAI, and clean up stale exported settings.
- Preserve supported custom/non-Azure provider behavior where applicable;
  any intentional removal or incompatibility needs separate explicit approval.
- Do not let inherited model-switch defaults enable OpenAI deployments when
  `USE_OPENAI=none`.

The exact compatibility precedence and deprecation mechanism must be approved
before implementation.

## Requirements

### 7.1 Focused infrastructure change-control exception

Phase 7 intentionally changes deployment behavior and requires its own
focused infrastructure change-control exception.

Approve only the necessary changes to `infra/main.bicep`,
`infra/main.parameters.json`, AI modules, and directly coupled application
settings, outputs, RBAC, diagnostics, and private-endpoint wiring. Reuse
existing modules and shared policies where possible. Do not refactor,
reformat, rename, or upgrade unrelated protected infrastructure.

Capture the pre-change baseline and review exact resource-graph differences.
Update `docs/infrastructure/CHANGE_CONTROL.md` and
`infra/bicep-baseline.sha256` only through the approved review process. The
checksum manifest must not be refreshed simply to make validation pass.

### 7.2 Foundry model readiness

The Phase 6 Foundry module creates or references an account/project but does
not deploy a model. Define and implement the minimum model-deployment contract
needed for the demo:

- model name/version, deployment name, SKU/capacity, region, and availability;
- the supported inference API/version and endpoint resolution;
- PDF input and strict structured-output compatibility;
- managed-identity authentication audience and least-privilege permissions
  for the identities that actually invoke inference;
- public, restricted, and private connectivity, DNS, and diagnostics; and
- deployment ownership and explicit mutation policy for existing accounts.

For Foundry `new`, the default solution must provision the required model
deployment. For Foundry `existing`, reference a compatible deployment or
create one only with explicit opt-in. Fail clearly when the required deployment
is absent or incompatible; do not fall back to standalone OpenAI.

Keep `FOUNDRY_CONNECT_BASE_OPENAI=false` by default. If explicitly enabled,
require both an enabled Foundry mode and OpenAI `new` or `existing`.

All services may be `none` for infrastructure-only use, but attempting to run
or deploy the Foundry-dependent processing flow without its required service
and model must report the missing dependency explicitly.

### 7.3 Consistent solution and setup defaults

Trace and update every applicable surface:

- Bicep declaration defaults and conditional references;
- `infra/main.parameters.json` substitutions;
- preprovision validation and authentication/setup hooks;
- azd loading/export helpers and postprovision configuration;
- `.github/workflows/azure-dev.yml` and other provisioning/deployment paths;
- application settings, deployment helpers, environment examples, and smoke
  tooling; and
- repository validation and parameter-catalog coverage.

Defaults must agree for omitted and empty inputs according to a documented
resolution policy. Explicit choices must survive setup and reprovisioning.
Remove unconditional OpenAI requirements and ensure disabling OpenAI does
not evaluate disabled module outputs or existing-account references.

Preserve the flat deployment-parameter schema and keep the catalog aligned
with intentionally added or removed mappings rather than freezing the old
parameter count.

### 7.4 Demo application and Logic App migration

Update the demo's configuration, any backend inference client, frontend
provider descriptions, and operational guidance wherever they currently
depend on standalone Azure OpenAI. Do not introduce a backend AI call merely
to replace a provider name if the workflow owns inference.

Update the Phase 4 workflow HTTP action, model/endpoint settings, managed
identity, package fixtures, deployment wiring, and smoke expectations to
invoke Foundry. Preserve:

- authenticated PDF intake and the existing size limit;
- instruction loading and versioning;
- `summary`, `category`, and `key_points` structured output;
- ETag-protected state transitions and idempotency;
- bounded concurrency, retries, and transient/terminal error handling; and
- correlation and safe logging without document content or credentials.

The frontend and backend must retain their public API and persistence
contracts. Update readiness/deployment checks where applicable to expose
missing Foundry configuration without making a false success claim.

### 7.5 Documentation and validation

Update current setup, deployment configuration, parameter catalog, AI service
guide, architecture/application flow, cost drivers, troubleshooting,
replacement guidance, and removal instructions. Explain the difference
between a Foundry-hosted model and an optional standalone Azure OpenAI account.
Keep historical phase decisions identifiable rather than rewriting history.

Extend existing validation and tests; do not add unrelated tooling.

| Acceptance criterion | Required evidence |
| --- | --- |
| Defaults agree | Omitted/empty-input tests across parameter resolution, validators, setup, and CI configuration produce Foundry `new`, OpenAI `none`, Document Intelligence `none` |
| Modes are independent | Configuration validation covers all 27 three-service mode combinations with valid inputs, plus invalid modes, malformed IDs, conflicting inputs, and dependent-action errors |
| OpenAI modes work | Resource-graph checks distinguish creation, compatible existing-account reference, and no standalone OpenAI resources/references |
| Existing-resource ownership is safe | Tests cover mutation disabled/enabled, explicit model-deployment opt-in, and incompatible existing resource kinds |
| Migration is explicit | Tests cover legacy-only settings, new selectors, conflicting settings, custom-provider compatibility, and stale environment exports |
| Foundry is inference-ready | Model deployment, supported PDF/structured-output API, endpoint, identity audience, permissions, and connectivity are reviewed |
| Default demo uses Foundry | Mocked workflow/client tests assert Foundry endpoint and deployment use with no required standalone OpenAI configuration or fallback |
| Work-item behavior is preserved | Synthetic-PDF tests cover success, duplicate delivery, schema failure, retryable errors, terminal errors, and disabled/missing Foundry |
| Infrastructure changes are bounded | Compiled graph comparisons for defaults, all-none, OpenAI `new`, and OpenAI `existing` show only approved differences |
| Governance remains intact | Bicep compilation, approved baseline verification, parameter/catalog consistency, and repository documentation checks pass |
| Deployed flow works when approved | Synthetic PDF reaches a Foundry-generated result and completed UI state with OpenAI `none`; deployed resource inventory confirms no standalone OpenAI account |

Local validation is required before review. A live Azure test is a separate
permission/cost gate and must not be implied by compilation or mocked tests.

## Sequence and Review Gates

1. Refine and approve service contracts, legacy precedence, Foundry model/API
   compatibility, Phase 4 prerequisite, and the infrastructure exception.
2. Implement and review independent OpenAI modes and ownership controls.
3. Implement Foundry model readiness and align solution/setup defaults.
4. Migrate the demo and Logic App, their configuration, and documentation.
5. Run local validation and present exact diff/resource-graph evidence before
   requesting approval for the baseline-manifest update.
6. Run deployed validation only after separate Azure approval; record its
   outcome separately from local evidence.
7. Pause for final phase review before any separately approved commit or push.

Record completed implementation evidence in
`docs/reviews/PHASE_7_IMPLEMENTATION_REPORT.md` only after implementation.

## Out of Scope and Stop Conditions

Azure AI Search, agents, capability hosts, unrelated infrastructure refactors,
new intake formats, public API/schema changes, automatic resource deletion,
releases, and unapproved live deployment remain out of scope.

Stop for review if Foundry cannot preserve PDF/structured-output behavior,
existing-resource mutation becomes implicit, legacy settings cannot be
migrated without an unapproved behavior change, or the resource diff extends
beyond the focused exception. Resolve those decisions before implementation;
do not hide them with provider fallback or a checksum update.
