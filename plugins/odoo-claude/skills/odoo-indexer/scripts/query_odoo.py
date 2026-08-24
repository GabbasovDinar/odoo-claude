#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from indexlib import default_db_path, search


def main():
    parser = argparse.ArgumentParser(description="Query the local Odoo source index.")
    parser.add_argument("kind")
    parser.add_argument("query")
    parser.add_argument("--module")
    parser.add_argument("--parent")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    rows = search((args.db or default_db_path()).expanduser().resolve(), args.kind, args.query, args.module, args.parent, args.limit)
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True)); return
    if not rows:
        print("No results"); return
    for row in rows:
        location = row["path"] + (f":{row['line']}" if row.get("line") else "")
        parent = f" parent={row['parent']}" if row.get("parent") else ""
        module = f" module={row['module']}" if row.get("module") else ""
        print(f"{row['kind']:14} {row['name']}{module}{parent} -> {location}")


if __name__ == "__main__":
    main()
