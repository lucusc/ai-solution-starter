# Before you start

Every deployment quick start assumes you have done this page once. It takes
about 15 minutes.

## 1. Install the tools

| Tool | Why you need it | Check |
| --- | --- | --- |
| [Git](https://git-scm.com/downloads) | Clone the repository | `git --version` |
| [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) | Sign in, build and push the container image | `az version` |
| [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) | Create the Azure resources | `azd version` |
| [Python 3.12](https://www.python.org/downloads/) | Runs the setup hooks | `python3 --version` |
| [Node.js 20.19+](https://nodejs.org/) | Builds the web frontend | `node --version` |
| `zip` | Packages the Logic App workflow | `zip -v` |

Use Bash (Linux, macOS, or WSL on Windows). The deployment scripts use
GNU `mktemp`; on macOS install GNU coreutils or use WSL/a dev container.
Docker is **not** required to deploy; the image is built in Azure.

## 2. Check your Azure permissions

You need, in the target subscription:

- **Owner**, or **Contributor** plus **User Access Administrator**. The
  template assigns roles to the app's managed identities.
- Permission to **create app registrations** in Microsoft Entra ID. This
  is used for the sign-in page. Ask your tenant admin if you are unsure.
- **Quota** for the default model (`gpt-4o`, Standard, 30K tokens per minute)
  and for a Logic Apps Standard (WS1) plan in your chosen region.

## 3. Sign in

```bash
az login
azd auth login
```

If you have several subscriptions, select one:

```bash
az account set --subscription "<subscription-name-or-id>"
```

## 4. Get the code

```bash
git clone https://github.com/lucusc/ai-solution-starter.git
cd ai-solution-starter
```

All commands in the quick starts run from this folder.

## 5. Pick a region

Choose a region that offers Logic Apps Standard and the `gpt-4o` model
(for example `eastus2` or `swedencentral`). See
[model availability](https://learn.microsoft.com/azure/ai-foundry/openai/concepts/models)
if you plan to change the model.

## 6. Understand the cost

A deployment runs billable resources around the clock until you delete it:
an App Service plan, a Logic Apps Standard plan, a Premium container
registry, private endpoints, and model usage. See [cost](../concepts/cost.md)
and remember to [clean up](../how-to/clean-up.md) when you are done.

## Next

Pick a scenario from the [quick starts](README.md).
