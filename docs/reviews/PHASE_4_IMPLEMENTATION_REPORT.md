# Phase 4 Workflow Implementation Report

## Status

The Logic Apps Standard package is implemented locally as the final step of
Phase 7. Azure deployment and live Foundry validation remain separate approval
gates and have not been performed.

## Delivered

- Added `app/agent/workflows` with Standard host configuration, managed-identity
  Blob connection, local/Azure parameter files, and the `process-document`
  workflow.
- Added generic, replaceable system and processing instructions and synthetic
  fixtures, including a generated PDF.
- Added a Blob path guard, Cosmos work-item correlation, a bounded
  `submitted` readiness loop, ETag-protected claim and terminal writes,
  instruction/PDF reads, Foundry Responses API inference, strict result
  parsing, safe failure persistence, and run-history secure-data settings.
- Used the Logic App's system-assigned identity for the built-in Blob
  connection and the existing user-assigned identity for Cosmos REST and
  Foundry HTTP calls. The infrastructure configuration assigns Blob data-plane
  roles to both identities. No standalone Azure OpenAI setting, account, key,
  or fallback is required.
- Added local and GitHub deployment paths that upload instructions using
  Azure CLI Entra authentication. Workflow packaging stages Azure parameters
  in a temporary directory and leaves source parameter files untouched.
- Added a package validator, contract tests, and CI integration.

## Local evidence

- `python scripts/verify_logic_app_package.py` passed.
- `python -m json.tool` parsed the workflow and package parameter/connection
  files.
- `PYTHONPATH=. .venv/bin/python -m pytest app/agent/tests app/backend/tests
  -q` passed: 82 tests.
- `bash -n app/agent/deploy.sh scripts/deploy_app.sh` passed.

These checks validate package structure and authored workflow contracts. They
do not execute the Logic Apps runtime or prove deployed connector behavior.

## Remaining approval-gated validation

- Deploy the package and confirm Standard workflow/connector schema acceptance,
  system-assigned Blob connector authentication, user-assigned HTTP identity
  selection, Cosmos REST RBAC and ETag behavior, Blob trigger fields, and
  Foundry request/response behavior.
- Verify the deployment's endpoint/model compatibility and network/DNS access.
- Exercise duplicate delivery, claim contention, failure persistence, and
  terminal-write conflicts against Azure.
- Measure the serialized request for a synthetic PDF near the 20 MB backend
  limit. The current inline PDF path has not been measured against runtime or
  service request limits.
- Review infrastructure resource-graph changes and the baseline checksum
  separately. The checksum manifest was not updated.

The workflow claim-conflict path re-reads the record and avoids model calls
when another writer has moved it to `processing` or a terminal state. A
still-`queued` conflict fails visibly rather than retrying the claim. No live
Azure behavior is claimed by this report.
