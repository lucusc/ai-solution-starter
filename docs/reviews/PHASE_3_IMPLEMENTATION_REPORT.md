# Phase 3 Implementation Report

## Scope

Phase 3 implements the replaceable hello-world frontend:

- React 19, TypeScript, Vite, and Material UI
- routed dashboard and work-item detail views
- Easy Auth account display and sign-in/sign-out controls
- PDF-only submission with bounded client validation
- retry-safe in-memory idempotency keys
- status filtering and continuation-token paging
- nonterminal detail polling
- completed summary/category and safe generic result rendering
- failed-state presentation
- test-only API fixtures
- Quart static asset and SPA fallback hosting
- combined frontend/backend container packaging
- frontend CI, local deployment integration, and replacement documentation

No Logic App processing, AI invocation, runtime mock mode, browser automation,
or infrastructure change is included.

## Route and component inventory

| Route | Primary components |
| --- | --- |
| `/` | Architecture introduction, `WorkItemForm`, and `WorkItemList` |
| `/work-items/:id` | Source metadata, status polling, result or failure |
| `*` | Accessible not-found page |

Reusable shell boundaries include providers, routing, theme, account controls,
API error handling, status presentation, and formatting utilities. The
work-item feature, pages, public types, API functions, and synthetic fixtures
are explicitly documented as replaceable.

## API and state behavior

- All application requests use relative same-origin URLs.
- Owner identity remains backend-controlled.
- Create requests use `FormData` and a UUID idempotency key.
- An ambiguous retry reuses the key in memory.
- Changing the file or completing a create discards the key.
- Continuation tokens remain opaque and in component memory.
- The dashboard refreshes manually and does not poll.
- An open nonterminal detail polls every five seconds.
- Polling pauses while hidden, does not overlap, and stops on terminal,
  unauthorized, or missing state.
- Terminal status triggers one full-detail refresh.

## Result and privacy behavior

Completed output prefers string `summary` and `category` fields, then renders
remaining JSON-compatible fields through a bounded text-only renderer. No HTML
injection API is used.

Frontend code does not log file content, filenames, identity payloads,
idempotency keys, continuation tokens, API response bodies, or AI results.
Generated frontend assets are ignored by Git.

## Validation evidence

- 11 frontend tests pass across 7 files.
- Frontend ESLint and strict TypeScript checks pass.
- Production frontend build passes on Node 20.
- `npm audit` reports zero runtime or development vulnerabilities.
- 45 backend tests pass.
- Backend Ruff, formatting, and Mypy checks pass.
- Backend checks pass on Python 3.12.
- The combined production image builds successfully.
- The running image serves `/`, a routed SPA detail URL, and `/healthz`.
- Missing assets and unknown API routes return `404`, not SPA HTML.
- The Phase 1 Bicep checksum baseline remains unchanged.
- Generated assets are confirmed ignored and untracked.

The host Python 3.14 environment still emits the previously documented
`pytest-asyncio` deprecation warnings. The supported Python 3.12 validation is
clean.

## Deferred validation

No live Azure deployment was performed. Easy Auth browser behavior and the
deployed frontend/backend combination will be exercised only after explicit
deployment approval. Phase 4 remains responsible for real `processing` and
`completed` workflow transitions.

## Review gate

The implementation is committed locally only. It must not be pushed and Phase
4 must not begin until the Phase 3 review gate is explicitly approved.
