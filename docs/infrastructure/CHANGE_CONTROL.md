# Infrastructure Change Control

The approved Bicep files form a protected behavioral baseline.

## Rules

- Do not refactor, optimize, reorganize, rename, reformat, simplify, or upgrade
  baseline Bicep as routine maintenance.
- Application phases must adapt to the emitted configuration contract.
- Bug fixes require an explicit issue, focused review, compilation, resource
  graph comparison, and baseline manifest update.
- Optional services must use additive modules and explicitly approved
  conditional wiring. Phase 6 permits new AI modules under
  `infra/modules/ai/` plus the minimum parameters, module calls, and outputs
  in `infra/main.bicep`.
- Existing baseline modules, resource definitions, identities, networking,
  RBAC, diagnostics, and application settings must not be optimized,
  reorganized, simplified, reformatted, renamed, upgraded, or behaviorally
  changed.
- When conditional AI wiring changes a file covered by the checksum manifest,
  update the manifest only after exact-diff review, Bicep compilation, and
  no-service resource-graph comparison. The manifest update requires explicit
  approval.
- Every infrastructure change must run:

```bash
az bicep build --file infra/main.bicep --stdout > /dev/null
./scripts/verify_bicep_baseline.sh
```

The checksum command is expected to fail when an approved Bicep change is in
progress. Update the manifest only after the change has been explicitly
approved.
