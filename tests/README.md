# Tests

This directory contains cross-component fixtures and generated sample
boundaries.

Component-specific tests should remain close to their application component
when the selected framework supports that convention.

## Test locations

| Location | Coverage |
| --- | --- |
| `app/backend/tests/` | API/auth/configuration/persistence contracts with mocked Azure boundaries |
| `app/frontend/src/` test files | Browser components and request fixtures |
| `app/agent/tests/` | Authored workflow/package contracts and synthetic fixtures |
| `scripts/tests/` | Repository-policy validator |

See [development](../docs/contributing/development.md#run-the-checks) for the
commands and their limits. Static and mocked tests do not execute the Logic
Apps runtime or prove Foundry PDF compatibility.

`sample-data/generated/` is ignored. Use the
[synthetic sample guide](sample-data/README.md) to generate the starter PDF.
