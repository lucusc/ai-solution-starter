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

Microsoft Foundry and Azure AI Document Intelligence are additive conditional
modules under `modules/ai/`; both default to `none`. Azure AI Search remains
deferred. See
[`AI_SERVICES.md`](../docs/infrastructure/AI_SERVICES.md).
