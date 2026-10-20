# BUG-11: Verify the maximum PDF size end to end

**Type:** Bug · **Area:** Workflow · **Priority:** Low · **Status:** Needs verification

## Summary

The API accepts PDFs up to `MAX_PDF_SIZE_MB` (default 20 MiB, maximum 100).
Nobody has tested that a file of that size gets through the Logic App and
the model call.

## Current behavior

- [`app/backend/backend/config.py`](../../../app/backend/backend/config.py)
  line ~138 reads `MAX_PDF_SIZE_MB`.
- The [workflow](../../../app/agent/workflows/process-document/workflow.json)
  reads the blob and sends it to the model as base64, which is about a
  third larger than the file. Logic App message limits, connector limits
  and the model's file limits all apply along the way.

## Impact

Large files may be accepted by the API and then fail in the workflow,
leaving the item `failed`.

## Proposed change

Test with synthetic PDFs at 5, 10, 20 MiB and at the model's page limit. Set
the default `MAX_PDF_SIZE_MB` to the largest size that works reliably, and
document the limit in the [API reference](../../reference/api.md).

## Acceptance criteria

- [ ] A synthetic PDF at the documented limit completes successfully.
- [ ] A larger file is rejected by the API with a clear error.
