# Quick starts

Short, copy-paste guides that get one scenario running. Do
[before you start](before-you-start.md) once, then pick a scenario.

| I want to... | Guide | Time |
| --- | --- | --- |
| Deploy the demo app to Azure from my machine | [Deploy the demo](deploy-demo.md) | ~45 min |
| Deploy with private endpoints, Foundry and Document Intelligence | [Private Foundry + Document Intelligence](deploy-private-foundry-docintel.md) | ~60 min |
| Deploy from GitHub Actions instead of my machine | [Deploy with GitHub Actions](deploy-github-actions.md) | ~60 min |
| Deploy into a VNet my network team already owns | [Deploy into an existing VNet](deploy-existing-vnet.md) | ~60 min |
| Use a Foundry, OpenAI or Document Intelligence resource I already have | [Bring your own AI resources](bring-your-own-ai.md) | ~45 min |
| Create only the Azure resources and bring my own app | [Infrastructure only](infrastructure-only.md) | ~40 min |
| Run the app on my machine against Azure resources | [Develop against Azure](develop-against-azure.md) | ~20 min |
| Try the code with no Azure subscription | [Run tests without Azure](run-tests-without-azure.md) | ~10 min |

Times are rough. Most of the time is spent waiting for Azure to provision.

Every guide uses the same building blocks: an **azd environment** that holds
your settings, `azd provision` to create resources, and
`./scripts/deploy_app.sh` to deploy the code. To understand them, read
[how deployment works](../concepts/how-deployment-works.md).
