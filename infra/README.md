# Infrastructure

This directory contains the reviewed Azure infrastructure baseline.

`main.bicep` is the subscription-scoped entry point and
`main.parameters.json` maps Azure Developer CLI environment values to template
parameters.

Validate the template with:

```bash
az bicep build --file infra/main.bicep --stdout > /dev/null
./scripts/verify_bicep_baseline.sh
```

The baseline must be preserved without refactoring or optimization. See
[`CHANGE_CONTROL.md`](../docs/infrastructure/CHANGE_CONTROL.md).

Microsoft Foundry defaults to `new` and includes the model deployment required
by the demo inference workflow. Standalone Azure OpenAI and Document
Intelligence default to `none`; Azure OpenAI also supports `existing`.
Azure AI Search remains deferred. See
[`AI_SERVICES.md`](../docs/infrastructure/AI_SERVICES.md).
