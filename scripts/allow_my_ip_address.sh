#!/bin/bash
#
# Configures Azure resources for local development access:
#   1. Detects the developer's public IP
#   2. Updates AZURE_ALLOWED_IPS in the azd environment
#   3. Ensures RBAC role assignments (Storage Blob Data Owner, Cosmos DB Data Contributor)
#   4. Opens Storage and Cosmos DB firewalls for the developer and the Azure Portal
#

set -euo pipefail

# --- Helpers ---

azd_value() { azd env get-value "$1" 2>/dev/null || echo ''; }

# Deduplicate a comma-separated IP list
dedup_ips() { echo "$1" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v '^$' | sort -u | paste -sd,; }

get_public_ip() {
  local ip=''
  if command -v dig &>/dev/null; then
    ip=$(dig +short myip.opendns.com @resolver1.opendns.com 2>/dev/null | head -1)
  fi
  if [ -z "$ip" ] && command -v host &>/dev/null; then
    ip=$(host -t A myip.opendns.com resolver1.opendns.com 2>/dev/null | awk '/address/{print $4; exit}')
  fi
  if [ -z "$ip" ] && command -v curl &>/dev/null; then
    ip=$(curl -fsS https://api.ipify.org 2>/dev/null || curl -fsS https://ifconfig.me/ip 2>/dev/null || true)
  fi
  echo "$ip" | tr -d '[:space:]'
}

# --- Resolve public IP ---

ip_address=$(get_public_ip)
if ! [[ "$ip_address" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Failed to resolve a valid public IPv4 address."
  exit 1
fi
echo "Public IP: $ip_address"

# --- Read azd environment ---

storage_rg=$(azd_value AZURE_STORAGE_RESOURCE_GROUP)
storage_account=$(azd_value AZURE_STORAGE_ACCOUNT)
cosmos_rg=$(azd_value AZURE_COSMOSDB_RESOURCE_GROUP)
cosmos_account=$(azd_value AZURE_COSMOSDB_ACCOUNT)
principal_id=$(azd_value AZURE_PRINCIPAL_ID)

# --- Update AZURE_ALLOWED_IPS in azd env ---

allowed_ips=$(dedup_ips "$(azd_value AZURE_ALLOWED_IPS),${ip_address}")
azd env set AZURE_ALLOWED_IPS "$allowed_ips"
echo "AZURE_ALLOWED_IPS=$allowed_ips"

# --- Resolve principal for RBAC ---

if [ -z "$principal_id" ]; then
  echo "Resolving signed-in user for RBAC assignments..."
  principal_id=$(az ad signed-in-user show --only-show-errors --query id -o tsv)
  azd env set AZURE_PRINCIPAL_ID "$principal_id"
  azd env set AZURE_PRINCIPAL_TYPE User
fi

# --- RBAC: Storage Blob Data Owner ---

if [ -n "$storage_rg" ] && [ -n "$storage_account" ]; then
  sub_id=$(az account show --query id -o tsv --only-show-errors)
  scope="/subscriptions/${sub_id}/resourceGroups/${storage_rg}/providers/Microsoft.Storage/storageAccounts/${storage_account}"
  count=$(az role assignment list --assignee-object-id "$principal_id" --scope "$scope" \
    --query "[?roleDefinitionName=='Storage Blob Data Owner'] | length(@)" -o tsv --only-show-errors)
  if [ "${count:-0}" = "0" ]; then
    echo "Assigning Storage Blob Data Owner..."
    az role assignment create --assignee-object-id "$principal_id" --assignee-principal-type User \
      --role "Storage Blob Data Owner" --scope "$scope" --only-show-errors >/dev/null
  fi
fi

# --- RBAC: Cosmos DB Data Contributor ---

if [ -n "$cosmos_rg" ] && [ -n "$cosmos_account" ]; then
  cosmos_id=$(az cosmosdb show -g "$cosmos_rg" -n "$cosmos_account" --query id -o tsv --only-show-errors)
  role_def="${cosmos_id}/sqlRoleDefinitions/00000000-0000-0000-0000-000000000002"
  count=$(az cosmosdb sql role assignment list -a "$cosmos_account" -g "$cosmos_rg" \
    --query "[?principalId=='${principal_id}' && roleDefinitionId=='${role_def}'] | length(@)" -o tsv --only-show-errors)
  if [ "${count:-0}" = "0" ]; then
    echo "Assigning Cosmos DB Data Contributor..."
    az cosmosdb sql role assignment create -a "$cosmos_account" -g "$cosmos_rg" \
      --principal-id "$principal_id" --role-definition-id "$role_def" --scope "$cosmos_id" --only-show-errors >/dev/null
  fi
fi

# --- Storage: firewall rules ---
# network-rule add is idempotent so we can add without checking first.
# Portal Storage Browser proxies data-plane requests through middleware IPs
# that are NOT covered by the "Allow trusted Microsoft services" bypass.

if [ -n "$storage_rg" ] && [ -n "$storage_account" ]; then
  echo "Updating storage account firewall..."
  az storage account update -g "$storage_rg" -n "$storage_account" \
    --public-network-access Enabled --default-action Deny --bypass AzureServices \
    --only-show-errors >/dev/null

  for ip in "$ip_address" 4.210.172.107 13.88.56.148 13.91.105.215 40.91.218.243 52.148.171.5; do
    az storage account network-rule add -g "$storage_rg" --account-name "$storage_account" \
      --ip-address "$ip" --only-show-errors >/dev/null 2>&1 || true
  done
  echo "Storage firewall updated."
fi

# --- Cosmos DB: firewall rules ---
# --ip-range-filter is a full replacement, so we read existing IPs and merge.
# 0.0.0.0 is the Azure datacenter meta-IP — it covers all Portal middleware IPs
# regardless of region or rotation, so the Data Explorer always works.

if [ -n "$cosmos_rg" ] && [ -n "$cosmos_account" ]; then
  echo "Updating Cosmos DB firewall..."
  existing=$(az cosmosdb show -g "$cosmos_rg" -n "$cosmos_account" \
    --query 'ipRules[].ipAddressOrRange' -o tsv --only-show-errors | paste -sd,)
  merged=$(dedup_ips "${existing},${ip_address},0.0.0.0")

  az cosmosdb update -g "$cosmos_rg" -n "$cosmos_account" \
    --public-network-access ENABLED --network-acl-bypass AzureServices \
    --ip-range-filter "$merged" --only-show-errors >/dev/null
  echo "Cosmos DB firewall updated."
fi

echo ""
echo "Done. Cosmos DB changes may take a few minutes to propagate."