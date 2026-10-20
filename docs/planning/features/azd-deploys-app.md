# FEAT-01: Make `azd up` deploy the app

**Type:** Feature · **Area:** azd · **Priority:** High · **Status:** Proposed

## Summary

`azd up` and `azd deploy` only provision infrastructure. People familiar
with azd expect one command to give them a working app.

## Current behavior

- [`azure.yaml`](../../../azure.yaml) defines only `preprovision` and
  `postprovision` hooks. It has no `services` section, so `azd deploy` has
  nothing to deploy.
- The app is deployed separately with
  [`scripts/deploy_app.sh`](../../../scripts/deploy_app.sh), which builds the
  frontend, builds the image with `az acr build`, updates the web app, and
  zip-deploys the Logic App.

## Impact

Every quick start needs an extra step, and newcomers who run only `azd up`
get an empty web app.

## Proposed change

1. Add a `backend` service to `azure.yaml` (`host: appservice`,
   `project: app/backend`, `docker.remoteBuild: true`) with a `prepackage`
   hook that builds the frontend.
2. Logic Apps Standard isn't an azd host type, so add a `postdeploy` hook
   that runs `./scripts/deploy_app.sh agent`.
3. The web app is already tagged `azd-service-name: backend`
   (`infra/main.bicep` line ~535), so azd can find it without a Bicep
   change.
4. Keep `deploy_app.sh` for partial redeploys.

## Acceptance criteria

- [ ] `azd up` in a new environment results in a working upload and result.
- [ ] `azd deploy` redeploys both the image and the Logic App.
- [ ] No change to the protected Bicep.
- [ ] Quick starts drop the separate `deploy_app.sh` step.
