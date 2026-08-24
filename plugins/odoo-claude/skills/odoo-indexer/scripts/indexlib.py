from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sqlite3
import time
import xml.etree.ElementTree as ET
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, mtime_ns INTEGER, size INTEGER, sha1 TEXT, root TEXT);
CREATE TABLE IF NOT EXISTS symbols(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,
  name TEXT NOT NULL,
  module TEXT,
  parent TEXT,
  path TEXT NOT NULL,
  line INTEGER,
  meta TEXT
);
CREATE INDEX IF NOT EXISTS idx_symbols_kind_name ON symbols(kind, name);
CREATE INDEX IF NOT EXISTS idx_symbols_parent ON symbols(parent);
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
"""


def default_db_path() -> Path:
    return Path(os.environ.get("ODOO_INDEX_DB", "~/.odoo-indexer/odoo_index.sqlite3")).expanduser()


def normalize_roots(values: list[str] | None) -> list[Path]:
    candidates = values or [
        os.environ.get("ODOO_PATH"),
        os.environ.get("ODOO_SOURCE"),
        os.environ.get("ODOO_SOURCE_16"),
        os.environ.get("ODOO_SOURCE_18"),
        "./odoo/custom/src",
        "./odoo/auto/addons",
    ]
    roots: list[Path] = []
    for value in candidates:
        if not value:
            continue
        path = Path(value).expanduser().resolve()
        if path.exists() and path not in roots:
            roots.append(path)
    if not roots:
        roots = [Path.cwd().resolve()]
    return roots


def _connect(db: Path) -> sqlite3.Connection:
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db)
    conn.executescript(SCHEMA)
    return conn


def _module_for(path: Path, root: Path) -> str | None:
    current = path.parent
    while current != root.parent:
        if (current / "__manifest__.py").exists() or (current / "__openerp__.py").exists():
            return current.name
        if current == root:
            break
        current = current.parent
    return None


def _add(rows: list[tuple], kind: str, name: str, module: str | None, parent: str | None, path: Path, line: int | None, meta=None):
    rows.append((kind, name, module, parent, str(path), line, json.dumps(meta or {}, sort_keys=True)))


def _str(node):
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _parse_python(path: Path, module: str | None, rows: list[tuple]):
    tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        model_names: list[str] = []
        for item in node.body:
            if isinstance(item, (ast.Assign, ast.AnnAssign)):
                target = item.targets[0] if isinstance(item, ast.Assign) else item.target
                value = item.value
                if isinstance(target, ast.Name) and target.id in {"_name", "_inherit"}:
                    values = []
                    if isinstance(value, (ast.List, ast.Tuple)):
                        values = [_str(v) for v in value.elts]
                    else:
                        values = [_str(value)]
                    for name in filter(None, values):
                        kind = "model" if target.id == "_name" else "model-inherit"
                        _add(rows, kind, name, module, node.name, path, getattr(item, "lineno", None))
                        model_names.append(name)
        parent = model_names[0] if model_names else node.name
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _add(rows, "method", item.name, module, parent, path, item.lineno)
                for deco in item.decorator_list:
                    if isinstance(deco, ast.Call) and isinstance(deco.func, ast.Attribute) and deco.func.attr == "route":
                        for arg in deco.args:
                            route = _str(arg)
                            if route:
                                _add(rows, "route", route, module, parent, path, item.lineno)
            elif isinstance(item, (ast.Assign, ast.AnnAssign)):
                target = item.targets[0] if isinstance(item, ast.Assign) else item.target
                value = item.value
                if isinstance(target, ast.Name) and isinstance(value, ast.Call):
                    fn = value.func
                    if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name) and fn.value.id == "fields":
                        _add(rows, "field", target.id, module, parent, path, getattr(item, "lineno", None), {"field_type": fn.attr})


def _parse_manifest(path: Path, module: str | None, rows: list[tuple]):
    try:
        data = ast.literal_eval(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return
    mod = module or path.parent.name
    _add(rows, "module", mod, mod, None, path, 1, {"version": data.get("version") if isinstance(data, dict) else None})
    if isinstance(data, dict):
        for dep in data.get("depends", []) or []:
            _add(rows, "dependency", str(dep), mod, mod, path, 1)


def _xmlid(module: str | None, ident: str) -> str:
    return ident if "." in ident or not module else f"{module}.{ident}"


def _parse_xml(path: Path, module: str | None, rows: list[tuple]):
    root = ET.parse(path).getroot()
    for elem in root.iter():
        line = getattr(elem, "sourceline", None)
        ident = elem.attrib.get("id")
        if ident:
            kind = "xmlid"
            if elem.tag == "menuitem":
                kind = "menu"
            elif elem.tag in {"template", "t"}:
                kind = "template"
            elif elem.tag == "record":
                model = elem.attrib.get("model", "")
                if model == "ir.ui.view":
                    kind = "view"
                elif model.startswith("ir.actions."):
                    kind = "action"
            _add(rows, kind, _xmlid(module, ident), module, elem.attrib.get("model"), path, line)
        for key, value in elem.attrib.items():
            if key in {"ref", "inherit_id", "groups"} and value:
                for ref in re.split(r"[, ]+", value):
                    if ref:
                        _add(rows, "ref", ref, module, None, path, line)
        tname = elem.attrib.get("t-name")
        if tname:
            _add(rows, "template", tname, module, None, path, line)


def _parse_js(path: Path, module: str | None, rows: list[tuple]):
    text = path.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r"class\s+([A-Za-z_$][\w$]*)", text):
        _add(rows, "js-class", m.group(1), module, None, path, text.count("\n", 0, m.start()) + 1)
    for m in re.finditer(r"\.template\s*=\s*['\"]([^'\"]+)['\"]", text):
        _add(rows, "template-ref", m.group(1), module, None, path, text.count("\n", 0, m.start()) + 1)
    for m in re.finditer(r"registry\.category\(['\"]([^'\"]+)['\"]\)\.add\(['\"]([^'\"]+)['\"]", text):
        _add(rows, "registry", m.group(2), module, m.group(1), path, text.count("\n", 0, m.start()) + 1)


def _parse(path: Path, root: Path) -> list[tuple]:
    rows: list[tuple] = []
    module = _module_for(path, root)
    name = path.name
    if name in {"__manifest__.py", "__openerp__.py"}:
        _parse_manifest(path, module, rows)
    elif path.suffix == ".py":
        _parse_python(path, module, rows)
    elif path.suffix == ".xml":
        _parse_xml(path, module, rows)
    elif path.suffix in {".js", ".mjs"}:
        _parse_js(path, module, rows)
    elif path.suffix == ".csv":
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines()[1:], 2):
            ident = line.split(",", 1)[0].strip().strip('"')
            if ident:
                _add(rows, "xmlid", _xmlid(module, ident), module, None, path, i)
    return rows


def index(roots: list[Path], db: Path, full: bool = False) -> dict:
    roots = [Path(r).resolve() for r in roots]
    conn = _connect(db)
    if full:
        conn.execute("DELETE FROM symbols")
        conn.execute("DELETE FROM files")
    changed = unchanged = errors = 0
    seen: set[str] = set()
    for root in roots:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".xml", ".js", ".mjs", ".csv"}:
                continue
            if any(part in {".git", "node_modules", "__pycache__", ".venv"} for part in path.parts):
                continue
            p = str(path.resolve())
            seen.add(p)
            stat = path.stat()
            old = conn.execute("SELECT mtime_ns,size FROM files WHERE path=?", (p,)).fetchone()
            if old == (stat.st_mtime_ns, stat.st_size):
                unchanged += 1
                continue
            changed += 1
            conn.execute("DELETE FROM symbols WHERE path=?", (p,))
            try:
                rows = _parse(path, root)
                conn.executemany("INSERT INTO symbols(kind,name,module,parent,path,line,meta) VALUES(?,?,?,?,?,?,?)", rows)
                sha1 = hashlib.sha1(path.read_bytes()).hexdigest()
                conn.execute("INSERT OR REPLACE INTO files(path,mtime_ns,size,sha1,root) VALUES(?,?,?,?,?)", (p, stat.st_mtime_ns, stat.st_size, sha1, str(root)))
            except Exception:
                errors += 1
    for (p,) in conn.execute("SELECT path FROM files").fetchall():
        if p not in seen and any(str(p).startswith(str(r)) for r in roots):
            conn.execute("DELETE FROM symbols WHERE path=?", (p,))
            conn.execute("DELETE FROM files WHERE path=?", (p,))
    conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('last_indexed_epoch',?)", (str(int(time.time())),))
    conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('roots',?)", (json.dumps([str(r) for r in roots]),))
    conn.commit()
    counts = dict(conn.execute("SELECT kind,COUNT(*) FROM symbols GROUP BY kind").fetchall())
    files = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    symbols = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
    conn.close()
    return {
        "files": files,
        "symbols": symbols,
        "changed_files": changed,
        "unchanged_files": unchanged,
        "errors": errors,
        "modules": counts.get("module", 0),
        "models": counts.get("model", 0) + counts.get("model-inherit", 0),
        "fields": counts.get("field", 0),
        "db": str(db),
    }


def _like(query: str) -> str:
    escaped = query.replace("\\", "\\\\").replace("_", "\\_")
    return escaped if "%" in query else f"%{escaped}%"


def search(db: Path, kind: str, query: str, module: str | None = None, parent: str | None = None, limit: int = 20) -> list[dict]:
    if not db.exists():
        return []
    conn = _connect(db)
    where = ["name LIKE ? ESCAPE '\\'"]
    params: list[object] = [_like(query)]
    if kind == "xmlid":
        where.append("kind IN ('xmlid','view','action','menu','template')")
    elif kind != "any":
        where.append("kind=?")
        params.append(kind)
    if module:
        where.append("module=?")
        params.append(module)
    if parent:
        where.append("parent=?")
        params.append(parent)
    sql = (
        "SELECT kind,name,module,parent,path,line,meta FROM symbols WHERE "
        + " AND ".join(where)
        + " ORDER BY CASE WHEN name=? THEN 0 ELSE 1 END, kind,name LIMIT ?"
    )
    params.extend([query, limit])
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    keys = ["kind", "name", "module", "parent", "path", "line", "meta"]
    result = []
    for row in rows:
        item = dict(zip(keys, row))
        item["meta"] = json.loads(item["meta"] or "{}")
        result.append(item)
    return result


def status(db: Path) -> dict:
    if not db.exists():
        return {"db": str(db), "size_bytes": 0, "files": 0, "symbols": 0, "counts": {}, "roots": []}
    conn = _connect(db)
    counts = dict(conn.execute("SELECT kind,COUNT(*) FROM symbols GROUP BY kind").fetchall())
    meta = dict(conn.execute("SELECT key,value FROM meta").fetchall())
    files = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    symbols = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
    conn.close()
    return {
        "db": str(db),
        "size_bytes": db.stat().st_size,
        "files": files,
        "symbols": symbols,
        "counts": counts,
        "roots": json.loads(meta.get("roots", "[]")),
        "last_indexed_epoch": meta.get("last_indexed_epoch"),
    }
