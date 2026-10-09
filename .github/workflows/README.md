# Workflows

Workflows:

- `infra-validation.yml`: compile Bicep and verify the immutable baseline
- `azure-dev.yml`: manually provision infrastructure and optionally deploy
  future application packages
- `assign-rbac.yml`: manually assign one of the supported Azure roles

Deployment uses GitHub OIDC authentication and environment-scoped variables.
