# Application flow

## Implemented intake flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Cosmos
    participant Blob

    User->>Frontend: Select PDF and submit
    Frontend->>Backend: POST /api/v1/work-items
    Backend->>Backend: Authenticate and validate PDF
    Backend->>Cosmos: Create submitted work item
    Backend->>Blob: Upload work-items/<id>/source.pdf
    Backend->>Cosmos: Replace status with queued
    Backend-->>Frontend: Public work-item response
```

The API accepts PDFs only, up to 20 MB. A required idempotency key prevents an
ambiguous client retry from creating another work item.

## Document processing flow

The Phase 4 Logic Apps Standard package, implemented as Phase 7's final step,
processes eligible PDFs:

```text
queued
  -> Logic App claims processing with Cosmos ETag
  -> reads PDF and generic instructions
  -> calls the configured Foundry model with managed identity
  -> validates summary, category, and key_points
  -> persists completed or failed
```

The Foundry inference endpoint and deployment are emitted by infrastructure;
standalone Azure OpenAI is not required. Azure execution remains a separate
approval and validation gate. See the
[Phase 4 plan](../phases/PHASE_4_IMPLEMENTATION_PLAN.md) and
[Phase 7 plan](../phases/PHASE_7_IMPLEMENTATION_PLAN.md).

## Read flow

The frontend lists owner-scoped records and loads one detail route. It polls
only an open nonterminal detail view. Polling stops on `completed`, `failed`,
authorization failure, not-found, navigation, or page cleanup.

## Lifecycle ownership

| Transition | Owner |
| --- | --- |
| create `submitted` | Backend |
| `submitted -> queued` | Backend |
| `submitted -> failed` | Backend intake compensation |
| `queued -> processing` | Logic App |
| `processing -> completed` | Logic App |
| `processing -> failed` | Logic App |

Completed and failed records are terminal.
