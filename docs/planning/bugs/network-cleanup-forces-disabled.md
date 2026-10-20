# BUG-05: Network cleanup forces public access to `Disabled`

**Type:** Bug · **Area:** GitHub Actions · **Priority:** Medium · **Status:** Proposed

## Summary

The deploy actions open resources to the runner IP and then always set
public access to `Disabled`, whatever it was before.

## Current behavior

| Action | Cleanup lines | Sets |
| --- | --- | --- |
| [`logicapp-deploy`](../../../.github/actions/logicapp-deploy/action.yml) | ~113–124 | Logic App `publicNetworkAccess=Disabled` |
| [`webapps-deploy`](../../../.github/actions/webapps-deploy/action.yml) | ~86–97 | Web app `publicNetworkAccess=Disabled` |
| [`acr-build-deploy`](../../../.github/actions/acr-build-deploy/action.yml) | ~76–93 | Registry public access off |
| [`storage-upload`](../../../.github/actions/storage-upload/action.yml) (unused) | last step | Storage `--public-network-access Disabled` |

## Impact

If the environment uses `AZURE_ALLOWED_IPS` or a public mode, a workflow
deploy turns off that access. Browser access to the web app stops until
someone runs `azd provision` again.

## Proposed change

In each action, read the current setting (and IP rules) before opening
access, and restore exactly that in the `always()` cleanup. Remove only the
rule that the action added.

## Acceptance criteria

- [ ] After a deploy, public access settings and IP rules match their
      values before the deploy, in both private and `AZURE_ALLOWED_IPS`
      setups.
