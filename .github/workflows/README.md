# Workflows

| Workflow | Trigger | What it does |
| --- | --- | --- |
| `azure-dev.yml` | Manual | **Changes Azure.** Runs `azd provision` and can deploy the app. |
| `assign-rbac.yml` | Manual | **Changes Azure.** Assigns a role on the environment's resource group. |
| `infra-validation.yml` | PRs and pushes touching `infra/` or `azure.yaml` | Builds the Bicep and checks the protected baseline. |
| `backend-ci.yml` | All PRs and pushes to `main` | Backend, frontend, container and repository-policy checks. |

The check workflows don't sign in to Azure.

- Set up deployment: [Deploy with GitHub Actions](../../docs/quickstarts/deploy-github-actions.md)
- Inputs, variables, secrets and steps: [GitHub workflows reference](../../docs/reference/github-workflows.md)
- Run the same checks locally: [Development](../../docs/contributing/development.md)
