# Networking Matrix

The baseline supports public, restricted-public, private, and
customer-managed-network modes without changing templates.

| Mode | Key settings | Behavior |
| --- | --- | --- |
| Public | `AZURE_PUBLIC_NETWORK_ACCESS=Enabled`, no allowed IPs, private endpoints disabled | Resource public endpoints are enabled subject to each service ACL |
| Restricted public | `AZURE_ALLOWED_IPS` populated | Public endpoints are enabled with default-deny ACLs and explicit IP rules |
| Generated private network | `AZURE_USE_PRIVATE_ENDPOINT=true`, `USE_EXISTING_VNET=false` | Creates VNet, integration subnets, private endpoints, and private DNS zones |
| Existing VNet | `AZURE_USE_PRIVATE_ENDPOINT=true`, `USE_EXISTING_VNET=true` | Uses named existing VNet and subnets |
| Existing private DNS | `USE_EXISTING_PRIVATE_DNS_ZONES=true` | Resolves zones from the configured subscription and resource group |
| Externally managed DNS | `SKIP_PRIVATE_DNS_ZONES=true` | Creates private endpoints without creating or linking private DNS zones |
| App Service Environment | App Service or Logic App ASE ID populated | Uses the supplied ASE and adjusts public access and VNet behavior accordingly |

## Generated address plan

| Network | Default range |
| --- | --- |
| VNet | `10.0.0.0/16` |
| Backend/private endpoint subnet | `10.0.1.0/24` |
| Application integration subnet | `10.0.2.0/24` |
| Logic App integration subnet | `10.0.3.0/24` |

## Private endpoint coverage

Private endpoints can be created for:

- primary and Logic App Storage blob, table, queue, file, and DFS endpoints
- Cosmos DB SQL endpoint
- Azure Container Registry
- backend Web App and Logic App sites
- Azure OpenAI
- Azure Monitor private link scope for Application Insights and Log Analytics

The deployment supports central private DNS zones and optional VNet linking.
