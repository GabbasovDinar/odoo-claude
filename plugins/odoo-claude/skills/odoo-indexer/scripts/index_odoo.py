#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from indexlib import default_db_path, index, normalize_roots


def main():
    parser = argparse.ArgumentParser(description="Build/update a local SQLite index of Odoo source symbols.")
    parser.add_argument("--root", action="append", help="Source root; repeat for multiple roots. Auto-detected when omitted.")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = index(normalize_roots(args.root), (args.db or default_db_path()).expanduser().resolve(), full=args.full)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Indexed {result['files']} files / {result['symbols']} symbols")
        print(f"Changed: {result['changed_files']}; unchanged: {result['unchanged_files']}; parse errors: {result['errors']}")
        print(f"Modules: {result['modules']}; models: {result['models']}; fields: {result['fields']}")
        print(f"DB: {result['db']}")


if __name__ == "__main__":
    main()
