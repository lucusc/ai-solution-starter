#!/bin/bash

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
mode="${1:-all}"
python_bin="$repo_root/.venv/bin/python"

usage() {
  echo "Usage: $0 [application|infrastructure|repository|all]" >&2
}

validate_application() {
  if [ ! -x "$python_bin" ]; then
    echo "Missing .venv. Follow docs/development/LOCAL_SETUP.md first." >&2
    exit 1
  fi

  pushd "$repo_root/app/frontend" >/dev/null
  npm ci
  npm run lint
  npm run typecheck
  npm test -- --run
  npm run build
  popd >/dev/null

  "$python_bin" -m pytest
  "$python_bin" -m ruff check \
    app/backend \
    scripts/generate_sample_pdf.py \
    scripts/smoke_backend_azure.py \
    scripts/validate_ai_service_config.py \
    scripts/validate_repository.py
  "$python_bin" -m ruff format --check \
    app/backend \
    scripts/generate_sample_pdf.py \
    scripts/smoke_backend_azure.py \
    scripts/validate_ai_service_config.py \
    scripts/validate_repository.py
  "$python_bin" -m mypy app/backend/backend
  docker build \
    -f "$repo_root/app/backend/Dockerfile" \
    -t ai-solution-starter:validation \
    "$repo_root/app/backend"
  "$repo_root/scripts/probe_container.sh" ai-solution-starter:validation
}

validate_infrastructure() {
  python3 "$repo_root/scripts/validate_ai_service_config.py"
  az bicep build --file "$repo_root/infra/modules/ai/foundry.bicep" --stdout >/dev/null
  az bicep build --file "$repo_root/infra/modules/ai/document-intelligence.bicep" --stdout >/dev/null
  az bicep build --file "$repo_root/infra/main.bicep" --stdout >/dev/null
  "$repo_root/scripts/verify_bicep_baseline.sh"
  bash -n "$repo_root"/scripts/*.sh
}

validate_repository() {
  if [ ! -x "$python_bin" ]; then
    echo "Missing .venv. Follow docs/development/LOCAL_SETUP.md first." >&2
    exit 1
  fi
  "$python_bin" "$repo_root/scripts/validate_repository.py"
  "$python_bin" "$repo_root/scripts/generate_sample_pdf.py" \
    "$repo_root/tests/sample-data/generated/hello-world.pdf" \
    --overwrite
  git -C "$repo_root" diff --check
}

case "$mode" in
  application)
    validate_application
    ;;
  infrastructure)
    validate_infrastructure
    ;;
  repository)
    validate_repository
    ;;
  all)
    validate_application
    validate_infrastructure
    validate_repository
    ;;
  *)
    usage
    exit 2
    ;;
esac
