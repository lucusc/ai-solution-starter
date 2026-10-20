# Deploy into an existing VNet

Deploy the demo into a virtual network that your network team already
manages, optionally reusing central private DNS zones. The template does not
create or change the VNet; it only places resources in its subnets.

**You will need:** everything in [before you start](before-you-start.md), plus
network access from your machine to the VNet (VPN, ExpressRoute or a jump
box), or permission to add your IP to the allowlist.

## 1. Prepare the subnets

Ask your network team for three subnets in one VNet:

| Subnet | Used for | Requirements |
| --- | --- | --- |
| Backend | Private endpoints | `/24` recommended; no delegation |
| App integration | Web app outbound traffic | Delegated to `Microsoft.Web/serverFarms` |
| Logic integration | Logic App outbound traffic | Delegated to `Microsoft.Web/serverFarms`; service endpoint `Microsoft.AzureCosmosDB` |

Your deployment identity needs **Network Contributor** (or
`Microsoft.Network/virtualNetworks/subnets/join/action`) on the VNet.

## 2. Create the environment

```bash
azd env new starter-vnet
azd env set AZURE_LOCATION eastus2
azd env set AZURE_USE_AUTHENTICATION true

azd env set USE_EXISTING_VNET true
azd env set EXISTING_VNET_SUBSCRIPTION_ID "<subscription-id>"
azd env set EXISTING_VNET_RESOURCE_GROUP_NAME "<network-rg>"
azd env set EXISTING_VNET_NAME "<vnet-name>"
azd env set EXISTING_BACKEND_SUBNET_NAME "<backend-subnet>"
azd env set EXISTING_APP_INT_SUBNET_NAME "<app-integration-subnet>"
azd env set EXISTING_LOGIC_INT_SUBNET_NAME "<logic-integration-subnet>"
```

The VNet must be in the same region as `AZURE_LOCATION`.

## 3. Choose how DNS works

Pick **one**:

| Option | Settings | When to use |
| --- | --- | --- |
| Create new zones (default) | Nothing to set | Sandbox or isolated VNet |
| Reuse central zones | `USE_EXISTING_PRIVATE_DNS_ZONES=true`, `PRIVATE_DNS_ZONES_SUBSCRIPTION_ID`, `PRIVATE_DNS_ZONES_RESOURCE_GROUP_NAME` | Hub-and-spoke with central zones. Set `LINK_PRIVATE_ENDPOINT_TO_PRIVATE_DNS_ZONE=false` if the zones are already linked to your VNet. |
| Do not touch DNS | `SKIP_PRIVATE_DNS_ZONES=true` | DNS records are created by Azure Policy or another team |

Example for central zones:

```bash
azd env set USE_EXISTING_PRIVATE_DNS_ZONES true
azd env set PRIVATE_DNS_ZONES_SUBSCRIPTION_ID "<hub-subscription-id>"
azd env set PRIVATE_DNS_ZONES_RESOURCE_GROUP_NAME "<dns-rg>"
```

## 4. Provision and deploy

If you are not connected to the VNet, first allow your IP:
`azd env set AZURE_ALLOWED_IPS "$(curl -fsS https://api.ipify.org)"`.

```bash
azd provision
./scripts/deploy_app.sh all
```

## 5. Verify

From a machine on the VNet, check that names resolve to private addresses in
your backend subnet:

```bash
nslookup "$(azd env get-value AZURE_STORAGE_ACCOUNT).blob.core.windows.net"
```

Then open `azd env get-value BACKEND_URI` and upload a PDF.

## Clean up

If you reused central DNS zones, **do not run `azd down`**. It deletes every
resource group the deployment wrote into, which can include the DNS zone
resource group. Delete only the app's resource group:

```bash
az group delete --name "$(azd env get-value AZURE_RESOURCE_GROUP)"
```

Then check the DNS zones for leftover records. The VNet and subnets are not
changed by the template. See [clean up](../how-to/clean-up.md).

## Next

- [Networking concepts and the full option matrix](../concepts/networking.md)
- [Access a private deployment](../how-to/access-a-private-deployment.md)
