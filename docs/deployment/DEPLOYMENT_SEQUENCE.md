# Deployment Sequence

## Local or operator-driven deployment

1. Authenticate with Azure CLI and Azure Developer CLI.
2. Create or select an azd environment.
3. Run the `preprovision` hook:
   - validate optional AI service modes and existing resource kinds
   - determine whether authentication setup is enabled
   - create or update server and client Microsoft Entra applications
   - store generated application IDs and secrets in the azd environment
4. Run `azd provision` using `infra/main.bicep` and
   `infra/main.parameters.json`.
   The deployment conditionally creates or references Foundry and Document
   Intelligence according to their `USE_*` modes.
5. Run the `postprovision` hook:
   - update deployed and local redirect URIs using `BACKEND_URI`
6. Optionally run `scripts/allow_my_ip_address.sh` for restricted local access.
7. Build and validate implemented application packages.
8. **Azure mutation:** run `scripts/deploy_app.sh` only for components whose
   implementation phase is complete and whose target environment is approved.

## GitHub Actions deployment

`.github/workflows/azure-dev.yml` is manually triggered for a GitHub
environment.

1. Authenticate to Azure through GitHub OIDC.
2. Configure azd to use Azure CLI authentication.
3. Run `azd provision --no-prompt`.
4. Export azd outputs.
5. Update GitHub environment variables using the configured management token.
6. If `deploy-application` is selected:
   - package and deploy the Logic App
   - build the frontend
   - build and push the backend container
   - update the backend Web App image

Application deployment must remain disabled for incomplete packages. The Logic
App business workflow is not implemented yet.

## Temporary network access

The deployment actions temporarily allow the GitHub runner IP for protected
deployment endpoints and remove it in `always()` cleanup steps.

## Failure behavior

Provisioning and deployment steps fail the workflow on errors. Authentication
setup can be explicitly bypassed through
`AZURE_BYPASS_AUTHENTICATION_SETUP=true`; it is not silently skipped.

## Cleanup

Resource cleanup is an Azure-mutating operation. Confirm the exact azd
environment and resource groups before deletion. Follow organization retention
and soft-delete requirements for Storage, Key Vault-equivalent secrets, and
other recoverable services. Phase 5 does not execute provisioning or cleanup.

See [deployment configuration](CONFIGURATION.md) and
[troubleshooting](TROUBLESHOOTING.md).
