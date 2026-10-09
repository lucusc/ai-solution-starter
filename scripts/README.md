# Scripts

This directory contains generic authentication, environment, network-access,
validation, and deployment helpers.

Scripts must not contain customer identifiers, environment-specific values, or
references to private source repositories.

Key commands:

- `./scripts/allow_my_ip_address.sh`: allow the current developer through
  supported resource firewalls and assign required data-plane roles
- `./scripts/deploy_app.sh`: deploy backend and Logic App packages when their
  implementation phase is complete and Azure deployment is approved
- `./scripts/generate_sample_pdf.py`: generate a deterministic synthetic PDF
- `./scripts/probe_container.sh`: start and probe the combined production image
- `./scripts/validate.sh`: run application, infrastructure, repository, or all
  local validation
- `./scripts/validate_repository.py`: validate documentation links and tracked
  artifact policy
- `./scripts/verify_bicep_baseline.sh`: verify immutable Bicep checksums
