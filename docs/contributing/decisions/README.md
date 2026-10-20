# Architecture decisions

Record significant decisions here as architecture decision records (ADRs).
There are none yet. Current behavior is described in
[architecture](../../concepts/architecture.md).

## When to write one

Write an ADR when the alternatives and their consequences matter for future
maintenance. For example: changing how data is partitioned, identity
boundaries, the AI provider, or who owns deployment. Small fixes don't need
one. An ADR doesn't replace
[infrastructure change control](../infra-change-control.md).

For a proposed feature or bug fix that isn't decided yet, use
[planning](../../planning/README.md) instead.

## Format

Name the file with a number and a short title, for example
`0001-use-cosmos-db-for-work-items.md`. Include:

1. Title, status (`proposed`, `accepted`, `rejected` or `superseded`), date
   and decision owner.
2. Context and requirements.
3. Options considered, with tradeoffs.
4. Decision and why.
5. Consequences: migration, compatibility and rollback.
6. How it was validated, and what's still uncertain.

Don't backdate decisions or label existing code as an accepted decision after
the fact. Keep the how-to and reference docs describing current behavior;
they shouldn't depend on reading ADRs.
