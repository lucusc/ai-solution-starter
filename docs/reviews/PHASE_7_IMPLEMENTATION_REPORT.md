# Phase 7 Implementation Report

## Status

Local implementation is complete for review. The phase is not marked fully
accepted: resource-graph review, baseline-manifest approval, and live Azure
validation remain outstanding. No Azure deployment, checksum-manifest update,
commit, or push was performed.

## Delivered

- Added independent `USE_OPENAI=new|existing|none` handling and made fresh
  defaults Foundry `new`, standalone OpenAI `none`, and Document Intelligence
  `none`.
- Added Foundry model deployment parameters, existing-model opt-in, inference
  app settings, and managed-identity role assignment.
- Extended configuration validation for defaults, legacy conflicts, resource
  ID shape, dependent actions, existing resource kinds, and Foundry model
  presence.
- Updated deployment workflow inputs, parameter catalog, operator guidance,
  replacement documentation, and the Foundry-first application flow.
- Implemented the Phase 4 Foundry workflow package as Phase 7's final
  implementation step. See
  [the Phase 4 report](PHASE_4_IMPLEMENTATION_REPORT.md).

## Local validation

- All Python backend and workflow tests passed: 82 tests.
- Ruff lint and formatting checks passed for the changed Python validation,
  backend, and workflow-test files.
- `python scripts/verify_logic_app_package.py` passed.
- `python scripts/validate_ai_service_config.py` passed.
- `az bicep build --file infra/main.bicep --stdout` compiled successfully.
- Modified JSON configuration files parsed successfully.
- Shell syntax and `git diff --check` passed.

## Outstanding review gates

- Compare the exact resource graph for default, all-none, OpenAI-new, and
  OpenAI-existing parameter sets against the approved pre-change baseline.
- Review the focused Bicep resource diff and decide whether to update
  `infra/bicep-baseline.sha256`. It has intentionally not been refreshed.
- Validate workflow definition and connector behavior in the Logic Apps
  Standard runtime, including managed identity, Cosmos ETags, Foundry PDF
  inference, and the 20 MB payload boundary.
- Obtain separate approval before any Azure deployment or live smoke test.

Local compilation and mocked/static tests do not substitute for these
infrastructure and deployment checks.
