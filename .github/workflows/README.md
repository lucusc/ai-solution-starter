# Workflows

Workflows:

- `backend-ci.yml`: validate backend, frontend, production container, synthetic
  sample generation, documentation links, tracked-artifact policy, and the
  Bicep checksum baseline
- `infra-validation.yml`: compile Bicep and verify the immutable baseline
- `azure-dev.yml`: manually provision infrastructure and optionally deploy
  implemented application packages
- `assign-rbac.yml`: manually assign one of the supported Azure roles

Deployment uses GitHub OIDC authentication and environment-scoped variables.
Validation workflows do not provision or modify Azure resources.
