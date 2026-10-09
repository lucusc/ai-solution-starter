# Frontend

React 19, TypeScript, Vite, and Material UI application for the generic PDF
work-item flow.

## Development

Install dependencies from the repository root:

```bash
cd app/frontend
npm ci
```

Start the Quart backend on port 8000 with `LOCAL_AUTH_SUBJECT` configured, then
start Vite:

```bash
cp .env.example .env.local
npm run dev
```

Vite proxies `/api` to `VITE_PROXY_TARGET`. The local account label is
display-only; backend ownership always comes from Quart authentication.

## Validation

```bash
npm run lint
npm run typecheck
npm test -- --run
npm run build
```

The production build is written to `app/backend/static/`. That directory is
generated, Git-ignored, and served by Quart in the production container.

## Replacement boundaries

Reusable starter shell:

- `src/app/` - providers, routing, and theme
- `src/api/client.ts` and `src/api/errors.ts` - API and error-envelope handling
- `src/api/auth.ts` - Easy Auth account controls
- `src/components/AppShell.tsx`, `ErrorAlert.tsx`, and `LoadingState.tsx`
- `src/utils/` - generic formatting helpers
- Vite, TypeScript, lint, test, build, and deployment configuration

Replaceable sample feature:

- `src/features/workItems/` - PDF intake, polling, and result rendering
- `src/pages/DashboardPage.tsx` - architecture copy and recent-item experience
- `src/pages/WorkItemDetailPage.tsx` - work-item presentation
- `src/types/workItems.ts` and `src/api/workItems.ts` - public domain contract
- `src/test/fixtures.ts` - synthetic sample states

When adapting the starter:

1. Replace the work-item public types and API functions.
2. Replace the sample pages and feature components.
3. Preserve same-origin requests unless hosting intentionally changes.
4. Keep identity and authorization on the backend.
5. Keep generated assets out of Git.
6. Update tests before changing deployment integration.

## Authentication

In Azure, App Service Easy Auth protects the application and provides
`/.auth/me`, `/.auth/login/aad`, and `/.auth/logout`. The browser account name
is presentation-only and is never sent as an owner identifier.

## Phase boundary

Phase 3 represents every lifecycle state with test-only fixtures. The Logic App
and Azure AI workflow that produces processing and completed states is Phase 4
work.
