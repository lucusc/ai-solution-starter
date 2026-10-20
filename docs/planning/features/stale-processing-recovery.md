# FEAT-03: Recover work items stuck in `processing`

**Type:** Feature · **Area:** Workflow · **Priority:** Medium · **Status:** Proposed

## Summary

A work item can stay in `processing` permanently, and nothing detects or
retries it.

## Current behavior

In [`workflow.json`](../../../app/agent/workflows/process-document/workflow.json):

- `Only_process_queued_records` (line ~457) processes an item only when its
  status is `queued`, and claims it by setting `processing` with an ETag
  check.
- `Handle_claimed_failure` (line ~882) runs when processing fails or times
  out, and sets the item to `failed` if it is still `processing` at the same
  version.

The item is never moved out of `processing` if:

- the run is cancelled, or the Logic App restarts mid-run;
- the failure handler itself fails (for example, Cosmos DB is unreachable);
  or
- the version changed between the claim and the failure.

## Impact

The user sees the item as processing forever. An operator must find the
run in the Logic App run history and fix the Cosmos DB record by hand.

## Proposed change

Add a second, scheduled workflow (for example every 15 minutes) that queries
for items in `processing` with `updated_at` older than a threshold, and sets
them to `failed` with a retryable error, using the same ETag pattern. Make
the threshold a Logic App app setting. This is a new workflow in the app
package, not a Bicep change, unless a new app setting is needed in the
baseline.

## Acceptance criteria

- [ ] A stale item moves to `failed` within one schedule interval after the
      threshold.
- [ ] Items being processed normally aren't touched.
- [ ] Workflow package tests cover the new workflow.
- [ ] The [architecture](../../concepts/architecture.md#work-item-lifecycle)
      lifecycle is updated.
