# FEAT-05: Use OIDC for registry login

**Type:** Feature · **Area:** GitHub Actions · **Priority:** Medium · **Status:** Proposed

## Summary

Provisioning uses OIDC, but pushing the image still needs a long-lived
service principal secret.

## Current behavior

- [`azure-dev.yml`](../../../.github/workflows/azure-dev.yml) lines ~246–247
  pass `AZURE_SERVICE_PRINCIPAL_CLIENT_ID` and the secret
  `AZURE_SERVICE_PRINCIPAL_CLIENT_SECRET` to `acr-build-deploy`.
- [`acr-build-deploy/action.yml`](../../../.github/actions/acr-build-deploy/action.yml)
  lines ~59–63 use `docker/login-action` with that username and password.

## Impact

Users have to create, store and rotate a client secret, which the OIDC
setup was meant to avoid.

## Proposed change

After `azure/login`, run `az acr login --name <registry>` (it uses the
signed-in OIDC identity), or build with `az acr build` like the local
script. The deployment identity needs `AcrPush` on the registry (`Owner`
already covers it). Remove the username and password inputs.

## Acceptance criteria

- [ ] The workflow pushes an image without `AZURE_SERVICE_PRINCIPAL_CLIENT_SECRET`.
- [ ] The secret is removed from the
      [GitHub Actions quick start](../../quickstarts/deploy-github-actions.md)
      and the [workflows reference](../../reference/github-workflows.md).
