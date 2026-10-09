# AI Solution Starter Implementation Plan

## Goal

Build a reusable Azure AI solution starter with a replaceable hello-world
application and a production-shaped deployment. The finished starter will
demonstrate:

- a web frontend
- a backend API
- object storage
- a document database
- a Logic App workflow
- Azure AI model usage
- managed identity and role-based access
- application monitoring
- automated infrastructure and application deployment

## Constraints

- The repository begins with clean, independent Git history.
- Proprietary material must never enter the repository, even temporarily.
- Existing implementation patterns must be generalized in a local staging area
  before they are copied or reimplemented here.
- The reviewed infrastructure baseline must be preserved as-is after it is
  introduced. Do not optimize, reorganize, simplify, or refactor it.
- Every phase pauses after task refinement and again after implementation for
  review.
- Future AI services must be additive and must not rewrite the base
  infrastructure.

## Hello-World Scenario

The starter will use a generic AI work item:

1. A user enters text or uploads a small supported document.
2. The backend validates and stores the source.
3. A Logic App processes the item.
4. Azure AI produces a structured summary and category.
5. The workflow persists processing status and output.
6. The web application displays pending, completed, and failed items.

This vertical slice proves the architecture while remaining easy for a new
solution to replace.

## Phased Approach

### Phase 0 - Clean project shell and planning

Create the independent repository structure, sanitization policy, phased plan,
and proposed task backlog.

Exit criteria:

- Repository has a single clean root history.
- Only generic shell and planning content is tracked.
- No source repository identifiers or proprietary artifacts exist.
- Later phases are tasked but not implemented.
- Work pauses for review.

### Phase 1 - Infrastructure and deployment baseline

In a local staging area outside the Git worktree, inventory the complete proven
infrastructure and deployment behavior required by the starter. Generalize and
sanitize it before introducing it to this repository.

The approved scope is the full proven capability baseline, including Bicep,
Azure Developer CLI configuration, deployment scripts, and GitHub Actions.
Architecture and operational behavior must be preserved while names and
descriptive metadata are generalized. Real Azure provisioning is a separate
decision gate after local validation.

See the
[detailed Phase 1 implementation plan](phases/PHASE_1_IMPLEMENTATION_PLAN.md).

Exit criteria:

- Infrastructure and deployment contracts are documented.
- Sanitized infrastructure supports the required Azure architecture.
- Deployment configuration contains no customer-specific values.
- The inherited infrastructure configuration has not been optimized or
  refactored.
- Validation and leakage scans pass.
- Work pauses for review.

### Phase 2 - Backend and data contracts

Implement the generic API, storage, database, identity, configuration,
telemetry, and application error contracts.

The approved contract uses Quart, authenticated PDF-only intake up to 20 MB,
record-before-blob persistence, owner-only visibility, required idempotency
keys, continuation-token pagination, and the explicit
`submitted → queued → processing → completed/failed` lifecycle.

See the
[detailed Phase 2 implementation plan](phases/PHASE_2_IMPLEMENTATION_PLAN.md).

Exit criteria:

- Typed work-item API and persistence schema are implemented.
- Storage and database operations use managed identity where supported.
- Health, readiness, validation, and explicit error behavior are implemented.
- Backend tests pass.
- Infrastructure remains unchanged.
- Work pauses for review.

### Phase 3 - Frontend hello-world application

Implement a small frontend for creating, listing, and viewing generic work
items and their processing states.

Exit criteria:

- Primary submission and result-viewing flow works.
- Pending, completed, and failed states are represented.
- Frontend build, lint, and tests pass.
- Replaceable application boundaries are documented.
- Work pauses for review.

### Phase 4 - Logic App and Azure AI integration

Implement the workflow package that processes work items, invokes Azure AI,
validates structured output, and persists results.

Exit criteria:

- Workflow behavior is idempotent and observable.
- AI output is schema-validated.
- Retryable and terminal failures are explicit.
- The complete deployed vertical slice passes smoke validation.
- Infrastructure remains unchanged.
- Work pauses for review.

### Phase 5 - Starter readiness

Complete documentation, sample content, continuous integration, deployment
validation, replacement guidance, and release preparation.

See the
[detailed Phase 5 implementation plan](phases/PHASE_5_IMPLEMENTATION_PLAN.md).

Exit criteria:

- A new team can set up, run, deploy, and replace the sample app from the
  documentation.
- All examples are synthetic and generic.
- CI validates code, deployment assets, and infrastructure integrity.
- A fresh local clone passes documented validation without relying on
  developer-local state or Azure access.
- No tag, release, or template configuration is created.
- Work pauses for starter-readiness review.

### Phase 6 - Optional Azure AI services

Plan and implement optional Microsoft Foundry and Azure AI Document
Intelligence capabilities through additive infrastructure. Plan Azure AI
Search as a future module without implementing Search resources or
examples in this phase.

The approved approach adds conditional AI modules under
`infra/modules/ai/`, with minimal additive parameter, module, and output
wiring in `infra/main.bicep`. Environment variables select each service and
either deploy a new resource or reference a compatible pre-existing resource.
`USE_FOUNDRY` and `USE_DOCUMENT_INTELLIGENCE` each support `new`, `existing`,
or `none` and default to `none`. When both use `none`, the base resource graph
and behavior remain unchanged.

See the
[detailed Phase 6 implementation plan](phases/PHASE_6_IMPLEMENTATION_PLAN.md).

Exit criteria:

- Each AI service is independently optional.
- Foundry and Document Intelligence support deploy-or-reference-existing
  modes.
- No selected services is a successful no-op for the new modules.
- Base deployments remain compatible.
- Identity, networking, diagnostics, region availability, quotas, and cost are
  documented.
- Foundry and Document Intelligence include documentation-only REST/SDK usage
  commands and removal instructions.
- Azure AI Search is clearly marked as planned but not implemented.
- Every AI service module receives an independent review.

## Review Protocol

For each phase:

1. Refine the proposed tasks and measurable acceptance criteria.
2. Pause for approval.
3. Implement only the approved scope.
4. Validate functionality, infrastructure integrity, and source sanitization.
5. Present the results and pause again.
