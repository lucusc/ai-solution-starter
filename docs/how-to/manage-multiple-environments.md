# Manage multiple environments

Each azd environment is an independent copy of the solution with its own
settings and its own resource group. Use one per stage (dev, test, prod) or
per developer.

## Locally

```bash
azd env new starter-test         # create and select
azd env list                     # see all environments
azd env select starter-dev       # switch
azd env get-value AZURE_RESOURCE_GROUP
```

Settings live in `.azure/<environment>/.env` (ignored by Git). Every `azd`
and `./scripts/*.sh` command works on the **selected** environment, so check
`azd env list` before you provision or deploy.

Resource names include a token made from the subscription, environment name
and region. Two environments with different names never collide. The same
name in the same subscription and region always targets the same resources.

## In GitHub Actions

A GitHub **environment** maps to an azd environment. The variables you set
on it, especially `AZURE_ENV_NAME`, decide which resources a run touches.

To add a `test` environment:

1. Create a GitHub environment named `test`, with the same variables and
   secrets as `dev` and a different `AZURE_ENV_NAME`.
2. Add a federated credential for it to the deployment identity, with
   subject `repo:<owner>/<repo>:environment:test`.
3. Add `test` to the `environment` input `options` list in
   `.github/workflows/azure-dev.yml`. Today it lists only `dev`.
4. Optionally add **required reviewers** to the environment so runs wait
   for approval.

## Tips

- Use smaller SKUs and lower model capacity outside production. See
  [cost](../concepts/cost.md).
- Do not share one environment between your machine and GitHub unless the
  settings match. The last `azd provision` wins.
- Delete environments you no longer need. See [clean up](clean-up.md).
