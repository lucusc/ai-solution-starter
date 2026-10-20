# Bring your own AI resources

Deploy the demo but use a Microsoft Foundry, Azure OpenAI or Document
Intelligence resource that already exists, instead of creating new ones.

**You will need:** everything in [before you start](before-you-start.md), and
the full resource ID of each resource you want to reuse. Get it with:

```bash
az resource show -g "<rg>" -n "<name>" \
  --resource-type Microsoft.CognitiveServices/accounts --query id -o tsv
```

## 1. Create the environment

```bash
azd env new starter-byo
azd env set AZURE_LOCATION eastus2
azd env set AZURE_USE_AUTHENTICATION true
azd env set AZURE_ALLOWED_IPS "$(curl -fsS https://api.ipify.org)"
```

## 2. Point at your resources

Add the block for each service you want to reuse.

**Existing Foundry account** (creates a project and model deployment in it):

```bash
azd env set USE_FOUNDRY existing
azd env set EXISTING_FOUNDRY_ACCOUNT_RESOURCE_ID "<foundry-account-resource-id>"
azd env set AZURE_FOUNDRY_LOCATION "<the account's region>"
azd env set DEPLOY_FOUNDRY_MODEL_EXISTING true
azd env set CONFIGURE_EXISTING_AI_SERVICES true
```

- To use an existing **project** instead, set
  `EXISTING_FOUNDRY_PROJECT_RESOURCE_ID`.
- If the model deployment already exists, skip `DEPLOY_FOUNDRY_MODEL_EXISTING`
  and set `AZURE_FOUNDRY_MODEL_DEPLOYMENT` to its name.

**Existing Document Intelligence:**

```bash
azd env set USE_DOCUMENT_INTELLIGENCE existing
azd env set EXISTING_DOCUMENT_INTELLIGENCE_RESOURCE_ID "<docintel-resource-id>"
```

**Existing Azure OpenAI** (optional; the sample workflow does not use it):

```bash
azd env set USE_OPENAI existing
azd env set EXISTING_OPENAI_RESOURCE_ID "<openai-resource-id>"
```

### What `CONFIGURE_EXISTING_AI_SERVICES` does

By default the template **does not change** existing resources. Set
`CONFIGURE_EXISTING_AI_SERVICES=true` to let it add a private endpoint,
diagnostic settings, and role assignments, including the role the workflow
needs to call the model. If you leave it `false`, someone must grant the
Logic App's managed identity **Cognitive Services OpenAI User** on the
Foundry account and make sure the account is reachable from the VNet.

## 3. Check, provision and deploy

The settings are checked automatically, but you can check them first:

```bash
python3 scripts/validate_ai_service_config.py --from-azd --check-azure
azd provision
./scripts/deploy_app.sh all
```

## Clean up

> **Do not run `azd down` for this scenario.** `azd down` deletes every
> resource group the deployment wrote into. That can include the resource
> group of your existing AI account, because the template adds a project,
> model deployment or role assignments there.

Delete only the app's resource group instead:

```bash
az group delete --name "$(azd env get-value AZURE_RESOURCE_GROUP)"
```

Then remove the project or model deployment the template created in your
existing account, if you no longer need them. See
[clean up](../how-to/clean-up.md).

## Next

- [Choose AI services and models](../how-to/choose-ai-services-and-models.md)
- [Identity and access](../concepts/identity-and-access.md)
