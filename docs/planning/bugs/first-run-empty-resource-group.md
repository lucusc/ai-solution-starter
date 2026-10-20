# BUG-02: First workflow run deploys with an empty resource group

**Type:** Bug · **Area:** GitHub Actions · **Priority:** High · **Status:** Proposed

## Summary

The first run with **Deploy application packages** checked fails, because
the deploy steps read the resource group from a GitHub variable that doesn't
exist yet.

## Current behavior

In [`azure-dev.yml`](../../../.github/workflows/azure-dev.yml):

- The provision step writes `resource_group` to its outputs (line ~196).
- The deploy steps instead use `${{ vars.AZURE_RESOURCE_GROUP }}`
  (lines ~228, ~245 and ~257).
- `vars.*` is read when the job starts. On the first run the variable is
  only created later by the **Update Dev Environment Variables** step, so
  the deploy steps get an empty value.

## Impact

You have to run the workflow twice. If the resource group name changes, the
deploy steps target the old one.

## Proposed change

Replace the three `vars.AZURE_RESOURCE_GROUP` references with
`${{ steps.provision.outputs.resource_group }}`.

## Acceptance criteria

- [ ] A first run with app deployment succeeds, given network access
      (see [BUG-01](hosted-runner-private-storage-upload.md)).
- [ ] The quick start no longer says to provision first.
