# Cost

A deployment costs money while it exists, even when nobody uses it. Delete
environments you don't need. See [Clean up](../how-to/clean-up.md).

Prices depend on region, currency and agreement, so this page doesn't give a
total. Use it to work out what to put into the
[Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/).

## What you pay for with the defaults

**Always-on charges**, billed by the hour whether or not the app is used:

| Resource | Default | Setting to change it |
| --- | --- | --- |
| App Service plan (web app) | B1, 1 instance | `AZURE_APP_SERVICE_SKU` |
| Logic Apps Standard plan | WS1 | `AZURE_LOGIC_APP_SERVICE_SKU` |
| Container Registry | Premium (needed for private endpoints) | Not configurable |
| Private endpoints | About 16 in the default private setup | `AZURE_USE_PRIVATE_ENDPOINT` |
| Private DNS zones | One per service type | `USE_EXISTING_PRIVATE_DNS_ZONES`, `SKIP_PRIVATE_DNS_ZONES` |

**Usage-based charges**, which grow with the number of documents:

| Resource | Default | Billed on | Setting |
| --- | --- | --- | --- |
| Foundry model | `gpt-4o`, Standard deployment, capacity 30 | Input and output tokens. Each PDF is sent in full. | `AZURE_FOUNDRY_MODEL_*` |
| Cosmos DB | Serverless | Request units and storage | `AZURE_COSMOSDB_SKU` |
| Storage | Standard LRS | Capacity and operations | `AZURE_STORAGE_SKU` |
| Application Insights and Log Analytics | On | Data ingested and retained | `AZURE_USE_APPLICATION_INSIGHTS` |
| Document Intelligence | Off (`none`) | Pages analyzed, when you turn it on | `USE_DOCUMENT_INTELLIGENCE` |
| Standalone Azure OpenAI | Off (`none`) | Tokens, when you turn it on | `USE_OPENAI` |

Setting a service to `existing` avoids creating it. The owner of the existing
account still pays for its usage.

Exact setting names are in the [configuration reference](../reference/configuration.md).

## Estimate your cost

1. Open the Azure Pricing Calculator, and choose your region and currency.
2. Add each always-on resource with the same SKU as your configuration.
3. Multiply by the number of environments, such as dev, test and prod.
4. Estimate your monthly PDF volume and average size. Then estimate model tokens.
5. Add Cosmos DB, Storage and monitoring based on that volume.

## Ways to reduce cost

- Delete temporary environments as soon as you're done with them.
- Share one environment among a team instead of one per person.
- Reuse central private DNS zones instead of creating new ones.
- Reuse an existing Foundry account. See
  [Bring your own AI services](../quickstarts/bring-your-own-ai.md).

Changing SKUs that the template doesn't expose as settings, such as the
registry tier, requires an infrastructure change. See
[infrastructure change control](../contributing/infra-change-control.md).
