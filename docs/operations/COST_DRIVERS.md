# Azure cost drivers

Azure prices vary by region, currency, agreement, date, SKU, capacity, and
usage. This document identifies what to estimate; it does not provide a fixed
monthly total.

| Service | Main cost drivers | Configuration starting point |
| --- | --- | --- |
| App Service | plan SKU, instance count, runtime hours | `AZURE_APP_SERVICE*` |
| Logic Apps Standard | hosting plan SKU, instance count, runtime hours | `AZURE_LOGIC_APP_SERVICE*` |
| Container Registry | Premium registry, storage, build and transfer activity | registry parameters and image cadence |
| Cosmos DB | serverless requests or provisioned RU/s, storage, regions | `AZURE_COSMOSDB_SKU`, throughput |
| Storage | capacity, operations, redundancy, transfer | Storage SKU and workload volume |
| Azure OpenAI | model deployment capacity and input/output tokens | model, SKU, capacity, document volume |
| Log Analytics | ingestion and retention | monitoring enablement and telemetry volume |
| Application Insights | telemetry volume and retention | monitoring enablement |
| Private networking | private endpoints and related network services | private-endpoint settings |
| Environment count | duplicated baseline resources and runtime duration | dev/test/prod strategy |

## Estimate with Azure Pricing Calculator

1. Select the intended Azure region and billing currency.
2. Add each enabled service from the table.
3. Match the configured SKU rather than selecting a cheaper proxy.
4. Estimate monthly runtime hours and environment count.
5. Estimate PDF volume, average PDF size, and Azure OpenAI token usage.
6. Estimate Cosmos requests or provisioned throughput.
7. Estimate telemetry ingestion and retention.
8. Include private endpoints and data transfer when enabled.
9. Confirm quotas and regional service/model availability separately.

Use the [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)
and current service pricing pages.

## Temporary environments

Before creating a temporary environment:

- record its owner and intended lifetime;
- obtain cost approval;
- use the exact approved region and SKUs;
- avoid duplicate abandoned environments; and
- schedule cleanup verification.

Resource deletion and soft-delete purging are explicit Azure operations and
must follow organization policy.

## Infrastructure boundary

Do not optimize or rewrite the Bicep baseline for cost during Phase 5. A
cost-driven infrastructure change requires separate review with measured
impact, compatibility analysis, and customer-environment constraints.
