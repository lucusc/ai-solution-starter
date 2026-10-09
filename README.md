# AI Solution Starter

AI Solution Starter is a clean project shell for building reusable,
AI-enabled solutions on Azure. It will provide a replaceable hello-world
application that demonstrates a web frontend, backend API, data persistence,
workflow automation, observability, and Azure AI integration.

The repository currently contains the reviewed infrastructure and deployment
baseline. Application implementation will be delivered in later phases.

## Planned Solution Shape

```text
.
├── app/
│   ├── frontend/       # Web application
│   ├── backend/        # API and service integration
│   └── agent/          # Logic App workflow package
├── infra/              # Azure infrastructure
├── scripts/            # Local development and deployment helpers
├── docs/               # Architecture and implementation guidance
├── tests/              # Cross-component and end-to-end tests
├── .github/workflows/  # Continuous integration and deployment
└── azure.yaml          # Azure Developer CLI project definition
```

## Current Status

Phase 1 establishes the Azure infrastructure, Azure Developer CLI hooks,
deployment scripts, and GitHub Actions. The backend, frontend, and Logic App
business workflow remain placeholders for later phases.

See:

- [Implementation plan](docs/PLAN.md)
- [Phase task backlog](docs/PHASE_TASKS.md)
- [Source sanitization policy](docs/SOURCE_SANITIZATION.md)
- [Infrastructure resource contract](docs/infrastructure/RESOURCE_CONTRACT.md)
- [Deployment sequence](docs/deployment/DEPLOYMENT_SEQUENCE.md)

## Guiding Principles

- Keep the hello-world application small, functional, and easy to replace.
- Demonstrate the complete deployed architecture rather than isolated samples.
- Treat infrastructure compatibility as a requirement, not an optimization
  opportunity.
- Add future AI capabilities without destabilizing the base deployment.
- Never commit proprietary source material, source history, customer data, or
  unsanitized copied content.
