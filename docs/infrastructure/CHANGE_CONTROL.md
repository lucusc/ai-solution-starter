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
- Phase 7 grants a focused behavioral exception for Foundry-first defaults and
  independent Azure OpenAI `new`/`existing`/`none` selection. It permits only
  the required AI parameters, Foundry model deployment, conditional AI module
  wiring, directly coupled app settings, inference RBAC, and associated
  networking/diagnostics. Unrelated baseline modules and behavior remain
  protected.
- When conditional AI wiring changes a file covered by the checksum manifest,
  update the manifest only after exact-diff review, Bicep compilation, and
  no-service resource-graph comparison. The manifest update requires explicit
  approval separate from this implementation request.
- Every infrastructure change must run:

```bash
az bicep build --file infra/main.bicep --stdout > /dev/null
./scripts/verify_bicep_baseline.sh
```

The checksum command is expected to fail when an approved Bicep change is in
progress. Update the manifest only after the change has been explicitly
approved.
