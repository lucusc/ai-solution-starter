# Troubleshoot

Problems are grouped by when they happen. Never paste `azd env get-values`
output, secrets, or document content into issues or logs.

## During `azd provision`

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `validate_ai_service_config` error before anything is created | Wrong `USE_*` value or resource ID | Use lowercase `new`, `existing` or `none`. `existing` needs a full resource ID. Foundry must be kind `AIServices`; Document Intelligence must be `FormRecognizer`. |
| Conflict with `DEPLOY_AZURE_OPENAI`/`OPENAI_HOST` | Legacy settings | Remove them and use `USE_OPENAI`. See [AI services](choose-ai-services-and-models.md#standalone-azure-openai). |
| `InsufficientQuota` or model not available | No quota for the model in that region | Lower `AZURE_FOUNDRY_MODEL_CAPACITY`, change model/SKU, or pick another region |
| Logic Apps plan creation fails | No regional capacity for WS1 | Try another region |
| `AuthorizationFailed` on role assignments | You lack Owner/User Access Administrator | See [before you start](../quickstarts/before-you-start.md#2-check-your-azure-permissions) |
| Auth hook fails with Graph or permission errors | You cannot create app registrations | Ask an admin, or [use existing registrations](configure-authentication.md#use-app-registrations-you-already-have) |
| "No tenant ID set for authentication" | Tenant not known yet | `azd env set AZURE_AUTH_TENANT_ID "$(az account show --query tenantId -o tsv)"` |
| Soft-deleted resource name conflict | An earlier environment with the same name was deleted but not purged | Use `azd down --purge` next time, or purge it in the portal |

## During `./scripts/deploy_app.sh`

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `403` / "not authorized by network rules" on ACR, Storage or the Logic App | Your IP is not allowed or has changed | [Allow your IP](access-a-private-deployment.md#allow-your-ip) and run `azd provision` |
| `403` on Storage right after provisioning | Role assignment still propagating | Wait 5 minutes and retry |
| `mktemp: unrecognized option` | macOS BSD `mktemp` | Use Linux, WSL or a dev container |
| `zip: command not found` | `zip` missing | Install it |
| Frontend build fails | Node.js too old | Use Node.js 20.19 or later |

## When using the app

| Symptom | Check | Fix |
| --- | --- | --- |
| `401` for every request | `AZURE_USE_AUTHENTICATION` was not `true` | Set it and `azd provision`. See [authentication](configure-authentication.md). |
| Sign-in error about redirect URI | Post-provision hook did not run | Run `./scripts/auth_update.sh` |
| `/` returns 404 | Image built without the frontend | Run `./scripts/deploy_app.sh backend` |
| Site shows the default App Service page | App not deployed yet | Run `./scripts/deploy_app.sh backend` |
| `/healthz` works, `/readyz` returns 503 | API cannot reach Storage or Cosmos | Check the web app identity's roles and the private DNS. `/readyz` is cached for 30 s. |
| Upload returns 502/503 | Storage or Cosmos rejected the write | Note the `request_id` in the error and check App Insights. Check the item's status before resubmitting. |
| Item stays **queued** | Workflow not deployed, or it cannot read Blob/Cosmos | Run `./scripts/deploy_app.sh agent`. Check the Logic App run history in the portal. |
| Item stays **processing** | The model call failed or timed out mid-run | Check the run history. There is no automatic recovery; see below. |
| Item **failed** | The workflow recorded an error code | Check the error `code` and the run history. Foundry `403` means the Logic App identity lacks **Cognitive Services OpenAI User** or cannot reach the endpoint. |

### Stuck items

The starter does not automatically retry or reset items. If an item is stuck
in **processing**:

1. Confirm no workflow run is still active for it.
2. Use the request ID, work-item ID and run ID to find the cause.
3. Fix the cause, then upload the file again with a **new** idempotency key.
   Reusing the old key returns the old item.

Do not edit Cosmos records by hand while a workflow run might still write to
them.

## Local development

| Symptom | Fix |
| --- | --- |
| `ModuleNotFoundError` | Install with `.venv/bin/python -m pip install -r app/backend/requirements-dev.txt` and run with `.venv/bin/python` |
| npm rejects the engine | Use Node.js 20.19 or later |
| Startup says a required Azure setting is missing | Create `app/backend/.env`; see [develop against Azure](../quickstarts/develop-against-azure.md) |
| `DefaultAzureCredential` failed | Run `az login` |
| Port 8000 or 5173 in use | Stop the other process |
| `verify_bicep_baseline.sh` mismatch | A protected Bicep file changed. Stop and see [infrastructure change control](../contributing/infra-change-control.md). Do not update the checksum file to make it pass. |

## Still stuck?

- Check Application Insights for the request ID.
- Check the Logic App's **Run history** in the Azure portal.
- See [known limitations](../concepts/known-limitations.md).
