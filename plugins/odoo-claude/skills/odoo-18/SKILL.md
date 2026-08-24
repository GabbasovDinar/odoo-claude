---
name: odoo-18
description: Odoo 18-specific engineering and migration reference. Use when implementing or reviewing Odoo 18 addons, porting code from Odoo 16/17 to 18, resolving ORM/view/security API changes, or validating whether older Odoo patterns remain valid in 18.0.
---

# Odoo 18 reference

Use this as a checklist, then verify sensitive behavior against the project's exact Odoo 18 source tree.

## Views

- Use `<list>` for list-view roots in Odoo 18; do not rename XML IDs merely because they contain `tree`.
- Odoo 17+ modifiers use Python expressions directly in `invisible`, `readonly`, and `required`; do not restore legacy `attrs`/`states`.
- Use `column_invisible` when hiding a whole list column.
- Validate inherited XPath anchors against the actual Odoo 18 parent view.

## ORM and access

Verify upstream signatures before changing overrides. High-value migration checks include:

- `_search_display_name` for display-name searching;
- `check_access`, `has_access`, and `_filtered_access` for access APIs;
- `aggregator` instead of old `group_operator` metadata;
- `search_fetch` when the extension point is result fetching rather than search-domain construction;
- multi-record behavior of `copy` and `copy_data`.

## Security

- Treat public RPC methods and controller parameters as untrusted.
- Do not use `sudo()` as a generic access-error fix.
- Re-check portal/public controller auth, ownership, CSRF, and input validation.
- Re-test record rules under realistic allowed-company combinations.

## JavaScript and OWL

- Verify registry/service/component imports against Odoo 18 source.
- Keep templates in the correct asset bundle.
- Do not add obsolete `owl="1"` markers.
- Validate inherited QWeb/OWL selectors against target source.

## Migration sequence

For 16 -> 18, apply compatibility changes in order: 16 -> 17, then 17 -> 18. Do not skip intermediate removals.

## Source-of-truth rule

When this checklist conflicts with local Odoo 18 code, follow local source and record the upstream file/method inspected.
