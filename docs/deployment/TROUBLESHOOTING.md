# Troubleshooting

## Tool version rejected

**Symptom:** npm, TypeScript, or Python commands fail before tests start.

**Check:** `python3 --version`, `node --version`, and `npm --version`.

**Action:** install Python 3.12 and Node 20.19 or later in the Node 20 line,
then recreate `.venv` and run `npm ci`.

## Backend dependency import fails

**Symptom:** `ModuleNotFoundError` for Quart or an Azure SDK.

**Action:**

```bash
.venv/bin/python -m pip install -r app/backend/requirements-dev.txt
```

Use `.venv/bin/python`, not an unrelated system interpreter.

## Frontend or SPA returns 404

**Symptom:** the backend starts but `/` has no application.

**Action:**

```bash
cd app/frontend
npm ci
npm run build
cd ../..
```

Confirm `app/backend/static/index.html` exists and remains ignored.

## Local backend configuration is missing

**Symptom:** startup reports a required Azure setting.

**Cause:** the production-shaped backend uses real Storage and Cosmos adapters.

**Action:** use mocked tests for no-Azure development, or export values from an
explicitly selected development environment as documented in
[local setup](../development/LOCAL_SETUP.md).

## Azure credential unavailable

**Symptom:** Azure SDK or azd reports no usable credential.

**Diagnostic:** `az account show` and `azd env get-values`.

**Azure mutation:** none for these diagnostic commands.

Authenticate and select the intended nonproduction environment. Never insert a
key into source as a workaround.

## Storage or Cosmos returns 403

**Likely causes:** missing data-plane role, role propagation delay, wrong
identity, or network restrictions.

Review the [RBAC matrix](../infrastructure/RBAC_MATRIX.md), selected identity,
and network mode. Do not enable public access broadly as a shortcut.

## Private endpoint cannot be reached

Verify DNS resolution, VNet access, private DNS links, and the selected mode in
the [networking matrix](../infrastructure/NETWORKING_MATRIX.md). The local
machine may require VPN or an approved temporary restricted-public path.

## Bicep checksum verification fails

**Symptom:** `verify_bicep_baseline.sh` reports a mismatch.

Stop. Do not update the checksum manifest. Inspect the Bicep diff and request
infrastructure review.

## Logic App package is missing

The Logic App business workflow is Phase 4 work and is not implemented. The
infrastructure resource can exist without the starter processing package.

## Logic Apps Standard capacity is unavailable

Regional capacity can prevent plan creation even when the template is valid.
Check approved alternate regions and organization constraints. Do not change
the infrastructure baseline during Phase 5.

## Work item remains queued or processing

Until Phase 4 is implemented, queued records are expected to remain queued.
After Phase 4, use its workflow run history and safe correlation ID guidance;
do not expose document or prompt content in diagnostics.

## Azure OpenAI deployment fails

Check regional model availability, quota, model version, SKU, and approved
existing-account configuration. Capacity and quota are external constraints,
not reasons to commit credentials or silently select another model.

## Repository validation fails

Run:

```bash
.venv/bin/python scripts/validate_repository.py
```

Remove generated, environment, or cache files from tracking and correct broken
relative links. Do not delete evidence from Git history without explicit
history-remediation review.
