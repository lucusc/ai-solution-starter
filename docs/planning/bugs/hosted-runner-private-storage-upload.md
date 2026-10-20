# BUG-01: Hosted runners can't upload prompts to private Storage

**Type:** Bug · **Area:** GitHub Actions · **Priority:** High · **Status:** Proposed

## Summary

With **Deploy application packages** checked, the workflow fails on a
GitHub-hosted runner when Storage is private, which is the default.

## Current behavior

[`logicapp-deploy/action.yml`](../../../.github/actions/logicapp-deploy/action.yml):

- Lines ~20–32 open the **Logic App** to the runner's IP.
- Lines ~55–80 upload `system.md` and `processing.md` with
  `az storage blob upload`, but don't open the **Storage** firewall. The
  upload is refused from outside the VNet.

The unused [`storage-upload`](../../../.github/actions/storage-upload/action.yml)
action already shows the pattern: add an IP rule, upload, remove the rule.

## Impact

GitHub-only users can't deploy the app. The workaround is to deploy from a
machine or self-hosted runner with network access.

## Proposed change

Before the upload, add a Storage network rule for the runner IP (and enable
public access with default `Deny` if it's `Disabled`), wait for the rule to
apply, then remove the rule and restore the previous setting in an
`always()` cleanup step. Restore what was there before rather than forcing
`Disabled` (see [BUG-05](network-cleanup-forces-disabled.md)).

## Acceptance criteria

- [ ] A run on `ubuntu-latest` with default private settings deploys the
      prompts and the Logic App.
- [ ] After the run, the Storage network settings match those before it.
- [ ] The [GitHub Actions quick start](../../quickstarts/deploy-github-actions.md)
      drops the deploy-from-your-machine workaround.
