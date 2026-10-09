# Replacement guide

Use this guide when turning the hello-world PDF flow into a solution-specific
application.

## Keep versus replace

| Surface | Direction |
| --- | --- |
| `infra/` | Keep unchanged |
| `azure.yaml` and authentication hooks | Keep unless separately reviewed |
| managed identity, RBAC, networking, and diagnostics | Keep |
| deployment actions and environment export | Keep; adapt documented inputs only |
| backend app factory, dependency construction, errors, and telemetry | Usually keep |
| authentication and owner authorization | Keep |
| work-item model and lifecycle | Replace only with a coordinated contract change |
| PDF validation and 20 MB limit | Keep or deliberately replace across all layers |
| frontend shell, theme, auth controls, and API error handling | Usually keep |
| work-item pages, types, API module, and fixtures | Replace |
| Logic App prompts and result schema | Replace after Phase 4 implementation |
| synthetic sample content | Replace with newly authored synthetic content |
| tests | Update with every changed contract |

## Safe replacement order

1. Define the new domain, users, inputs, and expected output.
2. Decide whether the existing work-item lifecycle still fits.
3. Define the public API and persisted record together.
4. Update backend models, validation, services, routes, and tests.
5. Update the Logic App trigger, instructions, output schema, and failure codes.
6. Update frontend types, API functions, pages, result rendering, and tests.
7. Replace synthetic fixtures and sample generation.
8. Update architecture, setup, and troubleshooting documentation.
9. Run `./scripts/validate.sh all`.
10. Request separate infrastructure review if the solution cannot fit the
    existing resource contract.

## Cross-component contract map

### Input type and size

Current contract: one PDF, `application/pdf`, up to 20 MB.

Update together:

- `app/backend/backend/pdf.py`
- backend route and service tests
- frontend file validation and submission components
- frontend tests and user guidance
- Blob content metadata
- Logic App source handling
- synthetic sample generator
- documentation

### Work-item lifecycle

Current states:

```text
submitted -> queued -> processing -> completed
                  \-> failed
```

Update together:

- backend `WorkItemStatus` and transition rules
- persistence compensation behavior
- public API types
- frontend status chips and polling termination
- workflow trigger, claim, completion, and failure branches
- test fixtures
- operational documentation

### Public result

The planned generic result is:

```json
{
  "summary": "Concise grounded summary",
  "category": "informational",
  "key_points": ["Grounded point"]
}
```

Update together:

- workflow structured-output schema
- Cosmos result document
- backend response tests
- frontend result component and types
- frontend fixtures and tests
- replacement and troubleshooting docs

### Blob path

Current server-generated path:

```text
work-items/<id>/source.pdf
```

The client never supplies this path. Changing it affects backend upload and
cleanup, workflow correlation, tests, and operational diagnostics.

### Authentication and ownership

The browser account display is not authorization. Backend identity from App
Service authentication owns every work item. Do not add a caller-provided
owner ID to requests.

## Backend replacement surfaces

Reusable:

- `backend/app.py`
- `backend/auth.py`
- `backend/errors.py`
- `backend/telemetry.py`
- repository error mapping and dependency construction patterns

Domain-specific:

- `backend/models/work_items.py`
- `backend/services/work_items.py`
- `backend/routes/work_items.py`
- PDF validation when the input contract changes
- work-item repository query behavior when the data model changes

Preserve explicit errors and compensation. Do not turn dependency failures into
success-shaped empty responses.

## Frontend replacement surfaces

Reusable:

- `src/app/`
- `src/api/client.ts`
- `src/api/errors.ts`
- `src/api/auth.ts`
- shared loading and error components
- Vite, TypeScript, test, and static-hosting configuration

Replaceable:

- `src/features/workItems/`
- work-item pages
- `src/api/workItems.ts`
- `src/types/workItems.ts`
- work-item fixtures

Keep same-origin API calls unless hosting is intentionally redesigned.

## Workflow and prompt replacement

The workflow is planned in Phase 4 and not implemented yet. When present:

- replace generic instruction files with newly authored solution instructions;
- change the structured output schema together with backend/frontend contracts;
- preserve managed identity, safe tracking, retries, and ETag concurrency;
- keep source and prompt content out of run-history telemetry; and
- test duplicate delivery and terminal-state behavior.

Do not copy prompts or criteria from a private solution.

## Adding Azure services

If the new solution needs Foundry projects, AI Search, Document Intelligence,
or another Azure service, use the additive Phase 6 strategy:

1. define an optional infrastructure entry point;
2. preserve the baseline deployment unchanged;
3. define outputs and application settings;
4. add managed identity and least-privilege RBAC;
5. add networking and diagnostics;
6. document region, quota, and cost constraints; and
7. validate the extension alone and with the base solution.

Do not make opportunistic edits under `infra/`.
