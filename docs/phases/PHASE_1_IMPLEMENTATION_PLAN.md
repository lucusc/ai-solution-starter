# Phase 1 Implementation Plan

## Status

**Planning only.** No private source material has been inspected, staged,
copied, generalized, or introduced as part of this plan.

Phase 1 implementation must not begin until this plan is explicitly approved.

## Objective

Establish the complete, sanitized infrastructure and deployment baseline for
the AI Solution Starter. The baseline must reproduce the proven deployment
architecture and operational behavior while removing all proprietary,
customer-specific, environment-specific, and domain-specific content before
anything enters this repository.

Phase 1 includes:

- the full infrastructure capability set
- Azure Developer CLI configuration
- local setup and deployment scripts
- GitHub Actions deployment automation
- infrastructure and deployment documentation
- validation and privacy controls
- an immutable post-sanitization infrastructure baseline

Phase 1 does not include:

- backend application implementation
- frontend application implementation
- Logic App business workflow definitions
- domain prompts or sample documents
- application data models
- optional Microsoft Foundry, Azure AI Search, or Azure AI Document
  Intelligence resources
- optimization or redesign of the proven infrastructure

## Approved Decisions

| Decision | Phase 1 direction |
| --- | --- |
| Infrastructure scope | Reproduce the full capability baseline |
| Preservation rule | Preserve architecture and behavior; generalize names, comments, descriptions, metadata, and examples |
| Deployment automation | Include azd configuration, generic scripts, and GitHub Actions |
| Azure provisioning | Prepare compile-only and clean-environment paths; decide whether to provision at the implementation review gate |
| Required artifacts | Resource contract, parameter catalog, RBAC matrix, networking matrix, deployment sequence, sanitization report, baseline hash manifest |

## Non-Negotiable Rules

1. No existing Git history may be imported.
2. No private repository may be added as a Git remote.
3. No private source file may be copied directly into this repository.
4. Candidate material must be placed in a temporary directory outside both Git
   worktrees.
5. Sanitization and generalization must occur before material enters this
   repository.
6. Architecture, resource relationships, deployment sequencing, RBAC behavior,
   networking behavior, conditions, and compatibility options must not be
   optimized or redesigned.
7. Generic naming and descriptive metadata may change when required to remove
   private context.
8. Once the sanitized infrastructure baseline is approved, its Bicep files
   become immutable except for separately approved bug fixes or additive
   conditional modules.
9. No source data, prompts, PDFs, images, generated application assets, or
   database records are allowed in Phase 1.
10. Every commit must contain only reviewed, generalized content.

## Target Capability Categories

The local inventory must capture the complete proven behavior. At minimum, the
inventory is expected to evaluate these categories:

- subscription- and resource-group-scoped deployment behavior
- deterministic environment-based resource naming
- application hosting plans and web application hosting
- container image registry and image deployment integration
- Storage accounts, containers, access settings, and application integration
- Cosmos DB account, database, container, throughput, and data-plane access
- Azure OpenAI account and model deployment configuration
- Logic Apps Standard hosting, storage, connections, and application settings
- managed identities and Azure role assignments
- application authentication configuration
- Application Insights, Log Analytics, and monitoring dashboards
- virtual network integration
- private endpoints and private DNS behavior
- public network access and allowed-IP behavior
- support for creating resources or connecting to approved existing resources
- environment outputs consumed by application and deployment automation
- Azure Developer CLI provisioning hooks
- local and hosted deployment sequences

This list is a validation checklist, not permission to add capabilities that
are absent from the proven baseline.

## Working Directories and Data Boundaries

Three locations must remain distinct:

| Location | Purpose | Git status |
| --- | --- | --- |
| Private reference worktree | Read-only behavioral reference | Existing private history; never connected to starter |
| Temporary sanitization workspace | Candidate analysis and generalization | Outside all Git worktrees; must be deleted at phase completion |
| AI Solution Starter worktree | Approved generalized output only | Public Git history |

The temporary workspace path must be resolved explicitly before use. It must
not be nested under the starter repository, and `.source-staging/` remains
ignored as a defense-in-depth measure rather than an approved staging
location.

## Work Package 1.0 - Establish Phase Controls

### Tasks

1. Confirm both worktrees are clean before analysis begins.
2. Record the current starter commit as the Phase 1 starting point.
3. Create a temporary sanitization workspace outside both repositories.
4. Create a local-only prohibited-content checklist containing:
   - organization and customer identifiers
   - private repository names and URLs
   - domain terminology
   - known environment and Azure resource identifiers
   - tenant, subscription, identity, DNS, and network values
   - filenames associated with private data
5. Configure the workspace so it cannot be accidentally added to the starter.
6. Define the exact scan commands that will run before every file transfer and
   commit.
7. Confirm no cloud deployment or Azure mutation is authorized during the
   planning and inventory work.

### Outputs

- Phase 1 starting commit recorded in the local implementation log
- temporary workspace outside Git
- local-only prohibited-term list
- repeatable pre-transfer and pre-commit scan commands

### Acceptance criteria

- Starter worktree contains no staged implementation files.
- Temporary workspace is not under a Git worktree.
- Neither repository has a new remote or imported history.
- The prohibited-term list itself is not committed.

## Work Package 1.1 - Build a Behavioral Inventory

### Tasks

1. Inspect only infrastructure and deployment-related material in the private
   reference.
2. Inventory resources, modules, conditions, loops, dependencies, scopes, API
   versions, and outputs.
3. Inventory all parameters and identify:
   - required inputs
   - defaults
   - allowed values
   - secure values
   - environment-specific values
   - existing-resource integration values
4. Trace identities and role assignments from principal creation through
   resource access.
5. Trace networking behavior for public access, firewall rules, VNet
   integration, private endpoints, and private DNS.
6. Trace application settings from infrastructure outputs through deployment
   scripts to hosted services.
7. Trace the complete deployment sequence:
   - pre-provision hooks
   - infrastructure provisioning
   - post-provision hooks
   - environment export
   - container build and publish
   - web application update
   - Logic App package deployment
8. Classify each candidate item:
   - required unchanged behavior
   - required but requiring generic metadata
   - application/domain-specific and excluded
   - uncertain and requiring review

### Outputs

Only generalized facts may enter repository documentation:

- resource contract draft
- parameter catalog draft
- RBAC matrix draft
- networking matrix draft
- deployment sequence draft
- unresolved-items list

Raw filenames, identifiers, values, and copied text remain local-only.

### Acceptance criteria

- Every infrastructure resource and deployment step has a classification.
- Every output consumed by automation has a traced consumer.
- Every role assignment has a principal, scope, and purpose.
- Every network mode has documented prerequisites and effects.
- No raw inventory containing private identifiers is committed.

## Work Package 1.2 - Define the Generic Contract

### Tasks

1. Convert the behavioral inventory into generic resource names and purposes.
2. Define a stable parameter naming convention without changing parameter
   semantics.
3. Define generic Azure Developer CLI environment variable names.
4. Define generic output names consumed by deployment automation.
5. Define which values are:
   - safe defaults
   - required operator inputs
   - secure inputs
   - generated deployment values
6. Define supported environment modes, including:
   - public network access behavior
   - restricted IP behavior
   - private networking behavior
   - existing-resource integration where present
7. Define the application-facing configuration contract for later phases.
8. Identify metadata-only substitutions required for privacy:
   - descriptions
   - comments
   - tags
   - project names
   - default container/database names
   - example parameter values

### Outputs

- `docs/infrastructure/RESOURCE_CONTRACT.md`
- `docs/infrastructure/PARAMETER_CATALOG.md`
- `docs/infrastructure/RBAC_MATRIX.md`
- `docs/infrastructure/NETWORKING_MATRIX.md`
- `docs/deployment/DEPLOYMENT_SEQUENCE.md`

### Acceptance criteria

- Contracts describe behavior without identifying the private implementation.
- Parameter and output semantics cover every inventoried consumer.
- Secure values have no example resembling a real secret or identifier.
- Generic substitutions do not alter resource relationships or runtime
  behavior.

## Work Package 1.3 - Sanitize Infrastructure Outside Git

### Tasks

1. Copy only infrastructure candidate files into the temporary workspace.
2. Remove or replace:
   - private names and abbreviations
   - customer tags and descriptions
   - private comments
   - real resource names and IDs
   - tenant, subscription, DNS, IP, and network values
   - application-domain container, database, or setting names
   - private file paths and uploaded asset references
3. Preserve:
   - module boundaries
   - deployment scopes
   - API versions
   - resource types and properties
   - conditions and loops
   - dependencies
   - role IDs and assignment behavior
   - networking modes
   - authentication behavior
   - parameter semantics
   - outputs required by deployment automation
4. Exclude resources or values only when the behavioral inventory confirms
   they are application content rather than infrastructure capability.
5. Avoid style-only formatting, module movement, helper extraction, naming
   cleanup unrelated to sanitization, API upgrades, or simplification.
6. Compile the sanitized entry points in the temporary workspace.
7. Compare compiled resource behavior against the inventory.
8. Run prohibited-content and secret scans before any transfer.

### Outputs

- sanitized Bicep candidate set in temporary workspace
- local comparison report
- list of intentional metadata substitutions
- list of excluded application-specific inputs

### Acceptance criteria

- Sanitized templates compile.
- Expected resource graph, conditions, dependencies, and outputs are retained.
- No prohibited identifiers or values remain.
- Every semantic difference has an explicit privacy or application-boundary
  justification.
- No candidate file has entered the public worktree yet.

## Work Package 1.4 - Sanitize Deployment Automation Outside Git

### Tasks

1. Prepare a generic `azure.yaml` candidate.
2. Prepare generic pre-provision and post-provision authentication hooks.
3. Prepare local scripts for:
   - environment setup
   - configuration loading/export
   - infrastructure provisioning support
   - application deployment orchestration
   - network-access support where present
4. Prepare GitHub Actions for:
   - authentication
   - infrastructure provisioning
   - environment output export
   - container build and publish
   - web application deployment
   - Logic App package deployment
5. Replace all repository, branch, environment, secret, variable, resource,
   artifact, and application names with generic contracts.
6. Remove application-specific uploads and workflow package assumptions that
   belong to later phases; retain safe placeholders only where deployment
   wiring requires them.
7. Preserve sequencing, failure behavior, and authentication model.
8. Validate shell, PowerShell, YAML, and action metadata syntax where tooling
   is available.
9. Run prohibited-content and secret scans before any transfer.

### Outputs

- sanitized azd candidate
- sanitized deployment-script candidates
- sanitized GitHub Actions candidates
- local deployment sequence comparison

### Acceptance criteria

- Automation uses only generic names and documented environment contracts.
- No private URL, repository reference, branch name, artifact name, or Azure
  identifier remains.
- Failure behavior is explicit; required steps do not silently continue.
- Hosted and local deployment sequences agree with the documented contract.
- No candidate file has entered the public worktree yet.

## Work Package 1.5 - Privacy Review Before Transfer

### Tasks

1. Scan the complete temporary workspace for:
   - prohibited terms
   - secrets and credential patterns
   - GUIDs and resource IDs
   - URLs and hostnames
   - IP addresses and CIDR ranges
   - email addresses
   - organization and domain terminology
   - private filenames
2. Review all comments, descriptions, metadata, defaults, and sample values
   manually.
3. Compare the sanitized candidates with the generic contracts.
4. Confirm that no data, prompts, documents, generated assets, or application
   code are included.
5. Produce a sanitized transfer manifest containing destination paths and file
   purposes, but no private source paths.
6. Stop for an internal privacy check before copying any candidate into the
   starter worktree.

### Outputs

- transfer manifest
- scan results
- privacy-review checklist

### Acceptance criteria

- Automated scans report no unexplained matches.
- Manual review covers every candidate file.
- Transfer manifest contains only approved Phase 1 files.
- Any uncertain match blocks transfer until resolved.

## Work Package 1.6 - Introduce the Sanitized Baseline

### Tasks

1. Copy only transfer-manifest files into the starter worktree.
2. Keep infrastructure and deployment changes in reviewable groups:
   - core Bicep and parameter files
   - infrastructure modules
   - azd configuration and local scripts
   - GitHub Actions
   - documentation and validation controls
3. Run prohibited-content scans after each group is introduced.
4. Inspect the full Git diff after each group.
5. Do not commit until the complete Phase 1 change set passes validation.
6. Do not add application placeholders containing copied logic; deployment
   automation may reference only documented future package boundaries.

### Outputs

- generalized infrastructure tree
- generic azd and deployment automation
- required Phase 1 documentation

### Acceptance criteria

- Every tracked file appears in the approved transfer manifest.
- No file contains unexplained private-context text or values.
- Git history remains independent.
- The implementation matches the generic resource and deployment contracts.

## Work Package 1.7 - Validate the Baseline

### Required local validation

1. Format-independent Bicep compilation for every entry point.
2. Bicep linter evaluation using repository configuration, if present.
3. Parameter-file validation against template contracts.
4. YAML syntax validation.
5. Shell syntax validation.
6. PowerShell parser validation where PowerShell files exist.
7. GitHub Actions structural validation where supported.
8. Cross-check of infrastructure outputs against:
   - azd environment values
   - deployment scripts
   - GitHub Actions
   - later application configuration contract
9. Secret scan.
10. prohibited-identifier and private-context scan.
11. staged-diff inspection.
12. Git history and remote inspection.

### Optional clean-environment provisioning path

Prepare, but do not execute without review approval:

1. Select an approved subscription and region.
2. Create a fresh azd environment with generic values.
3. Provision infrastructure.
4. Verify resource creation, role assignments, network settings, and outputs.
5. Do not deploy backend, frontend, or workflow business logic.
6. Capture only non-sensitive validation evidence.
7. Remove the environment if the review requires temporary validation only.

### Provisioning decision gate

After local validation, present:

- local validation results
- expected resources and cost-bearing services
- required permissions and quotas
- expected provisioning duration
- cleanup approach

Then request explicit approval to either:

- provision a clean Azure environment in Phase 1, or
- defer provisioning until the application vertical slice is available

## Work Package 1.8 - Establish the Immutable Baseline

### Tasks

1. Generate a sorted SHA-256 manifest for all approved Bicep files.
2. Add a validation script that checks current Bicep files against the
   manifest.
3. Document the change-control rule:
   - no refactoring or optimization
   - approved bug fixes require explicit review
   - optional services use additive infrastructure
4. Produce the Phase 1 sanitization report.
5. Confirm all temporary workspace content is deleted after review evidence is
   complete.
6. Inspect the commit and all objects to be pushed.

### Outputs

- `infra/bicep-baseline.sha256`
- baseline verification script
- `docs/infrastructure/CHANGE_CONTROL.md`
- `docs/reviews/PHASE_1_SANITIZATION_REPORT.md`

The sanitization report must describe categories of changes and validation
performed without naming or identifying the private reference.

### Acceptance criteria

- Hash verification succeeds.
- No temporary files or raw review artifacts are tracked.
- Repository and commit scans pass.
- The temporary sanitization workspace is deleted.
- The final commit contains only approved Phase 1 artifacts.

## Work Package 1.9 - Phase Review and Commit Strategy

### Proposed commit strategy

Do not create incremental commits containing partially sanitized material.
After all candidates have passed privacy and technical validation:

1. Create one local Phase 1 implementation commit, or a small set of commits
   split only by fully sanitized deliverable group.
2. Inspect every new commit and its complete diff.
3. Do not push until the Phase 1 implementation review is approved.
4. If prohibited material is found after commit but before push, rebuild the
   local Phase 1 commits so the material never appears in public history.

### Phase 1 review package

Present:

- introduced file manifest
- resource contract
- parameter catalog
- RBAC matrix
- networking matrix
- deployment sequence
- local validation results
- sanitization report
- Bicep baseline hash verification
- provisioning recommendation and decision request
- complete unpushed commit diff

### Final Phase 1 acceptance criteria

- Full proven infrastructure capability is represented.
- Architecture and behavior are preserved.
- Names and metadata are generic and publishable.
- azd, scripts, and GitHub Actions use one consistent deployment contract.
- Required documentation artifacts are complete.
- All local validation passes.
- No proprietary content or private history exists in the repository.
- Bicep integrity controls are active.
- No Phase 2 application work has started.
- Changes remain unpushed until explicitly approved.

## Planned Task Dependencies

```text
1.0 Establish controls
 └─> 1.1 Behavioral inventory
      └─> 1.2 Generic contract
           ├─> 1.3 Sanitize infrastructure
           └─> 1.4 Sanitize deployment automation
                └─> 1.5 Privacy review
                     └─> 1.6 Introduce baseline
                          └─> 1.7 Validate
                               └─> provisioning decision gate
                                    └─> 1.8 Establish immutable baseline
                                         └─> 1.9 Phase review
```

## Stop Conditions

Stop immediately and request review if:

- preserving behavior appears to require retaining identifying content
- a value cannot be confidently classified as generic or environment-specific
- infrastructure and deployment automation disagree about a required contract
- a candidate change would alter resource behavior for cleanup or optimization
- a private identifier appears after transfer into the starter worktree
- validation requires an Azure mutation that has not been approved
- a required service, region, quota, or permission is unavailable
