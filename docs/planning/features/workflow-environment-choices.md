# FEAT-02: Offer more environments in the workflows

**Type:** Feature · **Area:** GitHub Actions · **Priority:** Medium · **Status:** Proposed

## Summary

The deploy and RBAC workflows can only target a GitHub environment called
`dev`.

## Current behavior

- [`azure-dev.yml`](../../../.github/workflows/azure-dev.yml) lines 7–12:
  the `environment` input is a `choice` with the single option `dev`.
- [`assign-rbac.yml`](../../../.github/workflows/assign-rbac.yml) has the
  same single-option input.

## Impact

To add `test` or `prod`, users must edit both workflows. The
[multiple environments guide](../../how-to/manage-multiple-environments.md)
has to explain this.

## Proposed change

Change both inputs to `type: environment`, so GitHub lists every environment
configured in the repository. Optionally add `required reviewers` on
production-like environments in the docs.

## Acceptance criteria

- [ ] Both workflows list all repository environments.
- [ ] A run against a second environment uses that environment's variables
      and secrets.
- [ ] The multiple environments guide drops the edit-the-workflow step.
