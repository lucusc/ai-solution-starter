# BUG-03: Secrets read from GitHub variables

**Type:** Bug · **Area:** GitHub Actions · **Priority:** High · **Status:** Proposed

## Summary

The workflow reads some secret settings from GitHub **variables**, which are
stored and shown in plain text.

## Current behavior

In the job `env` of [`azure-dev.yml`](../../../.github/workflows/azure-dev.yml):

| Line | Setting | Read from |
| --- | --- | --- |
| ~53 | `AZURE_CLIENT_APP_SECRET` | `vars` (overridden by `secrets` in the provision step only, line ~206) |
| ~74 | `AZURE_OPENAI_API_KEY` | `vars` |
| ~107 | `AZURE_SERVER_APP_SECRET` | `vars` (overridden by `secrets` in the provision step only, line ~207) |
| ~161 | `OPENAI_API_KEY` | `vars` |

## Impact

Anyone following the variable names may store a key as a variable, where
anyone with repository read access to environments can see it.

## Proposed change

Read all four from `secrets.*` at job level and remove the step-level
override. Document them as secrets in the
[workflows reference](../../reference/github-workflows.md).

## Acceptance criteria

- [ ] No setting whose name contains `SECRET` or `KEY` is read from `vars`.
- [ ] Provisioning still receives the sign-in app secrets.
