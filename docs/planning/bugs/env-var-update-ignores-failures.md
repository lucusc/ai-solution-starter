# BUG-06: Variable update step ignores failures

**Type:** Bug · **Area:** GitHub Actions · **Priority:** Medium · **Status:** Proposed

## Summary

If saving an output as a GitHub variable fails, the step still succeeds.

## Current behavior

[`create-variables.ps1`](../../../.github/actions/create-environment-variables/scripts/create-variables.ps1)
lines ~65–70 catch every error for each variable, print a message and
continue. The script always ends with `Done.` and exit code 0.

## Impact

A bad or expired `MANAGE_ENV_VARS_PAT`, or a missing permission, leaves
the GitHub variables stale while the run shows green. Later runs then use
the old values.

## Proposed change

Collect failures, print each as a `::error::` annotation, and exit with a
non-zero code at the end if any failed.

## Acceptance criteria

- [ ] An invalid token fails the step.
- [ ] A successful run behaves as now.
