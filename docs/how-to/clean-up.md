# Clean up

Delete what a deployment created so it stops costing money.

## Standard deployment

```bash
azd env select <environment>
azd down --purge
```

`--purge` permanently deletes soft-deleted resources (Foundry, Document
Intelligence, OpenAI) so the names can be reused. You are asked to confirm.

> **If you reused existing resources** (an existing Foundry account, VNet DNS
> zones, or resource groups), do not use `azd down`. It deletes every
> resource group the deployment wrote into. Delete only the app's resource
> group instead:
>
> ```bash
> az group delete --name "$(azd env get-value AZURE_RESOURCE_GROUP)"
> ```
>
> Then purge soft-deleted AI accounts in the portal (**Azure AI services →
> Manage deleted resources**) if you want to reuse their names.

## Things `azd down` leaves behind

| Item | How to remove |
| --- | --- |
| Sign-in app registrations | `az ad app delete --id "$(azd env get-value AZURE_CLIENT_APP_ID)"`, and the same for `AZURE_SERVER_APP_ID` |
| Your local azd environment | `rm -rf .azure/<environment>` |
| GitHub deployment identity | `az ad app delete --id <app-id>` |
| GitHub environment variables and secrets | **Settings → Environments** in GitHub |
| Model deployments, projects or role assignments in an existing AI account | Delete them in the portal or with `az` |

## Check nothing is left

```bash
az group list --query "[?contains(name, '<environment>')].name" -o tsv
```
