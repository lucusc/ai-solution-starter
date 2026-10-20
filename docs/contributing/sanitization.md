# Source sanitization

This repository must not expose proprietary code, customer data, private
repository information or identifying implementation details. You can look
at existing solutions for proven patterns, but never copy their content
straight into this repository or bring in their Git history.

## Reusing an existing pattern

1. Identify the minimum behavior or configuration you need.
2. Copy only the files you need into a temporary folder **outside** this
   repository.
3. Remove all customer data, domain content, names, URLs, tenant and
   subscription details, resource identifiers, comments, documentation,
   examples, generated assets and repository references.
4. Generalize names, configuration, schemas, prompts, sample data and
   deployment assumptions.
5. Review the result for leaked text and for copying more structure than you
   need.
6. Reimplement, or copy only the sanitized result, into this repository.
7. Scan the repository for secrets, identifiers and prohibited terms.
8. Review the complete staged diff before committing.
9. Commit only when the change meets its review criteria.
10. Delete the temporary folder.

## Never commit

- Git history from another solution
- Source repository names, URLs, commit IDs, pull requests or issue references
- Customer or organization names
- Real documents, prompts, records, PDFs, images or database exports
- Tenant, subscription, resource group, service, storage or account identifiers
- Secrets, credentials, tokens, certificates, connection strings or keys
- Environment-specific firewall, DNS, network or identity values
- Domain-specific schemas, terminology, business rules or evaluation criteria
- Comments or documentation that reveal private implementation context
- Generated artifacts copied from another solution

Allowed: generic placeholders such as `<subscription-id>`, synthetic fixtures,
and Azure built-in role or API identifiers needed to explain a public
contract. Label examples clearly. Links to public SDK and Microsoft
documentation are fine. When a scan matches, review it in context rather than
removing every UUID or service name.

## Git safety

- Never add another solution as a Git remote.
- Never use subtree, filter-branch, unrelated-history merges or other history
  imports.
- Never commit the temporary staging folder.
- Before every push, review all commits that aren't on the remote yet.
- If prohibited content is committed, stop and remove it from history before
  pushing. Deleting it in a later commit isn't enough.

## What to record in the pull request

If you consulted existing material, note:

- which behaviors you looked at
- which files you added
- how you generalized them
- which scans and tests you ran
- that no proprietary content or source history was committed
