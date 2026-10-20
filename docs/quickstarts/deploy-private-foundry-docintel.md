# Deploy with private endpoints, Foundry and Document Intelligence

Deploy the demo with every service, including a new Document Intelligence
resource, reachable only through private endpoints. Use this when you need a
locked-down network design.

**You will need:** everything in [before you start](before-you-start.md).
For the fully private option, you also need a machine or runner that can
reach the VNet (VPN, ExpressRoute, a jump box, or a self-hosted runner).

## What you get

| Resource | Access |
| --- | --- |
| New VNet `10.0.0.0/16` with 3 subnets | Created for you |
| Web app, Logic App, Storage, Cosmos DB, Container Registry | Private endpoints |
| Microsoft Foundry account, project, and `gpt-4o` deployment | Private endpoint (`privatelink.services.ai.azure.com`) |
| Document Intelligence (`FormRecognizer`, keys disabled) | Private endpoint (`privatelink.cognitiveservices.azure.com`) |
| Private DNS zones for each service | Created and linked to the VNet |

Document Intelligence is provisioned for you to use in your own code. The
sample workflow does not call it. See
[choose AI services](../how-to/choose-ai-services-and-models.md#document-intelligence).

## 1. Create the environment

```bash
azd env new starter-private
azd env set AZURE_LOCATION eastus2
azd env set AZURE_USE_AUTHENTICATION true
azd env set USE_DOCUMENT_INTELLIGENCE new
```

Private endpoints and Foundry are already the defaults
(`AZURE_USE_PRIVATE_ENDPOINT=true`, `AZURE_PUBLIC_NETWORK_ACCESS=Disabled`,
`USE_FOUNDRY=new`).

## 2. Choose how you will reach it

Pick **one** option.

**Option A: private with your IP allowed (simplest).** Your machine can
deploy and open the site. Everything else stays private.

```bash
azd env set AZURE_ALLOWED_IPS "$(curl -fsS https://api.ipify.org)"
```

**Option B: fully private.** Leave `AZURE_ALLOWED_IPS` empty. Run steps 4
and 5 from a machine inside the VNet or connected to it, and make sure that
machine uses the private DNS zones. You can also start with option A and
switch to B later; see
[access a private deployment](../how-to/access-a-private-deployment.md).

## 3. Create the resources

```bash
azd provision
```

## 4. Deploy the code

```bash
./scripts/deploy_app.sh all
```

## 5. Verify

Check that the private endpoints exist and are approved:

```bash
az network private-endpoint list \
  --resource-group "$(azd env get-value AZURE_RESOURCE_GROUP)" \
  --query "[].{name:name, state:privateLinkServiceConnections[0].privateLinkServiceConnectionState.status}" \
  -o table
```

From inside the VNet, service names should resolve to `10.0.1.x` addresses:

```bash
nslookup "$(azd env get-value AZURE_STORAGE_ACCOUNT).blob.core.windows.net"
```

Then open `azd env get-value BACKEND_URI`, sign in, and upload a PDF as in
[deploy the demo](deploy-demo.md#4-try-it).

## Clean up

```bash
azd down --purge
```

## Next

- [How the networking works](../concepts/networking.md)
- [Use your organization's VNet and DNS zones instead](deploy-existing-vnet.md)
- [Call Document Intelligence from your code](../how-to/choose-ai-services-and-models.md#document-intelligence)
