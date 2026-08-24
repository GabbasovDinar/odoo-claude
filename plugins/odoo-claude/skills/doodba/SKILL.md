---
name: doodba
description: Optional Doodba-aware Odoo workflow. Use only when a repository contains Doodba/Copier/Invoke configuration, tasks.py, copier metadata, odoo/custom/src, odoo/auto/addons, or project docs that use Invoke; discover setup, test, update, shell, service, and addon-source commands without guessing project-specific tasks.
---

# Doodba workflow

Doodba is an optional project adapter. Do not assume a repository uses it unless actual markers are present.

## Detect Doodba

Look for multiple signals such as `tasks.py`, Invoke task collections, `copier.yml`/`.copier-answers.yml`, `odoo/custom/src`, `odoo/auto/addons`, Docker Compose files, and README instructions that use `invoke`.

## Read-only discovery first

Prefer `pwd`, `git status --short --branch`, file inspection, `invoke --list`, and relevant task help. Only use a task name or flag after it is confirmed by this project's task list/docs.

## Source layout

Prefer editable source under `odoo/custom/src` for reasoning. Treat `odoo/auto/addons` as generated/runtime assembly unless project docs explicitly say otherwise.

For migrations, support distinct `ODOO_SOURCE_16` and `ODOO_SOURCE_18` trees; never silently point both variables at one checkout.

## Runtime safety

Read-only inspection is safe by default. Ask before starting/stopping services, creating/restoring/dropping databases, installing/updating/uninstalling modules, pruning Docker resources, or running production-like operations.

## Indexer integration

When useful, index Doodba roots with `odoo-index --root ./odoo/custom/src` and query them with `odoo-search`.
