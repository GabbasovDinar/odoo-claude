# Odoo Claude Code Toolkit

A focused Claude Code marketplace for Odoo engineering: addon development, version-aware migrations, testing, code review, OWL/frontend work, and fast local source navigation.

The repository combines selected ideas from two upstream approaches without bundling overlapping Odoo knowledge packs:

- version-aware Odoo development, migration, testing, review, and OWL workflows;
- optional Doodba project discovery when a repository actually uses Doodba;
- an independent local SQLite source indexer for fast symbol lookup.

Doodba is supported as an optional environment adapter, not as the primary product focus. Conventional Odoo repositories, custom addon repositories, OCA repositories, Docker-based projects, and other source layouts are first-class use cases.

## Included plugin

Marketplace: `gabbasov-odoo-tools`  
Plugin: `odoo-claude`

The plugin provides eight skills:

| Skill | Purpose |
| --- | --- |
| `odoo` | Main Odoo task router, source-verification workflow, and safety policy |
| `odoo-18` | Odoo 18 target-version guidance |
| `odoo-migration` | Sequential Odoo 16 -> 17 -> 18 addon migration workflow |
| `odoo-testing` | Regression, security, ORM, HTTP, and migration tests |
| `odoo-review` | Findings-first Odoo code review |
| `odoo-owl` | OWL/frontend work verified against the target Odoo source |
| `odoo-indexer` | Local SQLite static source index for fast symbol lookup |
| `doodba` | Optional Doodba/Invoke discovery and runtime-safety workflow |

It also includes a read-only `odoo-context-gatherer` subagent.

## Install from GitHub

Add the marketplace:

```bash
claude plugin marketplace add GabbasovDinar/odoo-claude --scope project
```

Then inside Claude Code:

```text
/plugin install odoo-claude@gabbasov-odoo-tools
```

For local marketplace development:

```text
/plugin marketplace add ./odoo-claude
/plugin install odoo-claude@gabbasov-odoo-tools
```

## Odoo source configuration

The skills prefer exact local source verification over memory. For Odoo 16 -> 18 migration, expose both framework source trees when available:

```bash
export ODOO_SOURCE_16=/work/odoo-16/odoo
export ODOO_SOURCE_18=/work/odoo-18/odoo
```

For a single-version project:

```bash
export ODOO_SOURCE=/work/odoo
```

For repositories with an aggregate source root, including Doodba-style layouts:

```bash
export ODOO_PATH=/work/project/odoo/custom/src
```

The context gatherer inspects the actual repository before proposing commands. When Doodba markers are present, the optional `doodba` skill discovers project-specific Invoke tasks from `tasks.py`, `invoke --list`, task help, project documentation, `copier.yml`, and the real source layout. It does not assume that all Doodba projects expose identical commands.

## Local Odoo indexer

The plugin `bin/` directory exposes three commands while the plugin is enabled:

```bash
# Full initial index
odoo-index --root ./addons --full

# Multiple roots are supported
odoo-index \
  --root /work/odoo-18/odoo \
  --root /work/enterprise \
  --root ./custom-addons \
  --full

# Doodba layouts work too when present
odoo-index \
  --root ./odoo/custom/src \
  --root ./odoo/auto/addons \
  --full

# Queries
odoo-search model sale.order
odoo-search field partner_id --parent sale.order
odoo-search method action_confirm --parent sale.order
odoo-search xmlid sale.view_order_form
odoo-search ref base.group_user
odoo-search model 'sale.%'

# Index metadata and counts
odoo-index-status
```

The indexer uses only the Python standard library. It statically indexes Python, XML, JavaScript, manifests, and CSV files into SQLite. It is a navigation accelerator, not runtime database truth and not a replacement for source inspection or tests.

Default database location:

```text
~/.odoo-indexer/odoo_index.sqlite3
```

Override it when useful:

```bash
export ODOO_INDEX_DB="$PWD/.cache/odoo-index.sqlite3"
```

## Migration policy

For a 16 -> 18 migration, the plugin requires a sequential compatibility pass:

```text
16.0 -> 17.0 -> 18.0
```

Compatibility changes stay separate from opportunistic refactoring. Framework-sensitive claims should be checked against the exact target branch source. Existing behavior should receive regression coverage before or alongside compatibility changes.

The plugin does not run module installation/update, database creation/restoration, destructive Git operations, or service-changing commands merely because it discovered a likely command. Such operations require explicit user intent.

## Validation

Repository-level validation and indexer tests have no third-party Python dependencies:

```bash
python tools/validate_repo.py
python -m py_compile plugins/odoo-claude/skills/odoo-indexer/scripts/*.py
python -m unittest discover -s tests -v
```

With Claude Code installed, also run the official validators:

```bash
claude plugin validate .
claude plugin validate ./plugins/odoo-claude
```

GitHub Actions runs the local validation suite on Python 3.11 and 3.12.

## Project layout

```text
.claude-plugin/
  marketplace.json
plugins/
  odoo-claude/
    .claude-plugin/plugin.json
    agents/
    bin/
    skills/
      odoo/
      odoo-18/
      odoo-migration/
      odoo-testing/
      odoo-review/
      odoo-owl/
      odoo-indexer/
      doodba/
tests/
tools/
```

## Upstream provenance

The design was informed by `mart337i/odoo-skills` and selected Doodba/indexing ideas from `letzdoo/claude-marketplace`. The implementation is curated and rewritten rather than a blind file-level merge. See `THIRD_PARTY_NOTICES.md` for pinned source revisions and licensing notes.

## License

MIT.
