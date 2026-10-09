# Phase 4 Implementation Plan

## Status

**Planning complete; awaiting approval.** This document defines the proposed
Logic Apps Standard and Azure OpenAI implementation. It does not authorize
implementation, deployment, a push, or any Bicep change.

Phase 2 and Phase 3 remain local and unpushed. Phase 4 implementation must be
added only after this plan is explicitly approved.

## Objective

Implement a generic, replaceable document-processing workflow that completes
the starter's PDF vertical slice:

1. detect a newly stored work-item PDF;
2. correlate the blob to its Cosmos DB work-item record;
3. wait for the backend to finish the `submitted -> queued` transition;
4. claim queued work with optimistic concurrency;
5. load versioned instructions from Blob Storage;
6. send the PDF directly to the configured vision-capable Azure OpenAI
   deployment;
7. validate a strict structured response;
8. persist an explicit `completed` or `failed` state; and
9. expose the result through the existing backend and frontend contracts.

The implementation must adapt to the Phase 1 infrastructure exactly as it
exists. It must not modify, optimize, reorganize, or replace any Bicep file.

## Approved Decisions

| Decision | Phase 4 direction |
| --- | --- |
| Trigger | Azure Blob Storage: blob added or updated |
| Trigger scope | `work-items/<work-item-id>/source.pdf` in the configured input container |
| Workflow concurrency | One trigger run at a time |
| PDF processing | Azure OpenAI Responses API with inline base64 PDF input |
| Azure authentication | Existing user-assigned managed identity; no keys |
| Prompt source | Existing instruction Blob container and configured filenames |
| Result fields | `summary`, `category`, and `key_points` |
| Categories | `informational`, `action_required`, `reference`, `other` |
| State claim | ETag-protected `queued -> processing` replacement |
| Terminal persistence | ETag-protected `processing -> completed/failed` replacement |
| Deployment validation | Local/package validation first; Azure deployment only after explicit approval |
| Input validation scope | Synthetic PDFs only; text submission remains excluded |

## Phase Boundaries

### Included

- deployable Logic Apps Standard package under `app/agent/workflows`
- generic system and processing instruction files
- managed-identity built-in Blob and Cosmos connections
- Blob-added-or-updated trigger
- exact blob-path validation and work-item ID extraction
- bounded handling of the blob-created-before-queued race
- cross-partition Cosmos lookup by validated work-item ID
- ETag-protected processing claim
- PDF and instruction reads from Blob Storage
- Azure OpenAI Responses API call through the HTTP action
- inline `data:application/pdf;base64,...` file input
- strict JSON Schema structured output
- result parsing and validation
- completed and failed state persistence
- action retries for transient dependencies
- workflow tracking properties and safe operational logging
- package, contract, fixture, and regression validation
- instruction upload integration in local and GitHub deployment paths
- optional deployed synthetic-PDF validation after approval
- workflow replacement-boundary documentation

### Excluded

- every Bicep change
- new Azure resources, identities, roles, connectors, or application settings
- Cosmos DB indexing or partition-key changes
- backend public endpoint changes
- text, image, Office document, or multi-file intake
- PDF text extraction through Document Intelligence or another service
- Azure OpenAI keys, Storage keys, Cosmos keys, connection strings, or SAS
  tokens
- Azure OpenAI Files API uploads
- the built-in Azure OpenAI chat connector
- human review, approval, retry, cancel, delete, or requeue UI actions
- workflow-triggered callbacks to the backend
- automatic recovery of indefinitely stale `processing` records
- parallel work-item processing
- prompt editing in the application UI
- deployment before explicit approval
- Phase 5 starter hardening
- Phase 6 Foundry, AI Search, and Document Intelligence optional services

## Immutable Contracts

### Infrastructure

- Do not modify any file under `infra/`.
- Preserve `infra/bicep-baseline.sha256`.
- Use the existing Logic Apps Standard resource and elastic App Service plan.
- Use the existing input and instruction Blob containers.
- Use the existing Cosmos DB account, database, and work-item container.
- Use the existing vision-capable Azure OpenAI deployment.
- Use the existing user-assigned Logic App identity.
- Use the existing networking, diagnostics, and private-access behavior.
- Do not add an Event Grid resource, Service Bus resource, Function App,
  connector resource, or application setting.

### Existing Logic App settings

The workflow must consume the settings already supplied by the baseline:

| Setting | Use |
| --- | --- |
| `AZURE_STORAGE_ENDPOINT` | Built-in Blob connector endpoint |
| `AZURE_STORAGE_INPUT_CONTAINER` | Work-item PDF container |
| `AZURE_STORAGE_INSTRUCTIONS_CONTAINER` | Prompt asset container |
| `AZURE_STORAGE_SYSTEM_INSTRUCTIONS_FILE` | Generic system instructions |
| `AZURE_STORAGE_PROCESSING_INSTRUCTIONS_FILE` | Generic processing instructions |
| `AZURE_COSMOS_ACCOUNT_URI` | Built-in Cosmos connector endpoint |
| `AZURE_COSMOS_DATABASE` | Work-item database |
| `AZURE_COSMOS_CONTAINER` | Work-item container |
| `AZURE_OPENAI_ENDPOINT` | Responses API resource endpoint |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Vision-capable deployment name |
| `WORKFLOWS_IDENTITY_RESOURCE_ID` | User-assigned managed identity |

`AZURE_STORAGE_EVALUATION_INSTRUCTIONS_FILE`,
`AZURE_OPENAI_MODEL_NAME`, `AZURE_OPENAI_MODEL_VERSION`,
`AZURE_OPENAI_RESOURCE_ID`, and
`AZURE_COSMOS_CONNECTIONRUNTIMEURL` remain available but are not required by
the initial generic workflow.

The pre-created `documentdb` managed API connection must remain untouched. The
workflow will prefer the Standard built-in Cosmos connector because it accepts
the existing account URI and managed identity directly and exposes ETag-aware
item operations. This is an application-package choice, not an infrastructure
change.

### Backend and Blob contract

The backend creates records and blobs in this order:

```text
create Cosmos record as submitted
  -> upload work-items/<id>/source.pdf
  -> replace Cosmos record as queued
```

The workflow must treat the blob path as an untrusted correlation hint. A
trigger is eligible only when all conditions are true:

- the configured container is the input container;
- the normalized path exactly matches
  `work-items/<uuid>/source.pdf`;
- the extracted identifier is a canonical UUID;
- exactly one Cosmos item with that identifier is found;
- the record's `source.blob_name` exactly matches the triggered blob path;
- the record's `source.content_type` is `application/pdf`; and
- the record's source size remains within the backend's 20 MB limit.

Invalid or unrelated blob paths are ignored without reading content or
updating Cosmos.

### Cosmos contract

- Partition key: `/created_at`
- `created_at` is immutable and must be supplied for point writes.
- The workflow must preserve all unknown record fields.
- The workflow must preserve owner and idempotency fields.
- Every valid state transition increments `version` once.
- Every valid state transition refreshes `updated_at` in UTC.
- `_etag` is used for optimistic concurrency and is never persisted as a user
  property.
- A `412 Precondition Failed` or equivalent connector conflict means another
  writer won; the workflow must re-read and make a status-based decision.

The workflow may make a cross-partition query only to discover the record and
its `created_at` partition key:

```sql
SELECT TOP 2 * FROM c WHERE c.id = '<validated-uuid>'
```

The UUID must pass strict validation before interpolation. Returning zero or
more than one item is an explicit correlation failure. After discovery, all
reads and writes must use the item ID and `created_at` partition key.

### Lifecycle contract

The workflow owns only these transitions:

```text
queued -> processing
processing -> completed
processing -> failed
```

The workflow must not transition:

- `submitted` directly to `processing`;
- `submitted` directly to `failed`;
- `queued` directly to `completed`;
- `queued` directly to `failed` unless a future approved contract explicitly
  assigns that responsibility;
- either terminal state to any other state; or
- a record whose current ETag no longer matches.

Terminal records and records already in `processing` are idempotent no-ops for
duplicate Blob trigger deliveries.

## Proposed Repository Structure

```text
app/agent/
├── README.md
├── deploy.sh
├── instructions/
│   ├── system.md
│   └── processing.md
├── tests/
│   ├── fixtures/
│   │   ├── blob-trigger.json
│   │   ├── queued-work-item.json
│   │   ├── openai-success.json
│   │   └── openai-invalid-output.json
│   └── test_workflow_package.py
└── workflows/
    ├── host.json
    ├── connections.json
    ├── parameters.json
    ├── azure.parameters.json
    └── process-document/
        └── workflow.json
```

Supporting deployment and validation changes may be added to:

```text
.github/actions/logicapp-deploy/action.yml
.github/workflows/application-ci.yml
.github/workflows/azure-dev.yml
scripts/deploy_app.sh
scripts/verify_logic_app_package.py
docs/deployment/DEPLOYMENT_SEQUENCE.md
docs/replacement/
docs/reviews/
```

The exact validation-script location may be consolidated during
implementation, but workflow definitions, fixtures, and generic instructions
must remain separate from backend and frontend source.

## Logic Apps Standard Package Contract

### Package root

The existing GitHub workflow passes `app/agent/workflows/` to the deployment
action. That directory is therefore the zip package root and must contain
`host.json`, connections, parameters, and workflow directories directly.

The deployment action's current parameter swap remains authoritative:

1. save local `parameters.json`;
2. rename `azure.parameters.json` to `parameters.json`;
3. zip the package;
4. restore both files even when packaging fails.

Phase 4 implementation must harden cleanup so an interrupted package step
cannot leave the worktree with swapped or missing parameter files.

### Local parameters

`parameters.json` must permit package validation and Logic Apps local tooling
without embedding real resource identifiers, endpoints, secrets, or customer
values. Placeholder values must be visibly synthetic.

### Azure parameters

`azure.parameters.json` must use `@appsetting(...)` references for every
environment-specific value. It must not duplicate values from Bicep or
introduce settings that the baseline does not provide.

### Connections

`connections.json` must define service-provider connections for:

- Azure Blob Storage using `AZURE_STORAGE_ENDPOINT`;
- Azure Cosmos DB using `AZURE_COSMOS_ACCOUNT_URI`; and
- the user-assigned identity referenced by
  `WORKFLOWS_IDENTITY_RESOURCE_ID`.

No credential material may appear in the package. Connection validation must
fail rather than silently fall back to keys or connection strings.

## Instruction Asset Contract

### Files

The starter will provide two generic, sanitized files:

- `system.md`: role, safety, grounding, and output-quality constraints;
- `processing.md`: document-summary, classification, and key-point task.

The configured evaluation instruction filename remains reserved for later
phases and is not used by this workflow.

### Deployment

Local and GitHub deployment paths must upload the two instruction files to the
existing instruction container using Azure CLI login authentication:

```text
system.md     -> configured system instruction blob name
processing.md -> configured processing instruction blob name
```

Uploads may overwrite prior versions because the repository files are the
versioned deployment source. Deployment must:

- authenticate with Microsoft Entra ID;
- avoid account keys and generated SAS tokens;
- set a text content type;
- fail explicitly when the target container or data-plane permission is
  unavailable; and
- upload instructions before enabling the new workflow package.

No instruction content may be printed to logs.

### Runtime behavior

Every claimed work item reads both instruction blobs. Missing, empty, or
unreadable instructions are terminal processing failures; there is no embedded
production fallback. This keeps the deployed prompt explicit and replaceable.

## Trigger and Correlation Design

### Trigger

Use the Standard built-in Azure Blob Storage trigger:

```text
When a blob is added or updated
```

Configure it against the existing input container with the narrowest supported
`work-items/` path. Apply a trigger condition or the first workflow guard so
unrelated paths terminate before any dependency reads.

Trigger concurrency is one. This is an intentional starter simplification,
not a throughput target.

### Duplicate delivery

The trigger is treated as at-least-once. Duplicate events are expected.
Correctness comes from current record status and ETag checks, not from assuming
one event per blob.

### Blob/queued race

The backend uploads the blob before replacing the record as `queued`, so the
trigger can observe a valid record still in `submitted`.

The workflow must use a bounded readiness loop:

1. query and validate the work-item record;
2. if status is `submitted`, delay and re-read;
3. stop waiting as soon as the status changes;
4. proceed only when the current status is `queued`;
5. treat `processing`, `completed`, or `failed` as an idempotent no-op; and
6. fail the workflow visibly if the record remains `submitted` beyond the
   approved readiness window.

The initial implementation target is a short delay with a total readiness
window of approximately two minutes. Exact intervals must be constants in the
workflow package and covered by package tests.

The timeout must not mutate a `submitted` record. That state is still owned by
the backend's create/compensation sequence. An observed timeout is an
operational failure requiring investigation rather than a fabricated workflow
terminal result.

### Claim

For a `queued` record:

1. preserve the complete document;
2. set `status` to `processing`;
3. clear stale `result` and `error` values;
4. increment `version`;
5. set `updated_at` to UTC;
6. replace the item with its current ETag; and
7. retain the returned ETag for terminal persistence.

If the claim conflicts:

- re-read the item;
- terminate successfully when it is now `processing`, `completed`, or
  `failed`;
- retry the claim only if it is still `queued` and the retry budget remains;
- never invoke Azure OpenAI before a successful claim.

## Blob Read and PDF Transfer

After the claim succeeds, the workflow reads:

1. the source PDF from the exact `source.blob_name`;
2. the configured system instruction file; and
3. the configured processing instruction file.

The source content must remain in workflow memory only for the active run. It
must not be written to run outputs, logs, another Blob, Cosmos, or a diagnostic
message.

The PDF is sent inline as:

```text
data:application/pdf;base64,<base64-content>
```

The implementation must verify the connector's content representation and
must encode binary content exactly once. A package test must reject expressions
that would base64-encode an already encoded connector body.

The 20 MB backend limit implies an approximately 26.7 MB base64 payload before
JSON overhead. Deployed validation must confirm that this remains within the
effective Logic Apps action and Azure OpenAI request limits. If the accepted
20 MB contract cannot be processed inline, implementation must stop for design
review; it must not silently lower the backend limit or switch to the Files
API.

## Azure OpenAI Request Contract

### Endpoint and identity

Use an HTTP `POST` action against:

```text
<AZURE_OPENAI_ENDPOINT>/openai/v1/responses
```

Normalize the endpoint to avoid a duplicate slash. Use:

- the configured deployment name as `model`;
- the existing user-assigned managed identity;
- the Azure AI token audience corresponding to
  `https://ai.azure.com/.default`;
- `Content-Type: application/json`; and
- no API key or query-string API version.

The implementation must confirm managed-identity token acquisition in deployed
validation. Failure must not fall back to a secret.

### Request

The request must contain:

- system instructions loaded from Blob Storage;
- processing instructions loaded from Blob Storage;
- one user message with the source PDF as `input_file`;
- a short text instruction tying the file to the processing task;
- the strict output format below;
- bounded output tokens; and
- `store: false` when supported by the deployed Responses API contract.

The workflow must not include owner identifiers, idempotency hashes, storage
URLs, or Cosmos metadata in the model request.

### Structured output

Use Responses API structured output through `text.format` with strict JSON
Schema. The logical schema is:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["summary", "category", "key_points"],
  "properties": {
    "summary": {
      "type": "string"
    },
    "category": {
      "type": "string",
      "enum": [
        "informational",
        "action_required",
        "reference",
        "other"
      ]
    },
    "key_points": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
```

The instruction contract further requires:

- a concise plain-text summary;
- three to five concise key points when supported by the document;
- no Markdown requirement;
- no HTML;
- no invented facts;
- `other` when no more specific category is grounded; and
- no source-content quotation longer than necessary for a concise key point.

### Response extraction

The workflow must:

1. require an HTTP success response;
2. inspect the Responses API status;
3. reject incomplete, refused, or content-filtered output as an explicit
   processing failure;
4. extract the `output_text` content from the response shape;
5. parse it as JSON;
6. validate required fields, exact category membership, field types, and
   reasonable starter bounds; and
7. persist only the validated object.

Raw model output and the complete API response must not be persisted in Cosmos
or copied into user-visible errors.

## Persisted Result Contract

A completed work item stores:

```json
{
  "summary": "A concise grounded summary.",
  "category": "informational",
  "key_points": [
    "First grounded point.",
    "Second grounded point.",
    "Third grounded point."
  ]
}
```

The workflow must persist exactly these result fields for the starter. The
existing frontend already renders `summary` and `category` explicitly and
renders `key_points` through its bounded safe fallback.

Completion persistence must:

- start from the latest successfully claimed record;
- set `status` to `completed`;
- set `result` to the validated object;
- set `error` to `null`;
- increment `version`;
- update `updated_at`; and
- use the current ETag.

A completion-write conflict requires a re-read:

- `completed` means idempotent success;
- `failed` means another terminal writer won and this run must not overwrite it;
- `processing` permits a bounded retry only when the record still represents
  this claim's expected version;
- every other state is a visible contract failure.

## Failure Contract

### Public processing error

After a successful `processing` claim, unrecoverable processing failures must
attempt an ETag-protected transition to:

```json
{
  "status": "failed",
  "result": null,
  "error": {
    "code": "stable_machine_code",
    "message": "Safe user-facing explanation.",
    "retryable": false,
    "occurred_at": "UTC timestamp"
  }
}
```

Initial stable codes:

| Code | Meaning | Default retryable |
| --- | --- | --- |
| `instruction_read_failed` | Required instruction asset unavailable | `true` for transient dependency failures |
| `source_read_failed` | Source PDF unavailable after claim | `true` for transient dependency failures |
| `source_contract_invalid` | Stored source metadata or content is invalid | `false` |
| `ai_request_failed` | Azure OpenAI request failed after retries | based on final status |
| `ai_response_incomplete` | Model did not produce a complete usable response | `true` |
| `ai_response_invalid` | Structured output failed validation | `false` |
| `result_persistence_failed` | Reserved for operational reporting; cannot be reported as persisted success | `true` |

Messages must be generic and must not include source text, prompt text, model
output, bearer tokens, endpoints, account names, Blob paths, stack traces, or
connector response bodies.

### Pre-claim failures

Failures before the workflow owns the item must not write `failed`:

- unrelated or malformed blob path: ignored;
- record not yet visible: bounded retry, then workflow failure;
- record remains `submitted`: workflow failure;
- terminal or already-processing record: idempotent no-op;
- claim conflict: re-read and decide from current state.

### Persistence failure

Failure to persist either terminal state must leave the Logic App run failed.
The workflow must retry transient Cosmos errors and record safe tracking
properties, but it must never report success when the item remains
`processing`.

Automatic stale-processing recovery is outside Phase 4. The limitation and
manual diagnosis path must be documented for Phase 5 hardening.

## Retry and Timeout Policy

| Operation | Retry direction |
| --- | --- |
| Blob-trigger readiness | Bounded delay/re-read for the backend queue race |
| Cosmos query/read | Retry `408`, `429`, and `5xx` with bounded exponential backoff |
| ETag conflict | Re-read status; never blind-retry stale content |
| Instruction and PDF reads | Retry `408`, `429`, and `5xx` |
| Azure OpenAI | Retry `408`, `429`, and `5xx`; honor service delay where supported |
| JSON/schema validation | Do not retry the same response |
| Terminal Cosmos write | Retry transient failures; handle conflicts by re-read |
| Authentication/authorization | Do not repeatedly retry deterministic `401/403` failures |

Retry counts and delays must be explicit in `workflow.json` and asserted by
package tests. No scope may use an unbounded retry.

## Workflow Scope Design

The workflow should use named scopes so run history exposes the phase that
failed without exposing content:

```text
Validate_Trigger
  -> Correlate_Work_Item
  -> Wait_For_Queued
  -> Claim_Processing
  -> Load_Instructions_And_Source
  -> Invoke_Azure_OpenAI
  -> Validate_Result
  -> Persist_Completed

Handle_Claimed_Failure
  runs after failure/timeout/skipped states from claimed processing scopes
  -> classify safe error
  -> persist failed
  -> terminate failed
```

The failure handler must be gated by a successful claim flag. It must never
mutate a record that the workflow did not claim.

## Idempotency and Concurrency Invariants

The implementation is correct only if all invariants hold:

1. Azure OpenAI is not called before `queued -> processing` succeeds.
2. A duplicate Blob event for `processing`, `completed`, or `failed` performs
   no model call.
3. Every Cosmos replacement uses the ETag from the record version it modifies.
4. A conflict causes a re-read before any decision.
5. A terminal item is never overwritten.
6. The partition key never changes.
7. One trigger run at a time is configured in the starter.
8. A workflow run that cannot persist its terminal result is failed, not
   succeeded.

Single-run concurrency reduces load and simplifies demonstration behavior but
does not replace the ETag invariants.

## Observability Contract

### Correlation

Use the work-item ID as the cross-service correlation identifier. Add custom
tracking properties to major scopes and external actions:

- `work_item_id`
- `workflow_phase`
- `work_item_status`
- `work_item_version`
- `dependency`
- `outcome`
- safe error code

Where available, retain service request/activity IDs for operational
diagnostics without returning them through the public result.

### Prohibited telemetry

Do not log or track:

- PDF content or base64;
- source filename when not necessary;
- prompt or instruction content;
- Azure OpenAI request or response bodies;
- summary or key-point content;
- owner ID;
- idempotency key or hash;
- bearer tokens, keys, SAS tokens, or connection strings;
- complete Blob paths; or
- complete Cosmos records.

Run-history secure inputs and secure outputs must be enabled for actions that
hold document, instruction, authentication, or model content where the Logic
Apps runtime supports those settings.

## Backend and Frontend Compatibility

No new public route is planned. The existing backend reads the workflow's
Cosmos updates and continues to expose:

- full work-item detail;
- status polling;
- completed result; and
- safe processing error.

Phase 4 may add backend model tests that prove the exact result and failure
documents deserialize correctly. It must not add a workflow callback endpoint
or broaden public persistence fields.

The frontend requires no functional change for the approved result. A focused
test should confirm that `key_points` renders through the existing bounded,
text-only result component.

## Validation Strategy

### Package validation

Add a repository-owned validation script and tests that:

- parse every JSON package file;
- verify required package files and workflow directory layout;
- reject unresolved deployment placeholders in Azure parameters;
- reject secrets and key-based connection settings;
- verify all Azure values come from existing app settings;
- verify trigger concurrency is one;
- verify the exact Blob path guard;
- verify readiness-loop bounds;
- verify ETag use on claim and terminal writes;
- verify required retry policies;
- verify secure input/output settings on content-bearing actions;
- verify the Responses API path and managed-identity authentication;
- verify no API key and no deprecated deployment URL are used;
- verify the structured output schema and category enum;
- verify failure handling is gated by a successful claim;
- verify instruction file mappings; and
- verify fixtures satisfy or violate contracts as intended.

### Regression validation

Run:

- Phase 2 Python formatting, type checks, and tests;
- Phase 3 frontend lint, type checks, tests, and production build;
- Logic App package tests;
- combined backend container probe when application source changes;
- `./scripts/verify_bicep_baseline.sh`;
- `git diff --check`;
- secret and prohibited-identifier scans; and
- complete staged-diff inspection.

### Local workflow tooling

If Azure Functions Core Tools with Logic Apps Standard support is available,
start the workflow locally with synthetic settings and mocked external
endpoints only when this can be done without storing credentials or calling
production services. Package validation must not depend exclusively on that
optional tool.

### Deployed validation

Deployment is a separate approval gate. After approval:

1. select an approved region with Logic Apps Standard capacity;
2. provision or reuse an explicitly approved disposable environment;
3. upload generic instruction assets;
4. deploy the workflow package;
5. submit a small synthetic PDF through the public application;
6. verify Blob trigger execution;
7. verify `queued -> processing -> completed`;
8. verify the exact `summary`, `category`, and `key_points` result shape;
9. verify the UI displays the result;
10. deliver a duplicate Blob event or equivalent controlled replay and verify
    no second model call;
11. exercise one controlled post-claim failure and verify safe `failed`
    persistence;
12. inspect correlation and secure run-history behavior;
13. verify no keys or content appear in logs;
14. rerun Bicep and repository-hygiene checks; and
15. remove the disposable environment and purge recoverable resources when
    required.

The deployed test uses synthetic PDFs only. It does not submit synthetic text.

### Large-PDF acceptance

The first deployed validation may use a small PDF. Before Phase 4 is considered
fully compatible with the Phase 2 API contract, validate an approved synthetic
PDF near the 20 MB limit or obtain measured platform-limit evidence proving the
inline request path can carry it.

The measurement must use the actual PDF byte size and actual serialized request
size. It must not estimate from unrelated artifacts.

## Work Package 4.0 - Establish Workflow Package and Tooling

### Tasks

1. Create the Logic Apps Standard package root.
2. Add `host.json`, local parameters, Azure parameters, and connections.
3. Add package validation tooling and fixtures.
4. Harden deployment parameter swapping and cleanup.
5. Add package validation to application CI.

### Acceptance criteria

- The package zips from `app/agent/workflows`.
- Local and Azure parameter files have distinct safe purposes.
- No endpoint, resource ID, credential, or private identifier is hard-coded.
- Invalid package structure fails CI.
- Packaging cannot leave parameter files swapped.

## Work Package 4.1 - Add Generic Instruction Assets

### Tasks

1. Write generic sanitized system instructions.
2. Write generic summary/classification/key-point instructions.
3. Add local managed-identity upload behavior.
4. Add GitHub deployment upload behavior.
5. Document downstream prompt replacement.

### Acceptance criteria

- Instructions are generic and contain no source-project language.
- Deployment uses Entra authentication and the existing container.
- Missing permission or missing container fails explicitly.
- Runtime has no hidden embedded prompt fallback.

## Work Package 4.2 - Implement Trigger and Correlation

### Tasks

1. Configure the built-in Blob trigger.
2. Set trigger concurrency to one.
3. Validate the exact work-item source path.
4. Extract and validate the UUID.
5. Query Cosmos for the record and partition key.
6. Validate record/source/blob correlation.
7. Add duplicate-event no-op behavior.

### Acceptance criteria

- Unrelated blobs perform no dependency or model work.
- Malformed IDs cannot enter a Cosmos query.
- Zero or ambiguous record matches fail visibly.
- Existing terminal and processing records do not invoke Azure OpenAI.

## Work Package 4.3 - Bridge Readiness and Claim Processing

### Tasks

1. Implement the bounded `submitted` readiness loop.
2. Re-read current status after every delay.
3. Build the complete `processing` replacement document.
4. Claim with ETag.
5. Handle conflict through re-read and status decisions.

### Acceptance criteria

- The expected Blob/backend race does not lose normal submissions.
- `submitted` is never mutated by the workflow.
- Azure OpenAI is not called without a successful claim.
- Duplicate and competing runs cannot both claim one queued item.

## Work Package 4.4 - Read PDF and Instructions

### Tasks

1. Read the exact source Blob after claim.
2. Read configured system and processing instruction Blobs.
3. Configure secure action inputs and outputs.
4. Verify binary/base64 representation.
5. Enforce source metadata and size contracts.

### Acceptance criteria

- Only the correlated PDF is read.
- Content is encoded exactly once.
- PDF and prompt content do not appear in run history or logs.
- Missing or invalid assets enter the claimed failure path.

## Work Package 4.5 - Invoke Azure OpenAI

### Tasks

1. Build the Responses API request.
2. Configure user-assigned managed-identity authentication.
3. Add inline PDF input and Blob-hosted instructions.
4. Add strict structured output.
5. Add bounded retries and timeout.
6. Classify service, refusal, filter, and incomplete responses.

### Acceptance criteria

- Request uses `/openai/v1/responses`.
- Request uses the configured deployment name.
- No API key or API-version setting is introduced.
- Schema requires only approved result fields.
- Transient and deterministic failures are distinguished.

## Work Package 4.6 - Validate and Persist Terminal State

### Tasks

1. Extract and parse output JSON.
2. Validate fields, types, category, and bounds.
3. Persist ETag-protected completion.
4. Implement the claimed failure scope.
5. Persist safe structured errors.
6. Handle terminal-write conflicts explicitly.

### Acceptance criteria

- Invalid output is never stored as completed.
- Completed records contain the exact result contract.
- Failed records contain no raw dependency content.
- Terminal records are never overwritten.
- Persistence failure leaves the workflow run failed.

## Work Package 4.7 - Add Observability

### Tasks

1. Add safe tracking properties to major scopes.
2. Correlate by work-item ID.
3. Capture safe dependency activity IDs.
4. Secure content-bearing action history.
5. Document common failure codes and diagnosis.

### Acceptance criteria

- Operators can locate a run from a work-item ID.
- Operators can identify the failed phase and safe error code.
- Content, prompts, results, and credentials are absent from telemetry.
- Diagnostics rely on existing infrastructure settings.

## Work Package 4.8 - Test Contracts and Regressions

### Tasks

1. Test package structure and parameter mapping.
2. Test path and UUID guards.
3. Test readiness and duplicate-delivery contracts.
4. Test ETag and retry configuration.
5. Test valid and invalid Azure OpenAI fixtures.
6. Test result compatibility in backend and frontend.
7. Run existing backend and frontend validation.
8. Verify Bicep checksums and repository hygiene.

### Acceptance criteria

- Workflow contract tests fail on removal of a critical guard.
- Existing backend and frontend behavior remains green.
- Bicep is byte-for-byte unchanged.
- No proprietary content, identifiers, history, or generated secrets are
  introduced.

## Work Package 4.9 - Deploy and Validate After Approval

### Tasks

1. Obtain explicit deployment approval.
2. Confirm region capacity and environment cleanup plan.
3. Provision or select the approved environment.
4. Upload instructions and deploy the workflow.
5. Run success, duplicate, failure, and size-limit scenarios.
6. Collect safe review evidence.
7. Remove the temporary environment when required.

### Acceptance criteria

- Deployment was explicitly approved.
- Synthetic PDF completes through UI, backend, Blob, workflow, AI, and Cosmos.
- Duplicate delivery produces no duplicate AI processing.
- Controlled failure persists a safe terminal error.
- Measured payload behavior supports the accepted PDF contract.
- Cleanup is complete and recorded.

## Work Package 4.10 - Document and Review

### Tasks

1. Update the workflow README.
2. Document replaceable prompts and workflow boundaries.
3. Document deployment and troubleshooting.
4. Write the Phase 4 implementation report.
5. Inspect the complete local commit stack and diff.
6. Create a local-only implementation commit.
7. Pause before push or Phase 5.

### Acceptance criteria

- Downstream teams know what to replace and what to preserve.
- Known Blob-trigger and stale-processing limitations are explicit.
- Review evidence contains no document or prompt content.
- Implementation remains unpushed until approved.

## Planned Task Dependencies

```text
4.0 Workflow package and tooling
 ├─> 4.1 Generic instruction assets
 └─> 4.2 Trigger and correlation
      └─> 4.3 Readiness and processing claim
           └─> 4.4 PDF and instruction reads
                └─> 4.5 Azure OpenAI invocation
                     └─> 4.6 Terminal persistence
                          └─> 4.7 Observability
                               └─> 4.8 Tests and regressions
                                    └─> 4.9 Approved deployed validation
                                         └─> 4.10 Documentation and review
```

Instruction authoring and trigger implementation may proceed in parallel after
package scaffolding. Azure OpenAI work begins only after the processing claim
and content-read contracts are testable.

## Review Artifacts

The Phase 4 implementation review must include:

- workflow package inventory;
- app-setting and connection mapping;
- sanitized instruction files;
- trigger path and correlation contract;
- readiness-loop evidence;
- ETag claim and terminal-write evidence;
- exact Responses API request shape with content removed;
- strict output schema;
- retry and failure matrix;
- secure input/output inventory;
- workflow package test inventory and results;
- backend and frontend regression results;
- Bicep checksum result;
- privacy, secret, identifier, and history scan results;
- optional deployed validation evidence when approved; and
- complete unpushed commit diff.

## Final Phase 4 Acceptance Criteria

- A valid work-item PDF triggers the Logic App.
- The Blob/backend queue race is handled without mutating `submitted`.
- Queued work is claimed exactly once with ETag concurrency.
- PDF and instructions are read with managed identity.
- Azure OpenAI receives the PDF through the Responses API.
- Output is strictly validated as summary, category, and key points.
- Completion and failure states preserve the existing Cosmos contract.
- Duplicate deliveries do not repeat model processing.
- Content and credentials are excluded from telemetry and Git.
- Existing backend and frontend behavior remains compatible.
- Local package and regression validation passes.
- Approved deployed validation passes when that gate is exercised.
- Bicep remains unchanged.
- Implementation remains unpushed until explicitly approved.

## Stop Conditions

Stop and request review if:

- any requirement appears to need a Bicep change;
- Blob trigger support requires a new connector resource or Event Grid
  resource;
- the built-in connector cannot authenticate with the existing user-assigned
  identity;
- Cosmos ETag replacement is unavailable in the deployable connector shape;
- the blob event cannot be correlated without changing the backend contract;
- the readiness loop cannot reliably bridge the backend queue race;
- the Azure OpenAI deployment does not support Responses API PDF input and
  strict structured outputs;
- managed identity cannot obtain the required Azure AI token;
- inline request limits cannot support the accepted 20 MB PDF contract;
- secure inputs/outputs cannot prevent document or prompt content from entering
  run history;
- terminal persistence cannot preserve unknown record fields and ETag
  semantics;
- instruction upload would require account keys or secrets;
- deployed validation would create or modify Azure resources without explicit
  approval;
- regional Logic Apps Standard capacity is unavailable; or
- any proprietary content, identifier, or source history is detected.
