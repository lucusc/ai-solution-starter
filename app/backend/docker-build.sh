#!/bin/bash

set -euo pipefail

if [ "$#" -ne 4 ]; then
  echo "Usage: $0 <resource-group> <registry-name> <webapp-name> <image-name>" >&2
  exit 1
fi

resource_group="$1"
registry_name="$2"
webapp_name="$3"
image_name="$4"
image="${registry_name}.azurecr.io/${image_name}:latest"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd "$script_dir/../.." && pwd)"

pushd "$repository_root/app/frontend" >/dev/null
npm ci
npm run build
popd >/dev/null

pushd "$repository_root" >/dev/null
az acr build \
  --registry "$registry_name" \
  --image "${image_name}:latest" \
  app/backend \
  --only-show-errors
popd >/dev/null

az webapp config container set \
  --resource-group "$resource_group" \
  --name "$webapp_name" \
  --container-image-name "$image" \
  --container-registry-url "https://${registry_name}.azurecr.io" \
  --only-show-errors >/dev/null

echo "Deployed $image to $webapp_name."
