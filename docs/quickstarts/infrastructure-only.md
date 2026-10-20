# Infrastructure only

Create the Azure platform (web app hosting, Logic App, Storage, Cosmos DB,
Foundry and networking) without deploying the sample app. Use this when you
plan to deploy your own code onto the same resources.

**You will need:** everything in [before you start](before-you-start.md).

## 1. Create the environment and provision

```bash
azd env new starter-infra
azd env set AZURE_LOCATION eastus2
azd env set AZURE_USE_AUTHENTICATION true
azd env set AZURE_ALLOWED_IPS "$(curl -fsS https://api.ipify.org)"
azd provision
```

Skip `./scripts/deploy_app.sh`. The web app shows a placeholder container
and the Logic App has no workflow until you deploy something.

## 2. Find what was created

List the important outputs without printing secrets:

```bash
for v in AZURE_RESOURCE_GROUP BACKEND_URI AZURE_BACKEND_SERVICE_NAME \
         AZURE_LOGICAPP_SERVICE_NAME AZURE_CONTAINER_REGISTRY_NAME \
         AZURE_STORAGE_ACCOUNT AZURE_COSMOSDB_ACCOUNT \
         AZURE_FOUNDRY_INFERENCE_ENDPOINT AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME; do
  echo "$v=$(azd env get-value $v)"
done
```

> Avoid sharing `azd env get-values` output. It also contains the sign-in app
> secrets.

See [resources](../reference/resources.md) for everything that is created and
[app settings](../reference/app-settings.md) for the settings the web app
and Logic App receive.

## 3. Deploy your own code

- **Web app:** push an image to the registry and point the web app at it.
  `app/backend/docker-build.sh` shows the commands.
- **Workflow:** zip-deploy a Logic Apps Standard project, as in
  `app/agent/deploy.sh`.

Both use managed identities. There are no keys or connection strings to copy.
See [customize the app](../how-to/customize-the-app.md).

## Clean up

```bash
azd down --purge
```
