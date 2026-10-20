# Backend

Quart API for generic PDF work items.

## Setup

Follow [development](../../docs/contributing/development.md#set-up) from the
repository root.

## Development

Use [develop against Azure](../../docs/quickstarts/develop-against-azure.md)
for server startup, identity and network requirements, and
[app settings](../../docs/reference/app-settings.md)
for settings and `.env` precedence. `LOCAL_AUTH_SUBJECT` is rejected in
production. The backend does not provide an offline Storage/Cosmos emulator.

The [API reference](../../docs/reference/api.md) describes HTTP contracts.
See [customize the app](../../docs/how-to/customize-the-app.md) before
changing persisted schemas or lifecycle behavior.

## Validation

See [development](../../docs/contributing/development.md#run-the-checks) for the checks.
Backend tests use mocked persistence; they do not prove Azure readiness.

**Azure data mutation:** the optional live-Azure smoke test requires an explicitly selected azd
environment and a matching confirmation:

```bash
.venv/bin/python scripts/smoke_backend_azure.py \
  --environment <environment-name> \
  --confirm-environment <environment-name>
```

It creates only synthetic PDF records, verifies idempotency, filtering, and
continuation paging, and removes the temporary Blob and Cosmos data.
Verify cleanup completed if the process fails or is interrupted; never run
against production or with real documents.
