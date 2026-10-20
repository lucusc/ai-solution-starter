# Known limitations

These are the current gaps and caveats. Each one that needs a code or
infrastructure fix links to its item in [planning](../planning/README.md).

## Deployment

| Limitation | What to do now | Tracking |
| --- | --- | --- |
| `azd up` and `azd deploy` don't deploy the app code | Run `./scripts/deploy_app.sh all` after provisioning | [FEAT-01](../planning/features/azd-deploys-app.md) |
| The GitHub workflow can't upload the prompts to private Storage from a GitHub-hosted runner | Provision with the workflow, then deploy the app from a machine or self-hosted runner with network access | [BUG-01](../planning/bugs/hosted-runner-private-storage-upload.md) |
| The workflow's app deployment fails on the first run, because the resource group variable isn't set yet | Run provisioning first, then run again with app deployment | [BUG-02](../planning/bugs/first-run-empty-resource-group.md) |
| Sign-in apps aren't created in GitHub Actions | Create them once locally and store the values in GitHub | [BUG-09](../planning/bugs/auth-setup-skipped-in-ci.md) |
| The workflow offers only the `dev` environment | Edit the workflow's environment choices | [FEAT-02](../planning/features/workflow-environment-choices.md) |
| The workflow ignores the `AZURE_DOCUMENT_INTELLIGENCE_*` naming and placement variables | Use the defaults in CI, or add them to the workflow's `env` | [BUG-07](../planning/bugs/workflow-variable-drift.md) |
| Nothing rolls back the image, workflow, prompts and infrastructure together | Keep the previous versions and redeploy them together | [FEAT-04](../planning/features/coordinated-rollback.md) |
| `azd down` deletes every resource group the deployment wrote into, including shared ones | When you reuse existing AI or DNS resource groups, delete only the app resource group | [Clean up](../how-to/clean-up.md) |
| `deploy_app.sh` needs Bash, `zip` and GNU `mktemp` | On Windows, use WSL or a dev container | |

## Security

| Limitation | What to do now | Tracking |
| --- | --- | --- |
| The workflow copies **every** azd value, including any secrets, into GitHub environment variables | Keep secrets out of the azd environment used by CI, or disable the export step | [BUG-04](../planning/bugs/export-all-azd-values.md) |
| The workflow reads some secrets from GitHub variables instead of secrets | Don't set API keys as variables; the sample doesn't need them | [BUG-03](../planning/bugs/secrets-read-from-variables.md) |
| Registry login in the workflow uses a service principal secret | Store the secret only as a GitHub environment secret and rotate it | [FEAT-05](../planning/features/oidc-registry-login.md) |
| The env-var update step logs failures and carries on | Check the step output after each run | [BUG-06](../planning/bugs/env-var-update-ignores-failures.md) |

## Networking

| Limitation | What to do now | Tracking |
| --- | --- | --- |
| Public modes don't work end-to-end, because the web app can't reach Storage | Use a private mode | [BUG-08](../planning/bugs/public-mode-cannot-reach-storage.md) |
| The workflow's firewall cleanup sets public access to `Disabled` instead of restoring it | Run `azd provision` again to restore `AZURE_ALLOWED_IPS` access | [BUG-05](../planning/bugs/network-cleanup-forces-disabled.md) |
| `az acr build` against a registry limited to your IP hasn't been verified | If the backend build fails, use a VNet-connected machine | [BUG-10](../planning/bugs/verify-acr-build-restricted-registry.md) |
| Document Intelligence ignores `AZURE_NETWORK_BYPASS` | None needed for the sample | |

## Application

| Limitation | What to do now | Tracking |
| --- | --- | --- |
| A work item stays in `processing` for good if its run is cancelled, or if the failure handler can't record the failure | Look up the run in the Logic App run history and fix the item manually | [FEAT-03](../planning/features/stale-processing-recovery.md) |
| The workflow processes one PDF at a time and checks for new files every minute | Expect a short delay; change the trigger for higher volume | |
| The API accepts PDFs up to 20 MiB, but the full size hasn't been tested end-to-end through the model call | Test your largest expected document | [BUG-11](../planning/bugs/verify-maximum-pdf-size.md) |
| A replacement model must support the Responses API, PDF input and structured outputs | Check the model's capabilities before switching | |
| `/readyz` checks Storage and Cosmos DB, not the model | Check the Logic App run history for model errors | |
| Standalone Azure OpenAI and Document Intelligence are provisioned but not used by the sample | Use them in your own code | |
| There is no Azure AI Search or retrieval (RAG) support | Add it yourself | [FEAT-06](../planning/features/optional-ai-search.md) |

## Testing

The automated tests run without Azure. They don't prove that a deployment
works. That needs a live deployment and a test upload, as described in the
[demo quick start](../quickstarts/deploy-demo.md#4-try-it). The quick starts
follow the scripts and templates, but they haven't all been run end-to-end in
every configuration.
