# Phase 6 Implementation Plan

## Status

**Planning revision required; awaiting approval.** This document defines the
proposed conditional Microsoft Foundry and Azure AI Document Intelligence
modules, the deployment-selection contract, and the deferred Azure AI Search
design. It does not authorize implementation, Azure deployment, a push, or
any infrastructure change.

Phase 6 implementation must begin only after this plan is explicitly approved.
Each implemented extension must then stop at its own review gate before the
next extension or composition work begins.

## Objective

Extend the starter's base infrastructure with conditionally optional Azure AI
capabilities while preserving the existing resource graph and behavior when
the new capabilities are not selected:

1. add a Microsoft Foundry account and project extension;
2. add an Azure AI Document Intelligence extension;
3. allow either extension to deploy a new service or reference a compatible
   pre-existing service;
4. select each service through base-infrastructure parameters sourced from
   deployment environment variables;
5. place service modules under `infra/modules/ai/` and invoke them
   conditionally from `infra/main.bicep`;
6. document managed-identity usage through REST and SDK command examples;
7. plan, but do not implement, Azure AI Search in this phase; and
8. prove that a deployment with no selected services preserves the current
   base resource graph and behavior.

The new services are part of the base infrastructure install, but remain
disabled by default. Phase 6 will not integrate them into the base backend,
frontend, Logic App, or work-item data model.

## Non-Negotiable Infrastructure Rule

The established Bicep resource graph and behavior remain protected. Phase 6
has explicit approval to add only the conditional AI-service wiring required
by this plan:

- new service modules under `infra/modules/ai/`;
- new optional parameters in `infra/main.bicep`;
- conditional module invocations in `infra/main.bicep`;
- outputs for deployed or referenced service resources; and
- corresponding parameter and documentation entries.

The existing baseline modules, resource definitions, identities, networking,
RBAC, diagnostics, and application settings must not be optimized,
reorganized, simplified, reformatted, renamed, upgraded, or behaviorally
changed. The implementation must not duplicate or replace the baseline.

Because `infra/main.bicep` is currently covered by the checksum manifest, the
approved Phase 6 additive change must update the manifest only after the exact
diff is reviewed, the no-service resource graph is compared with the
pre-Phase-6 graph, and `az bicep build` passes. The manifest update itself
requires explicit approval.

Any change outside the additive scope above is a stop condition.

## Approved Decisions

| Decision | Phase 6 direction |
| --- | --- |
| Base infrastructure | Preserve existing resource graph and behavior; add only approved conditional AI wiring |
| Extension selection | Optional base-infrastructure parameters sourced from deployment environment variables |
| New versus existing services | Support deployment of new services and reference to approved pre-existing services |
| Enablement shape | Per-extension deploy boolean plus optional existing-resource variables |
| Deployment integration | Conditional modules under `infra/modules/ai/` invoked by `infra/main.bicep` |
| Composition | One base deployment selects zero, one, or both services |
| Networking | Mirror applicable baseline public, restricted-public, generated-private, existing-VNet, existing-DNS, and externally managed DNS modes |
| Foundry scope | Foundry account/project, managed-identity model connection, and documentation-only SDK/REST usage commands |
| Foundry parent | Support a new compatible `AIServices` account or an approved existing compatible account |
| Existing Azure OpenAI | Keep the baseline Azure OpenAI account unchanged; reference it only as an optional Foundry project connection when supported |
| Foundry agent scope | No prompt agent, hosted agent, capability host, or agent runtime in the initial extension |
| Document Intelligence scope | Prebuilt Layout usage contract with normalized text/table guidance |
| Application surface | Documentation and command snippets only; no executable sample module and no base application integration |
| Azure AI Search | Detailed future design only; no Search resources, schemas, scripts, dependencies, or examples implemented in Phase 6 |
| Review sequence | Strategy, Foundry, Document Intelligence, composition, and final review use separate gates |
| Azure validation | Local validation first; each live deployment requires explicit approval |
| Publication | Local implementation commits only until separately approved for push |

## Phase Boundaries

### Included

- additive `infra/modules/ai/` module boundaries;
- conditional Foundry and Document Intelligence module calls from the base
  template;
- base parameter and environment-variable entries;
- deterministic deploy-or-reference-existing resolution;
- resource-ID validation before Azure changes;
- typed Bicep outputs suitable for documentation and future application
  wiring;
- system-assigned or user-assigned managed identity where supported;
- least-privilege Azure RBAC owned by each extension;
- diagnostic settings owned by each extension when a compatible destination is
  supplied;
- baseline-parity network modes where the target service supports them;
- private endpoint and private DNS integration owned by each extension;
- existing VNet and private DNS lookup contracts;
- public and restricted-public access behavior;
- Foundry account/project provisioning or existing-resource reference;
- optional Foundry project connection to the existing Azure OpenAI resource;
- Document Intelligence provisioning or existing-resource reference;
- prebuilt Layout REST and SDK documentation;
- validation for standalone and selected combined deployments;
- cost-driver, quota, region, permissions, troubleshooting, and removal
  documentation;
- a future Azure AI Search design and decision gate;
- clean-room and source-sanitization validation; and
- implementation reports for each approved work package.

### Excluded

- optimization or behavioral changes to the existing baseline modules;
- automatic deployment of either new AI service when its selector is false and
  no existing-resource reference is supplied;
- modifications to `azure.yaml` unless separately required by the base
  parameter contract;
- changes to base infrastructure outputs or application settings;
- changes to backend or frontend dependency manifests;
- backend routes, frontend pages, or feature flags;
- Logic App workflow stages or connector changes;
- Cosmos DB schema or index changes;
- deployment of Microsoft Foundry agents;
- Foundry Standard Agent Setup, capability hosts, or bring-your-own agent
  stores;
- Foundry model deployment changes to the baseline Azure OpenAI resource;
- executable Foundry or Document Intelligence sample applications;
- custom Document Intelligence model training;
- Document Intelligence training containers or training-data RBAC;
- Azure AI Search resource deployment;
- Search indexes, indexers, skillsets, vectorizers, semantic configurations,
  or query examples;
- fixed price estimates;
- automatic live-Azure validation;
- destructive removal of referenced existing resources; and
- release, tag, template publication, or push without separate approval.

## Completion Semantics

Phase 6 is divided into independently reviewed increments.

### Planning complete

Planning is complete when:

- this document records all approved decisions;
- the high-level phase plan and task backlog agree with it;
- implementation work packages and dependencies are explicit;
- the baseline checksum still passes; and
- no extension code or Azure resource has been created.

### Foundry extension complete

The Foundry increment is complete when its additive templates, scripts,
documentation, and local validation pass. A live deployment is additional
evidence only when separately approved.

### Document Intelligence extension complete

The Document Intelligence increment is complete when its additive templates,
scripts, documentation, and local validation pass. A live deployment is
additional evidence only when separately approved.

### Conditional composition complete

Conditional composition is complete when the base Bicep deployment can:

- select neither extension without changing Azure;
- select Foundry only;
- select Document Intelligence only;
- select both;
- mix deploy and existing-resource modes; and
- report outputs without confusing newly deployed and referenced resources.

### Search planned

Azure AI Search is complete for Phase 6 when its future contract, prerequisites,
open decisions, and implementation gate are documented. No Search deployment
artifact is expected.

## Proposed Repository Layout

```text
infra/
├── main.bicep                         # Existing template plus approved conditional wiring
├── main.parameters.json               # Existing parameter file plus approved defaults
└── modules/
    └── ai/
        ├── foundry.bicep
        ├── document-intelligence.bicep
        └── README.md

docs/
└── infrastructure/
    └── AI_SERVICES.md
```

The existing deployment scripts remain the entry point. Exact module names may
follow repository conventions during implementation, but the ownership
boundaries must remain:

- each service module owns only its service resources and service-specific
  outputs;
- `infra/main.bicep` owns selection, parameter plumbing, module conditions,
  and top-level outputs;
- the existing baseline modules remain untouched;
- no service module changes unrelated baseline resources; and
- the normal `azd provision` path installs selected services atomically with
  the base deployment.

PowerShell parity is not automatically required for Phase 6. If the existing
deployment support matrix requires Windows-native extension scripts,
implementation must add equivalent `.ps1` entry points in the same increment
or stop for a scope decision.

## Deployment and Enablement Contract

### Selection parameters and environment variables

The base Bicep deployment will use explicit booleans populated by the
deployment environment:

| Environment value | Default | Meaning |
| --- | --- | --- |
| `DEPLOY_FOUNDRY` | `false` | Create or enable Foundry resources when no existing resource ID is supplied |
| `DEPLOY_DOCUMENT_INTELLIGENCE` | `false` | Create or enable Document Intelligence when no existing resource ID is supplied |

Azure AI Search has no deployment selector in Phase 6 because its
implementation is deferred.

The word `DEPLOY` enables creation when no existing resource reference is
supplied. An existing resource reference always takes precedence, even when
the corresponding deploy boolean is `false`; the module validates and
references that resource instead of creating a duplicate. If the boolean is
false and no existing resource information is supplied, the service is
skipped.

### Foundry existing-resource variables

The exact names must remain environment-oriented and secret-free:

| Environment value | Required when supplied | Purpose |
| --- | --- | --- |
| `FOUNDRY_ACCOUNT_RESOURCE_ID` | Existing-account mode | Full resource ID of a compatible `AIServices` account |
| `FOUNDRY_PROJECT_NAME` | Deploy or existing-project mode | Project name to create or resolve |
| `FOUNDRY_PROJECT_RESOURCE_ID` | Optional existing-project mode | Full resource ID of an existing project |
| `FOUNDRY_LOCATION` | New-account mode | Deployment location |
| `FOUNDRY_ACCOUNT_NAME` | New-account mode | Account name or deterministic naming seed |
| `FOUNDRY_RESOURCE_GROUP` | New-account mode or short-name lookup | Resource group |
| `FOUNDRY_CONNECT_BASE_OPENAI` | `false` | Request a project connection to the baseline Azure OpenAI resource |
| `FOUNDRY_BASE_OPENAI_RESOURCE_ID` | Required when connection requested | Full resource ID; never inferred by editing or parsing baseline Bicep |

An implementation may accept azd environment values exported by the base
deployment, but it must treat them as inputs. It must not require a change to
the base outputs or parameter file.

### Document Intelligence existing-resource variables

| Environment value | Required when supplied | Purpose |
| --- | --- | --- |
| `DOCUMENT_INTELLIGENCE_RESOURCE_ID` | Existing-resource mode | Full resource ID of a compatible `FormRecognizer` account |
| `DOCUMENT_INTELLIGENCE_NAME` | New-resource mode | Account name or deterministic naming seed |
| `DOCUMENT_INTELLIGENCE_RESOURCE_GROUP` | New-resource mode or short-name lookup | Resource group |
| `DOCUMENT_INTELLIGENCE_LOCATION` | New-resource mode | Deployment location |
| `DOCUMENT_INTELLIGENCE_SKU` | New-resource mode | Supported SKU selected explicitly |

### Resolution rules

The selector and extension scripts must implement these rules before
deployment:

1. A full existing resource ID enters reuse mode even when its deploy boolean
   is false.
2. A false deploy boolean with no existing resource ID skips the service.
3. A true deploy boolean with no existing resource ID enters new-resource
   mode.
4. A supplied existing project ID takes precedence over creating a Foundry
   project, after compatibility validation.
5. Partial existing-resource identifiers are invalid; scripts must not guess
   subscriptions, resource groups, providers, or account kinds.
6. New-resource and existing-resource values that conflict are rejected.
7. Existing-resource validation occurs before any deployment operation.
8. Existing resources must be in a tenant and subscription accessible to the
   deployment principal.
9. Existing resources are never deleted by extension removal guidance.
10. Secrets, API keys, connection strings, and SAS tokens are not accepted as
    deployment configuration.

### Boolean parsing

Accepted boolean values must be documented and normalized consistently.
Unrecognized values must fail. Empty values must resolve to the documented
default rather than being treated as truthy.

### Deployment order

The existing base deployment will:

1. load the selected azd environment;
2. validate all base and optional AI-service parameters;
3. validate Azure login, tenant, subscription, and required providers;
4. validate the approved Bicep checksum;
5. compile and validate `infra/main.bicep`;
6. produce a deployment preview or what-if when supported;
7. request or verify the explicit live-deployment gate;
8. deploy the base resource graph and conditionally selected AI modules in one
   Bicep deployment; and
9. export non-secret top-level Bicep outputs through the existing azd output
   flow.

Foundry and Document Intelligence must not depend on one another.

## Bicep Output Contract

Each AI module will expose typed Bicep outputs required by
`infra/main.bicep`. The base template will emit corresponding top-level
outputs for azd and future application configuration.

The output contract will include, where applicable:

- mode: `disabled`, `deployed`, or `existing`;
- resource ID;
- resource group;
- service location;
- non-secret endpoint;
- project ID and project endpoint for Foundry; and
- managed identity principal ID when required for RBAC review.

Skipped services emit empty resource and endpoint values with mode
`disabled`. Credentials, keys, connection strings, tokens, and document
content are never outputs.

No shared JSON object, JSON schema, generated output file, or separate local
state contract is required. Resource ownership is determined from the
selected mode and the Bicep deployment/resource graph.

## Naming, Tags, and Scope

New resources must:

- use the active subscription and explicitly selected resource group;
- use a deterministic extension suffix derived from the environment name only
  when a resource name is not supplied;
- include the existing `azd-env-name` tag when an azd environment is active;
- add an extension tag such as `ai-solution-starter-extension`;
- avoid customer, source-repository, and document-review terminology; and
- avoid assuming that every extension shares the base resource group.

Extension templates may deploy at subscription or resource-group scope as
needed, but the choice must be documented and independently compilable.

## Identity and Authentication Contract

### Production and Azure-hosted usage

- Use Microsoft Entra authentication and managed identity.
- Do not use API keys, account keys, connection strings, or embedded tokens.
- Assign only the roles required for the selected extension behavior.
- Keep control-plane deployment identity separate from runtime identities.
- Do not grant broad subscription roles when a resource or resource-group
  scope is sufficient.

### Local documentation commands

Documentation may use `DefaultAzureCredential` or Azure CLI user credentials
for local development. Every example must state that:

- local credentials are developer-only;
- production workloads should use managed identity;
- the caller needs the documented data-plane role; and
- no credential value should be copied into source or environment files.

### Role ownership

Each extension owns any new role assignments it creates. It must not edit the
base RBAC matrix or role-definition file. Documentation will add an extension
RBAC matrix that distinguishes:

- deployment-principal permissions;
- local operator permissions;
- future application runtime permissions; and
- service-managed-identity permissions.

## Networking Contract

Extensions should mirror applicable baseline modes without importing or
editing baseline modules.

### Public mode

- Public network access is enabled.
- No private endpoint is created.
- Service-specific firewall defaults are explicit.
- Documentation warns that data-plane authorization still requires Entra ID
  and RBAC.

### Restricted-public mode

- Public network access remains enabled only when required by the service.
- Supported IP firewall rules are applied from extension-specific environment
  values.
- The extension must document service limitations rather than pretending all
  baseline ACL behavior maps identically.

### Generated-private mode

- The extension may create only the additional subnet, private endpoint, DNS
  zone, and links it owns.
- It may reference the base VNet through explicit environment values or
  discovered deployment outputs.
- It must not redeploy or alter the base VNet address plan.
- New subnet ranges must be explicit and collision-checked.

### Existing-VNet mode

- The extension resolves an explicitly named VNet and subnet.
- The selected subnet must satisfy private-endpoint policies and service
  requirements.
- No route table, network security group, or delegation is modified unless
  that exact change is included and approved in the extension plan.

### Existing private DNS

- Existing zone resource IDs are preferred over inferred names.
- Zone links are created only when explicitly enabled.
- Externally managed DNS mode creates no DNS zone or link.
- Documentation lists the required service-specific zone names.

### Compatibility rule

“Baseline parity” means equivalent operator choices where the service supports
them; it does not permit copying a baseline networking module or claiming
unsupported service behavior. Unsupported combinations must fail validation
or be documented as unavailable.

## Diagnostics and Observability

When diagnostics are enabled and a compatible Log Analytics destination is
provided, each newly deployed service should:

- enable supported resource logs and metrics;
- use extension-owned diagnostic setting names;
- emit the diagnostic setting resource ID;
- document category availability as provider- and API-version-dependent; and
- avoid logging document content, request bodies, model prompts, tokens, or
  credentials.

Existing-resource mode must not add or replace diagnostic settings unless an
explicit extension variable authorizes that change.

Documentation must distinguish:

- Azure resource health and activity logs;
- service data-plane metrics;
- application telemetry, which Phase 6 does not implement; and
- diagnostic settings that remain owned by the customer.

## Microsoft Foundry Extension

### Resource model

The initial Foundry extension will support:

- a compatible `Microsoft.CognitiveServices/accounts` parent with
  `kind: AIServices`;
- a child `Microsoft.CognitiveServices/accounts/projects` project;
- account and project managed identity where supported and needed;
- project metadata such as display name and generic description;
- extension-owned RBAC;
- extension-owned networking and diagnostics; and
- an optional project connection to the baseline Azure OpenAI resource when
  the selected service/API supports that connection model.

The implementation must verify current stable or supported API versions before
coding. Preview APIs may be used only when the required Foundry resource has no
supported stable equivalent, and that dependency must be documented.

### New-account mode

New-account mode will:

1. validate regional availability and provider registration;
2. create a compatible `AIServices` account;
3. configure identity and network access;
4. create one generic project;
5. add approved role assignments;
6. add diagnostics when selected;
7. optionally add the baseline Azure OpenAI connection; and
8. emit account, project, endpoint, identity, connection, and ownership
   outputs.

The extension must not deploy model capacity into the new account in the
initial increment unless a later review explicitly adds that scope.

### Existing-account mode

Existing-account mode will:

1. parse and validate the full account resource ID;
2. verify that the account kind and capabilities support Foundry projects;
3. verify location and networking compatibility;
4. create or resolve the requested project;
5. create only explicitly approved child resources, assignments, diagnostics,
   or private endpoints;
6. preserve all unrelated account settings and projects; and
7. mark the account as referenced, never extension-owned.

### Existing-project mode

When `FOUNDRY_PROJECT_RESOURCE_ID` is supplied:

- no account or project is created;
- account/project compatibility is validated;
- optional connection, RBAC, diagnostics, or networking changes require
  explicit variables;
- outputs identify both resources as referenced; and
- removal documentation performs no deletion.

### Baseline Azure OpenAI connection

The optional connection must:

- accept the base Azure OpenAI resource ID as input;
- avoid changing the base account, deployments, networking, or RBAC;
- use managed identity rather than an API key;
- identify the project or account identity that needs access;
- create only the least-privilege role assignment needed for use;
- avoid storing connection credentials; and
- fail clearly if the selected Foundry connection type cannot reference the
  baseline account.

It must not assume the existing Azure OpenAI account can itself host a Foundry
project. The Foundry project parent remains the compatible `AIServices`
account.

### Foundry documentation-only usage

`extensions/foundry/docs/USAGE.md` will include:

- Azure CLI commands to inspect the account and project;
- a minimal REST or current SDK authentication example;
- a project endpoint discovery example;
- a connection-list or connection-resolution example;
- a managed-identity token scope example;
- expected non-secret response fields;
- required operator and runtime roles;
- instructions for adapting the example to an application; and
- an explicit statement that no agent or application integration is included.

Code blocks are documentation examples, not executable repository modules.
Examples must use placeholders and environment values, not deployed resource
identifiers.

### Foundry exclusions

The initial increment will not create:

- prompt agents;
- hosted agents;
- agent versions;
- capability hosts;
- Azure AI Search stores;
- Cosmos DB thread stores;
- Storage-backed agent file stores;
- model deployments;
- evaluations;
- fine-tuning jobs; or
- base application configuration.

## Azure AI Document Intelligence Extension

### Resource model

The Document Intelligence extension will support:

- a `Microsoft.CognitiveServices/accounts` resource with
  `kind: FormRecognizer`;
- system-assigned identity where supported;
- extension-owned RBAC;
- public, restricted-public, and private network modes where supported;
- extension-owned diagnostics; and
- outputs needed for prebuilt Layout REST or SDK calls.

### New-resource mode

New-resource mode will:

1. validate provider registration, location, and SKU availability;
2. create the Document Intelligence account;
3. configure identity and approved network access;
4. add approved role assignments;
5. add diagnostics when selected; and
6. emit resource ID, endpoint, location, SKU, identity, and ownership outputs.

No training Storage account or custom model resource is created.

### Existing-resource mode

Existing-resource mode will:

1. parse and validate the full resource ID;
2. verify provider type and `FormRecognizer` kind;
3. resolve the endpoint without exposing keys;
4. validate networking compatibility;
5. add no changes by default;
6. apply extension-owned RBAC, diagnostics, or private endpoints only when
   explicitly selected; and
7. mark the service as referenced for removal.

### Prebuilt Layout usage contract

Documentation will demonstrate:

1. obtaining a Microsoft Entra token with an appropriate audience;
2. submitting a synthetic PDF to the current prebuilt Layout analyze
   operation;
3. polling the operation URL using bounded retry guidance;
4. handling success, throttling, invalid input, and terminal errors;
5. reading paragraphs, pages, tables, cells, and spans;
6. producing an application-owned normalized structure such as:

```json
{
  "content": "Normalized plain text",
  "pages": [
    {
      "page_number": 1,
      "text": "Page text"
    }
  ],
  "tables": [
    {
      "row_count": 2,
      "column_count": 3,
      "cells": []
    }
  ]
}
```

7. avoiding persistence or logging of source content by default; and
8. integrating the normalized output into a future backend or workflow.

The normalized structure is guidance, not a new base API contract.

### Document Intelligence documentation-only usage

`extensions/document-intelligence/docs/USAGE.md` will contain:

- REST examples using environment placeholders;
- a current Python or TypeScript SDK snippet;
- `DefaultAzureCredential` guidance for local use;
- managed-identity guidance for Azure-hosted use;
- the prebuilt Layout model identifier;
- asynchronous polling behavior;
- supported synthetic input guidance;
- response normalization guidance;
- role requirements; and
- troubleshooting for authorization, firewall, DNS, throttling, unsupported
  files, and regional availability.

No executable adapter package is added in Phase 6.

### Document Intelligence exclusions

The initial increment will not include:

- custom extraction models;
- training, labeling, or evaluation assets;
- training Storage;
- Storage Blob Data Contributor assignments for model training;
- application persistence;
- Logic App integration;
- document retention;
- batch processing; or
- changes to the starter's PDF intake limits.

## Azure AI Search Future Design

Azure AI Search remains a Phase 6 planning artifact only.

### Planned future goal

A later approved increment should provide an independently optional Search
extension with:

- deployment or existing-service reuse;
- RBAC-first authentication;
- baseline-parity networking;
- diagnostics;
- explicit index lifecycle ownership;
- keyword, vector, and hybrid search;
- an embedding deployment contract;
- optional Blob indexing;
- optional Foundry retrieval integration; and
- removal and data-retention guidance.

### Decisions intentionally deferred

Implementation must not start until a later review selects:

- push indexing versus Blob indexer;
- direct vectorization versus integrated vectorization;
- the embedding model and dimensions;
- index ownership and versioning;
- semantic ranker usage;
- private endpoint topology;
- Search service SKU and partition/replica expectations;
- document chunking;
- data source and skillset ownership;
- whether Foundry depends on Search;
- application or workflow integration; and
- live composition scenarios.

### Phase 6 Search deliverables

Phase 6 will add only:

- `extensions/ai-search/README.md`;
- `extensions/ai-search/FUTURE_IMPLEMENTATION_PLAN.md`;
- prerequisites and open decisions;
- proposed environment-variable names;
- proposed outputs and RBAC roles;
- proposed validation and review gates; and
- a clear `not implemented` status.

It will not add Search Bicep, scripts, package dependencies, schemas, REST
examples, SDK examples, or CI deployment jobs.

## Conditional Base Deployment

### Responsibilities

`infra/main.bicep` will:

- declare the two deploy booleans and existing-resource parameters;
- validate mutually exclusive or incomplete values;
- call the Foundry and Document Intelligence modules only when their effective
  mode is deploy or existing;
- pass resource group, location, networking, identity, RBAC, and diagnostics
  choices through explicit parameters;
- emit empty outputs when a service is skipped; and
- emit resource IDs and endpoints when a service is deployed or referenced.

### No-service behavior

When both booleans are false and no existing resource IDs are supplied:

- neither AI module is instantiated;
- no AI-service resource, role assignment, private endpoint, diagnostic
  setting, or project connection is created;
- all existing baseline resources are deployed exactly as before; and
- the pre-Phase-6 and post-Phase-6 resource graphs must match.

This is the primary compatibility proof for the conditional base deployment.

### Mixed-mode examples

The plan must support:

| Foundry | Document Intelligence | Expected behavior |
| --- | --- | --- |
| Disabled | Disabled | No-op |
| New | Disabled | Deploy Foundry only |
| Existing | Disabled | Validate/reference Foundry only |
| Disabled | New | Deploy Document Intelligence only |
| Disabled | Existing | Validate/reference Document Intelligence only |
| New | New | Deploy both independently |
| Existing | New | Reference Foundry; deploy Document Intelligence |
| New | Existing | Deploy Foundry; reference Document Intelligence |
| Existing | Existing | Validate/reference both |

No combination may introduce a hidden dependency between the services.

## Deployment State and Idempotency

Extension deployments must be repeatable.

- Bicep deployments use stable deployment names derived from environment and
  extension.
- Re-running the same selected configuration should converge.
- Existing-resource validation should not create state.
- Resource ownership must not be inferred only from resource names.
- Ownership comes from the selected deploy/existing mode and the Bicep
  deployment/resource graph.
- A failed combined run must identify which extension completed.
- Removal guidance must be safe after partial completion.

If extension state must persist beyond Azure deployment history, the
implementation must propose an ignored local state format and stop for review
before adding it.

## Removal Contract

Every extension will document removal separately for deployed and existing
modes.

### Deployed mode

Removal guidance may delete only:

- resources listed as created by the extension;
- extension-owned role assignments;
- extension-owned diagnostic settings;
- extension-owned private endpoints;
- extension-owned DNS links; and
- extension-owned project connections.

Shared resource groups must not be deleted.

### Existing mode

Removal guidance must preserve:

- the existing service;
- unrelated projects and connections;
- customer diagnostic settings;
- customer networking;
- customer role assignments; and
- customer data.

Only extension-owned child resources or assignments may be removed, and each
must be listed explicitly.

No automated destructive removal script is required in the initial
implementation. Documentation commands must require the operator to inspect
resolved resource IDs before deletion.

## Validation Strategy

### Local validation required for every increment

- compile `infra/main.bicep` and each new AI module;
- lint or format new scripts using existing repository tooling where
  applicable;
- validate parameter-file syntax;
- validate selector and resolution rules without Azure mutation;
- test typed module and top-level output behavior;
- test no-service no-op behavior;
- test contradictory and partial environment values;
- validate documentation links;
- run repository source-sanitization checks;
- run `git diff --check`;
- run `./scripts/verify_bicep_baseline.sh` against the approved manifest; and
- verify no unrelated baseline module or resource behavior changed.

### Mocked script tests

Deployment scripts should be designed so command execution can be replaced by
a fixture or command adapter. Tests must cover:

- new-resource resolution;
- existing-resource resolution;
- invalid resource IDs;
- wrong provider type or account kind;
- selectors set to false;
- malformed booleans;
- conflicting new and existing values;
- one extension failing after another succeeds;
- top-level output selection for disabled, deployed, and existing modes;
- secret-field rejection; and
- removal ownership classification.

Tests must not require an Azure subscription.

### Template validation

Each extension template must:

- compile independently;
- have an explicit target scope;
- avoid changes to protected baseline modules;
- expose documented outputs;
- pass repository naming and source-policy checks;
- support a what-if command when Azure validation is approved; and
- remain conditionally absent from the base resource graph when not selected.

### Live-Azure validation

No live validation occurs without explicit approval for that increment.

An approved validation must define:

- subscription and tenant;
- region;
- resource group and naming;
- expected billable resources;
- required providers and quotas;
- public or private networking mode;
- new or existing service mode;
- cleanup owner;
- maximum validation duration;
- evidence that may be retained; and
- resources that must be preserved.

Live tests should progress in this order:

1. Foundry new-account or approved existing-account mode;
2. Foundry project and optional baseline OpenAI connection;
3. Document Intelligence new-resource or approved existing-resource mode;
4. prebuilt Layout request using only a synthetic PDF;
5. both selected through the base deployment; and
6. cleanup or preservation verification.

No document content, response body, token, tenant-specific resource ID, or
credential is committed as evidence.

## Continuous Integration

Phase 6 implementation should add a separate extension-validation job or
workflow that:

- runs only when extension, shared validation, or relevant documentation files
  change;
- compiles additive Bicep entry points;
- tests selector logic;
- validates typed module and top-level outputs;
- checks documentation links;
- verifies the baseline checksum; and
- performs no Azure login or deployment.

The existing base application jobs must remain valid and independent.

Azure deployment workflows are excluded until live validation and publication
behavior receive separate approval.

## Documentation Requirements

The implementation will update:

- `README.md` with optional-extension status;
- `docs/README.md` with extension navigation;
- `docs/PLAN.md` with the approved Phase 6 scope;
- `docs/PHASE_TASKS.md` with independently reviewed increments;
- `docs/deployment/CONFIGURATION.md` with selectors and resource references;
- `docs/deployment/DEPLOYMENT_SEQUENCE.md` with post-base optional deployment;
- `docs/deployment/TROUBLESHOOTING.md` with extension failures;
- `docs/operations/COST_DRIVERS.md` with service-specific cost drivers;
- `docs/replacement/REPLACEMENT_GUIDE.md` with future integration boundaries;
  and
- extension-local README and operations documents.

Documentation must keep these statuses explicit:

- base infrastructure: implemented and protected;
- Phase 4 workflow: planned, not implemented;
- Foundry extension: planned until its increment is implemented;
- Document Intelligence extension: planned until its increment is implemented;
- Azure AI Search extension: planned for a later approval, not implemented.

## Security and Privacy Requirements

- No proprietary source, names, prompts, documents, endpoints, IDs, or history.
- No keys, secrets, tokens, connection strings, or SAS values.
- No source document or extracted content in telemetry or review evidence.
- Documentation examples use synthetic placeholders.
- Existing-resource validation errors redact subscription and tenant context
  where logs could be published.
- Environment-specific deployment values remain untracked.
- Role assignments are least privilege and scoped narrowly.
- Public network examples include explicit security warnings.
- Private DNS and firewall failures are surfaced rather than bypassed.
- No broad catches, silent fallbacks, or success-shaped deployment failures.

## Cost, Quota, and Region Guidance

Documentation will identify, without fixed prices:

- Foundry/AIServices account and model-related cost boundaries;
- the fact that no model deployment is included by default;
- Document Intelligence transaction/page billing;
- private endpoint and Log Analytics ingestion costs;
- regional availability and SKU constraints;
- provider registration requirements;
- quota checks required before approved deployment;
- the effect of retaining existing resources; and
- cleanup verification.

The implementation must not claim that a compiled template proves regional
capacity or service quota.

## Work Package 6.0 - Conditional Base Infrastructure Contract

### Tasks

1. Define the new base parameters and environment-variable mappings.
2. Define the `infra/modules/ai/` ownership boundaries.
3. Define existing-resource precedence and validation rules.
4. Define module outputs and top-level base outputs.
5. Add no-service resource-graph comparison tests.
6. Document naming, ownership, and removal semantics.

### Acceptance criteria

- No unrelated baseline behavior changes.
- Invalid configuration fails before Azure mutation.
- Disabled services without existing-resource references are true no-ops.
- New and existing resource ownership is unambiguous.
- Service modules contain no unrelated baseline deployment logic.
- Local tests pass.

### Review gate

Pause before implementing a service extension.

## Work Package 6.1 - Microsoft Foundry Extension

### Tasks

1. Add the Foundry module under `infra/modules/ai/`.
2. Add new-account, existing-account, and existing-project resolution.
3. Add project creation where selected.
4. Add managed identity and least-privilege RBAC.
5. Add approved networking and diagnostics modes.
6. Add the optional baseline Azure OpenAI project connection.
7. Add deploy, validate, and show scripts.
8. Add documentation-only REST/SDK usage commands.
9. Add local compilation and mocked script tests.
10. Write a Foundry implementation report.

### Acceptance criteria

- A compatible Foundry project can be planned independently.
- Existing resources are validated and preserved.
- The baseline Azure OpenAI resource is never modified.
- No agent, capability host, store, or model deployment is created.
- No application code is added.
- Local validation passes.
- Any live deployment has separate explicit approval.

### Review gate

Pause after the Foundry increment. Do not begin Document Intelligence until
the Foundry review is accepted or the user explicitly authorizes parallel
implementation.

## Work Package 6.2 - Document Intelligence Extension

### Tasks

1. Add the Document Intelligence module under `infra/modules/ai/`.
2. Add new-resource and existing-resource resolution.
3. Add managed identity and least-privilege RBAC.
4. Add approved networking and diagnostics modes.
5. Add deploy, validate, and show scripts.
6. Add prebuilt Layout REST/SDK documentation.
7. Document normalized text, page, and table handling.
8. Add local compilation and mocked script tests.
9. Write a Document Intelligence implementation report.

### Acceptance criteria

- The resource can be planned independently in new or existing mode.
- No custom model or training Storage is introduced.
- Usage examples require no committed credential.
- Existing resources are preserved by removal guidance.
- No application code is added.
- Local validation passes.
- Any live deployment has separate explicit approval.

### Review gate

Pause after the Document Intelligence increment.

## Work Package 6.3 - Azure AI Search Future Plan

### Tasks

1. Add the clearly deferred Search extension README.
2. Document the future resource, RBAC, networking, and output contracts.
3. Record unresolved indexing, vectorization, and integration decisions.
4. Define a future approval and validation gate.
5. Ensure no Search implementation artifacts are added.

### Acceptance criteria

- Search status is unmistakably `not implemented`.
- No Search resource can be deployed by Phase 6 scripts.
- No package dependency or example implies support.
- The future plan is sufficient to start a later clarification cycle.

### Review gate

Search planning may be reviewed with either service increment, but Search
implementation remains prohibited.

## Work Package 6.4 - Conditional Base Composition

### Tasks

1. Add the minimal conditional module calls to `infra/main.bicep`.
2. Pass environment-backed parameters into both AI modules.
3. Emit empty, deployed, or referenced outputs consistently.
4. Test all deploy/existing/disabled combinations without Azure.
5. Document partial deployment and rerun behavior.
6. Validate that no-service selection preserves the base resource graph.
7. Write composition review evidence.

### Acceptance criteria

- Every approved combination resolves deterministically.
- Neither extension depends on the other.
- Existing resources are never misclassified as created.
- Partial failure is explicit and recoverable.
- Conditional AI modules never change unrelated base infrastructure.
- Local composition tests pass.

### Review gate

Pause before any combined live-Azure deployment.

## Work Package 6.5 - Approved Azure Validation

### Tasks

1. Obtain explicit approval for each proposed deployment.
2. Record subscription, region, mode, networking, cost, and cleanup scope.
3. Run what-if before deployment where supported.
4. Deploy or resolve one extension at a time.
5. Run documentation-only service calls with synthetic input where approved.
6. Exercise the selected combined path.
7. Collect sanitized evidence.
8. remove only extension-owned temporary resources.
9. verify referenced resources remain unchanged.

### Acceptance criteria

- Every Azure mutation was explicitly approved.
- New and existing modes behave as documented.
- Managed identity/RBAC and networking are verified.
- Synthetic Document Intelligence Layout analysis succeeds when included.
- Foundry project and connection inspection succeeds when included.
- Cleanup or preservation is verified.
- No sensitive or proprietary evidence enters Git.

### Review gate

Live evidence does not automatically authorize production use or publication.

## Work Package 6.6 - Documentation and Final Review

### Tasks

1. Update root and documentation indexes.
2. Complete configuration, deployment, troubleshooting, cost, and replacement
   guidance.
3. Add implementation reports for completed increments.
4. Run full repository validation.
5. inspect the complete local diff and commit stack.
6. Create local-only implementation commits per approved increment.
7. Pause before push, release, or future Search implementation.

### Acceptance criteria

- Current, planned, and deferred features are accurate.
- A new team can select, deploy/reuse, inspect, and safely remove extensions.
- Baseline checksum and base validation pass.
- Extension validation passes.
- No generated environment output is tracked.
- Work remains unpushed until approved.

## Planned Task Dependencies

```text
6.0 Additive extension contract
 ├─> 6.1 Foundry extension ───────────────┐
 ├─> 6.2 Document Intelligence extension ├─> 6.4 Selector and composition
 └─> 6.3 Azure AI Search future plan ────┘       └─> 6.5 Approved Azure validation
                                                    └─> 6.6 Documentation and review
```

The Foundry and Document Intelligence increments are technically independent,
but the approved review sequence is serial. Search planning has no deployment
dependency.

## Final Phase 6 Acceptance Criteria

- Foundry and Document Intelligence are independently optional.
- Each selected extension supports new-resource and compatible
  existing-resource modes.
- Environment selection is explicit and validated.
- Conditional module calls support approved combinations within the base
  `azd provision` deployment.
- No selected services is a successful no-op for the new modules.
- Base resource behavior and graph are unchanged when no new services are
  selected.
- The approved Bicep checksum and manifest policy pass after any reviewed
  additive wiring change.
- Managed identity and least-privilege RBAC are the production contract.
- Applicable baseline networking choices are represented without changing the
  base network.
- Diagnostics, cost drivers, quotas, regions, and removal are documented.
- Foundry usage is documentation-only and creates no agent.
- Document Intelligence demonstrates prebuilt Layout through documentation,
  not application code.
- Azure AI Search is clearly planned but not implemented.
- Local validation passes for every completed increment.
- Azure deployment occurs only after explicit approval.
- Proprietary content and environment-specific outputs remain absent.
- Each increment pauses for review and remains unpushed until approved.

## Stop Conditions

Stop and request review if:

- any implementation exceeds the approved additive `infra/modules/ai/` and
  `infra/main.bicep` wiring scope;
- an existing baseline module or resource behavior must be changed;
- current Foundry resources cannot be deployed without Standard Agent Setup,
  capability hosts, or stores;
- an existing Azure OpenAI connection requires a key or base-resource
  modification;
- a requested role exceeds the approved least-privilege scope;
- a service cannot support the selected network mode;
- a private endpoint requires modification of a baseline subnet, route table,
  NSG, or DNS resource;
- existing-resource compatibility cannot be validated before mutation;
- output ownership cannot distinguish created and referenced resources;
- Document Intelligence prebuilt Layout requires custom training resources;
- any Search infrastructure or example becomes necessary;
- an extension dependency must be added to the base backend or frontend;
- live validation would create billable resources without explicit approval;
- regional support, quota, or provider registration blocks the approved
  deployment;
- cleanup could delete a shared or referenced resource;
- source content, extracted content, identifiers, endpoints, or credentials
  would enter Git or published logs;
- local validation cannot prove no-service no-op behavior; or
- proprietary content or source history is detected.
