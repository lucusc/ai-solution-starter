# Phase 7 Implementation Plan

## Status

**Implemented locally; awaiting review.** The selected approach is a grouped,
flat `infra/main.parameters.json` with a matching, expanded parameter catalog.
The changes preserve deployment mappings and do not authorize Azure deployment,
a commit, or a push.

Phase 7 follows the completed Phase 6 implementation. Historical Phase 6
review and deployment evidence remains separate; this phase does not imply
that any pending review or live Azure validation has occurred.

## Objective

Make infrastructure configuration easier to find, understand, and maintain
without changing the deployment contract.

The planning inventory contains **124 parameter mappings**, including **51
substitution expressions with explicit defaults**. These counts describe
`infra/main.parameters.json`, not all Bicep parameters or every environment
variable consumed by deployment scripts.

## Selected Organizational Approach

- Keep `infra/main.parameters.json` as the single executable mapping file.
- Preserve the flat `parameters` object and standard deployment-parameters
  schema.
- Order parameters by functional domain rather than globally alphabetically.
- Separate groups with one blank line, retaining two-space indentation.
- Use documentation headings for group labels; do not add JSON comments,
  pseudo-parameters, nested groups, or unsupported metadata.
- Expand `docs/infrastructure/PARAMETER_CATALOG.md` using the same group names
  and order.
- Keep values in existing azd environments or GitHub configuration; do not
  introduce per-domain environment files, generated JSON, or a merge step.

The file answers "what is passed to Bicep?" The catalog answers "what should
an operator set, when, and why?"

## Proposed Group Order and Ownership

Every current parameter belongs to exactly one group. Counts below are the
planning baseline; implementation must confirm complete membership.

| Order | Group | Count | Membership and internal order |
| --- | --- | --- | --- |
| 1 | Deployment context | 4 | `environmentName`, `location`, `createResourceGroup`, `resourceGroupName` |
| 2 | Hosting | 12 | Backend service settings, `containerRegistryName`, `allowedOrigin`, then Logic App service settings |
| 3 | Data services | 19 | Storage (11): account placement and SKU; content, token, instruction, and input containers; system, processing, and evaluation instruction filenames. Cosmos DB (8): account name, resource group, location, SKU, throughput, database, container, API version |
| 4 | AI services | 52 | Azure OpenAI account and provider (13): `openAiHost`; account/model creation switches; Azure account name, resource group, location, SKU; API version, custom URL, key-disable switch; Azure and non-Azure keys; non-Azure organization. Model deployments (23): chat (5), embedding (6), vision (6), and evaluation (6), each model's selector and settings together. Optional AI services (16): shared `configureExistingAiServices` policy, then Foundry (9) and Document Intelligence (6) |
| 5 | Identity and access | 9 | Tenant override; server ID/secret; client ID/secret; authentication-disable and anonymous-access switches; `assignRoles`, `principalId` |
| 6 | Networking | 23 | Network access policy (4), generated VNet/subnets (7), existing VNet/subnets (7), and private DNS (5) |
| 7 | Monitoring and pipeline context | 5 | `useApplicationInsights`, `applicationInsightsName`, `logAnalyticsName`, `runningOnGh`, `runningOnAdo` |

Shared controls have one home. Service-specific documentation should link to
identity, networking, monitoring, or shared AI policy rather than duplicating
their parameter entries. The catalog should use subsections inside larger
groups (for example, storage versus Cosmos DB, Azure OpenAI account versus
model deployments versus Foundry, or generated versus existing VNet settings);
these are navigation aids, not additional JSON groups or blank-line
separators. Data and AI services are separate from hosting because the backend
and planned workflow share them rather than own them.

Preserve existing identifiers exactly, including
`cosmodDbResourceGroupName`, capitalization such as `useGPT4V`, and model
version naming differences. Renaming them is not organizational work.

## Requirements

### 7.1 Preserve the executable contract

- Preserve `$schema`, `contentVersion`, the exact parameter-name set, and
  every complete parameter entry.
- Preserve environment-variable names, substitution syntax, explicit
  defaults, empty-value handling, and value types.
- Make only ordering and whitespace changes to `main.parameters.json`.
- Do not add mappings for currently unmapped Bicep parameters.
- Do not change `main.bicep`, its modules, outputs, or the checksum manifest.
- Keep azd hooks and provisioning/application workflows behaviorally unchanged.
- Continue supporting both azd and GitHub environment configuration.
- Keep optional AI service defaults at `none`; keep Azure AI Search deferred.

The general no-reorganization constraint in `docs/PLAN.md` requires an
explicit, narrow exception for this parameter-file presentation change.
Approving Phase 7 must not grant permission to refactor protected Bicep.

### 7.2 Make the catalog complete and actionable

Document one row for each of the 124 mapped parameters, grouped in the
7-section order above. The catalog may use subsections within a group to make
related settings easier to scan. Use these columns:

| Column | Requirement |
| --- | --- |
| Bicep parameter | Exact key from `main.parameters.json` |
| Environment variable | Exact variable referenced by its substitution |
| Type | Type declared by Bicep, not the JSON placeholder's string type |
| Mapping default | Exact `${VARIABLE=default}` default, or explicitly "No inline default" |
| Purpose and effective fallback | Operator-facing meaning; distinguish generated names, Bicep fallbacks, and hook behavior from inline defaults |
| Required when / allowed values | Unconditional, conditional, optional, or pipeline-supplied; describe relevant modes and dependencies |
| Handling | Secret, ordinary configuration, or pipeline context; mark hook-managed values where applicable |

Additional requirements:

- Describe the resolution path from environment input through substitution to
  Bicep, without treating an empty variable as universally safe.
- Trace effective behavior where mapping and Bicep defaults differ; report
  existing discrepancies rather than silently changing them.
- Put selectors before their dependent settings and keep model settings
  together.
- Explain `new`, `existing`, and `none` modes and link to `AI_SERVICES.md`.
- Link network combinations to `NETWORKING_MATRIX.md`; do not invent new
  supported combinations.
- Distinguish secure Bicep inputs from non-secret IDs and resource names.
- List deployment inputs not mapped by this file in a separate supplementary
  section, including `AZURE_BYPASS_AUTHENTICATION_SETUP`. Do not count these
  as part of the 124 mapped parameters.
- Use placeholders only; do not commit real secrets or environment values.

### 7.3 Provide an operator reading path

Update `docs/deployment/CONFIGURATION.md` with a short checklist that directs
operators to:

1. choose environment, region, and resource-group behavior;
2. select hosting, storage, database, and OpenAI account/model settings;
3. choose optional AI service modes;
4. configure authentication, role assignment, and network/DNS modes;
5. review monitoring and pipeline-supplied context.

Explain which values users normally set, which are conditional or advanced,
and which hooks or pipelines supply. Link to the catalog rather than
maintaining a second full inventory or copying all defaults.

Update `infra/README.md` to explain the grouped file and catalog relationship.
Update infrastructure change-control guidance with the approved
presentation-only exception.

### 7.4 Guard against organizational drift

Use existing validation tooling; do not add a configuration generator or a
second production mapping file.

- Extend `scripts/validate_repository.py` to reject duplicate JSON keys before
  they can be silently overwritten by parsing.
- Validate the schema/header contract, entry shapes, complete group
  membership, and parameter group order. Define the group key lists once in
  the validator; do not copy environment mappings into those lists.
- Validate exact catalog coverage using the Bicep-parameter column, excluding
  supplementary hook/pipeline inputs.
- Add focused positive and negative tests for missing, extra, duplicate,
  misgrouped, and undocumented entries, with explicit failure messages.
- Wire parameter-organization validation into the existing local
  infrastructure validation path and infrastructure CI. Ensure relevant
  validator, test, and catalog changes trigger the CI check.
- Preserve existing optional AI configuration checks.

A documented intentional change may update group membership later. CI must
not assume that the project can never add a 125th parameter.

## Out of Scope

- splitting or generating parameter files;
- adding JSONC, YAML, or `.bicepparam` as a replacement;
- changing parameter names, defaults, types, or environment-variable names;
- changing authentication, networking, RBAC, resource behavior, or AI modes;
- adding deployment presets or provisioning new resources;
- implementing Azure AI Search or the Phase 4 application workflow;
- changing dependencies solely for documentation or grouping;
- live Azure deployment, commits, pushes, releases, or approval of earlier
  phase review gates.

## Implementation Sequence and Review Gates

1. **Approve the requirements.** Confirm group order, catalog columns,
   validation scope, and the presentation-only infrastructure exception.
2. **Capture the baseline.** Record the pre-change parameter document and
   exact group membership in review evidence. Use Git or session artifacts,
   not a duplicate production configuration.
3. **Reorder and document.** Apply the approved grouping, expand the catalog,
   and update the operator guide and change-control documentation.
4. **Add focused validation.** Extend existing tooling and test the failure
   cases above.
5. **Review locally.** Present the complete diff, equivalence evidence,
   coverage results, and validation results. Pause before any separately
   approved commit, push, or Azure activity.

## Acceptance Criteria and Evidence

| Acceptance criterion | Required evidence |
| --- | --- |
| All current mappings are preserved | Strict duplicate-aware parsing and full parsed-document equality against the pre-change version, ignoring object-key order only |
| No default or environment-variable change | Equality includes all 124 complete entries and 51 explicit-default expressions |
| Grouping is complete and deterministic | Every parameter appears once in the approved 7-group order; one blank line separates groups |
| Catalog is complete | Exactly one mapped-parameter row per current key; no missing, duplicate, or extra mapped rows |
| Configuration can be understood | Types, inline defaults, effective fallbacks, conditional requirements, sensitivity, and cross-domain links reviewed against implementation |
| Errors are visible | Focused tests demonstrate duplicate, missing, extra, misgrouped, and undocumented entries fail validation |
| Deployment behavior is untouched | No diff in Bicep, baseline manifest, hooks, or provisioning/application behavior; only approved validation-related CI changes |
| Existing infrastructure checks remain intact | Bicep compilation, baseline verification, and optional AI configuration checks pass locally |
| Documentation is navigable | Existing repository Markdown-link validation passes |
| Scope remains planning/local-only | No Azure resources changed; no commit or push without separate approval |

For the one-time equivalence check, compare the full JSON document against the
captured pre-Phase-7 version. A successful Bicep build or unchanged parameter
count alone does not prove unchanged mappings.

Record implementation evidence in
`docs/reviews/PHASE_7_IMPLEMENTATION_REPORT.md` only when implementation is
complete. Do not claim that organizational validation is an Azure deployment
or application smoke test.

## Stop Conditions

- A proposed change requires renaming a parameter or correcting its value.
- A documented fallback cannot be established from current implementation.
- Reorganization requires Bicep, hooks, deployment behavior, or checksum
  changes.
- A group has missing, duplicate, or ambiguous ownership.
- Semantic equality fails or an existing check regresses.

Resolve ambiguity through review. Handle independently discovered behavioral
defects through the existing infrastructure change-control process rather
than bundling them into this phase.
