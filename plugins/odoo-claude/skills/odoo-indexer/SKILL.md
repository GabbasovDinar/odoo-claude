---
name: odoo-indexer
description: Build and query a local SQLite static index of Odoo source trees. Use before broad code reading when locating models, inherited models, fields, methods, XML IDs/references, routes, JavaScript classes, OWL templates, registry entries, module manifests, and dependencies; use it to reduce context usage and validate names against local source.
---

# Odoo Indexer

Use the bundled indexer as a fast discovery layer over local source. It is navigation evidence, not runtime database truth.

## Commands

```bash
odoo-index --root /path/to/source --full
odoo-index --root /path/to/odoo --root /path/to/enterprise --root ./custom-addons
odoo-search model sale.order
odoo-search field partner_id --parent sale.order
odoo-search method action_confirm --parent sale.order
odoo-search xmlid sale.view_order_form
odoo-search ref base.group_user
odoo-search model 'sale.%'
odoo-index-status
```

Use `%` as the explicit wildcard. Underscores in Odoo identifiers are treated literally.

## Root discovery

Prefer explicit `--root` values. Without them, inspect `ODOO_PATH`, `ODOO_SOURCE`, `ODOO_SOURCE_16`, `ODOO_SOURCE_18`, common Doodba roots when present, then current directory as a last resort.

## Workflow

1. Build or refresh the index before broad source exploration.
2. Query exact symbols first.
3. Open the returned file/line and verify implementation.
4. For version-sensitive behavior, inspect the exact framework branch too.
5. Re-index incrementally after changes; use `--full` after major source-layout/branch changes.

The indexer must never modify Odoo source files; it only writes its SQLite database.
