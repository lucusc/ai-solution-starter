# FEAT-06: Optional Azure AI Search

**Type:** Feature · **Area:** Infra · **Priority:** Low · **Status:** Proposed

## Summary

Many document solutions need retrieval (RAG). The starter has no search
service.

## Current behavior

The template offers Foundry, Azure OpenAI and Document Intelligence, each
as `new`, `existing` or `none`. There's no search option.

## Impact

Teams add AI Search by hand, often without private endpoints, RBAC or
diagnostics that match the rest of the template.

## Proposed change

**Infra.** Follow the pattern of the existing optional AI modules:

1. Add `infra/modules/ai/search.bicep` with a private endpoint, private DNS
   zone, managed identity RBAC and diagnostics.
2. Add `USE_AI_SEARCH` (`new`, `existing`, `none`, default `none`) and the
   minimum parameters, module call and outputs to `main.bicep`.
3. Pass the endpoint to the backend and Logic App as app settings.
4. Update the baseline manifest only after approval.

## Acceptance criteria

- [ ] With `USE_AI_SEARCH=none`, the deployed resources are unchanged.
- [ ] With `new`, the search service is private and reachable from the app.
- [ ] `validate_ai_service_config.py` and the configuration reference cover
      the new setting.
