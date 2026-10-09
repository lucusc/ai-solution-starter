# Prerequisites

## Local validation

| Tool | Supported baseline | Verify |
| --- | --- | --- |
| Git | Current supported version | `git --version` |
| Python | 3.12 | `python3 --version` |
| Node.js | 20.19 or later in Node 20 | `node --version` |
| npm | Compatible with Node 20 and the lockfile | `npm --version` |
| Docker | Current supported engine | `docker version` |
| Azure CLI | Current version with Bicep | `az version` |

Azure CLI is used only to compile Bicep during local infrastructure validation.
No login or subscription is required for that operation.

## Azure deployment

Deployment additionally requires:

- Azure Developer CLI: `azd version`
- Azure CLI authentication: `az login`
- access to an Azure subscription
- permission to create or use the configured resource groups
- permission to create role assignments when `ASSIGN_ROLES=true`
- permission to manage Microsoft Entra application registrations unless
  authentication setup is explicitly bypassed
- regional quota and capacity for the configured services and models

Review the [RBAC matrix](../infrastructure/RBAC_MATRIX.md),
[networking matrix](../infrastructure/NETWORKING_MATRIX.md), and
[parameter catalog](../infrastructure/PARAMETER_CATALOG.md).

## Shell support

- POSIX setup and validation examples use Bash.
- Windows authentication and environment helpers include PowerShell variants.
- Commands using `.venv/bin/python` should use the Windows virtual-environment
  Python path when run from PowerShell.

## Not required for local validation

- Azure credentials
- an azd environment
- deployed Azure resources
- real documents
- prebuilt frontend assets
- globally installed Python packages
