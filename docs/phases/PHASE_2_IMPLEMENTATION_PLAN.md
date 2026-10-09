# Phase 2 Implementation Plan

## Status

**Implemented locally; pending review.** The Phase 2 backend implementation is
complete in an unpushed local commit. Phase 3 must not begin and this
implementation must not be pushed until the review gate is explicitly
approved.

## Objective

Implement the generic backend and data contracts for a PDF-based AI work-item
starter. The backend will accept authenticated PDF uploads, establish
observable work-item state in Cosmos DB, store source PDFs in Blob Storage, and
provide owner-scoped read APIs for later frontend and Logic App phases.

Phase 2 must adapt to the immutable Phase 1 infrastructure contract. It must
not modify Bicep, infrastructure parameters, role assignments, networking, or
deployment behavior.

## Approved Decisions

| Decision | Phase 2 direction |
| --- | --- |
| Framework | Quart asynchronous Python API |
| Input type | PDF files only |
| Maximum PDF size | 20 MB |
| Creation sequence | Create submitted record, upload blob, mark queued |
| Lifecycle | `submitted`, `queued`, `processing`, `completed`, `failed` |
| Idempotency | Required `Idempotency-Key` header |
| Authentication | App Service Easy Auth identity in Azure; explicit local-development bypass |
| Visibility | Owners can read only their own work items |
| Health access | Anonymous, with no sensitive dependency detail |
| API prefix | `/api/v1` |
| Pagination | Opaque Cosmos continuation token |
| List behavior | Newest first with optional status filter |
| Validation | Mocked tests plus an optional live-Azure smoke script |

## Phase Boundaries

### Included

- Quart application and container scaffolding
- typed configuration and dependency construction
- Easy Auth identity parsing and local-development identity mode
- PDF request validation
- Blob Storage adapter
- Cosmos DB adapter
- work-item service and lifecycle enforcement
- create, list, detail, and status APIs
- liveness and readiness endpoints
- consistent error responses
- request correlation and Azure Monitor/OpenTelemetry integration
- unit, route, service, and adapter-contract tests
- optional live-Azure backend smoke script
- backend development and validation documentation

### Excluded

- React frontend
- Logic App workflow package
- Azure OpenAI calls
- PDF text extraction or OCR
- prompt management
- AI results beyond the reserved data contract
- work-item mutation endpoints for users
- delete, retry, cancel, or review actions
- infrastructure or deployment-pipeline changes
- production Azure deployment

## Immutable Infrastructure Constraints

The backend must use the existing Phase 1 outputs:

| Environment value | Backend use |
| --- | --- |
| `AZURE_STORAGE_ACCOUNT` | Construct the Blob Storage account endpoint |
| `AZURE_STORAGE_CONTAINER` | Store source PDFs in the input container |
| `AZURE_COSMOSDB_ACCOUNT` | Construct the Cosmos DB endpoint |
| `AZURE_COSMOSDB_DATABASE` | Work-item database |
| `AZURE_COSMOSDB_CONTAINER` | Work-item container |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Configure Azure Monitor telemetry |
| `AZURE_TENANT_ID` | Identity context |
| `AZURE_AUTH_TENANT_ID` | Optional authentication tenant override |
| `RUNNING_IN_PRODUCTION` | Disable local-only behavior in Azure |

The Cosmos container contract is fixed:

- partition key: `/created_at`
- indexed paths: `/created_at/?` and `/source_name/?`
- all other application fields are excluded from indexing

Owner and status filters are therefore not optimized by the inherited index
policy. Phase 2 will preserve the infrastructure and use bounded cross-partition
queries with scan explicitly enabled where required. This tradeoff must be
documented and verified with the optional live-Azure smoke test. It must not be
worked around through a Bicep change.

## Proposed Backend Structure

```text
app/backend/
├── Dockerfile
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── gunicorn.conf.py
├── backend/
│   ├── __init__.py
│   ├── app.py
│   ├── auth.py
│   ├── config.py
│   ├── dependencies.py
│   ├── errors.py
│   ├── main.py
│   ├── telemetry.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── work_items.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── blobs.py
│   │   └── work_items.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   └── work_items.py
│   └── services/
│       ├── __init__.py
│       └── work_items.py
└── tests/
    ├── conftest.py
    ├── fixtures/
    ├── test_auth.py
    ├── test_config.py
    ├── test_health.py
    ├── test_pdf_validation.py
    ├── test_work_item_models.py
    ├── test_work_item_routes.py
    └── test_work_item_service.py
```

Exact filenames may be adjusted to follow the implemented package tooling, but
the boundaries between routes, services, repositories, models, configuration,
and authentication must remain explicit.

## Work-Item Data Contract

### Stored Cosmos document

```json
{
  "id": "uuid",
  "created_at": "2026-01-01T00:00:00.000000Z",
  "updated_at": "2026-01-01T00:00:01.000000Z",
  "owner_id": "stable-authenticated-subject",
  "status": "queued",
  "version": 1,
  "source_name": "example.pdf",
  "source": {
    "blob_name": "work-items/<id>/source.pdf",
    "content_type": "application/pdf",
    "size_bytes": 12345,
    "sha256": "hex-digest"
  },
  "idempotency_key_hash": "sha256-hex",
  "result": null,
  "error": null
}
```

### Field rules

| Field | Rule |
| --- | --- |
| `id` | UUID generated deterministically from owner identity and idempotency-key hash |
| `created_at` | UTC RFC 3339 timestamp; Cosmos partition key; immutable |
| `updated_at` | UTC RFC 3339 timestamp; updated on every state change |
| `owner_id` | Stable Easy Auth subject identifier; never supplied by the caller |
| `status` | One of the approved lifecycle values |
| `version` | Positive integer for optimistic application-level updates |
| `source_name` | Sanitized original filename for display; never used as a path |
| `source.blob_name` | Server-generated path; never accepts caller path segments |
| `source.content_type` | Always `application/pdf` after validation |
| `source.size_bytes` | Validated size, maximum 20 MB |
| `source.sha256` | Content digest used for observability, not deduplication |
| `idempotency_key_hash` | Hash only; raw idempotency key is never persisted or logged |
| `result` | Reserved for Phase 4 structured AI output |
| `error` | Reserved structured processing or intake failure |

### Error object

```json
{
  "code": "blob_upload_failed",
  "message": "The source file could not be stored.",
  "retryable": true,
  "occurred_at": "2026-01-01T00:00:01.000000Z"
}
```

Internal exceptions, Azure request IDs, account names, endpoints, stack traces,
and credentials must not be stored in user-readable fields.

## Lifecycle Contract

```text
submitted -> queued -> processing -> completed
    |           |           |
    +-----------+-----------+-> failed
```

### Phase 2 transitions

- API creates `submitted`.
- Successful blob upload changes `submitted` to `queued`.
- Blob upload failure changes `submitted` to `failed`.

### Reserved Phase 4 transitions

- Logic App changes `queued` to `processing`.
- Logic App changes `processing` to `completed` or `failed`.

### Transition rules

- Terminal statuses are `completed` and `failed`.
- A repeated idempotent create request never resets status.
- State changes increment `version`.
- State changes preserve `created_at`, `owner_id`, and source identity.
- Invalid transitions raise an explicit conflict error.
- Later workflow writes must use Cosmos `_etag` or equivalent optimistic
  concurrency where available.

## Authentication and Authorization Contract

### Azure mode

The backend trusts only the App Service Easy Auth client-principal header after
App Service authentication has validated it. The parser must:

1. Require the configured client-principal header.
2. Base64-decode and parse the JSON payload.
3. Require a stable subject claim.
4. Optionally extract display information for request context only.
5. Reject malformed or incomplete identity payloads with `401`.
6. Never accept owner identity from request JSON, form fields, query values, or
   custom user-controlled headers.

### Local-development mode

An explicit environment setting provides a fixed synthetic development subject.
The bypass is allowed only when `RUNNING_IN_PRODUCTION` is not true.

Application startup must fail if a local authentication bypass is configured
while production mode is enabled.

### Authorization

- Create assigns the authenticated subject as owner.
- List always adds the authenticated owner predicate.
- Detail and status return `404`, not `403`, for another owner's item.
- Health and readiness are anonymous and reveal only healthy/unhealthy state.
- No tenant-wide or reviewer access is implemented in Phase 2.

## PDF Validation Contract

The upload endpoint accepts `multipart/form-data` with one `file` part.

Validation order:

1. Require a file part and a non-empty filename.
2. Reject requests that exceed the configured request limit.
3. Require a `.pdf` filename extension, case-insensitively.
4. Require the declared content type `application/pdf`.
5. Require the file signature to begin with `%PDF-`.
6. Stream or spool the file without retaining an unbounded in-memory copy.
7. Compute SHA-256 and exact size while reading.
8. Reject empty or greater-than-20-MB content.
9. Normalize the display filename:
   - strip path components
   - remove control characters
   - enforce a bounded length
   - preserve a `.pdf` suffix
10. Generate the blob path independently of the filename.

This phase validates that a file is structurally presented as a PDF. It does
not parse, execute, render, OCR, or inspect PDF contents.

## Idempotency Contract

### Header

`Idempotency-Key` is required for create requests.

- accepted length: 8 to 128 visible ASCII characters
- raw value is never logged or persisted
- backend stores a SHA-256 hash scoped to the authenticated owner
- work-item ID is derived deterministically from owner ID and key hash using a
  fixed application namespace UUID

### Repeated requests

- First successful create returns `201 Created`.
- A repeated request for the same owner and key returns the existing item with
  `200 OK` and `Idempotent-Replayed: true`.
- The repeated request does not upload another blob or alter state.
- The same key used by a different owner is independent.
- A collision with inconsistent ownership or persisted key hash is treated as
  a server-side integrity error.

Because the partition key is `created_at`, replay lookup requires a bounded
cross-partition query by deterministic `id`. This behavior must be isolated in
the repository adapter and covered by tests.

## Creation and Compensation Flow

```text
authenticate
  -> validate idempotency key
  -> validate and spool PDF
  -> derive deterministic work-item ID
  -> lookup replay
  -> create submitted Cosmos record
  -> upload blob with overwrite disabled
  -> replace record as queued
  -> return created item
```

### Failure behavior

| Failure | Required behavior |
| --- | --- |
| Validation fails | Return `400` or `413`; create no record and upload no blob |
| Cosmos submitted-record create fails | Return dependency error; upload no blob |
| Record already exists | Resolve as idempotent replay; do not upload |
| Blob upload fails | Attempt to replace submitted record with `failed`; return `502` or `503` |
| Failed-status update also fails | Log both failures with request ID; return dependency error; do not report success |
| Queued-status update fails after upload | Attempt blob deletion; attempt failed-status update; report dependency error |
| Blob cleanup fails | Log explicit cleanup failure; never return success |
| Client disconnects | Complete or cancel safely according to the current persistence boundary; leave no success-shaped partial response |

Broad exception catches and silent cleanup failures are prohibited.

## Blob Storage Contract

- Async Azure Blob Storage SDK
- Token credential only; no account key or connection string
- Default endpoint:
  `https://<AZURE_STORAGE_ACCOUNT>.blob.core.windows.net`
- Optional explicit endpoint override for non-public Azure clouds or tests
- Container from `AZURE_STORAGE_CONTAINER`
- Blob name: `work-items/<work-item-id>/source.pdf`
- `overwrite=false`
- content type set to `application/pdf`
- metadata limited to non-sensitive work-item ID and SHA-256
- filename, owner identity, and idempotency key are not blob path components

Repository operations:

- upload source
- delete source for compensation
- readiness probe

## Cosmos DB Contract

- Async Azure Cosmos SDK
- Token credential only
- Default endpoint:
  `https://<AZURE_COSMOSDB_ACCOUNT>.documents.azure.com:443/`
- Optional explicit endpoint override for tests or non-public Azure clouds
- Database and container from Phase 1 outputs

Repository operations:

- create work item
- find by deterministic ID across partitions
- list owner work items with optional status
- replace work item with optimistic concurrency
- readiness probe

### Query constraints

- List queries are always owner-scoped.
- Optional status accepts only the lifecycle enum.
- Page size default: 20.
- Page size range: 1 to 100.
- Sort: `created_at DESC`.
- Continuation tokens are treated as opaque and are never logged.
- Cross-partition scanning is explicitly enabled for owner/status predicates
  excluded by the inherited index policy.
- Query implementation must cap page size and must not load the full container.
- The live smoke script must verify owner filtering, status filtering, ordering,
  and continuation behavior against a provisioned container before starter
  release.

## HTTP API Contract

### `POST /api/v1/work-items`

Creates a work item from one PDF.

Request:

- authenticated Easy Auth identity
- `Idempotency-Key` header
- `multipart/form-data`
- `file` part

Responses:

- `201`: created and queued
- `200`: idempotent replay
- `400`: malformed request, key, filename, content type, or PDF signature
- `401`: missing or invalid identity
- `409`: integrity or state conflict
- `413`: PDF exceeds 20 MB
- `502`: Azure dependency rejected the operation
- `503`: Azure dependency unavailable

### `GET /api/v1/work-items`

Query parameters:

- `status`: optional lifecycle value
- `page_size`: optional integer from 1 to 100
- `continuation_token`: optional opaque token

Response:

```json
{
  "items": [],
  "continuation_token": null
}
```

Items are owner-scoped and newest first.

### `GET /api/v1/work-items/<id>`

Returns an owner-scoped work item.

- `200`: found
- `400`: invalid ID format
- `401`: missing identity
- `404`: absent or owned by another subject

### `GET /api/v1/work-items/<id>/status`

Returns a minimal polling response:

```json
{
  "id": "uuid",
  "status": "queued",
  "updated_at": "timestamp",
  "error": null
}
```

### `GET /healthz`

Anonymous process liveness.

- does not call Azure
- returns `200` if the application event loop is responsive
- exposes no configuration or dependency data

### `GET /readyz`

Anonymous dependency readiness.

- checks Blob Storage and Cosmos DB through bounded operations
- caches results briefly to avoid probe-driven dependency load
- returns `200` or `503`
- response contains only a generic ready/not-ready state
- detailed failures appear only in structured server telemetry

## Public Response Model

Public responses must not expose:

- owner ID
- idempotency-key hash
- blob account, container, or internal blob path
- Cosmos partition key implementation details
- `_etag`
- Azure request IDs
- stack traces

A work-item response contains:

```json
{
  "id": "uuid",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "status": "queued",
  "version": 1,
  "source": {
    "name": "example.pdf",
    "content_type": "application/pdf",
    "size_bytes": 12345,
    "sha256": "hex-digest"
  },
  "result": null,
  "error": null
}
```

## Error Response Contract

All errors use:

```json
{
  "error": {
    "code": "invalid_pdf",
    "message": "The uploaded file is not a valid PDF.",
    "request_id": "uuid",
    "details": null
  }
}
```

Rules:

- stable machine-readable codes
- concise user-safe messages
- request correlation ID in body and response header
- field details only for validation errors
- no exception text or dependency internals
- consistent JSON for framework, validation, authorization, and dependency
  failures

## Configuration Contract

Configuration is loaded once at startup into a typed immutable object.

Required in Azure:

- `AZURE_STORAGE_ACCOUNT`
- `AZURE_STORAGE_CONTAINER`
- `AZURE_COSMOSDB_ACCOUNT`
- `AZURE_COSMOSDB_DATABASE`
- `AZURE_COSMOSDB_CONTAINER`

Optional:

- `AZURE_STORAGE_ENDPOINT`
- `AZURE_COSMOSDB_ENDPOINT`
- `APPLICATIONINSIGHTS_CONNECTION_STRING`
- `RUNNING_IN_PRODUCTION`
- `LOCAL_AUTH_SUBJECT`
- `MAX_PDF_SIZE_MB`, default `20`
- `DEFAULT_PAGE_SIZE`, default `20`
- `MAX_PAGE_SIZE`, default `100`
- `READINESS_CACHE_SECONDS`, default `30`
- `LOG_LEVEL`, default `INFO`

Startup fails with an actionable configuration error when required settings are
missing. Local test fixtures inject configuration directly and do not rely on
developer environment state.

## Dependency and Credential Lifecycle

- Construct one async token credential per application.
- Construct reusable Blob service and Cosmos clients.
- Close all Azure clients and credentials during Quart shutdown.
- Use explicit protocols or interfaces at repository boundaries for testing.
- Route handlers do not construct Azure clients.
- Models do not import Azure SDK types.
- Dependency failures are mapped centrally to application errors.

## Telemetry Contract

- Generate or accept a bounded `X-Request-ID`.
- Return the request ID on every response.
- Emit structured logs with request ID, route, method, status, duration, and
  work-item ID when available.
- Do not log PDF content, filenames, owner identities, raw idempotency keys,
  continuation tokens, or authentication headers.
- Configure Azure Monitor only when the connection string is present.
- Instrument Quart and outbound Azure SDK calls where supported.
- Preserve local console logging when Azure Monitor is not configured.
- Avoid duplicate instrumentation across app-factory calls in tests.

## Work Package 2.0 - Establish Backend Tooling

### Tasks

1. Create the Python package and test structure.
2. Pin supported Python to 3.12.
3. Add runtime and development dependency manifests.
4. Configure pytest and asynchronous test support.
5. Add a production container using the existing port `8000` contract.
6. Add a production ASGI server configuration.
7. Document backend setup and commands.

### Acceptance criteria

- Package imports without Azure credentials.
- Empty application starts locally with injected test configuration.
- Container build reaches a runnable backend image.
- No infrastructure file changes.

## Work Package 2.1 - Implement Models and Lifecycle

### Tasks

1. Add status, source, result, processing-error, persistence, and public
   response models.
2. Add UTC timestamp helpers.
3. Add transition validation.
4. Add public-response mapping that excludes internal fields.
5. Add deterministic ID and idempotency-key hashing helpers.

### Acceptance criteria

- Invalid statuses and transitions fail explicitly.
- Stored and public models cannot be confused by type.
- Serialization is stable and documented.
- Raw idempotency keys and owner IDs cannot enter public responses.

## Work Package 2.2 - Implement Configuration and Dependencies

### Tasks

1. Implement typed startup configuration.
2. Validate production/local authentication combinations.
3. Build async Azure credentials and clients.
4. Build repository and service instances.
5. Register startup and shutdown lifecycle handlers.
6. Implement injectable test dependencies.

### Acceptance criteria

- Production refuses local authentication bypass.
- Missing Azure configuration fails startup.
- Clients and credentials close cleanly.
- Tests use no network unless explicitly marked live.

## Work Package 2.3 - Implement Authentication

### Tasks

1. Parse and validate Easy Auth client-principal data.
2. Define authenticated request context.
3. Implement explicit local synthetic identity mode.
4. Add route decorators or middleware.
5. Exempt only health and readiness routes.

### Acceptance criteria

- Missing, malformed, or incomplete identities return `401`.
- Caller-controlled owner fields are ignored or rejected.
- Another owner's resource is indistinguishable from a missing resource.
- Authentication header values never appear in logs.

## Work Package 2.4 - Implement PDF Intake

### Tasks

1. Configure bounded multipart request handling.
2. Sanitize display filenames.
3. Validate extension, content type, signature, emptiness, and size.
4. Spool upload content safely.
5. Compute exact size and SHA-256.
6. Guarantee temporary-file cleanup.

### Acceptance criteria

- Non-PDF and oversized files are rejected before Azure writes.
- A filename cannot control a filesystem or blob path.
- Tests cover malformed multipart data and deceptive filenames.
- No test fixture contains private or real documents.

## Work Package 2.5 - Implement Azure Repositories

### Tasks

1. Implement Blob upload, cleanup, and readiness operations.
2. Implement Cosmos create, replay lookup, list, read, replace, and readiness
   operations.
3. Preserve Cosmos continuation tokens without logging them.
4. Apply bounded cross-partition query settings.
5. Map Azure exceptions into typed repository errors.

### Acceptance criteria

- Repositories are asynchronous.
- No account keys or connection strings are accepted.
- Blob overwrite is disabled.
- Owner predicates are mandatory for user-facing reads.
- Continuation tokens work without exposing internal query state.

## Work Package 2.6 - Implement Work-Item Service

### Tasks

1. Orchestrate authentication-independent creation inputs.
2. Implement idempotent replay.
3. Create the submitted record.
4. Upload the PDF.
5. Transition to queued.
6. Implement every compensation path.
7. Implement owner-scoped list, detail, and status behavior.

### Acceptance criteria

- No partial failure is returned as success.
- Every cleanup failure is logged explicitly.
- Replay creates no duplicate record or blob.
- Service tests cover each persistence boundary failure.

## Work Package 2.7 - Implement Routes and Error Handling

### Tasks

1. Add health and readiness blueprints.
2. Add versioned work-item routes.
3. Add request correlation middleware.
4. Add central exception-to-response mapping.
5. Add request and response schema serialization.
6. Enforce route-level content and query validation.

### Acceptance criteria

- Every error response follows the shared envelope.
- Unsupported methods and media types return JSON errors.
- Public responses contain no internal persistence fields.
- OpenAPI generation is not required in Phase 2.

## Work Package 2.8 - Implement Telemetry

### Tasks

1. Configure structured local logs.
2. Configure Azure Monitor conditionally.
3. Add request spans and dependency instrumentation.
4. Add safe work-item lifecycle events.
5. Verify sensitive fields are excluded.

### Acceptance criteria

- Telemetry initialization is idempotent in tests.
- Request IDs correlate error responses and logs.
- PDF content and identity headers never enter telemetry.

## Work Package 2.9 - Test the Backend

### Unit and service tests

- configuration success and failure
- production/local authentication guard
- Easy Auth parsing
- filename and PDF validation
- work-item serialization
- valid and invalid transitions
- deterministic ID and idempotency replay
- submitted-record failure
- blob-upload failure
- failed-status update failure
- queued-status update failure
- blob-cleanup failure
- owner-scoped detail and status
- owner-scoped list and status filtering
- continuation-token pass-through

### Route tests

- health and readiness
- authentication failures
- create success and replay
- invalid multipart and PDF cases
- page-size and status validation
- another owner's item returns `404`
- dependency error mapping
- request ID propagation

### Adapter contract tests

- Azure SDK calls receive token credentials and expected endpoints
- Blob upload uses `overwrite=false`
- Cosmos queries include owner constraints and bounded page size
- optimistic concurrency options are passed on replace

### Optional live-Azure smoke script

The script is opt-in and must:

1. Require an explicitly selected azd environment.
2. Refuse to run against an environment whose name does not match an explicit
   confirmation value.
3. Create a synthetic minimal PDF locally.
4. Exercise Blob and Cosmos repository operations.
5. Verify replay, owner filtering, status filtering, ordering, and
   continuation behavior.
6. Delete all records and blobs created by the script.
7. Print no secrets, identity payloads, or continuation tokens.

## Work Package 2.10 - Validate and Review

### Required commands

- backend unit and route tests
- backend type checking
- backend formatting or lint check
- backend container build
- Bicep baseline verification
- repository-wide prohibited-content scan
- secret scan
- staged-diff inspection

### Review artifacts

- final work-item schema
- API request and response examples
- lifecycle and compensation matrix
- test inventory and results
- container build result
- optional live-smoke result, if executed
- confirmation that the Bicep baseline is unchanged
- complete unpushed commit diff

### Commit strategy

1. Implementation may use local commits only after files are generalized and
   tests pass.
2. Do not push Phase 2 implementation until the review gate is approved.
3. If prohibited content enters a local commit, rebuild the local commits
   before any push.
4. Do not begin Phase 3 frontend implementation as part of Phase 2.

## Planned Task Dependencies

```text
2.0 Backend tooling
 ├─> 2.1 Models and lifecycle
 ├─> 2.2 Configuration and dependencies
 │    └─> 2.3 Authentication
 ├─> 2.4 PDF intake
 └─> 2.5 Azure repositories
      └─> 2.6 Work-item service
           ├─> 2.7 Routes and errors
           └─> 2.8 Telemetry
                └─> 2.9 Tests
                     └─> 2.10 Validation and review
```

## Final Phase 2 Acceptance Criteria

- Quart backend runs locally and in its production container.
- Only validated PDFs up to 20 MB are accepted.
- Create operations follow the submitted-record, blob-upload, queued-state
  sequence.
- Idempotent replay creates no duplicate record or blob.
- Work items expose the approved lifecycle and public schema.
- List, detail, and status reads are owner-only.
- Continuation pagination and status filtering are implemented.
- Health and readiness expose no sensitive dependency information.
- Azure access uses token credentials and asynchronous clients.
- Failure compensation is explicit and tested.
- Telemetry contains no PDF, identity, key, or token content.
- Backend tests, type checks, lint checks, and container build pass.
- Bicep checksum verification passes with no infrastructure changes.
- No proprietary content, private history, or source references exist.
- Implementation remains unpushed until explicitly approved.

## Stop Conditions

Stop and request review if:

- Cosmos query behavior cannot enforce owner isolation reliably
- idempotent replay cannot be implemented without infrastructure change
- a compensation path can silently leave a success-shaped partial state
- Easy Auth does not provide a stable non-PII subject claim
- PDF request handling requires unbounded memory
- a proposed fix would change the Bicep baseline
- live validation requires creating Azure resources without approval
- an Azure SDK or telemetry library forces credential or content logging
