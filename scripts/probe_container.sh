#!/bin/bash

set -euo pipefail

image="${1:-ai-solution-starter:validation}"
container="ai-solution-starter-probe-$$"

cleanup() {
  docker rm -f "$container" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker run -d \
  --name "$container" \
  -P \
  -e AZURE_STORAGE_ACCOUNT=localvalidation \
  -e AZURE_STORAGE_CONTAINER=inputs \
  -e AZURE_COSMOSDB_ACCOUNT=localvalidation \
  -e AZURE_COSMOSDB_DATABASE=starter \
  -e AZURE_COSMOSDB_CONTAINER=inputs \
  -e LOCAL_AUTH_SUBJECT=local-validation \
  "$image" >/dev/null

port=$(docker port "$container" 8000/tcp | head -1 | sed -E 's/.*:([0-9]+)$/\1/')
if [ -z "$port" ]; then
  echo "Could not determine the container port." >&2
  exit 1
fi

for _ in $(seq 1 30); do
  if curl --fail --silent "http://127.0.0.1:${port}/healthz" >/dev/null; then
    curl --fail --silent "http://127.0.0.1:${port}/" | grep -q "<div id=\"root\"></div>"
    echo "Container probe passed on port ${port}."
    exit 0
  fi
  sleep 1
done

docker logs "$container" >&2
echo "Container did not become healthy." >&2
exit 1
