#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "odoo-claude"
errors: list[str] = []


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return {}


market = load_json(ROOT / ".claude-plugin" / "marketplace.json")
manifest = load_json(PLUGIN / ".claude-plugin" / "plugin.json")

if market.get("name") != "gabbasov-odoo-tools":
    errors.append("marketplace name must be gabbasov-odoo-tools")
plugins = market.get("plugins", [])
if len(plugins) != 1 or plugins[0].get("source") != "./plugins/odoo-claude":
    errors.append("marketplace must expose exactly ./plugins/odoo-claude")
if manifest.get("name") != "odoo-claude":
    errors.append("plugin manifest name must be odoo-claude")

frontmatter = re.compile(r"\A---\n(.*?)\n---\n", re.S)
for skill_dir in sorted((PLUGIN / "skills").iterdir()):
    if not skill_dir.is_dir():
        continue
    path = skill_dir / "SKILL.md"
    if not path.exists():
        errors.append(f"{skill_dir.relative_to(ROOT)}: missing SKILL.md")
        continue
    text = path.read_text(encoding="utf-8")
    match = frontmatter.match(text)
    if not match:
        errors.append(f"{path.relative_to(ROOT)}: malformed frontmatter")
        continue
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    name = fields.get("name", "")
    description = fields.get("description", "")
    if name != skill_dir.name:
        errors.append(f"{path.relative_to(ROOT)}: name '{name}' must match directory '{skill_dir.name}'")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append(f"{path.relative_to(ROOT)}: invalid lowercase skill name '{name}'")
    if not description or "TODO" in description or len(description) < 40:
        errors.append(f"{path.relative_to(ROOT)}: description is incomplete")

for binary in ("odoo-index", "odoo-search", "odoo-index-status"):
    path = PLUGIN / "bin" / binary
    if not path.exists():
        errors.append(f"missing bin/{binary}")
    elif path.stat().st_mode & 0o111 == 0:
        errors.append(f"bin/{binary} is not executable")

if errors:
    print("Repository validation failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print(f"Repository validation passed: {len(list((PLUGIN / 'skills').glob('*/SKILL.md')))} skills")
