"""On-disk cache (SQLite, transactional) keyed by sha256 of the input.

Namespaces carry an algorithm version so a changed algorithm never reads stale entries.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Callable, Optional

from .core import Point

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "cache" / "cache.sqlite"

CANON_VERSION = "canon-v1"        # bump if group.canonical changes semantics


class DiskCache:
    def __init__(self, path: Path = DEFAULT_DB):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path), timeout=60)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("CREATE TABLE IF NOT EXISTS kv (ns TEXT, key TEXT, value TEXT, PRIMARY KEY(ns, key))")
        self.db.commit()
        self.hits = self.misses = 0

    @staticmethod
    def hkey(obj: Any) -> str:
        return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()

    def get(self, ns: str, key: str) -> Optional[Any]:
        r = self.db.execute("SELECT value FROM kv WHERE ns=? AND key=?", (ns, key)).fetchone()
        return None if r is None else json.loads(r[0])

    def put(self, ns: str, key: str, value: Any) -> None:
        self.db.execute("INSERT OR REPLACE INTO kv VALUES (?,?,?)", (ns, key, json.dumps(value)))
        self.db.commit()

    def memo(self, ns: str, inp: Any, fn: Callable[[], Any]) -> Any:
        k = self.hkey(inp)
        v = self.get(ns, k)
        if v is not None:
            self.hits += 1
            return v
        self.misses += 1
        v = fn()
        self.put(ns, k, v)
        return v

    def canonical(self, p: Point) -> Point:
        from .group import canonical
        v = self.memo(CANON_VERSION, [p.n, p.D, list(p.nums)],
                      lambda: (lambda c: [c.D, list(c.nums)])(canonical(p)))
        return Point(p.n, v[0], tuple(v[1]))
