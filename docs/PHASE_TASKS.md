# Proposed Phase Tasks

This backlog is planning material, not implementation authorization. The tasks
for each phase must be refined and approved before work begins.

## Phase 1 - Infrastructure and Deployment Baseline

The implementation-ready task plan, dependencies, deliverables, validation
steps, privacy controls, and review gates are defined in
[Phase 1 Implementation Plan](phases/PHASE_1_IMPLEMENTATION_PLAN.md).

The summary below remains the high-level backlog.

### 1.1 Define the target resource contract

- Confirm required hosting, storage, database, workflow, AI, identity,
  monitoring, registry, and networking resources.
- Define required parameters, outputs, application settings, and deployment
  dependencies.
- Identify which settings must remain configurable for different environments.

### 1.2 Prepare a local sanitization workspace

- Create a temporary directory outside the Git worktree.
- Stage only candidate infrastructure and deployment files needed for analysis.
- Record a checklist of prohibited identifiers and domain terms.
- Ensure the staging directory is never added to Git.

### 1.3 Generalize infrastructure locally

- Remove customer and domain identifiers.
- Replace environment-specific values with parameters.
- Remove unrelated resources and application-specific assets only when their
  behavior is not required by the starter.
- Preserve required deployment configuration without refactoring or
  optimization.
- Review identity, RBAC, networking, and service dependencies for completeness.

### 1.4 Generalize deployment automation locally

- Prepare the Azure Developer CLI project definition.
- Prepare authentication, configuration export, application deployment, and
  workflow deployment helpers.
- Prepare CI/CD workflows using generic secret and variable names.
- Remove private URLs, repository references, and environment assumptions.

### 1.5 Introduce and validate sanitized assets

- Copy only reviewed, sanitized files into the clean repository.
- Compile or validate infrastructure templates.
- Check shell and workflow syntax.
- Run secret, identifier, and prohibited-term scans.
- Inspect the full staged diff before commit.
- Record the infrastructure integrity baseline for later phases.

### Phase 1 review gate

- Review every introduced file.
- Confirm no proprietary source, history, identifiers, or data are present.
- Approve the infrastructure and deployment baseline.

## Phase 2 - Backend and Data Contracts

**Status:** Implemented locally and pending the Phase 2 review gate.

The implementation-ready schema, API contract, failure-compensation behavior,
test matrix, dependencies, and review gates are defined in
[Phase 2 Implementation Plan](phases/PHASE_2_IMPLEMENTATION_PLAN.md).

The summary below remains the high-level backlog.

### 2.1 Define the generic work-item schema

- Define identifiers, source metadata, processing state, timestamps, AI output,
  and structured errors.
- Define valid state transitions and idempotency requirements.
- Define database partitioning and indexing expectations.

### 2.2 Scaffold the backend

- Configure the Python project and web framework.
- Add typed configuration and dependency construction.
- Add health and readiness endpoints.
- Add structured logging and telemetry integration.

### 2.3 Implement storage and database access

- Validate text and file inputs.
- Store source content using the provisioned object storage.
- Create and query work-item records in the document database.
- Use explicit errors and safe concurrency behavior.

### 2.4 Implement the API

- Add create, list, detail, and status endpoints.
- Define consistent request, response, pagination, and error contracts.
- Enforce content type, size, and identifier validation.

### 2.5 Test and validate

- Add unit and route tests with Azure dependencies mocked at client boundaries.
- Cover invalid input and service failure behavior.
- Run formatting, type, test, leakage, and infrastructure-integrity checks.

### Phase 2 review gate

- Review API and persistence contracts.
- Demonstrate tests and local API behavior.
- Approve the frontend integration contract.

## Phase 3 - Frontend Hello-World Application

### 3.1 Scaffold the frontend

- Configure TypeScript, the selected web framework, build tooling, linting, and
  tests.
- Configure development API proxying and production static output.

### 3.2 Implement the starter flow

- Add a concise architecture-oriented landing page.
- Add text or supported-file submission.
- Add work-item list and detail views.
- Show pending, completed, and failed states.

### 3.3 Define replacement boundaries

- Separate reusable application shell from sample-domain components.
- Centralize API models and configuration.
- Mark hello-world assets that downstream solutions should replace.

### 3.4 Test and validate

- Test validation, API errors, loading, empty, success, and failure states.
- Run lint, type checking, tests, production build, and leakage scans.
- Verify generated assets are excluded from Git.

### Phase 3 review gate

- Demonstrate the local frontend and mocked vertical slice.
- Review accessibility and replacement boundaries.
- Approve the workflow integration contract.

## Phase 4 - Logic App and Azure AI Integration

### 4.1 Define the workflow contract

- Define the trigger payload, correlation identifiers, status updates,
  idempotency keys, retries, and terminal failures.
- Define the structured AI output schema.

### 4.2 Implement the generic workflow

- Read the stored source content.
- Invoke the configured Azure AI deployment.
- Request a concise summary and category.
- Validate structured output before persistence.
- Persist completed or failed state explicitly.

### 4.3 Add workflow observability

- Correlate frontend, backend, workflow, storage, database, and AI operations.
- Avoid logging source content or sensitive values.
- Expose actionable failure details without leaking internals.

### 4.4 Validate the deployed vertical slice

- Deploy to a clean environment.
- Submit synthetic text and a synthetic document.
- Verify storage, workflow execution, AI result, database persistence, and UI
  display.
- Exercise one controlled failure and retry case.
- Re-run leakage and infrastructure-integrity checks.

### Phase 4 review gate

- Demonstrate the deployed end-to-end flow.
- Review reliability, error behavior, and operational visibility.
- Approve starter-hardening scope.

## Phase 5 - Starter Readiness

### 5.1 Complete documentation

- Document prerequisites, setup, local development, deployment, validation, and
  troubleshooting.
- Document architecture and application/infrastructure boundaries.
- Document expected Azure resources and cost drivers.

### 5.2 Create the replacement guide

- Identify the files and contracts downstream solutions should replace.
- Explain how to add domain models, routes, pages, prompts, and workflow logic.
- Explain which identity, telemetry, deployment, and infrastructure mechanisms
  should remain intact.

### 5.3 Add continuous validation

- Validate backend and frontend code.
- Validate infrastructure and deployment assets.
- Detect infrastructure baseline drift.
- Scan for secrets, private identifiers, and prohibited content.

### 5.4 Perform clean-room release validation

- Clone the public repository into a new directory.
- Follow documentation without relying on developer-local state.
- Provision, deploy, and smoke-test a clean environment.
- Confirm Git history and release artifacts contain only approved material.

### Phase 5 review gate

- Approve the repository for reusable starter release.
- Decide release versioning and template-distribution approach.

## Phase 6 - Optional Azure AI Extensions

### 6.1 Approve an additive infrastructure strategy

- Evaluate a separate template entry point or equivalent additive mechanism.
- Do not modify or refactor the base infrastructure baseline.
- Define output and configuration integration with the application.

### 6.2 Add Microsoft Foundry integration

- Add optional project resources, identity, RBAC, diagnostics, and a minimal
  application example.

### 6.3 Add Azure AI Search integration

- Add optional search resources, index schema, identity, networking,
  diagnostics, and a minimal indexing/query example.

### 6.4 Add Azure AI Document Intelligence integration

- Add optional service resources, identity, networking, diagnostics, and a
  minimal extraction example.

### 6.5 Validate independent composition

- Test each extension alone and in approved combinations.
- Document quotas, region support, permissions, cost, and removal.
- Confirm deployments without extensions remain unchanged.

### Phase 6 review gate

- Review and release each extension independently.
