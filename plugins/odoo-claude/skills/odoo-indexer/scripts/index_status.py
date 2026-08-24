#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from indexlib import default_db_path, status


def main():
    parser = argparse.ArgumentParser(description="Show local Odoo index status.")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = status((args.db or default_db_path()).expanduser().resolve())
    epoch = result.get("last_indexed_epoch")
    if epoch:
        result["last_indexed"] = datetime.fromtimestamp(int(epoch), tz=timezone.utc).isoformat()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True)); return
    print(f"DB: {result['db']}")
    print(f"Size: {result['size_bytes']} bytes")
    print(f"Files: {result['files']}; symbols: {result['symbols']}")
    if result.get("last_indexed"): print(f"Last indexed: {result['last_indexed']}")
    if result.get("roots"): print(f"Roots: {result['roots']}")
    for kind, count in sorted(result.get("counts", {}).items()): print(f"  {kind}: {count}")


if __name__ == "__main__":
    main()
