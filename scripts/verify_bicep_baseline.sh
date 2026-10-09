#!/bin/bash

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
manifest="$repo_root/infra/bicep-baseline.sha256"

if [ ! -f "$manifest" ]; then
  echo "Missing Bicep baseline manifest: $manifest" >&2
  exit 1
fi

cd "$repo_root"
sha256sum --check "$manifest"
