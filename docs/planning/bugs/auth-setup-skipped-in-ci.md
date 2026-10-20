# BUG-09: Sign-in app setup is skipped in CI

**Type:** Bug · **Area:** GitHub Actions · **Priority:** Medium · **Status:** Proposed

## Summary

In GitHub Actions, the azd hooks never create the sign-in apps or update
their redirect URL.

## Current behavior

- [`auth_init.sh`](../../../scripts/auth_init.sh) and
  [`auth_update.sh`](../../../scripts/auth_update.sh) run only if
  `azd env get-value AZURE_USE_AUTHENTICATION` is `true`.
- `azd env get-value` reads the azd environment file, not the process
  environment. The runner starts with a new azd environment, and the
  workflow never runs `azd env set AZURE_USE_AUTHENTICATION true`, so
  both hooks exit early.

## Impact

Users must create the apps locally and run `auth_update.sh` by hand after
the first deploy, as in the
[GitHub Actions quick start](../../quickstarts/deploy-github-actions.md).

## Proposed change

1. Add an optional workflow step that runs `azd env set
   AZURE_USE_AUTHENTICATION true` when a GitHub variable asks for it, so
   `auth_update` updates the redirect URL after each provision.
2. Keep creating the apps locally, or grant the deployment identity
   Microsoft Graph `Application.ReadWrite.OwnedBy` so it can create them.
3. Fix [BUG-04](export-all-azd-values.md) first, because `auth_init.py`
   writes secrets to the azd environment.

## Acceptance criteria

- [ ] After a workflow provision, the client app's redirect URL matches
      `BACKEND_URI` with no manual step.
- [ ] No sign-in secret becomes a GitHub variable.
