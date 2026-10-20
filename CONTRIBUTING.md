# Contributing

Thanks for improving AI Solution Starter.

## Before you start

1. Set up your machine with [development](docs/contributing/development.md).
2. Read [source sanitization](docs/contributing/sanitization.md).
3. Keep changes focused, and update the related tests and docs in the same
   pull request.

## Rules

- Don't change the Bicep baseline without approval. See
  [infrastructure change control](docs/contributing/infra-change-control.md).
- Don't commit real documents, credentials, Azure IDs, customer data,
  private URLs, private repository references or proprietary prompts.
- Don't import history from another repository.
- Don't commit build output, generated PDFs, caches, `.azure/`, virtual
  environments or `node_modules/`.
- Keep authentication and authorization decisions in the backend.
- When you change a shared contract, update the backend, workflow, frontend,
  fixtures and docs together.

## Checks

Run the checks that cover your change (see
[development](docs/contributing/development.md#run-the-checks)). For changes
across components, run everything:

```bash
./scripts/validate.sh all
```

Documentation-only changes don't need any checks.

## Writing documentation

Put each page in the section that matches its reader. See the
[documentation hub](docs/README.md).

| Section | Contains |
| --- | --- |
| `docs/quickstarts/` | One scenario from start to finish, for someone new to Azure |
| `docs/how-to/` | One task on an existing deployment |
| `docs/concepts/` | How and why things work |
| `docs/reference/` | Exact settings, resources, API and scripts |
| `docs/contributing/` | Rules and setup for contributors |
| `docs/planning/` | Proposed features and bug fixes, not current behavior |

Style:

1. Write for the reader of that section. Quick starts assume no Azure or IaC
   knowledge; reference pages can be terse.
2. Lead with what the reader will get, then the steps.
3. Use short sentences, second person ("you") and plain words. Explain an
   Azure term the first time a quick start uses it.
4. Give copy-paste commands in fenced blocks with a language, and use
   placeholders like `<resource-group>`, never real values.
5. Mark commands that change Azure.
6. Say how to check that a step worked.
7. Keep one home for each fact. Settings live in
   [configuration](docs/reference/configuration.md); link to it rather than
   copying tables.
8. Describe current behavior only. Put proposed changes in
   [planning](docs/planning/README.md), and workarounds in
   [known limitations](docs/concepts/known-limitations.md).
9. Say what hasn't been tested in Azure.
10. Use relative links and sentence-case headings. Check that links still
    work when you rename or move a page.

## Pull requests

Include:

- the problem and the intended behavior;
- the files and contracts you changed;
- the checks you ran and their results;
- any Azure resource impact;
- confirmation that the Bicep is unchanged, unless approved; and
- confirmation that nothing proprietary or sensitive is included.

Don't paste real production logs or documents into issues or pull requests.
