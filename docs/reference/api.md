# HTTP API reference

The backend's REST API, for frontend developers and other clients. The
[routes](../../app/backend/backend/routes/work_items.py),
[models](../../app/backend/backend/models/work_items.py) and
[error handling](../../app/backend/backend/app.py) define the contract. There
is no generated OpenAPI endpoint.

## Authentication and correlation

All `/api/v1/` requests require backend identity. Production relies on App
Service authentication supplying `X-MS-CLIENT-PRINCIPAL` through its trusted
front door; do not expose the backend as a public header-trusting origin.
Local development can use `LOCAL_AUTH_SUBJECT`; production rejects it.
See [app settings](app-settings.md) and
[identity and access](../concepts/identity-and-access.md).

Clients never submit owner IDs. Reads are owner-scoped; another owner's item
is not visible. Responses omit owner IDs, internal Blob paths, partition
values, idempotency hashes and ETags.

Send an optional `X-Request-ID` of 1-64 ASCII letters, digits, dots,
underscores or hyphens. An invalid/missing value is replaced with a UUID.
Responses include `X-Request-ID`; errors also include it in their JSON body.
Platform authentication failures may occur before Quart and need not use
this response format.

## Endpoints

| Method / path | Request | Success |
| --- | --- | --- |
| `POST /api/v1/work-items` | Multipart `file`, `Idempotency-Key` header | 201 for new record, 200 for replay; full work-item response |
| `GET /api/v1/work-items` | Optional `status`, `page_size`, `continuation_token` | 200 with `items` and nullable `continuation_token` |
| `GET /api/v1/work-items/{id}` | UUID work-item ID | 200 full response; 404 if not visible |
| `GET /api/v1/work-items/{id}/status` | UUID work-item ID | 200 with `id`, `status`, `updated_at`, nullable `error` |
| `GET /healthz` | None | 200 `{"status":"healthy"}`; process liveness only |
| `GET /readyz` | None | 200 `{"status":"ready"}` or 503 `{"status":"not_ready"}` |

Quart does not require backend identity on the health routes, but App Service
authentication/network rules may still protect them externally. Readiness
checks Blob container and Cosmos container access, caches the result, and has
a five-second dependency timeout. It does not check Foundry or the workflow.
There are no public update, delete, retry, cancellation or download endpoints.

## Upload and idempotency

- The form field must be named `file`, with MIME type `application/pdf`, a
  nonempty `.pdf` filename, and `%PDF-` signature.
- The default file limit is 20 MiB; see runtime configuration for bounds.
  This is signature validation, not full PDF parsing or malware scanning.
- `Idempotency-Key` is required: 8-128 visible ASCII characters (codes 33-126).
  Reuse it only for retries of the same submission.
- Identity plus key determine the work-item ID. Replay returns the existing
  record and `Idempotent-Replayed: true`, even if a later upload uses different
  bytes. The API does not compare the retry payload with the stored PDF.
- A new request creates `submitted`, uploads its Blob, then persists `queued`.
  Upload/queue failure triggers best-effort compensation; a failed HTTP
  request does not prove that no data was written.

Example against a **local backend connected to Azure**. It writes real
Blob and Cosmos DB data:

```bash
curl --fail-with-body \
  -H 'Idempotency-Key: synthetic-request-0001' \
  -F 'file=@tests/sample-data/generated/hello-world.pdf;type=application/pdf' \
  http://127.0.0.1:8000/api/v1/work-items
```

See [Develop against Azure](../quickstarts/develop-against-azure.md) and the
[sample data guide](../../tests/sample-data/README.md).

## Responses and paging

A full response contains `id`, `created_at`, `updated_at`, `status`, `version`,
`source`, nullable `result` and nullable `error`. `source` contains display
`name`, `content_type`, `size_bytes` and `sha256`. Timestamps are UTC serialized
datetimes; IDs are UUID strings.

Completed workflow results contain `summary`, `category` and `key_points`;
categories are `informational`, `action_required`, `reference` or `other`.
The authored workflow validates its output schema, while the backend's stored
result type is a general object. Keep all consumers coordinated when changing
that schema.

List results are ordered by descending creation time. `status` accepts
`submitted`, `queued`, `processing`, `completed` or `failed`. `page_size`
defaults to 20 and is bounded by `MAX_PAGE_SIZE` (default 100). Treat the
continuation token as opaque; it is limited to 4096 characters and returned
as `null` when exhausted. Do not promise an exact number of items per page
or infer a fixed snapshot while processing continues.

See the [work item lifecycle](../concepts/architecture.md#work-item-lifecycle)
for which component owns each state change. Terminal states are not retried
automatically.

## Errors

```json
{
  "error": {
    "code": "missing_idempotency_key",
    "message": "The Idempotency-Key header is required.",
    "request_id": "synthetic-request-0001",
    "details": null
  }
}
```

| Status | Examples / meaning |
| --- | --- |
| 400 | Invalid ID, status, page size, continuation-token length, key, filename, MIME type or PDF signature; missing file/key |
| 401 | Missing or invalid backend identity |
| 404 | Work item not visible or route/static asset absent |
| 409 | Idempotent work item could not be resolved or record inconsistency |
| 413 | PDF or multipart request exceeds configured limit |
| 502 | Dependency rejected an operation |
| 503 | Dependency unavailable; readiness also uses 503 with its simpler status body |
| 500 | Unexpected error; details remain server-side |

Dependency error codes describe the failed operation (for example
`blob_upload_failed` or `queue_transition_failed`). A work item's persisted
processing error is separate: `code`, `message`, `retryable`, `occurred_at`.
`retryable` does not mean the starter schedules retries or exposes a retry API.
