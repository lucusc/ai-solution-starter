# Phase 3 Implementation Plan

## Status

**Planning only.** Phase 3 frontend code has not been implemented.

Implementation must not begin until this plan is explicitly approved. Phase 2
remains in an unpushed local commit, so Phase 3 planning and any later
implementation must also remain local until the applicable review gates allow
the commit stack to be pushed.

## Objective

Implement a small, accessible React application that demonstrates the generic
PDF work-item flow established in Phase 2:

1. explain the starter architecture and replacement boundaries;
2. submit one validated PDF with an idempotency key;
3. list the authenticated user's work items;
4. inspect one work item and its processing state;
5. poll an open nonterminal detail view;
6. render completed AI output and explicit failures; and
7. build into the existing Quart container for same-origin deployment.

Phase 3 must adapt to the approved Phase 1 infrastructure and Phase 2 API. It
must not change Bicep, Azure resource configuration, persistence contracts, or
workflow behavior.

## Approved Decisions

| Decision | Phase 3 direction |
| --- | --- |
| Framework | React 19 with TypeScript |
| Build tool | Vite |
| UI library | Material UI |
| Navigation | Routed dashboard and work-item detail page |
| Submission type | PDF only, matching Phase 2 |
| Maximum PDF size | 20 MB, matching Phase 2 |
| Authentication UX | Easy Auth account display and sign-in/sign-out controls |
| API hosting | Relative same-origin `/api/v1` requests |
| List pagination | Explicit `Load more` using opaque continuation tokens |
| Status filtering | Optional lifecycle status filter |
| Polling | Poll only an open nonterminal detail view |
| Completed result | Prefer `summary` and `category`; safe generic fallback |
| Runtime mock mode | None |
| Mocking for tests | Test-only request fixtures |
| Browser automation | Deferred; use Vitest and Testing Library in Phase 3 |
| State management | React hooks and explicit API modules; no global state library |
| Production hosting | Static assets served by the Quart backend container |

## Phase Boundaries

### Included

- React, TypeScript, Vite, Material UI, routing, linting, and test tooling
- typed frontend representation of the Phase 2 public API
- centralized same-origin API client and error mapping
- architecture-oriented landing/dashboard page
- PDF submission form and client-side validation
- idempotent retry behavior for uncertain create outcomes
- owner-scoped work-item list, status filter, and continuation paging
- routed detail page
- nonterminal detail polling with cleanup and visibility awareness
- completed and failed result states
- Easy Auth account controls
- loading, empty, validation, dependency-error, not-found, and offline states
- accessible responsive presentation
- static asset serving and SPA fallback in Quart
- frontend build integration with local and GitHub deployment paths
- component, route, API-client, and backend static-serving tests
- replacement-boundary documentation

### Excluded

- backend API or persistence schema changes
- Logic App workflow implementation
- Azure OpenAI calls
- PDF previewing, parsing, rendering, OCR, or text extraction
- text submission
- delete, cancel, retry-processing, or review actions
- tenant-wide or reviewer views
- runtime demo data or mock API mode
- Storybook
- Playwright or deployed end-to-end browser tests
- service worker or offline-write support
- infrastructure changes
- production Azure deployment

## Immutable Contracts

### Infrastructure

- Do not modify any file under `infra/`.
- Preserve the Phase 1 Bicep checksum baseline.
- Continue using the existing App Service and container deployment.
- Do not add Static Web Apps, CDN, Front Door, or another hosting resource.
- Do not alter Easy Auth behavior through infrastructure.

### Backend API

The frontend consumes only these Phase 2 routes:

| Method | Route | Frontend use |
| --- | --- | --- |
| `POST` | `/api/v1/work-items` | Submit one PDF |
| `GET` | `/api/v1/work-items` | List and filter work items |
| `GET` | `/api/v1/work-items/<id>` | Load detail |
| `GET` | `/api/v1/work-items/<id>/status` | Poll nonterminal detail |
| `GET` | `/healthz` | Deployment diagnostics only |
| `GET` | `/readyz` | Deployment diagnostics only |

The frontend must not infer or access Blob paths, owner IDs, Cosmos partition
keys, `_etag`, raw authentication headers, or idempotency hashes.

### Lifecycle

The UI recognizes:

- `submitted`
- `queued`
- `processing`
- `completed`
- `failed`

`completed` and `failed` are terminal. Phase 3 does not create workflow state;
it only represents the public state returned by the backend.

## Proposed Frontend Structure

```text
app/frontend/
├── index.html
├── package.json
├── package-lock.json
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── vite.config.ts
├── eslint.config.js
├── README.md
└── src/
    ├── main.tsx
    ├── app/
    │   ├── App.tsx
    │   ├── AppProviders.tsx
    │   ├── routes.tsx
    │   └── theme.ts
    ├── api/
    │   ├── client.ts
    │   ├── errors.ts
    │   ├── workItems.ts
    │   └── auth.ts
    ├── components/
    │   ├── AppShell.tsx
    │   ├── ErrorAlert.tsx
    │   ├── LoadingState.tsx
    │   ├── StatusChip.tsx
    │   └── WorkItemSummary.tsx
    ├── features/
    │   └── workItems/
    │       ├── WorkItemForm.tsx
    │       ├── WorkItemList.tsx
    │       ├── WorkItemResult.tsx
    │       ├── useWorkItem.ts
    │       └── validation.ts
    ├── pages/
    │   ├── DashboardPage.tsx
    │   ├── WorkItemDetailPage.tsx
    │   └── NotFoundPage.tsx
    ├── types/
    │   ├── api.ts
    │   └── workItems.ts
    ├── utils/
    │   ├── dates.ts
    │   ├── files.ts
    │   └── results.ts
    └── test/
        ├── setup.ts
        ├── handlers.ts
        ├── server.ts
        └── fixtures.ts
```

Exact file boundaries may be adjusted during implementation, but API access,
sample-domain UI, reusable shell components, and test fixtures must remain
separate.

## Routing Contract

| Route | View |
| --- | --- |
| `/` | Architecture introduction, PDF submission, and recent work-item list |
| `/work-items/:id` | Work-item metadata, lifecycle state, output, and errors |
| `*` | Accessible not-found page with navigation back to the dashboard |

Routing uses browser history. Quart must provide an SPA fallback for
non-API paths while preserving JSON `404` behavior for `/api/*`.

## Application Shell and Landing Page

The shell will provide:

- a concise starter name and home link;
- an authenticated account area;
- a sign-in or sign-out action as appropriate;
- a centered responsive content region;
- consistent loading and error presentation; and
- no external or solution-specific branding.

The dashboard will explain the replaceable vertical slice without exposing
deployment internals. It will show:

1. **Submit** - validate and store a synthetic or user-selected PDF.
2. **Process** - indicate that a Logic App and Azure AI will process queued
   work in Phase 4.
3. **Review** - inspect explicit processing state and structured output.

The architecture explanation is application copy, not a diagram of an external
environment.

## Authentication UX

Azure App Service Easy Auth remains the authority for authentication.

### Azure behavior

- Query `/.auth/me` to obtain display-only account information.
- Never derive authorization or owner identity in the browser.
- Sign in through `/.auth/login/aad?post_login_redirect_uri=/`.
- Sign out through `/.auth/logout?post_logout_redirect_uri=/`.
- Treat an absent Easy Auth session as signed out.
- If an API call returns `401`, present a sign-in action rather than retrying.
- Do not log or persist the `/.auth/me` payload.

### Local development

- Vite proxies `/api` to the local Quart server.
- Quart uses the approved `LOCAL_AUTH_SUBJECT` backend setting.
- The frontend may use a development-only display label such as
  `VITE_LOCAL_AUTH_DISPLAY_NAME`.
- Local account display is cosmetic and cannot influence backend identity.
- Production builds must not require the local display setting.

## Frontend API Contract

### API client

The centralized client will:

- use relative URLs;
- send `Accept: application/json`;
- send `FormData` without manually setting the multipart boundary;
- include `Idempotency-Key` only on create;
- parse the Phase 2 shared error envelope;
- retain the backend `request_id` as a user-visible support reference;
- map network failures separately from HTTP failures;
- support `AbortSignal`;
- never automatically log request bodies, files, auth data, or continuation
  tokens; and
- avoid automatic write retries.

### Frontend types

The frontend will define types for:

- `WorkItemStatus`
- `WorkItemSource`
- `ProcessingError`
- `WorkItem`
- `WorkItemStatusResponse`
- `WorkItemListResponse`
- `ApiErrorEnvelope`
- `EasyAuthPrincipal`

Types must match only the public API. Internal backend models must not be
recreated in frontend code.

### Error handling

The UI will distinguish:

- field validation errors;
- authentication required;
- not found;
- conflict;
- request too large;
- dependency rejected or unavailable;
- unexpected server response; and
- network/offline failure.

Messages remain concise and user-safe. When available, the backend request ID
is displayed as a support reference. Exception objects, stack traces, Azure
request IDs, and response internals are not rendered.

## PDF Submission Contract

The form accepts one PDF.

### Client validation

Validate before sending:

1. a file is selected;
2. the filename ends in `.pdf`, case-insensitively;
3. the browser-reported type is `application/pdf` when present;
4. the file is non-empty; and
5. the file is no larger than 20 MB.

Client validation is a usability feature only. The backend remains
authoritative.

### Submission behavior

- Generate an idempotency key with `crypto.randomUUID()` when a submission
  attempt begins.
- Reuse that key if the user retries after an ambiguous network failure.
- Generate a new key after the selected file changes, the form is reset, or a
  completed response is accepted.
- Disable duplicate submit actions while one request is active.
- On `201`, navigate to the created work item.
- On `200` replay, navigate to the existing work item and identify that the
  previous submission was recovered.
- Do not persist the file or idempotency key in local storage.
- Do not preview or parse PDF contents.

The form will use an accessible labeled file input with optional drag-and-drop
enhancement. Drag-and-drop must not be the only input mechanism.

## Work-Item List Contract

The dashboard list will:

- load newest-first items from `GET /api/v1/work-items`;
- default to all statuses;
- allow one status filter;
- reset paging when the status changes;
- show an explicit loading state;
- show an architecture-oriented empty state;
- render filename, status, creation time, and updated time;
- link each row or card to its detail route;
- expose an explicit refresh action; and
- use `Load more` when a continuation token is present.

Continuation tokens:

- remain opaque;
- are held only in component memory;
- are not logged, persisted, decoded, or placed in the URL;
- are sent back unchanged; and
- are discarded when the filter changes or the list is refreshed.

The list will not poll automatically in Phase 3.

## Work-Item Detail Contract

The detail page will show:

- source display name;
- content type and human-readable size;
- created and updated timestamps;
- status and version;
- lifecycle-oriented explanatory copy;
- structured failure details when failed; and
- structured output when completed.

The page must not display internal Blob paths, owner IDs, hashes used for
idempotency, continuation tokens, or persistence metadata. The public source
SHA-256 may be placed in a collapsed technical-details section rather than the
primary UI.

### Polling

- Fetch the full detail on initial navigation.
- While status is `submitted`, `queued`, or `processing`, poll the status route
  every five seconds.
- Pause polling while the document is hidden.
- Abort in-flight polling on route change or component unmount.
- Stop immediately on `completed`, `failed`, `401`, or `404`.
- After a terminal status response, refetch the full detail once to obtain
  result or error data.
- Use a visible manual refresh action regardless of polling state.
- Do not overlap polling requests.

## Result Rendering Contract

When `status === "completed"`:

1. If `result.summary` is a string, render it as the primary summary.
2. If `result.category` is a string, render it as a category label.
3. Render remaining safe JSON-compatible fields in a generic details section.
4. If preferred fields are absent, render the complete result through the
   generic fallback.

The generic renderer will:

- render strings, finite numbers, booleans, null, arrays, and plain objects;
- bound nesting depth and collection length;
- sort object keys for stable presentation;
- use text nodes rather than HTML injection;
- never use `dangerouslySetInnerHTML`; and
- present unsupported or excessively deep data as unavailable rather than
  recursively rendering without a bound.

When `status === "failed"`, render the public error code, message, retryable
indicator, and occurrence time. Phase 3 does not provide a processing retry
action.

## Accessibility and Responsive Behavior

Implementation will target WCAG 2.1 AA fundamentals:

- semantic landmarks and heading order;
- keyboard-accessible navigation and controls;
- visible focus indicators;
- labels and helper text connected to inputs;
- status announcements through an appropriate live region;
- status distinctions not based on color alone;
- sufficient color contrast through the MUI theme;
- error focus management after failed submission;
- reduced-motion preference respected;
- responsive list cards or table behavior on narrow screens; and
- touch targets suitable for mobile use.

Automated accessibility assertions may use Testing Library and `jest-axe`, but
manual keyboard and responsive review remains part of the review gate.

## Static Hosting and Container Integration

### Vite output

- Production output directory:
  `app/backend/static/`
- Clear the output directory before a production build.
- Use relative or root-based assets compatible with same-origin hosting.
- Generated assets remain Git-ignored and must never be committed.
- Source maps are disabled for the production starter unless a later
  observability decision explicitly enables them.

### Quart static serving

Quart will:

- serve generated assets from the backend static directory;
- serve `index.html` for `/`;
- provide SPA fallback for valid non-API browser routes;
- preserve backend API, health, readiness, and framework error behavior;
- return a normal `404` when a requested static asset does not exist; and
- avoid opening or serving arbitrary filesystem paths.

Static-serving changes are application changes, not infrastructure changes.

### Build and deployment paths

The following paths must all build the frontend before packaging the backend:

- local production validation;
- `app/backend/docker-build.sh`;
- backend container CI; and
- `.github/workflows/azure-dev.yml`.

The existing deployment architecture remains:

```text
Vite build -> app/backend/static -> backend container -> App Service
```

Use `npm ci` when a lockfile is present. The Docker build context and deployment
actions may be adjusted only as needed to package the generated assets; Bicep
must not change.

## Replacement Boundaries

### Reusable shell

Intended to remain across downstream solutions:

- app providers and theme foundation;
- routing setup;
- App Shell;
- API client and error envelope handling;
- auth account controls;
- loading and error components;
- date and file-size formatting;
- CI, build, and static-hosting integration.

### Replaceable sample domain

Expected to be adapted or removed:

- architecture landing copy;
- PDF submission form;
- work-item list fields;
- status explanatory copy;
- summary/category result presentation;
- sample empty states;
- work-item fixtures.

The frontend README will identify these boundaries and give a short replacement
checklist without referring to any private source project.

## Telemetry and Privacy

Phase 3 introduces no browser telemetry SDK.

Frontend code must not log:

- selected file content or filename;
- Easy Auth payloads;
- idempotency keys;
- continuation tokens;
- result payloads;
- API response bodies; or
- owner identity.

The browser may display the public filename and result because those fields are
part of the approved user-facing API. Console logging should be absent from
production application code except for a narrowly justified startup failure,
which should normally be rendered instead.

## Testing Strategy

### Tooling

- Vitest
- React Testing Library
- `@testing-library/user-event`
- jsdom
- Mock Service Worker for test-only HTTP fixtures
- optional `jest-axe` for targeted accessibility assertions

No test fixture may contain a real or private document. Synthetic PDFs use only
the minimum `%PDF-` marker needed for browser file objects.

### API-client tests

- relative route construction
- multipart create request and idempotency header
- no manual multipart content-type boundary
- create `201` and replay `200`
- shared error-envelope parsing
- request ID preservation
- network failure mapping
- status filter encoding
- page-size bounds
- continuation-token pass-through
- abort behavior

### Submission tests

- missing file
- deceptive extension
- invalid browser content type
- empty file
- file larger than 20 MB
- disabled duplicate submission
- successful create navigation
- replay navigation and recovery notice
- ambiguous failure retry reuses the idempotency key
- changed file produces a new idempotency key

### List tests

- initial loading
- empty state
- newest-first response rendering
- all lifecycle statuses
- status filter reset
- refresh
- `Load more`
- continuation-token append behavior
- API and offline errors

### Detail tests

- initial loading
- invalid or missing item
- submitted, queued, and processing states
- completed summary and category
- completed generic fallback
- bounded nested result rendering
- failed public error
- polling starts for nonterminal state
- polling pauses while hidden
- polling stops on terminal state
- terminal status triggers one full-detail refresh
- unmount aborts in-flight work

### Authentication tests

- signed-in account display
- signed-out sign-in action
- sign-out link
- `401` API response presents authentication recovery
- local development display cannot affect API ownership

### Backend integration tests

- `/` serves the built SPA when assets exist
- a frontend route serves SPA `index.html`
- `/api/v1/*` retains JSON behavior
- missing asset returns `404`, not SPA HTML
- static path traversal is rejected

## Validation Matrix

Required Phase 3 validation:

| Area | Command or evidence |
| --- | --- |
| Dependency restore | `npm ci` |
| Lint | `npm run lint` |
| Type checking | `npm run typecheck` |
| Component tests | `npm test -- --run` |
| Production build | `npm run build` |
| Backend regression | Python test, Ruff, and Mypy commands from Phase 2 |
| Container | Build image and probe `/` and `/healthz` |
| Generated assets | Confirm `app/backend/static/` is ignored and untracked |
| Infrastructure | `./scripts/verify_bicep_baseline.sh` |
| Repository hygiene | secret, identifier, prohibited-term, and history scans |
| Diff quality | `git diff --check` and complete staged-diff inspection |

The production container probe must confirm both the SPA and backend health
route from the same process.

## Work Package 3.0 - Establish Frontend Tooling

### Tasks

1. Scaffold React 19, TypeScript, and Vite in `app/frontend`.
2. Add Material UI and React Router.
3. Add ESLint, Vitest, Testing Library, jsdom, and Mock Service Worker.
4. Add scripts for development, lint, type checking, testing, and build.
5. Commit the lockfile.
6. Configure Vite development proxying and production output.
7. Configure a minimal application theme and test setup.

### Acceptance criteria

- The frontend starts without Azure credentials.
- TypeScript strict mode is enabled.
- The test environment performs no real network calls.
- Production output targets the ignored backend static directory.
- No generated asset is tracked.

## Work Package 3.1 - Define API and Authentication Boundaries

### Tasks

1. Add public API types.
2. Implement the centralized fetch client.
3. Implement error-envelope parsing and request-ID handling.
4. Implement work-item API functions.
5. Implement Easy Auth account lookup and sign-in/sign-out URLs.
6. Add local display-only identity configuration.

### Acceptance criteria

- All API requests are same-origin and typed.
- File, auth, key, token, and result content are never logged.
- `401` has a dedicated recovery path.
- No caller-controlled owner identity is sent.
- API-client tests cover request and response contracts.

## Work Package 3.2 - Implement Reusable Application Shell

### Tasks

1. Configure providers, router, and MUI theme.
2. Implement App Shell and account controls.
3. Add reusable loading, empty, and error components.
4. Add status chips and formatting utilities.
5. Add not-found routing.

### Acceptance criteria

- Shell works at desktop and mobile widths.
- Navigation and account actions are keyboard accessible.
- Status is not communicated by color alone.
- Generic shell code does not import sample feature internals.

## Work Package 3.3 - Implement PDF Submission

### Tasks

1. Implement bounded client validation.
2. Implement file selection and drag-and-drop enhancement.
3. Implement idempotency-key lifecycle.
4. Implement create, replay, retry, and navigation behavior.
5. Add accessible progress and validation feedback.

### Acceptance criteria

- Invalid files are rejected before an API call.
- The backend remains authoritative for PDF validation.
- Duplicate clicks cannot create concurrent submissions.
- An ambiguous retry reuses the same idempotency key.
- File data and idempotency keys are not persisted.

## Work Package 3.4 - Implement Work-Item Dashboard

### Tasks

1. Add architecture-oriented landing content.
2. Load the owner-scoped list.
3. Add lifecycle status filtering.
4. Add refresh and continuation-based `Load more`.
5. Add loading, empty, API-error, and offline states.

### Acceptance criteria

- The list uses only the Phase 2 public response.
- Status changes reset pagination.
- Continuation tokens remain opaque and in memory.
- The dashboard does not poll automatically.
- Each item links to the routed detail page.

## Work Package 3.5 - Implement Work-Item Detail and Polling

### Tasks

1. Load the full detail by route ID.
2. Render source metadata and lifecycle state.
3. Implement detail-only status polling.
4. Stop and clean up polling correctly.
5. Refetch full detail after a terminal transition.
6. Render completed and failed states.
7. Add bounded generic result rendering.

### Acceptance criteria

- Polling occurs only for an open nonterminal detail.
- Polling pauses when the page is hidden and never overlaps.
- Terminal, unauthorized, and not-found responses stop polling.
- Completed output cannot inject HTML.
- Failed output exposes only the approved public error.

## Work Package 3.6 - Integrate Static Hosting and Deployment

### Tasks

1. Add Quart SPA and static asset serving.
2. Add backend static-serving tests.
3. Ensure local container builds include frontend assets.
4. Update the local ACR deployment helper to build the frontend first.
5. Update GitHub deployment to use the lockfile and verified frontend build.
6. Extend CI to validate frontend and combined container behavior.

### Acceptance criteria

- `/` and frontend routes render the SPA from Quart.
- APIs and health routes retain existing behavior.
- Missing asset paths return `404`.
- Local and GitHub deployment package identical frontend output.
- No Bicep file changes.

## Work Package 3.7 - Document Replacement Boundaries

### Tasks

1. Update the frontend README with setup and validation commands.
2. Document reusable shell files.
3. Document replaceable sample feature files.
4. Document API and auth assumptions.
5. Add a replacement checklist.
6. Update repository status documentation.

### Acceptance criteria

- A downstream team can identify what to keep and what to replace.
- Documentation contains no private source references.
- Development and production hosting behavior is explicit.
- Phase 4 workflow assumptions are clearly separated.

## Work Package 3.8 - Validate and Review

### Tasks

1. Run frontend lint, type checks, tests, and production build.
2. Run Phase 2 backend regression validation.
3. Build and probe the combined production container.
4. Verify generated assets are ignored.
5. Verify the Bicep baseline.
6. Run repository hygiene and history scans.
7. Inspect the complete staged diff.
8. Create a local-only Phase 3 review commit.
9. Pause before push or Phase 4 implementation.

### Acceptance criteria

- All required validation passes.
- The combined local vertical slice can create, list, and inspect mocked API
  states through tests.
- The production container serves both frontend and backend routes.
- Infrastructure is unchanged.
- No proprietary content or source history is present.
- The implementation remains unpushed until approved.

## Planned Task Dependencies

```text
3.0 Frontend tooling
 ├─> 3.1 API and authentication boundaries
 └─> 3.2 Reusable application shell
      ├─> 3.3 PDF submission
      └─> 3.4 Work-item dashboard
           └─> 3.5 Detail and polling
                └─> 3.6 Static hosting and deployment
                     └─> 3.7 Replacement documentation
                          └─> 3.8 Validation and review
```

API work and shell work may proceed in parallel after tooling. Static hosting
integration begins only after the production frontend build exists.

## Review Artifacts

The Phase 3 implementation review must include:

- route and component inventory;
- public frontend type contract;
- idempotency-key behavior;
- polling state machine;
- completed and failed screenshots using test-only fixtures;
- accessibility review notes;
- test inventory and results;
- combined container probe result;
- generated-asset and Bicep-baseline confirmation;
- privacy and history scan results; and
- complete unpushed commit diff.

## Final Phase 3 Acceptance Criteria

- React dashboard and detail routes are implemented.
- Only PDFs up to 20 MB are offered for submission.
- Idempotent create and ambiguous retry behavior are correct.
- Lists support status filtering, refresh, and continuation paging.
- Detail polling is bounded and terminates correctly.
- Submitted, queued, processing, completed, and failed states are represented.
- Summary/category and generic result rendering are safe.
- Easy Auth account controls work without influencing authorization.
- Frontend and backend are served from one production container.
- Accessibility fundamentals are validated.
- Frontend lint, type checks, tests, and build pass.
- Phase 2 backend regressions and container probes pass.
- Bicep checksums remain unchanged.
- No generated assets, proprietary data, or private source references exist.
- Implementation remains unpushed until explicitly approved.

## Stop Conditions

Stop and request review if:

- a frontend requirement needs a backend API or persistence change;
- a deployment fix would require a Bicep change;
- Easy Auth browser behavior differs from the documented App Service contract;
- idempotent retry cannot preserve a key safely in memory;
- static fallback intercepts API, health, readiness, or missing-asset errors;
- PDF handling requires parsing or retaining file content beyond submission;
- result rendering cannot safely bound arbitrary structured output;
- generated assets enter Git history;
- a dependency introduces telemetry or content logging by default; or
- live Azure validation would create or modify resources without approval.
