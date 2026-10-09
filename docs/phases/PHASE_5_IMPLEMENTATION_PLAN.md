# Phase 5 Implementation Plan

## Status

**Implemented locally; pending review.** The approved starter-readiness work is
complete in the local unpushed commit stack. No Azure deployment, publication,
tag, release, repository-setting change, or Bicep change was performed.

Phase 5 implementation may proceed independently of Phase 4 implementation.
However, Phase 5 must describe the repository truthfully: it must not claim
that the complete AI workflow is implemented or validated until Phase 4 has
actually passed its review gate.

## Objective

Turn the repository from a phased implementation project into a clear,
maintainable starter that another team can clone, understand, validate, run
locally, deploy when authorized, and adapt without relying on undocumented
developer knowledge.

Phase 5 will:

1. make the root documentation task-oriented and accurate;
2. document architecture, prerequisites, setup, local development,
   deployment, validation, troubleshooting, and cost drivers;
3. define exact application and workflow replacement boundaries;
4. provide deterministic synthetic PDF generation;
5. add public-repository licensing and community health files;
6. consolidate continuous validation across implemented components;
7. validate the repository from a fresh local clone;
8. confirm infrastructure integrity and source-history cleanliness; and
9. produce review evidence without creating Azure resources or publishing a
   release.

## Approved Decisions

| Decision | Phase 5 direction |
| --- | --- |
| Dependency on Phase 4 | Phase 5 implementation may proceed independently |
| Repository consumption | Normal Git clone; no template-repository requirement |
| azd distribution | Keep `azure.yaml` for deployment, but do not publish an azd template |
| Release strategy | No version tag, GitHub release, or release automation |
| License | MIT |
| MIT holder | `AI Solution Starter contributors` |
| Copyright year | Year of implementation |
| Community files | `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`, and `CODE_OF_CONDUCT.md` |
| Code of conduct | Microsoft Open Source Code of Conduct |
| Clean-room gate | Fresh local clone and local/package validation only |
| Azure provisioning | Excluded from Phase 5 validation |
| Sample document | Deterministic generator; generated PDF remains untracked |
| Cost guidance | Cost drivers and Azure Pricing Calculator workflow; no fixed prices |
| Repository safeguards | Preserve project-specific source-sanitization and infrastructure-integrity checks |

## Completion Semantics

Phase 5 has two distinct outcomes:

### Phase 5 implementation complete

This means:

- documentation and governance files exist;
- implemented components have reproducible validation;
- the synthetic sample generator works;
- a fresh local clone passes the documented local validation path;
- repository and Bicep policies pass; and
- the Phase 5 changes are ready for review.

This outcome does not depend on Phase 4 being implemented.

### Starter end-to-end ready

This stronger statement may be made only after:

- Phase 4 workflow implementation is present;
- Phase 4 package and regression validation passes;
- all Phase 5 documentation reflects the implemented workflow; and
- any separately approved Azure end-to-end validation has the status described
  in the Phase 4 review evidence.

Phase 5 must use explicit component-status labels so these outcomes cannot be
confused.

## Phase Boundaries

### Included

- root README redesign
- documentation index and navigation
- architecture overview and Mermaid diagrams
- supported and unsupported scenario documentation
- prerequisites and version requirements
- local setup and development walkthrough
- application validation reference
- deployment preparation and command documentation
- troubleshooting guidance
- Azure resource and cost-driver documentation
- complete replacement guide
- deterministic synthetic PDF generator
- generator tests and usage documentation
- ignored generated-sample directory
- MIT license
- Microsoft Open Source Code of Conduct
- contribution, security-reporting, and support policies
- CI path and validation coverage review
- consolidated repository-owned validation commands
- documentation integrity checks
- Bicep baseline verification in relevant validation paths
- workflow package validation when Phase 4 package files are present
- fresh local clone validation
- tracked-file and Git-history hygiene checks
- Phase 5 implementation report

### Excluded

- every Bicep modification
- Azure resource creation, update, or deletion
- live-Azure clean-room deployment
- changes to GitHub repository security settings
- GitHub template-repository configuration
- azd template publication or template metadata
- version tags
- GitHub releases
- changelog or release-note automation
- package publication
- container image publication
- deployment-environment creation
- production support commitments or service-level objectives
- new application features
- new public APIs
- new workflow business behavior
- Phase 4 implementation
- Phase 6 optional AI services
- committed generated PDFs
- copied third-party sample documents

## Immutable Contracts

### Infrastructure

- Do not modify any file under `infra/`.
- Do not regenerate or update `infra/bicep-baseline.sha256`.
- Run `./scripts/verify_bicep_baseline.sh` during validation.
- Documentation must describe the baseline as it exists rather than proposing
  simplifications.
- Any discovered infrastructure defect is reported for separate review; it is
  not corrected in Phase 5.

### Source cleanliness

- No proprietary source, history, identifiers, documents, prompts, or data may
  enter the repository.
- No material may be recovered from or copied out of private history.
- All examples must be authored specifically for the starter.
- Generated documents must contain only synthetic generic content.
- Fresh-clone validation must inspect tracked files and reachable Git history.
- The existing source-sanitization policy remains authoritative.

### Application contracts

Phase 5 documents but does not alter:

- PDF-only intake;
- 20 MB maximum upload;
- Easy Auth production identity;
- owner-scoped work items;
- required idempotency keys;
- the `submitted`, `queued`, `processing`, `completed`, and `failed`
  lifecycle;
- Blob path generation;
- Cosmos partitioning and concurrency;
- same-origin frontend/API deployment;
- generated frontend output under `app/backend/static/`; and
- managed-identity Azure dependencies.

### Phase 4 compatibility

Phase 5 may prepare documentation and validation hooks for the planned Logic
App package, but it must:

- detect whether the package exists;
- never fabricate workflow validation results;
- label Phase 4 as planned when absent;
- label it implemented only when package files and Phase 4 review evidence are
  present; and
- avoid blocking unrelated local application validation solely because Phase 4
  has not yet been implemented.

Once Phase 4 is implemented, its package validator becomes mandatory in the
full validation command and CI.

## Proposed Documentation Structure

```text
README.md
LICENSE
CONTRIBUTING.md
SECURITY.md
SUPPORT.md
CODE_OF_CONDUCT.md
docs/
├── README.md
├── PLAN.md
├── PHASE_TASKS.md
├── SOURCE_SANITIZATION.md
├── architecture/
│   ├── OVERVIEW.md
│   └── APPLICATION_FLOW.md
├── development/
│   ├── PREREQUISITES.md
│   ├── LOCAL_SETUP.md
│   └── VALIDATION.md
├── deployment/
│   ├── DEPLOYMENT_SEQUENCE.md
│   ├── CONFIGURATION.md
│   └── TROUBLESHOOTING.md
├── operations/
│   └── COST_DRIVERS.md
├── replacement/
│   └── REPLACEMENT_GUIDE.md
├── phases/
│   └── ...
└── reviews/
    └── PHASE_5_IMPLEMENTATION_REPORT.md
```

The exact number of documents may be reduced when two short subjects are
clearer together. The required information and stable links matter more than
creating every proposed file.

## Root README Contract

The root README becomes the shortest successful entry point for a new team.
It must include:

1. a one-paragraph purpose statement;
2. current component-status labels;
3. a concise architecture diagram;
4. supported hello-world behavior;
5. repository structure;
6. prerequisites summary;
7. quick local validation commands;
8. links to local setup, deployment, replacement, cost, and troubleshooting;
9. the immutable Bicep warning;
10. source-sanitization expectations;
11. support and contribution links; and
12. the MIT license reference.

The README must not:

- claim Phase 4 behavior that does not exist;
- present the repository as a GitHub or azd template;
- promise a one-command Azure deployment without prerequisites;
- include fixed Azure price estimates;
- include real Azure identifiers;
- include screenshots requiring maintenance unless specifically approved;
- use the original application's domain language; or
- duplicate every detailed document.

### Status presentation

Status must be derived from repository evidence, not manually optimistic prose.
The implementation should centralize the component-status table in one
document and keep README wording concise:

| Component | Evidence |
| --- | --- |
| Infrastructure | Bicep baseline and validation script |
| Backend | package, tests, container build |
| Frontend | package, tests, production build |
| Workflow | package and Phase 4 implementation report, when present |
| Azure deployment | recorded review evidence only |

## Architecture Documentation

### Overview

Document:

- browser and Easy Auth boundary;
- Quart backend;
- Blob Storage input and instruction containers;
- Cosmos DB work-item persistence;
- Logic Apps Standard processing boundary;
- Azure OpenAI invocation;
- App Service and container registry;
- managed identities and RBAC;
- private networking;
- Azure Monitor and Application Insights; and
- azd/GitHub Actions deployment paths.

Use Mermaid diagrams that render in GitHub without external assets.

### Application flow

Document the implemented lifecycle:

```text
PDF submit
  -> submitted record
  -> Blob upload
  -> queued record
  -> workflow processing
  -> completed or failed
  -> frontend polling and result display
```

When Phase 4 remains unimplemented, the diagram must visibly label its segment
as planned. The document must link to the authoritative phase plan rather than
describing planned behavior as deployed behavior.

### Boundaries

Clearly distinguish:

- infrastructure baseline;
- reusable application shell;
- replaceable hello-world feature;
- deployment automation;
- operational configuration;
- generated artifacts; and
- optional future Azure services.

## Prerequisite Contract

Document minimum supported tooling with commands to verify each tool:

- Git;
- Python 3.12;
- Node.js 20;
- npm compatible with the committed lockfile;
- Docker for production-container validation;
- Azure CLI for Azure operations;
- Azure Developer CLI for provisioning and environment management;
- PowerShell only for Windows-specific scripts;
- Bash-compatible shell for POSIX scripts; and
- optional Logic Apps local tooling only when Phase 4 requires it.

The documentation must separate:

- prerequisites for local static validation;
- prerequisites for local application development;
- prerequisites for container validation; and
- prerequisites for Azure deployment.

Local validation must not require:

- an Azure subscription;
- Azure credentials;
- an azd environment;
- customer configuration;
- generated frontend assets already present; or
- developer-global Python or npm packages beyond the documented runtimes.

## Local Setup and Development Contract

### Clean setup

The documented setup starts from:

```bash
git clone <repository-url>
cd ai-solution-starter
python3 -m venv .venv
.venv/bin/python -m pip install -r app/backend/requirements-dev.txt
cd app/frontend
npm ci
```

The repository URL must be the public starter URL or a neutral placeholder
until publication is approved.

### Local application development

Document two supported modes:

1. test-driven development with mocked Azure boundaries; and
2. optional developer-connected Azure dependencies using an explicitly
   selected azd environment.

The default walkthrough must use tests and local builds. It must not imply that
the current backend can run a full persistence flow without Azure services.

### Environment configuration

Create one authoritative configuration reference that explains:

- variable name;
- consuming component;
- required or optional status;
- safe example shape;
- source of the value;
- whether it is secret;
- local-development behavior; and
- Azure deployment behavior.

Do not repeat all 100-plus infrastructure parameters in the root README.
Link to the existing parameter catalog and organize common application values
separately.

## Validation Command Contract

### Developer entry points

Provide stable repository-root commands:

```text
validate application
validate infrastructure
validate documentation and repository policy
validate everything implemented
generate synthetic sample
```

These may be implemented as scripts or a small task runner only if they wrap
the repository's existing package-manager commands transparently. Do not add a
large build framework.

The command names must be:

- discoverable from the README;
- noninteractive;
- deterministic;
- safe on a clean clone;
- explicit when an optional component is absent; and
- failing on any required check failure.

### Application validation

The full implemented-component validation must include:

- frontend `npm ci`;
- frontend lint;
- frontend type checking;
- frontend tests;
- frontend production build;
- backend dependency installation;
- backend tests;
- Ruff checks;
- Ruff formatting check;
- Mypy;
- backend container build;
- combined SPA and health probe when supported by the existing test path; and
- generated-artifact tracking checks.

### Infrastructure validation

Include:

- Bicep compilation;
- immutable checksum verification;
- deployment YAML and JSON syntax checks available without provisioning;
- shell syntax checks for POSIX deployment scripts; and
- confirmation that Phase 5 introduced no Bicep diff.

No Phase 5 command runs `azd provision`, `azd deploy`, or an Azure resource
mutation.

### Workflow validation

When the Phase 4 package exists:

- run the repository-owned workflow package validator;
- parse package JSON;
- verify required package structure;
- verify local and Azure parameter contracts;
- verify managed-identity connections;
- verify workflow expressions and schemas to the extent supported by the
  validator; and
- include the checks in CI.

When absent, the validation command prints a concise planned-component status
and continues only for modes that explicitly validate currently implemented
components.

### Documentation and repository-policy validation

Use repository-owned checks for:

- broken relative Markdown links;
- missing referenced files;
- stale phase-status contradictions;
- tracked files under generated or local-only paths;
- tracked `.env` files other than approved examples;
- tracked `.azure/`, `.venv/`, cache, build, or sample-output artifacts;
- non-generic placeholders that should have been resolved;
- prohibited private-source references supplied by the repository's approved
  policy configuration;
- unexpected Git remotes in clean-room instructions;
- Bicep checksum manifest consistency; and
- executable-bit expectations for shell scripts.

These checks enforce the repository-specific clean-source policy.

## Continuous Integration Design

### Existing workflows

Review and preserve the intent of:

- `.github/workflows/backend-ci.yml`;
- `.github/workflows/infra-validation.yml`; and
- `.github/workflows/azure-dev.yml`.

The workflow named `Application CI` may be renamed at the file level only when
the benefit outweighs link churn. Functional validation coverage is more
important than filename cleanup.

### Proposed jobs

The final CI shape should provide these independently diagnosable jobs:

| Job | Required coverage |
| --- | --- |
| `backend` | Python tests, Ruff, Mypy |
| `frontend` | npm restore, lint, types, tests, build |
| `container` | production image build and combined route probe |
| `workflow` | Phase 4 package validation when implemented |
| `infrastructure` | Bicep compile and immutable baseline |
| `repository` | docs links, generated artifacts, repository policy |

Jobs may remain in two workflows if that keeps path filters and runtimes
clearer. A monolithic job that hides which component failed is not acceptable.

### Trigger coverage

Path filters must include every file that can affect the corresponding job,
including:

- root Python configuration;
- dependency lockfiles;
- validation scripts;
- Dockerfile and server configuration;
- workflow package and instruction files;
- deployment actions used to package applications;
- documentation validator configuration;
- Bicep manifest and modules; and
- CI workflow definitions themselves.

`workflow_dispatch` remains available for complete manual validation.

### Action and dependency hygiene

- Use supported major versions of official actions already used by the
  repository.
- Avoid adding CI-only package managers or global dependencies when Python or
  Node tooling already in the repository can perform the check.
- Keep network-dependent dependency restoration explicit.
- Do not mutate generated source or commit changes from CI.
- Do not deploy from validation workflows.

## Synthetic PDF Generator Contract

### Purpose

Provide a reproducible hello-world document without committing a binary PDF or
using material from another solution.

### Proposed files

```text
scripts/generate_sample_pdf.py
tests/sample-data/README.md
tests/sample-data/.gitignore
app/backend/tests/test_sample_pdf_generator.py
```

The final test location should follow the existing Python test discovery
unless a repository-level test path is approved.

### Generator behavior

The generator must:

- use only Python standard-library functionality unless a compelling need is
  approved;
- generate a minimal valid PDF;
- use fixed synthetic generic content;
- avoid current timestamps, random identifiers, usernames, hostnames, or
  absolute paths;
- produce byte-for-byte identical output for the same inputs;
- write only to an explicit output path;
- create parent directories safely;
- refuse to overwrite by default;
- support an explicit overwrite flag;
- print the output path, byte size, and SHA-256 only;
- never auto-submit the document; and
- produce a file well below the 20 MB limit.

Default synthetic content should describe a fictional generic work item and
contain enough information to support the starter result categories without
mirroring any private domain.

### Tracking behavior

- Generated PDFs go to an ignored sample-output directory.
- CI generates the PDF into a temporary directory.
- Tests validate the `%PDF-` signature, deterministic hash, nonzero size, and
  expected bounded size.
- No generated PDF is added to Git.

### Documentation

Document:

- how to generate the sample;
- how to inspect its hash;
- how to use it with the frontend;
- how to use it with an approved smoke test; and
- how to remove generated outputs.

## Replacement Guide Contract

The guide is the central deliverable for downstream solution teams.

### Keep versus replace matrix

Document each surface:

| Surface | Default direction |
| --- | --- |
| `infra/` | Keep unchanged |
| `azure.yaml` and auth hooks | Keep unless separately reviewed |
| managed identity and RBAC flow | Keep |
| networking and diagnostics | Keep |
| deployment actions | Keep and adapt only through documented inputs |
| backend dependency construction | Keep |
| authentication boundary | Keep |
| work-item domain model | Replace when the new solution requires a new domain |
| PDF validation | Keep or replace deliberately |
| frontend shell and API error handling | Keep |
| work-item pages and components | Replace |
| workflow prompts | Replace |
| workflow result schema | Replace together with backend/frontend types |
| synthetic sample content | Replace |
| tests | Update with every replaced contract |

### Replacement sequence

Prescribe an order that prevents partial-contract drift:

1. define the new domain and input contract;
2. define persistence and lifecycle changes;
3. update backend models and API contract;
4. update workflow trigger, prompts, and result schema;
5. update frontend types and views;
6. update synthetic fixtures and generators;
7. update documentation;
8. run full validation; and
9. request separate infrastructure review if a requirement cannot fit the
   existing baseline.

### Cross-component contract map

For every replaceable contract, identify all affected files:

- input type and limits;
- work-item status;
- public API response;
- Cosmos record;
- Blob path;
- workflow output;
- frontend rendering;
- test fixtures; and
- deployment configuration.

The guide must warn against changing one representation without updating all
consumers.

### Infrastructure escalation

If a downstream solution requires new Azure services:

- do not edit the baseline opportunistically;
- follow the approved conditional-module strategy from Phase 6;
- define new outputs and application settings;
- document RBAC, networking, diagnostics, region support, quotas, and costs;
  and
- validate base deployment compatibility independently.

## Deployment Documentation Contract

Phase 5 documents deployment but does not execute it.

### Required subjects

- Azure subscription and permission prerequisites;
- azd environment creation and selection;
- authentication application setup;
- parameter and environment configuration;
- `azd provision` behavior;
- application deployment behavior;
- instruction/workflow deployment behavior when implemented;
- temporary network-access behavior;
- GitHub Actions environment setup;
- federated identity/OIDC requirements;
- cleanup and resource deletion considerations;
- region and quota checks;
- Logic Apps Standard capacity risk;
- retrying failed deployment safely; and
- explicit commands that mutate Azure resources.

Every resource-mutating command must be clearly labeled.

### Local-only Phase 5 boundary

Documentation verification confirms that commands are syntactically accurate
and correspond to repository scripts. It does not claim that Phase 5 executed
them.

Any prior Azure validation evidence remains in its phase-specific report and
must not be restated as a Phase 5 clean deployment.

## Troubleshooting Contract

Provide symptom-oriented entries for:

- unsupported Python or Node version;
- missing virtual environment;
- npm lockfile mismatch;
- frontend build output missing;
- backend import failure;
- local auth subject missing or incorrectly used in production;
- Azure credential unavailable;
- azd environment not selected;
- Blob or Cosmos RBAC propagation;
- private endpoint or firewall access;
- container build failure;
- SPA route returning 404;
- Logic App package missing;
- Logic Apps Standard regional capacity unavailable;
- workflow stuck in `submitted`, `queued`, or `processing`;
- Azure OpenAI authorization, quota, or model availability;
- Bicep checksum failure; and
- repository-policy validation failure.

Each entry should include:

- observable symptom;
- likely cause;
- safe diagnostic command;
- corrective action;
- whether the action mutates Azure; and
- the document to consult next.

Do not recommend disabling security controls as a shortcut.

## Cost Documentation Contract

### Scope

Document cost drivers for:

- App Service plans;
- Logic Apps Standard hosting;
- Azure Container Registry;
- Cosmos DB throughput/serverless configuration;
- Storage capacity, operations, and data transfer;
- Azure OpenAI tokens and model deployment capacity;
- Log Analytics ingestion and retention;
- Application Insights;
- private endpoints and networking;
- optional Azure DNS/network resources; and
- deployed environment count and lifetime.

### No fixed prices

Do not publish a monthly total or unit price because:

- prices vary by region;
- model pricing and availability change;
- negotiated agreements differ;
- usage is workload-specific; and
- the infrastructure exposes multiple SKU choices.

Instead, provide:

1. the Bicep parameter or deployment choice that controls each driver;
2. the usage quantity a team must estimate;
3. the Azure Pricing Calculator service to select;
4. region and currency reminders;
5. quota and capacity checks; and
6. cost-cleanup guidance for temporary environments.

The document must not recommend changing the established baseline merely to
reduce cost. It may identify cost-sensitive parameters and require separate
infrastructure review.

## Public Repository Governance

### License

Add an MIT `LICENSE` file with:

```text
Copyright (c) <implementation-year> AI Solution Starter contributors
```

Use the standard MIT text without additional restrictions.

### Contributing

`CONTRIBUTING.md` must cover:

- development setup links;
- issue and pull-request expectations;
- focused changes;
- required validation;
- documentation updates;
- source-sanitization requirements;
- no Bicep changes without explicit review;
- no generated artifacts;
- no real customer documents or values;
- commit and review expectations; and
- the Code of Conduct.

### Security policy

`SECURITY.md` must:

- provide a private vulnerability-reporting path appropriate for the public
  GitHub repository;
- ask reporters not to open public vulnerability issues;
- state which branch is supported while no releases exist;
- avoid promising response times that the maintainers have not approved; and
- distinguish vulnerability reports from general support.

### Support policy

`SUPPORT.md` must:

- route usage questions and reproducible defects to the approved issue path;
- request sanitized reproduction details;
- prohibit real documents, credentials, tenant IDs, or private logs in issues;
- state that Azure subscription, quota, regional capacity, and billing support
  remain Azure support concerns; and
- avoid production support or SLA promises.

### Code of Conduct

Add the Microsoft Open Source Code of Conduct using its authoritative,
current public text or reference structure during implementation. Record the
source URL and retrieval date in the implementation report, not in generated
application output.

## Clean-Room Local Validation

### Purpose

Prove that repository documentation and local validation do not depend on:

- the current worktree;
- ignored build outputs;
- installed frontend dependencies;
- the current `.venv`;
- `.azure/` state;
- shell aliases;
- developer environment variables;
- untracked files; or
- private source material.

### Clone procedure

From outside the repository:

1. create an empty temporary parent directory;
2. clone the local repository using a normal clone that transfers only Git
   content;
3. confirm the expected branch and commit;
4. inspect initial `git status`;
5. verify ignored local state is absent;
6. follow the README prerequisite and setup commands exactly;
7. generate the synthetic PDF;
8. run documentation/repository checks;
9. run implemented-component validation;
10. build the production container;
11. verify generated outputs remain ignored;
12. inspect final `git status`; and
13. delete the exact temporary clone directory after recording results.

The procedure must not copy the current `.venv`, `node_modules`, `.azure`,
frontend static output, caches, or environment files.

### Required evidence

Record:

- source commit;
- operating system;
- Python, Node, npm, Docker, Git, Azure CLI, and azd versions;
- commands run;
- pass/fail results;
- generated sample hash and byte size;
- optional-component skip reasons;
- final Git status;
- tracked-file policy result;
- Bicep baseline result; and
- cleanup confirmation.

Do not record environment secrets, account identifiers, absolute home paths,
or Azure subscription details.

### No Azure dependency

The clean-room procedure must not:

- authenticate to Azure;
- read an azd environment;
- run provisioning;
- deploy applications;
- call live Blob, Cosmos, Logic Apps, or Azure OpenAI endpoints; or
- incur Azure cost.

Azure deployment readiness is documented, not exercised, in Phase 5.

## Repository History Validation

Before Phase 5 review:

- inspect every local commit not on `origin/main`;
- list tracked files from the candidate commit;
- verify no unexpected remote exists;
- verify no prohibited source-repository reference appears in reachable
  history;
- verify generated PDF, static assets, caches, `.azure`, and environment files
  are absent from history;
- inspect the complete Phase 5 diff; and
- keep the Phase 5 commit local until approved.

Do not rewrite existing history during routine validation. If prohibited
content is found, stop and handle history remediation as a separate explicit
task before any push.

## Documentation Quality Standards

- Use task-oriented headings.
- Prefer repository-root commands.
- State the working directory when commands change it.
- Mark destructive or Azure-mutating commands.
- Do not assume shell state persists between unrelated command blocks.
- Use safe placeholders enclosed in angle brackets.
- Avoid placeholders in committed executable configuration.
- Keep one authoritative source per fact and link to it.
- Distinguish current behavior, planned behavior, and optional behavior.
- Include expected success evidence for critical commands.
- Keep generated output out of documentation unless it is stable and useful.
- Use relative links inside the repository.
- Ensure diagrams and tables render in GitHub.
- Avoid private URLs and real identifiers.
- Do not embed documentation that will immediately become stale after Phase 4;
  use component-status labels and links.

## Work Package 5.0 - Establish Readiness Information Architecture

### Tasks

1. Inventory current documentation and duplicate facts.
2. Define authoritative documents and navigation.
3. Add `docs/README.md`.
4. Define component-status semantics.
5. Add documentation-link validation.
6. Update phase links without changing historical review evidence.

### Acceptance criteria

- Every maintained document is reachable from README or `docs/README.md`.
- Current and planned behavior are distinguishable.
- Relative links resolve.
- Historical reports remain historical rather than silently rewritten.
- Phase 4 status is accurate.

## Work Package 5.1 - Rewrite the Starter Entry Experience

### Tasks

1. Rewrite the root README.
2. Add the concise architecture diagram.
3. Add prerequisites and quick validation.
4. Add links to setup, deployment, replacement, cost, and troubleshooting.
5. Add immutable-infrastructure and clean-source warnings.
6. Add contribution, support, security, conduct, and license links.

### Acceptance criteria

- A new reader understands the repository within the root README.
- No incomplete component is presented as complete.
- Quick commands work from a fresh clone.
- Detailed material is linked rather than duplicated.
- Normal clone usage is explicit.

## Work Package 5.2 - Complete Development and Validation Documentation

### Tasks

1. Document prerequisites and supported versions.
2. Document clean setup.
3. Document frontend development.
4. Document backend development.
5. Document optional Azure-connected development.
6. Create the validation reference.
7. Consolidate configuration guidance.

### Acceptance criteria

- Local validation requires no Azure access.
- Azure-connected steps are visibly optional and explicit.
- Commands match package scripts and repository paths.
- Windows/POSIX differences are documented where necessary.
- No developer-local state is assumed.

## Work Package 5.3 - Complete Architecture, Deployment, and Operations Docs

### Tasks

1. Document architecture and application flow.
2. Document identity and service boundaries.
3. Expand deployment sequence and configuration.
4. Document GitHub Actions deployment prerequisites.
5. Add troubleshooting.
6. Add cost-driver guidance.
7. Document cleanup considerations without executing cleanup.

### Acceptance criteria

- Architecture matches actual Bicep and application contracts.
- Azure-mutating commands are labeled.
- Phase 5 makes no deployment claim.
- Troubleshooting is symptom-oriented and safe.
- Cost documentation contains no fixed prices.

## Work Package 5.4 - Create the Replacement Guide

### Tasks

1. Add keep-versus-replace matrix.
2. Map cross-component contracts.
3. Document the safe replacement order.
4. Document prompt and workflow replacement.
5. Document backend and frontend replacement.
6. Document test and fixture updates.
7. Document infrastructure escalation and Phase 6 optional AI modules.

### Acceptance criteria

- A team can identify every domain-specific starter surface.
- Shared mechanisms are clearly protected from accidental replacement.
- Contract changes list all consumers.
- The guide never recommends casual Bicep edits.
- Phase 4 absence or presence is handled accurately.

## Work Package 5.5 - Add Deterministic Synthetic Sample Generation

### Tasks

1. Implement the standard-library PDF generator.
2. Add deterministic content.
3. Add overwrite protection.
4. Add ignored output location.
5. Add generator tests.
6. Add README and walkthrough usage.

### Acceptance criteria

- Repeated runs produce identical bytes.
- The PDF is valid for the backend's signature and size checks.
- Generated PDFs remain untracked.
- Output contains no machine or user-specific values.
- CI can generate and validate the sample.

## Work Package 5.6 - Add License and Community Health Files

### Tasks

1. Add MIT license.
2. Add Microsoft Open Source Code of Conduct.
3. Add contributing guide.
4. Add private security-reporting policy.
5. Add support policy.
6. Link all policies from README.

### Acceptance criteria

- License holder is `AI Solution Starter contributors`.
- No release-version support promise is invented.
- Security and support channels are distinct.
- Issue guidance prohibits sensitive or proprietary attachments.
- Conduct text uses the approved Microsoft source.

## Work Package 5.7 - Consolidate Continuous Validation

### Tasks

1. Split or reorganize CI into diagnosable jobs.
2. Correct path filters.
3. Add documentation and repository-policy validation.
4. Add sample-generator validation.
5. Integrate Phase 4 package validation conditionally.
6. Preserve Bicep compile and checksum validation.
7. Add a full manual validation entry point.
8. Document local equivalents for each CI job.

### Acceptance criteria

- Each job has a clear failure domain.
- Pull requests run every relevant check for changed files.
- Full manual validation covers all implemented components.
- CI creates no Azure resources.
- CI commits no generated artifacts.

## Work Package 5.8 - Perform Clean-Room Local Validation

### Tasks

1. Create an exact temporary clone target.
2. Clone the candidate commit.
3. Follow README setup without shortcuts.
4. Generate and validate the synthetic PDF.
5. Run all implemented-component validation.
6. Build and probe the production container.
7. Verify ignored and tracked files.
8. Record tool versions and results.
9. Remove the temporary clone.

### Acceptance criteria

- No developer-local dependency is used.
- No Azure access occurs.
- Documented commands succeed.
- Optional missing Phase 4 behavior is reported accurately.
- Initial and final worktrees are clean except ignored generated outputs.
- Cleanup removes only the explicit temporary clone.

## Work Package 5.9 - Review Starter Readiness

### Tasks

1. Write `docs/reviews/PHASE_5_IMPLEMENTATION_REPORT.md`.
2. Record documentation inventory.
3. Record CI and local validation results.
4. Record clean-room evidence.
5. Record synthetic sample hash and size.
6. Record Bicep integrity.
7. Record tracked-file and history review.
8. Inspect the complete Phase 5 diff.
9. Create a local-only Phase 5 commit.
10. Pause before push, release, or Phase 6.

### Acceptance criteria

- Evidence distinguishes executed checks from documented future steps.
- No Azure deployment is implied.
- No release or tag is created.
- Bicep remains unchanged.
- No proprietary content or generated PDF is tracked.
- The commit remains local until approved.

## Planned Task Dependencies

```text
5.0 Readiness information architecture
 ├─> 5.1 Starter entry experience
 ├─> 5.2 Development and validation docs
 ├─> 5.3 Architecture, deployment, and operations docs
 ├─> 5.4 Replacement guide
 ├─> 5.5 Synthetic PDF generator
 ├─> 5.6 License and community files
 └─> 5.7 Continuous validation

5.1 ─┐
5.2 ─┤
5.3 ─┤
5.4 ─┤
5.5 ─┤─> 5.8 Clean-room local validation
5.6 ─┤
5.7 ─┘
      └─> 5.9 Readiness review
```

Work packages 5.1 through 5.7 may proceed in parallel after the documentation
inventory establishes authoritative sources. Clean-room validation begins only
after all user-facing commands and CI-equivalent scripts are stable.

Phase 4 implementation is not a dependency for beginning these tasks.
Phase 4 package validation is activated when the package exists.

## Validation Matrix

| Area | Required evidence |
| --- | --- |
| Documentation | Relative links, file references, status consistency |
| Backend | Tests, Ruff, Mypy |
| Frontend | npm restore, lint, types, tests, build |
| Container | Build and combined route probe |
| Workflow | Package validator when implemented; explicit status otherwise |
| Infrastructure | Bicep build and checksum verification |
| Samples | Deterministic PDF tests and ignored output |
| Governance | Required files and internal links |
| Repository | Tracked-file policy, remotes, unpushed commits, clean diff |
| Clean room | Fresh-clone command transcript and clean final status |

## Review Artifacts

The Phase 5 implementation review must include:

- final documentation map;
- root README preview;
- current component-status table;
- architecture diagrams;
- replacement matrix and cross-component contract map;
- synthetic PDF generator source and test result;
- generated PDF byte size and SHA-256;
- governance-file inventory;
- CI job and path-filter matrix;
- local validation command results;
- clean-room clone evidence;
- Bicep checksum result;
- tracked-file and Git-history review;
- explicit statement that no Azure deployment occurred;
- explicit statement that no release or tag was created; and
- complete unpushed Phase 5 diff.

## Final Phase 5 Acceptance Criteria

- The repository has a clear clone-based onboarding path.
- README accurately reflects implemented and planned components.
- Architecture, setup, development, deployment, validation, troubleshooting,
  and cost drivers are documented.
- Replacement boundaries cover frontend, backend, persistence, workflow,
  prompts, tests, and infrastructure escalation.
- A deterministic synthetic PDF can be generated without committing it.
- MIT licensing and approved community files are present.
- CI covers all implemented components with diagnosable jobs.
- Repository-specific source and artifact policies are validated.
- A fresh local clone passes documented implemented-component validation.
- Clean-room validation performs no Azure operation.
- Bicep is byte-for-byte unchanged.
- No proprietary content, private history, or generated PDF is tracked.
- No release, tag, or template configuration is added.
- Phase 5 implementation remains unpushed until explicitly approved.

## Stop Conditions

Stop and request review if:

- a documentation fix appears to require a Bicep change;
- actual application behavior contradicts an immutable approved contract;
- Phase 4 status cannot be represented accurately without implementation
  changes;
- a local validation path requires Azure credentials unexpectedly;
- a proposed CI check would deploy or mutate Azure resources;
- generated PDF output cannot be made deterministic;
- a community file requires an unapproved legal or support commitment;
- the authoritative Microsoft Code of Conduct source cannot be identified;
- repository policy would require storing private prohibited-term data;
- clean-room setup depends on ignored or untracked files;
- Bicep checksum verification fails;
- a generated artifact enters Git;
- a private identifier or source-history reference is found;
- completing Phase 5 would require a tag, release, or repository setting
  change; or
- any validation would create Azure cost.
