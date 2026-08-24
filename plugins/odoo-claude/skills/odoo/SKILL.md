---
name: odoo
description: General Odoo addon engineering workflow for Claude Code. Use for Odoo Python/XML/JS work, debugging, architecture changes, models, fields, views, controllers, reports, security, manifests, data files, performance, integrations, or when the correct project context must be established before implementation.
---

# Odoo engineering control plane

Treat the repository and local Odoo source as the source of truth. Do not infer version-specific APIs from memory when local source or project configuration can answer the question.

## Start every non-trivial Odoo task with context discovery

1. Identify the target addon/module and changed area.
2. Detect the Odoo version from, in order of confidence:
   - explicit user requirement;
   - git branch/tag;
   - addon `__manifest__.py` version;
   - project configuration;
   - local Odoo source branch/version files.
3. Inspect project guidance: `CLAUDE.md`, `README*`, `AGENTS.md`, `copier.yml`, `.copier-answers.yml`, `tasks.py`, `pyproject.toml`, pre-commit and CI files.
4. Detect the actual runtime/tooling layer before proposing commands. Compose with the `doodba` skill only when Doodba files/layout are present.
5. Prefer the local indexer before broad file reading when it is available:
   - `odoo-index --root <path>...`
   - `odoo-search model sale.order`
   - `odoo-search field partner_id --parent sale.order`
6. If framework behavior matters, inspect local Odoo source. For 16 to 18 migrations prefer both source trees:
   - `ODOO_SOURCE_16`
   - `ODOO_SOURCE_18`
   - use `ODOO_SOURCE` only as a single-version fallback.

## Route specialized work

- Odoo 18 API or syntax: compose with `odoo-18`.
- Major-version migration: compose with `odoo-migration`.
- Test design or implementation: compose with `odoo-testing`.
- Code review: compose with `odoo-review`.
- OWL/frontend: compose with `odoo-owl`.
- Doodba runtime/setup: compose with `doodba` only when detected.
- Source lookup/indexing: compose with `odoo-indexer`.

## Implementation rules

- Preserve existing module boundaries and project conventions unless the task requires restructuring.
- Read `__manifest__.py` before editing an addon. Keep dependencies, data ordering and assets consistent with actual imports/XML IDs/inheritance.
- Verify `_name`, `_inherit`, field names, method signatures, XML IDs and view anchors against project/upstream source.
- Prefer Odoo ORM APIs over direct SQL. Parameterize SQL and use it only when justified.
- Treat public model methods and controllers as trust boundaries. Validate record access, ownership and inputs.
- Review ACLs, record rules, groups, `sudo()`, domains and multi-company behavior together.
- Avoid per-record searches/writes in unbounded loops. Use recordsets, batching and aggregation APIs.
- Do not add manual commits inside normal business methods.
- Keep external integrations behind narrow seams that tests can mock.
- For stable branches, prefer minimal compatibility fixes over unrelated refactoring.

## Verification

Before claiming completion:

1. Re-read the diff and manifest.
2. Check Python imports and XML references.
3. Check security impact and multi-company behavior.
4. Add or update regression tests for changed behavior.
5. Discover the project's actual test command; do not invent one.
6. Run read-only checks freely when permissions allow.
7. Ask before commands that create/drop/restore databases, install/update modules, start/stop services, mutate production-like data, or perform destructive git operations.

## Response discipline

State assumptions explicitly. When a framework detail is not verified, say so and show what source/file should be checked. Do not disguise guesses as Odoo version facts.
