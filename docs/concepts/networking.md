# Networking

The starter can run with private networking (the default) or with public
endpoints. This page explains the options in plain terms and then gives the
technical detail.

## The short version

- **Private (default).** Storage, Cosmos DB, the registry, AI services and
  the two apps get private IP addresses in a virtual network (VNet) that the
  template creates. Nothing accepts traffic from the internet unless you allow
  an IP address. Use this for anything beyond a throwaway demo.
- **Private plus your IP.** This is the same as private, but your public IP
  address is also allowed. Use it so you can deploy and test from your laptop
  without a VPN. This is what the
  [demo quick start](../quickstarts/deploy-demo.md) does.
- **Your own VNet.** Private endpoints go into subnets that you already have,
  usually connected to a corporate hub. See
  [Deploy into an existing VNet](../quickstarts/deploy-existing-vnet.md).
- **Public.** No VNet is created. **The sample app doesn't work end-to-end in
  this mode**: see [the public-mode limitation](#public-mode-limitation).

## Settings for each mode

| Mode | `AZURE_USE_PRIVATE_ENDPOINT` | `AZURE_PUBLIC_NETWORK_ACCESS` | `AZURE_ALLOWED_IPS` | `USE_EXISTING_VNET` |
| --- | --- | --- | --- | --- |
| Private (default) | `true` | `Disabled` | empty | `false` |
| Private plus your IP | `true` | `Disabled` | your IP | `false` |
| Your own VNet | `true` | `Disabled` | empty or your IP | `true`, plus `EXISTING_VNET_*` |
| Restricted public | `false` | `Enabled` | approved IPs | `false` |
| Public | `false` | `Enabled` | empty | `false` |

A non-empty `AZURE_ALLOWED_IPS` turns public access on for the services
below, limited to the listed addresses, even when
`AZURE_PUBLIC_NETWORK_ACCESS=Disabled`:

- the Container Registry
- the backend web app
- the Logic App and its storage
- primary Storage
- Cosmos DB
- Foundry, Document Intelligence and standalone Azure OpenAI

Separate addresses with commas. Cosmos DB entries get `/32` added.

### Public-mode limitation

Primary Storage always denies traffic by default. In public modes the template
creates no VNet, so the web app has no VNet integration and can't reach
Storage. Uploads then fail. Use a private mode until this is fixed; it's
tracked in [planning](../planning/README.md) as an infrastructure change.

## What gets created in private mode

### Generated address plan

| Network | Range | Used for |
| --- | --- | --- |
| VNet | `10.0.0.0/16` | |
| Backend subnet | `10.0.1.0/24` | Private endpoints |
| App integration subnet | `10.0.2.0/24` | Outbound traffic from the web app (delegated to `Microsoft.Web/serverFarms`) |
| Logic App integration subnet | `10.0.3.0/24` | Outbound traffic from the Logic App (delegated to `Microsoft.Web/serverFarms`, with a Cosmos DB service endpoint) |

When you use your own VNet, the template only references your subnets. It
doesn't change them. The
[existing VNet quick start](../quickstarts/deploy-existing-vnet.md) lists the
subnet requirements.

### Private endpoints

- Primary and Logic App Storage: blob, table, queue, file and DFS
- Cosmos DB (SQL)
- Container Registry
- Backend web app and Logic App sites
- Foundry, when `USE_FOUNDRY=new`
- Document Intelligence, when `USE_DOCUMENT_INTELLIGENCE=new`
- Standalone Azure OpenAI, when `USE_OPENAI=new`, or `existing` with
  `CONFIGURE_EXISTING_AI_SERVICES=true`
- Azure Monitor private link scope (Application Insights and Log Analytics)

Existing Foundry and Document Intelligence accounts get private endpoints
only when `CONFIGURE_EXISTING_AI_SERVICES=true`.

### Private DNS

A private endpoint works only if the service's normal hostname (for example
`<account>.blob.core.windows.net`) resolves to the private IP address. Private
DNS zones such as `privatelink.blob.core.windows.net` provide that mapping.

| Option | Settings | Use when |
| --- | --- | --- |
| Create zones (default) | none | Standalone deployments |
| Reuse central zones | `USE_EXISTING_PRIVATE_DNS_ZONES=true` plus the zone subscription and resource group; `LINK_PRIVATE_ENDPOINT_TO_PRIVATE_DNS_ZONE` controls VNet links | Your organization has a hub with shared zones |
| Manage DNS yourself | `SKIP_PRIVATE_DNS_ZONES=true` | DNS is handled by policy or another team |

To check DNS, run `nslookup <name>.blob.core.windows.net` from inside the
network. The answer should be a `10.x` address, not a public one.

### Trusted Azure services

`AZURE_NETWORK_BYPASS` (default `AzureServices`) lets trusted Azure services
reach Storage and Foundry. It isn't a general allow rule for people or apps.
Document Intelligence doesn't use it.

## Reaching a private deployment

To deploy the app or view data, your machine must reach the private
resources. There are three ways:

- allow your IP with `AZURE_ALLOWED_IPS`
- connect to the VNet with a VPN, peering or a jump box
- open access temporarily with a script

[Access a private deployment](../how-to/access-a-private-deployment.md)
explains each one.

The GitHub deployment workflow opens and then closes firewall rules for its
runner. Its cleanup sets public access to `Disabled` rather than restoring the
previous value, which removes access granted with `AZURE_ALLOWED_IPS` until
you provision again. If a run fails or is cancelled, check the settings in
the portal.

## Verify a deployment

From inside the network, check each of these:

- DNS resolves to private addresses.
- `GET /readyz` on the backend returns `200`. It checks Storage and Cosmos DB,
  but not Foundry.
- The Logic App run history shows successful runs.

A successful Bicep build or provision does not prove that the network is
reachable.
