# GitHub workflows reference

The repository has four workflows in `.github/workflows/`. Two change Azure
(`azure-dev.yml` and `assign-rbac.yml`) and only run when you start them
manually. The other two are checks that run on pull requests and pushes.

| Workflow | File | Trigger | Changes Azure |
| --- | --- | --- | --- |
| Deploy to Azure | `azure-dev.yml` | Manual | Yes |
| Assign RBAC to Resource Group | `assign-rbac.yml` | Manual | Yes |
| Infrastructure Validation | `infra-validation.yml` | PRs and pushes to `main` that touch `infra/**` or `azure.yaml` | No |
| Application CI | `backend-ci.yml` | All PRs and pushes to `main` | No |

For first-time setup, follow
[Deploy with GitHub Actions](../quickstarts/deploy-github-actions.md).

## Deploy to Azure

Provisions the infrastructure with `azd provision`, and can also deploy the
app.

### Inputs

| Input | Values | Meaning |
| --- | --- | --- |
| `environment` | `dev` | The GitHub environment to read settings from. Only `dev` is offered; edit the workflow to add more. |
| `deploy-application` | `true` / `false` (default) | Also deploy the Logic App workflow, prompts and backend image after provisioning. |

Runs for the same branch cancel each other (`cancel-in-progress`).

### GitHub environment settings

The job runs in the chosen GitHub environment and passes its **variables** to
azd as environment variables. Any setting in
[configuration](configuration.md) can be set this way, except the four
`AZURE_DOCUMENT_INTELLIGENCE_*` naming and placement settings, which the
workflow doesn't pass on yet.

Required variables:

| Variable | Used for |
| --- | --- |
| `AZURE_SERVICE_PRINCIPAL_CLIENT_ID` | Client ID of the deployment identity (OIDC sign-in) |
| `AZURE_TENANT_ID` | Tenant of the deployment identity |
| `AZURE_SUBSCRIPTION_ID` | Subscription to deploy into |
| `AZURE_ENV_NAME` | azd environment name; also drives resource names |
| `AZURE_LOCATION` | Azure region |

Needed for sign-in (see
[configure authentication](../how-to/configure-authentication.md)):
`AZURE_SERVER_APP_ID`, `AZURE_CLIENT_APP_ID`, `AZURE_AUTH_TENANT_ID`.

Secrets:

| Secret | Used for |
| --- | --- |
| `AZURE_SERVER_APP_SECRET`, `AZURE_CLIENT_APP_SECRET` | Sign-in app secrets, passed to `azd provision` |
| `MANAGE_ENV_VARS_PAT` | Fine-grained token with **Environments: read and write**, used to save outputs back as variables |
| `AZURE_SERVICE_PRINCIPAL_CLIENT_SECRET` | Registry login when deploying the app |

### Steps

1. **Sign in.** Installs azd, signs in with `azure/login` using OIDC, and
   tells azd to use the Azure CLI sign-in.
2. **Provision.** Runs `azd provision --no-prompt`. The `preprovision` and
   `postprovision` hooks run, but they don't create or update sign-in apps,
   because the runner's new azd environment never has
   `AZURE_USE_AUTHENTICATION` set. That's why you create the apps locally
   first.
3. **Save outputs.** `scripts/export_azd_values.ps1` reads every
   `azd env get-values` entry, and the `create-environment-variables` action
   writes each one to the GitHub environment as a variable. Later runs use
   these values (for example `AZURE_RESOURCE_GROUP`).
4. **Deploy the app** (only when `deploy-application` is `true`):
   1. `logicapp-deploy` uploads the prompts to Storage and zip-deploys the
      Logic App workflow.
   2. Builds the frontend with `npm ci` and `npm run build`.
   3. `acr-build-deploy` builds the backend image with Docker on the runner
      and pushes it to the registry, tagged with the commit SHA.
   4. `webapps-deploy` points the web app at the new image.

### Temporary network access

A GitHub-hosted runner is outside the VNet, so the deploy actions open a
temporary path for the runner's IP and close it in an `always()` cleanup
step:

| Action | Opens | Cleanup sets |
| --- | --- | --- |
| `logicapp-deploy` | Logic App public access plus an SCM rule for the runner IP | Logic App public access `Disabled` |
| `acr-build-deploy` | Registry public access, default `Deny`, plus an IP rule | IP rule removed, public access off |
| `webapps-deploy` | Web app public access plus an SCM rule for the runner IP | Web app public access `Disabled` |

Cleanup always sets `Disabled`, even if the resource allowed
`AZURE_ALLOWED_IPS` before the run. Run `azd provision` again to restore it.

The prompt upload in `logicapp-deploy` does **not** open the Storage firewall,
so it fails from a GitHub-hosted runner when Storage is private. Deploy the
app from a machine or self-hosted runner with network access. See
[known limitations](../concepts/known-limitations.md#deployment) for this
and other open issues.

### Composite actions

The `.github/actions/` folder also contains `storage-upload`,
`functions-deploy` and `my-ip-address`. No workflow uses them at the moment.

## Assign RBAC

`assign-rbac.yml` assigns a role on the environment's resource group
(`AZURE_RESOURCE_GROUP` from the GitHub environment). It signs in with the
same OIDC identity as **Deploy to Azure**.

| Input | Values |
| --- | --- |
| `environment` | `dev` |
| `role-name` | `All`, or one of: AcrPull, Cognitive Services OpenAI User, Cognitive Services User, DocumentDB Account Contributor, Storage Account Contributor, Storage Blob Data Contributor, Storage Blob Data Owner, Storage Blob Data Reader, Storage File Data Privileged Contributor, Storage Queue Data Contributor, Storage Queue Data Message Processor, Storage Queue Data Message Sender, Storage Queue Data Reader, Storage Table Data Contributor |
| `assignee-object-id` | Object ID of the user or service principal |
| `assignee-principal-type` | `User` or `ServicePrincipal` |
| `are-you-sure` | Must be checked, or the job does nothing |

The role is assigned at resource-group scope, which is broader than the
resource-level assignments the template creates. Use it for people who need
data access while developing, and prefer the narrowest role that works. See
[identity and access](../concepts/identity-and-access.md).

## Infrastructure Validation

Runs without Azure credentials:

1. `az bicep build` for `main.bicep` and the AI modules.
2. `python3 scripts/validate_ai_service_config.py` to check the optional AI
   service defaults.
3. `./scripts/verify_bicep_baseline.sh` to check the protected Bicep files
   against `infra/bicep-baseline.sha256`. See
   [infrastructure change control](../contributing/infra-change-control.md).

## Application CI

Runs without Azure credentials. Jobs:

| Job | Checks |
| --- | --- |
| Backend | pytest for the backend, agent and scripts; ruff lint and format; mypy |
| Frontend | lint, type check, tests and build; checks generated assets aren't committed |
| Production container | builds the frontend and the backend image, then probes the running container |
| Repository policy | tracked-file policy, deterministic sample generation, Bicep baseline and diff whitespace |

To run the same checks locally, see [development](../contributing/development.md).
