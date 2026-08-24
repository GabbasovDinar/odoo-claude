---
name: odoo-testing
description: Design, write, review, and run Odoo tests. Use for regression coverage, migration tests, ORM workflows, security/access tests, controllers, reports, mocked integrations, test tags, project-specific test execution, or diagnosing failing Odoo test suites.
---

# Odoo testing

Use the target Odoo source as the authority for available test helpers.

## Choose the test shape

- ORM/business transaction: `TransactionCase` or the repository's target-version base class.
- Shared-transaction behavior: `SingleTransactionCase` only when justified.
- UI/onchange behavior: use the target-version `Form` helper when it represents the real contract.
- HTTP/controller behavior: `HttpCase` or the project's established controller-test pattern.
- External APIs: mock the client/network seam; never depend on live services.

## Coverage priorities

Prioritize happy-path behavior, access denial/allowed cases, multi-company isolation, state/quantity/date/currency edges, integration failures, and a regression for the exact bug or migration incompatibility.

## Security tests

Use realistic users and companies. Prove both allowed access and forbidden enumeration/read/write. For portal/public controllers, test attempts to access another user's records.

## Migration tests

For 16 -> 18 ports, preserve source behavior, update only helpers that changed, separate framework-helper migration from business changes, and add explicit tests around access, computed fields, copy/search semantics, and view-driven behavior.

## Runtime execution

Discover the actual project command before proposing it. If Doodba is detected, compose with `doodba`, inspect `invoke --list`/task help, and prefer a targeted module/test scope first. Do not assume fixed Invoke flags across projects.

## Failure diagnosis

Classify failures before editing code: import/load, schema, fixture, security, XML/view validation, business assertion, external mock, or target-version helper mismatch. Fix the root cause and rerun the smallest failing scope before the full suite.
