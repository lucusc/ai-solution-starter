# Source Sanitization Policy

## Purpose

This repository must not expose proprietary code, customer data, private
repository information, or identifying implementation details. Existing
solutions may be consulted for proven patterns, but their content must never be
copied directly into this Git worktree or imported with Git history.

## Required Workflow

When an implementation phase needs an existing pattern:

1. Identify the minimum behavior or configuration needed.
2. Copy only the necessary candidate files into a temporary local staging
   directory outside this repository.
3. Remove all customer data, domain content, names, URLs, tenant or subscription
   details, resource identifiers, comments, documentation, examples, generated
   assets, and repository references.
4. Generalize names, configuration, schemas, prompts, sample data, and
   deployment assumptions.
5. Review the generalized material for both textual leakage and structural
   over-copying.
6. Reimplement or copy only the sanitized result into this repository.
7. Run repository-wide secret, identifier, and prohibited-term scans.
8. Inspect the complete staged Git diff before committing.
9. Commit only after the phase review criteria are satisfied.
10. Delete the temporary staging material after validation.

## Prohibited Content

- Git history from an existing solution
- Source repository names, URLs, commit IDs, pull requests, or issue references
- Customer or organization names
- Real documents, prompts, records, PDFs, images, or database exports
- Tenant, subscription, resource group, service, storage, or account identifiers
- Secrets, credentials, tokens, certificates, connection strings, or keys
- Environment-specific firewall, DNS, network, or identity values
- Domain-specific schemas, terminology, business rules, and evaluation criteria
- Comments or documentation that reveal private implementation context
- Generated artifacts copied from another solution

## Git Safety Rules

- Create files from a clean repository with independent history.
- Never add another solution as a Git remote.
- Never use subtree, filter-branch, merge with unrelated histories, or history
  import mechanisms.
- Never commit a temporary source-staging directory.
- Before every push, inspect all commits that are not yet on the remote.
- If prohibited content is committed, stop work and remove it from history
  before pushing. Deleting it in a later commit is insufficient.

## Review Evidence

Each phase must record:

- which behaviors were consulted
- which files were introduced
- how they were generalized
- which scans and tests were run
- confirmation that no proprietary content or source history was committed
