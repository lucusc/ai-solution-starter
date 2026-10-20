# BUG-07: Workflow variables out of step with the parameters

**Type:** Bug · **Area:** GitHub Actions · **Priority:** Medium · **Status:** Proposed

## Summary

The deploy workflow's list of variables doesn't match
[`infra/main.parameters.json`](../../../infra/main.parameters.json).

## Current behavior

The job `env` in [`azure-dev.yml`](../../../.github/workflows/azure-dev.yml)
(lines ~41–172) lists each setting by hand:

- **Not passed on:** `AZURE_DOCUMENT_INTELLIGENCE_ACCOUNT`,
  `AZURE_DOCUMENT_INTELLIGENCE_LOCATION`,
  `AZURE_DOCUMENT_INTELLIGENCE_RESOURCE_GROUP` and
  `AZURE_DOCUMENT_INTELLIGENCE_SKU`. Setting them in GitHub has no effect.
- **Obsolete:** `DEPLOY_AZURE_OPEN_MODELS` and `DEPLOY_AZURE_OPENAI`
  (lines ~133–134) aren't used by the parameters.
- **Overrides runner variables:** `GITHUB_ACTIONS` (line ~147) and
  `TF_BUILD` (line ~170) are read from GitHub variables.
  `GITHUB_ACTIONS` feeds the `runningOnGh` parameter, which sets the
  principal type for role assignments (`main.bicep` line ~1132). Check
  whether the runner's built-in value is kept; either way these lines aren't
  needed.

## Impact

Settings silently don't apply in CI, and every new parameter needs a
manual workflow edit.

## Proposed change

1. Add the four Document Intelligence variables and remove the two obsolete
   ones and the `GITHUB_ACTIONS` and `TF_BUILD` lines.
2. Add a test in `scripts/tests` that compares the workflow `env` with
   the `${...}` names in `main.parameters.json`, so drift fails CI.

## Acceptance criteria

- [ ] Every mapped parameter can be set from a GitHub variable.
- [ ] The drift test fails when a parameter is added without a workflow
      variable.
- [ ] The [workflows reference](../../reference/github-workflows.md) drops
      the Document Intelligence exception.
