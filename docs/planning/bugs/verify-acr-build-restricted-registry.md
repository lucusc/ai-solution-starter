# BUG-10: Verify `az acr build` against a restricted registry

**Type:** Bug · **Area:** Deployment · **Priority:** Medium · **Status:** Needs verification

## Summary

The local deploy builds the image with ACR Tasks. It hasn't been verified
that this works when the registry is private or limited to your IP.

## Current behavior

- [`app/backend/docker-build.sh`](../../../app/backend/docker-build.sh)
  line ~24 runs `az acr build`, which uploads the source and builds in
  Azure, not on your machine.
- The registry is Premium with public access disabled, or limited to
  `AZURE_ALLOWED_IPS`. ACR Tasks run from Azure-hosted agents whose
  addresses aren't your IP, so a network-restricted registry may refuse the
  push.

## Impact

`./scripts/deploy_app.sh backend` may fail in the default private setup,
even from a machine with VNet access.

## Proposed change

1. Test `deploy_app.sh backend` in the default private mode and with
   `AZURE_ALLOWED_IPS`.
2. If it fails, choose one: build locally with Docker and push over the
   allowed network path; use a dedicated ACR Tasks agent pool in the VNet
   (**Infra**); or allow trusted services for tasks on the registry
   (**Infra**).

## Acceptance criteria

- [ ] The documented backend deploy works in each supported network mode.
- [ ] [Access a private deployment](../../how-to/access-a-private-deployment.md)
      describes the tested path.
