#!/bin/bash

resource_group="$1"
acr_name="$2"
network_access="$3"

if [ -z "$resource_group" ] || [ -z "$acr_name" ]; then
    echo "Usage: $0 <resource_group> <acr_name>"
    exit 1
fi

if [ -z "$network_access" ]; then
    network_access="disabled"
elif [ "$network_access" != "enabled" ] && [ "$network_access" != "disabled" ]; then
    echo "Invalid network access option. Use 'enabled' or 'disabled'."
    exit 1
fi

az resource update --resource-group "$resource_group" \
    --name "$acr_name" \
    --resource-type "Microsoft.ContainerRegistry/registries" \
    --api-version "2021-06-01-preview" \
    --set "properties.policies.exportPolicy.status=$network_access" \
    --set "properties.publicNetworkAccess=$network_access"