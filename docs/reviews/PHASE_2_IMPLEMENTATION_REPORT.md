# Phase 2 Implementation Report

## Scope

Phase 2 implements the generic asynchronous backend and data contracts:

- Quart API and Python 3.12 production container
- App Service Easy Auth identity parsing with guarded local identity mode
- bounded PDF validation and temporary spooling
- owner-scoped Blob Storage and Cosmos DB repositories
- record-first work-item creation and idempotent replay
- explicit lifecycle and compensation behavior
- health, readiness, create, list, detail, and status routes
- structured logging and optional Azure Monitor telemetry
- mocked unit, route, service, and Azure SDK contract tests
- opt-in live-Azure repository smoke script
- backend CI and deployment helper integration

No frontend, Logic App workflow implementation, AI prompt, document content,
or infrastructure change is included.

## Work-item and API contracts

The persisted model uses the Phase 1 Cosmos partition key, `created_at`, while
owner and status reads use bounded scan-enabled cross-partition queries. Public
responses exclude owner identity, Blob paths, idempotency hashes, Cosmos
metadata, and dependency internals.

Implemented routes:

| Method | Route | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/work-items` | Validate one PDF and create or replay a work item |
| `GET` | `/api/v1/work-items` | List owner-scoped work items with status filtering and paging |
| `GET` | `/api/v1/work-items/<id>` | Read one owner-scoped work item |
| `GET` | `/api/v1/work-items/<id>/status` | Read minimal polling state |
| `GET` | `/healthz` | Anonymous process liveness |
| `GET` | `/readyz` | Anonymous cached dependency readiness |

Example create response:

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:01Z",
  "status": "queued",
  "version": 2,
  "source": {
    "name": "example.pdf",
    "content_type": "application/pdf",
    "size_bytes": 32,
    "sha256": "sha256-hex"
  },
  "result": null,
  "error": null
}
```

## Lifecycle and compensation

| Boundary | Failure behavior |
| --- | --- |
| Submitted record create | Return dependency error; do not upload a Blob |
| Blob upload | Attempt `submitted -> failed`; return dependency error |
| Failed-state update | Log both failures; return dependency error |
| `submitted -> queued` update | Attempt Blob deletion and failed-state update |
| Blob cleanup | Log explicitly; never return success |
| Idempotent replay | Return the existing record without another write or upload |

Phase 2 creates only `submitted`, `queued`, and intake `failed` states. The
`processing` and terminal workflow transitions remain reserved for Phase 4.

## Validation evidence

- 41 mocked tests pass.
- Ruff lint and format checks pass.
- Mypy passes for 20 backend source files.
- The Python 3.12 production container builds and serves a successful
  `/healthz` response.
- Bash syntax and smoke-script CLI loading pass.
- The Phase 1 Bicep SHA-256 baseline passes for every infrastructure file.
- Git diff whitespace validation passes.
- Repository and history scans found no private source repository identifier.
- No live Azure smoke test was run because no approved provisioned Phase 2
  environment is currently selected.

The host virtual environment currently uses Python 3.14 and emits
`pytest-asyncio` deprecation warnings for APIs scheduled for removal in Python
3.16. The supported application runtime remains Python 3.12 and the production
container was validated on Python 3.12.

## Review gate

The implementation is committed locally only. It must not be pushed and Phase
3 must not begin until the Phase 2 review gate is explicitly approved.
