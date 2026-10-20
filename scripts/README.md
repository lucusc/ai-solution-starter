# Scripts

Deployment hooks, deploy and access scripts, and local checks. Run them from
the repository root.

The most common ones:

| Command | What it does |
| --- | --- |
| `./scripts/deploy_app.sh all` | **Changes Azure.** Deploys the backend image and the Logic App workflow to the selected azd environment. |
| `./scripts/allow_my_ip_address.sh` | **Changes Azure.** Opens Storage and Cosmos DB to your IP and gives you data roles. |
| `./scripts/validate.sh application\|infrastructure\|repository\|all` | Runs the local checks. Doesn't touch Azure. |
| `./scripts/verify_bicep_baseline.sh` | Checks the protected Bicep files haven't changed. |

See the [scripts reference](../docs/reference/scripts.md) for every script,
and [development](../docs/contributing/development.md) for the checks.

Keep scripts generic: no real environment names, IDs or secrets. Never print
environment dumps, secrets or document text into issues or CI logs.
