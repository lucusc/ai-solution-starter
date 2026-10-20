# Access a private deployment

By default every service has public access turned off and is reachable only
through private endpoints in the VNet. To deploy code, open the site, or run
the API locally, your machine needs a way in. Pick the option that fits.

| Option | Good for | Effort |
| --- | --- | --- |
| [Allow your IP](#allow-your-ip) | Demos, development | Low |
| [Connect to the VNet](#connect-to-the-vnet) | Production-like, fully private | Medium to high |
| [Temporary script access](#temporary-script-access) | One-off data access from your machine | Low, but must be undone |

## Allow your IP

```bash
azd env set AZURE_ALLOWED_IPS "$(curl -fsS https://api.ipify.org)"
azd provision
```

Any IP or CIDR in this comma-separated list is allowed through the firewalls
of the web app, Logic App, Storage, Cosmos DB, Container Registry and the AI
services. Everything else stays blocked. Private endpoints keep working for
the services themselves.

To add a colleague, append their address: `"203.0.113.10,198.51.100.0/24"`.

### Go fully private

Clear the list and provision again:

```bash
azd env set AZURE_ALLOWED_IPS ""
azd provision
```

From then on, deploy and browse from a connected network only.

## Connect to the VNet

Use one of:

- **VPN or ExpressRoute** to the VNet (or a hub peered with it).
- **A jump box** (VM) in the VNet, for example through Azure Bastion.
- **A self-hosted GitHub runner** in the VNet for automated deployments.

Whichever you use, the machine must resolve service names through the
**private DNS zones** (for example `privatelink.blob.core.windows.net`).
On a VM in the VNet this works automatically. From on-premises you usually
need a DNS forwarder or Azure DNS Private Resolver. See
[networking](../concepts/networking.md#private-dns).

Check DNS from the connected machine. The answer should be a private
address:

```bash
nslookup "$(azd env get-value AZURE_STORAGE_ACCOUNT).blob.core.windows.net"
```

## Temporary script access

`./scripts/allow_my_ip_address.sh` is for local development when you cannot
re-provision. It:

1. Detects your public IP and adds it to `AZURE_ALLOWED_IPS`.
2. Gives your account **Storage Blob Data Owner** and **Cosmos DB Built-in
   Data Contributor**.
3. Turns on public access for Storage and Cosmos DB, adds your IP and the
   Azure portal IPs, and adds the Cosmos `0.0.0.0` rule. That rule allows
   all Azure datacenters.

These changes stay until you remove them. The next `azd provision` resets the
firewall rules to what your azd settings say.

`./scripts/update_acr_network_access.sh <resource-group> <registry> enabled`
opens the container registry the same way. Run it again with `disabled` to
close it.

## After a GitHub deployment

The GitHub deploy steps open the registry and Logic App to the runner. When
they finish, they set public access to **Disabled**, even if
`AZURE_ALLOWED_IPS` had it enabled. Run `azd provision` to restore your
settings. This is tracked in the [planning notes](../planning/README.md).
