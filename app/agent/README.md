# Document workflow

`workflows/` is a Logic Apps Standard stateful workflow package. The Blob
trigger correlates input PDFs with Cosmos work items, claims queued records
using Cosmos ETags, loads replaceable instructions from the instructions
container, calls the configured Microsoft Foundry Responses API deployment,
and validates the structured result before completion.

The workflow uses only managed identities. The built-in Blob connector uses
the Logic App's system-assigned identity; Cosmos and Foundry HTTP requests use
the existing user-assigned identity. It has no standalone Azure OpenAI
endpoint, key, account, or fallback. Work-item processing requires
`AZURE_FOUNDRY_INFERENCE_ENDPOINT` and `AZURE_FOUNDRY_DEPLOYMENT_NAME`.
`connections.json` uses the built-in Blob service provider. Both identities
must have the corresponding data-plane permissions in the deployed environment.

## Instructions and deployment

Use [scripts](../../docs/reference/scripts.md) for packaging tools and
[access a private deployment](../../docs/how-to/access-a-private-deployment.md)
for identity and network access. The command below changes Azure
Blob content and the deployed workflow; it is not a local validation command.

Replace `instructions/system.md` and `instructions/processing.md` with
application-specific, reviewed prompt assets. Do not place customer documents,
credentials, or environment-specific data in these files. Deployment uploads
them with Azure CLI Entra authentication before deploying the workflow:

```bash
./app/agent/deploy.sh <resource-group> <logic-app-name>
```

The deployment command reads storage/container/blob settings from the selected
azd environment. The caller needs both Blob data-plane write permission and
network access to the storage account and Logic App SCM endpoint. Packaging
uses a temporary staging directory and does not rename or overwrite local
parameter files.

## Local checks

```bash
python scripts/verify_logic_app_package.py
python -m pytest app/agent/tests -q
```

`parameters.json` contains synthetic local values. `azure.parameters.json`
resolves all environment-specific values from the existing Logic App app
settings. Local package validation does not deploy resources or prove live
Foundry/model compatibility, regional capacity, network reachability, or the
effective maximum PDF request size; those require separately approved Azure
validation.

## Replacement boundary

Keep path correlation, the `submitted -> queued` readiness window, ETag claim
and terminal writes, managed identity, strict result schema, and failure
handling when replacing the model or instruction assets. The workflow does
not recover indefinitely stale `processing` work items; diagnose these using
Logic App run correlation and the Cosmos work-item version/status.
