# Planning

Proposed features and bug fixes that aren't implemented yet. Each item
describes the current behavior, why it matters and what a fix would look
like, so it can be picked up as an issue or pull request.

Nothing here describes current behavior you can rely on. For what works
today and the workarounds, see
[known limitations](../concepts/known-limitations.md).

Items marked **Infra** change the protected Bicep baseline. They need
approval under [infrastructure change control](../contributing/infra-change-control.md)
before work starts.

## Features

| ID | Title | Area | Priority | Status |
| --- | --- | --- | --- | --- |
| FEAT-01 | [Make `azd up` deploy the app](features/azd-deploys-app.md) | azd | High | Proposed |
| FEAT-02 | [Offer more environments in the workflows](features/workflow-environment-choices.md) | GitHub Actions | Medium | Proposed |
| FEAT-03 | [Recover work items stuck in `processing`](features/stale-processing-recovery.md) | Workflow | Medium | Proposed |
| FEAT-04 | [Coordinated rollback](features/coordinated-rollback.md) | Deployment | Low | Proposed |
| FEAT-05 | [Use OIDC for registry login](features/oidc-registry-login.md) | GitHub Actions | Medium | Proposed |
| FEAT-06 | [Optional Azure AI Search](features/optional-ai-search.md) | Infra | Low | Proposed |

## Bugs

| ID | Title | Area | Priority | Status |
| --- | --- | --- | --- | --- |
| BUG-01 | [Hosted runners can't upload prompts to private Storage](bugs/hosted-runner-private-storage-upload.md) | GitHub Actions | High | Proposed |
| BUG-02 | [First workflow run deploys with an empty resource group](bugs/first-run-empty-resource-group.md) | GitHub Actions | High | Proposed |
| BUG-03 | [Secrets read from GitHub variables](bugs/secrets-read-from-variables.md) | GitHub Actions | High | Proposed |
| BUG-04 | [Every azd value is exported as a GitHub variable](bugs/export-all-azd-values.md) | GitHub Actions | Medium | Proposed |
| BUG-05 | [Network cleanup forces public access to `Disabled`](bugs/network-cleanup-forces-disabled.md) | GitHub Actions | Medium | Proposed |
| BUG-06 | [Variable update step ignores failures](bugs/env-var-update-ignores-failures.md) | GitHub Actions | Medium | Proposed |
| BUG-07 | [Workflow variables out of step with the parameters](bugs/workflow-variable-drift.md) | GitHub Actions | Medium | Proposed |
| BUG-08 | [Public modes can't reach Storage](bugs/public-mode-cannot-reach-storage.md) | Infra | High | Proposed |
| BUG-09 | [Sign-in app setup is skipped in CI](bugs/auth-setup-skipped-in-ci.md) | GitHub Actions | Medium | Proposed |
| BUG-10 | [Verify `az acr build` against a restricted registry](bugs/verify-acr-build-restricted-registry.md) | Deployment | Medium | Needs verification |
| BUG-11 | [Verify the maximum PDF size end to end](bugs/verify-maximum-pdf-size.md) | Workflow | Low | Needs verification |

## Adding an item

Copy [the template](TEMPLATE.md) into `features/` or `bugs/`, give it the
next ID, and add a row above. If it's a limitation users can hit today, add
it to [known limitations](../concepts/known-limitations.md) too. When the fix
ships, delete the file, remove the rows, and update the docs that describe the
behavior.
