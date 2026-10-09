# AI Solution Starter

AI Solution Starter is a clean project shell for building reusable,
AI-enabled solutions on Azure. It will provide a replaceable hello-world
application that demonstrates a web frontend, backend API, data persistence,
workflow automation, observability, and Azure AI integration.

The repository contains the reviewed infrastructure and deployment baseline,
the generic Quart backend, and the React hello-world frontend. The Logic App
business workflow and Azure AI processing behavior remain later-phase work.

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

Phase 3 adds the replaceable frontend flow for authenticated PDF submission,
owner-scoped work-item lists, routed details, lifecycle polling, and safe AI
result presentation. Phase 4 will implement the Logic App business workflow.

See:

- [Implementation plan](docs/PLAN.md)
- [Phase task backlog](docs/PHASE_TASKS.md)
- [Source sanitization policy](docs/SOURCE_SANITIZATION.md)
- [Phase 3 implementation plan](docs/phases/PHASE_3_IMPLEMENTATION_PLAN.md)
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
