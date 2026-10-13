#!/usr/bin/env bash
set -euo pipefail

resource_group="${1:?Usage: deploy.sh <resource-group> <logic-app-name>}"
logic_app_name="${2:?Usage: deploy.sh <resource-group> <logic-app-name>}"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
package_dir="$repo_root/app/agent/workflows"
storage_account="$(azd env get-value AZURE_STORAGE_ACCOUNT)"
instructions_container="$(azd env get-value AZURE_STORAGE_INSTRUCTIONS_CONTAINER)"
system_file="$(azd env get-value AZURE_STORAGE_SYSTEM_INSTRUCTIONS_FILE)"
processing_file="$(azd env get-value AZURE_STORAGE_PROCESSING_INSTRUCTIONS_FILE)"

test -n "$storage_account"
test -n "$instructions_container"
test -n "$system_file"
test -n "$processing_file"

az storage blob upload \
  --auth-mode login \
  --account-name "$storage_account" \
  --container-name "$instructions_container" \
  --name "$system_file" \
  --file "$repo_root/app/agent/instructions/system.md" \
  --content-type "text/markdown" \
  --overwrite true \
  --only-show-errors
az storage blob upload \
  --auth-mode login \
  --account-name "$storage_account" \
  --container-name "$instructions_container" \
  --name "$processing_file" \
  --file "$repo_root/app/agent/instructions/processing.md" \
  --content-type "text/markdown" \
  --overwrite true \
  --only-show-errors

stage="$(mktemp -d)"
archive="$(mktemp --suffix=.zip)"
cleanup() {
  rm -rf "$stage"
  rm -f "$archive"
}
trap cleanup EXIT

cp -R "$package_dir"/. "$stage"/
cp "$stage/azure.parameters.json" "$stage/parameters.json"
(cd "$stage" && zip -q -r "$archive" . -x "*.git*" "*.DS_Store" "node_modules/*" "dist/*" "*.bak")

az logicapp deployment source config-zip \
  --name "$logic_app_name" \
  --resource-group "$resource_group" \
  --src "$archive"
