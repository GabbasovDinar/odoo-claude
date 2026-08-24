---
name: odoo-migration
description: Migrate Odoo addons between major versions with compatibility-first discipline. Use for custom or OCA addon ports, especially Odoo 16 to 18, migration planning, version-delta analysis, manifest/XML/Python/OWL changes, regression tests, or review of a migration diff.
---

# Odoo addon migration

Migration is compatibility work first. Do not mix it with opportunistic refactoring unless explicitly requested.

## Inputs

Resolve source/target versions, modules, branches, exact framework source trees, existing tests/CI, and project runtime tooling.

For Odoo 16 -> 18, always analyze:

1. 16 -> 17
2. 17 -> 18

## Workflow

1. Baseline source behavior and read manifest/models/security/views/data/controllers/reports/assets/tests.
2. Add characterization/regression tests for high-risk behavior when practical.
3. Inventory Python/ORM, XML/views, security, JS/OWL/assets, reports, hooks, cron/server actions, and manifest changes.
4. Apply 16 -> 17 compatibility changes with a minimal diff.
5. Apply 17 -> 18 compatibility changes with a minimal diff.
6. Verify every framework-sensitive change against local target source.
7. Update tests for target-version helpers and behavior.
8. Discover the project's real install/update/test command from docs/config/tooling.
9. Ask before database/module/service mutations.
10. Re-run regression tests and review the final diff for accidental feature changes.

## 16 -> 17 hotspots

Check `attrs`/`states`, display-name customizations, module-hook signatures, settings views, `active_id`/`active_model` assumptions, OWL/template markers, frontend patches, HTTP calls in tests, and inherited XPath targets.

## 17 -> 18 hotspots

Check list/tree terminology, `_name_search` vs `_search_display_name`, access helpers, `group_operator` vs `aggregator`, `search_fetch`, multi-record copy behavior, chatter/kanban markup, assets, registry imports, and translation helpers.

## OCA vs private modules

Do not force OCA git-history conventions on private repositories. For OCA modules preserve authors/copyright, keep migration-only scope, follow target-branch pre-commit/manifest conventions, and use the established `[MIG]` workflow.

## Safety

Do not run database create/drop/restore, module install/update/uninstall, service lifecycle commands, or destructive git operations without explicit approval.

## Completion criteria

The addon loads on target Odoo, representative tests pass, security remains correct, no source-version-only syntax remains in migrated scope, framework-sensitive changes are traceable to target source/docs, and unrelated refactoring is separated.
