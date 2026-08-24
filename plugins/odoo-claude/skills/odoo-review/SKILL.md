---
name: odoo-review
description: Review Odoo addon code and migration diffs for correctness, security, performance, compatibility, tests, XML/data ordering, manifests, controllers, reports, OWL/assets, and multi-company risks. Use for PR reviews, changed files, pre-merge checks, or validating an Odoo 16 to 18 port.
---

# Odoo code review

Findings come first. Bugs, security regressions, migration hazards, and missing tests outrank style comments.

## Establish scope

Identify Odoo version, addon/module, diff/commit/PR range, stable vs development branch, project conventions/CI, and local framework source availability.

## Review checklist

### Models and ORM

- correct `_name`, `_inherit`, `_inherits`, and method signatures;
- multi-record-safe CRUD/compute/copy behavior;
- no unbounded ORM calls inside loops;
- complete compute dependencies;
- correct relational `ondelete`/inverse behavior;
- parameterized, justified direct SQL;
- no manual commit in normal business flow.

### XML/data/manifest

- target-version-valid view syntax and existing XPath anchors;
- valid XML IDs and safe data load order;
- manifest dependencies match imports/inheritance/XML refs/assets;
- production/demo/noupdate data are intentionally separated.

### Security

- ACLs and record rules match realistic users/companies;
- `sudo()` is an explicit trust-boundary decision;
- public methods validate untrusted input/recordsets;
- portal/public routes validate auth, ownership, CSRF, and parameters.

### Performance/concurrency

- avoid N+1 search/write patterns;
- use target-version batching/aggregation APIs;
- inspect race-prone state transitions and uniqueness assumptions.

### Tests

- regression covers changed behavior;
- access tests use non-admin users;
- external services are mocked;
- migration tests prove behavior, not just installability.

## Migration review

For 16 -> 18, verify both 16 -> 17 and 17 -> 18 deltas. Flag compatibility changes mixed with unrelated refactoring.

## Output

Return findings by severity with exact file/line references, then checks run, residual risks, and a concise summary. If there are no findings, state exactly what was and was not verified.
