# Customize the app

Replace the PDF summarization sample with your own use case while keeping
the platform: sign-in, managed identities, networking, and the reliable
upload → queue → process → result pattern.

## What to keep and what to replace

| Keep | Replace |
| --- | --- |
| Managed identities, per-user authorization, safe error responses | Data models, labels, and the result schema |
| Infrastructure, networking and role assignments | Frontend pages and how results are shown |
| Idempotency keys, ETag-protected status changes, terminal states | The prompts in `app/agent/instructions/` |
| Telemetry that never logs document content | Synthetic test files and fixtures |

Infrastructure changes follow [infrastructure change control](../contributing/infra-change-control.md).

## Where things live

| To change... | Edit |
| --- | --- |
| Prompts | `app/agent/instructions/system.md`, `processing.md` |
| What the model returns | Workflow JSON schema in `app/agent/workflows/process-document/workflow.json`, backend models in `app/backend/backend/models/`, frontend types in `app/frontend/src/` |
| Accepted file type or size | Backend PDF validator and `MAX_PDF_SIZE_MB`; frontend file picker; workflow `input_file` content type |
| Statuses | Backend `WorkItemStatus`, workflow claim and terminal actions, frontend polling |
| API routes | `app/backend/backend/routes/` and [API reference](../reference/api.md) |
| Blob path `work-items/<id>/source.pdf` | Backend storage service and the workflow trigger path |

## Suggested order

1. Write down the new input, statuses and result shape first.
2. Update the backend models, services, routes and tests together.
3. Update the workflow schema, response parsing and fixtures.
4. Update the prompts. Keep the instruction that document content is
   untrusted.
5. Update frontend types, API calls, pages and fixtures.
6. Update [API](../reference/api.md) and [app settings](../reference/app-settings.md)
   docs.
7. Run the checks:

   ```bash
   .venv/bin/python -m pytest app/backend/tests app/agent/tests scripts/tests
   .venv/bin/python scripts/verify_logic_app_package.py
   npm --prefix app/frontend test -- --run
   npm --prefix app/frontend run typecheck
   ```

8. Deploy to a dev environment and test with synthetic files only:
   `./scripts/deploy_app.sh all`.

## Things that are fixed by the infrastructure

- Cosmos DB partition key `/created_at` and the indexed paths. Design
  queries around them.
- Storage containers `content`, `tokens`, `instructions`, `inputs`. Names can
  be changed with settings; see [configuration](../reference/configuration.md).

## Rolling back

Deploying an older image does not roll back prompts, the workflow, or data
written in a new shape. Roll them back together, or keep the old and new
schemas compatible.
