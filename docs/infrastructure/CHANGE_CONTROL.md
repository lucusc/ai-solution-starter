# Infrastructure Change Control

The approved Bicep files form an immutable behavioral baseline.

## Rules

- Do not refactor, optimize, reorganize, rename, reformat, simplify, or upgrade
  baseline Bicep as routine maintenance.
- Application phases must adapt to the emitted configuration contract.
- Bug fixes require an explicit issue, focused review, compilation, resource
  graph comparison, and baseline manifest update.
- Optional services must use additive templates or another separately approved
  extension mechanism.
- Every infrastructure change must run:

```bash
az bicep build --file infra/main.bicep --stdout > /dev/null
./scripts/verify_bicep_baseline.sh
```

The checksum command is expected to fail when an approved Bicep change is in
progress. Update the manifest only after the change has been explicitly
approved.
