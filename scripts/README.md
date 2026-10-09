# Scripts

This directory contains generic authentication, environment, network-access,
validation, and deployment helpers.

Scripts must not contain customer identifiers, environment-specific values, or
references to private source repositories.

Key commands:

- `./scripts/allow_my_ip_address.sh`: allow the current developer through
  supported resource firewalls and assign required data-plane roles
- `./scripts/deploy_app.sh`: deploy future backend and Logic App packages
- `./scripts/verify_bicep_baseline.sh`: verify immutable Bicep checksums
