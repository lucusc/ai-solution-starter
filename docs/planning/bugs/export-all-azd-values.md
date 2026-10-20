# BUG-04: Every azd value is exported as a GitHub variable

**Type:** Bug · **Area:** GitHub Actions · **Priority:** Medium · **Status:** Proposed

## Summary

After provisioning, the workflow copies every azd environment value into
GitHub environment variables, with no allow-list.

## Current behavior

- [`scripts/export_azd_values.ps1`](../../../scripts/export_azd_values.ps1)
  lines 10–18 convert all of `azd env get-values` to JSON.
- The **Update Dev Environment Variables** step writes each one as a plain
  GitHub variable.

Today the runner's azd environment holds only names, region and Bicep
outputs, none of which are secret. But anything later written with
`azd env set` is published too. For example,
[`auth_init.py`](../../../scripts/auth_init.py) line ~71 stores the sign-in
app secrets with `azd env set`; if [BUG-09](auth-setup-skipped-in-ci.md) is
fixed by running it in CI, those secrets would be exported as plain
variables.

## Impact

A future change can leak secrets without anyone noticing.

## Proposed change

Export only an explicit list of output names (resource group, service
names, URIs and similar), or skip names containing `SECRET`, `KEY`,
`PASSWORD` or `TOKEN` and fail if one is found.

## Acceptance criteria

- [ ] Only the listed outputs become GitHub variables.
- [ ] A test or check fails if a secret-like name would be exported.
