# Infrastructure change control

The Bicep in `infra/` is a protected baseline. `infra/bicep-baseline.sha256`
records a checksum for each protected file, and CI fails if any of them
change. This keeps deployments predictable for everyone who uses the
starter.

## Rules

- Don't refactor, reformat, rename, reorganize or upgrade the baseline Bicep
  as routine maintenance.
- Change the app to fit the infrastructure's outputs and settings, not the
  other way round.
- A bug fix in the baseline needs an issue, a focused review, a Bicep build,
  a comparison of the deployed resources before and after, and a manifest
  update.
- Add optional services as **new modules** under `infra/modules/ai/` (or a
  similar folder), with the minimum parameters, module calls and outputs in
  `infra/main.bicep`. Don't change existing resources, identities,
  networking, RBAC, diagnostics or app settings along the way.
- The existing AI options (Foundry, Azure OpenAI and Document Intelligence,
  each `new`, `existing` or `none`) don't grant ongoing permission to change
  AI parameters, model deployments, app settings, RBAC, networking or
  diagnostics without review.
- Updating the checksum manifest needs **explicit approval**, separate from
  the code change. Never refresh it just to make a failing check pass.

## Check a change

```bash
az bicep build --file infra/main.bicep --stdout > /dev/null
./scripts/verify_bicep_baseline.sh
```

While an approved Bicep change is in progress, the checksum check is
expected to fail. Update the manifest only after approval.

Infrastructure fixes that are waiting for approval are tracked in
[planning](../planning/README.md).
