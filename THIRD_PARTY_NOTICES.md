# Third-party notices and design provenance

This repository is a curated implementation written for this project. It is not a verbatim merge of the upstream repositories.

The design was informed by:

- `mart337i/odoo-skills` at commit `326ad862a279b6549441b4a90928f528ef9b8bc1`: Odoo task routing, version-aware source verification, migration discipline, review/test workflows, and separation of compatibility work from refactoring.
- `letzdoo/claude-marketplace` at commit `be96e8b57268cc0f5da6142742857751c25cd860`: Doodba-specific environment discovery and the idea of a local Odoo source indexer.

The SQLite indexer in this repository is an independent implementation using only the Python standard library. It does not copy the Letzdoo indexer source code.

`letzdoo/claude-marketplace` is distributed under the MIT License. At the inspected `mart337i/odoo-skills` revision, `package.json` declares MIT while no root `LICENSE` file was present, so this repository avoids copying substantial source/text from it and reimplements the useful workflow ideas in original wording.
