# FEAT-04: Coordinated rollback

**Type:** Feature · **Area:** Deployment · **Priority:** Low · **Status:** Proposed

## Summary

There's no single way to go back to a previous version of the image,
Logic App workflow, prompts and infrastructure together.

## Current behavior

- Local deploys tag the image `backend:latest`
  ([`app/backend/docker-build.sh`](../../../app/backend/docker-build.sh)
  line ~24), so earlier images aren't easy to identify.
- The workflow tags images with the commit SHA
  ([`azure-dev.yml`](../../../.github/workflows/azure-dev.yml) line ~249).
- The Logic App zip and the prompt blobs are overwritten in place.

## Impact

A bad release has to be rolled back by redeploying an older commit by hand,
one component at a time.

## Proposed change

1. Tag local images with the Git commit SHA as well as `latest`.
2. Add a `ref` input to the deploy workflow so you can deploy any earlier
   commit.
3. Optionally enable blob versioning on the prompts container (**Infra**).
4. Document the rollback order in
   [customize the app](../../how-to/customize-the-app.md#rolling-back).

## Acceptance criteria

- [ ] Running the workflow with an earlier `ref` restores that version of
      all app components.
- [ ] Images can be traced to a commit.
