# odoo-claude plugin

Claude Code plugin for Odoo addon engineering and migrations across conventional, OCA, Docker-based, and Doodba source layouts.

## Design rules

- Use the local codebase and exact target-version Odoo source as primary technical evidence.
- For 16 -> 18 migrations, analyze 16 -> 17 and 17 -> 18 separately.
- Use `odoo-index` and `odoo-search` to locate symbols before opening broad source trees.
- Discover project-specific runtime and test commands instead of assuming a fixed command surface.
- When Doodba is detected, compose with the optional `doodba` skill for Invoke-specific discovery.
- Keep migration compatibility fixes separate from opportunistic refactors.
- Add or update tests for migrated behavior.
- Do not mutate databases, install/update Odoo modules, start/stop services, or use destructive Git commands without explicit user intent.
