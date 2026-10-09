# Contributing

Thank you for improving AI Solution Starter.

## Before contributing

1. Read the [Code of Conduct](CODE_OF_CONDUCT.md).
2. Follow the [local setup](docs/development/LOCAL_SETUP.md).
3. Review the [source sanitization policy](docs/SOURCE_SANITIZATION.md).
4. Keep changes focused and update directly related documentation and tests.

## Non-negotiable repository rules

- Do not modify, optimize, reorganize, or simplify the Bicep baseline without
  explicit infrastructure review.
- Do not commit real documents, credentials, Azure identifiers, customer data,
  private URLs, private repository references, or proprietary prompts.
- Do not import source history from another solution.
- Do not commit generated frontend assets, generated PDFs, caches, `.azure/`,
  virtual environments, or `node_modules/`.
- Keep authentication and authorization decisions on the backend.
- Update backend, workflow, frontend, fixtures, and documentation together
  when changing a shared contract.

## Validation

Set up dependencies, then run:

```bash
./scripts/validate.sh all
```

If a change affects only one area, the matching mode may be used during
development, but the complete implemented-component validation is expected
before review.

## Pull requests

Include:

- the problem and intended behavior;
- files and contracts changed;
- validation commands and results;
- Azure resource impact, if any;
- confirmation that Bicep remains unchanged unless separately approved; and
- confirmation that no proprietary or sensitive material is included.

Do not include real production logs or documents in issues or pull requests.
