#!/usr/bin/env python3
"""Independent check of Deza's m_9 orbit list (data/deza/orbits9, 1,056,367 rows; published count 1,056,368).

Per row: exact vertex test (all inequalities hold, certified tight rank = 36), denominator in lowest terms, and a
canonical form under switchings ⋊ S_9 (metricpoly/canon_large.py: bliss, validated against the lexmin form).
Then: number of distinct orbits (duplicates listed), and whether every one of Deza–Indik's 1,221 counterexample
orbits occurs in the list. This shows the list has NO DUPLICATES and contains only vertices; it says nothing about
completeness.
Parallel, chunked; each chunk is written atomically to checkpoints/verify_n9_list/ and skipped on rerun.
Usage: python -u scripts/verify_n9_list.py [--workers 19]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import multiprocessing as mp
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from metricpoly import deza  # noqa: E402
from metricpoly.canon_large import canonical_key  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.jobs import atomic_write_json, code_version, git_head  # noqa: E402

CK = ROOT / "checkpoints" / "verify_n9_list"
CHUNK = 5000
_W = {}


def _init():
    from metricpoly.dsl.prims import p_vertex
    _W["co"] = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
    _W["de"] = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
    _W["pv"] = p_vertex


def _chunk(c):
    path = CK / f"chunk_{c:04d}.json"
    if path.exists():
        return c
    lo, hi = c * CHUNK, min((c + 1) * CHUNK, len(_W["co"]))
    keys, nonvert, not_lowest = [], [], []
    for r in range(lo, hi):
        D = int(_W["de"][r])
        nums = [int(v) for v in _W["co"][r]]
        if math.gcd(D, *nums) != 1:
            not_lowest.append(r)
        x = Point.make(9, D, nums)
        if not _W["pv"](x):
            nonvert.append(r)
        keys.append(canonical_key(x))
    atomic_write_json(path, {"lo": lo, "hi": hi, "keys": keys, "non_vertex": nonvert, "not_lowest_terms": not_lowest})
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=19)
    args = ap.parse_args()
    CK.mkdir(parents=True, exist_ok=True)
    n = len(np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r"))
    chunks = list(range((n + CHUNK - 1) // CHUNK))
    t0 = time.time()
    with mp.Pool(args.workers, initializer=_init) as pool:
        for k, _ in enumerate(pool.imap_unordered(_chunk, chunks), 1):
            if k % 20 == 0 or k == len(chunks):
                el = time.time() - t0
                print(f"[n9 list] {k}/{len(chunks)} chunks  {el:.0f}s  eta {el / k * (len(chunks) - k):.0f}s", flush=True)
    keys, nonvert, notlow = [], [], []
    for c in chunks:
        d = json.loads((CK / f"chunk_{c:04d}.json").read_text())
        keys += d["keys"]
        nonvert += d["non_vertex"]
        notlow += d["not_lowest_terms"]
    pos = defaultdict(list)
    for r, k in enumerate(keys):
        pos[k].append(r)
    dups = {k: v for k, v in pos.items() if len(v) > 1}
    cex = deza.load_counterexamples()
    cex_keys = {canonical_key(x) for x, _, _ in cex}
    zsha = hashlib.sha256((ROOT / "data/deza/orbits9/Orbits.zip").read_bytes()).hexdigest()
    out = {"rows": len(keys), "published_orbit_count": 1056368, "distinct_orbits": len(pos),
           "duplicate_groups": len(dups), "duplicates": [v for v in dups.values()][:100],
           "non_vertex_rows": nonvert[:100], "non_vertex_count": len(nonvert),
           "not_lowest_terms_count": len(notlow),
           "counterexample_orbits_1221_present": sum(1 for k in cex_keys if k in pos),
           "counterexample_orbits_distinct": len(cex_keys),
           "denominators": dict(sorted(Counter(int(k.split("|")[1]) for k in pos).items())),
           "orbits_zip_sha256": zsha, "code_version": code_version(), "git": git_head(),
           "seconds": round(time.time() - t0, 1),
           "scope": "no duplicates + every row a vertex; completeness of the list is NOT tested"}
    atomic_write_json(ROOT / "results" / "n9" / "list_verification.json", out)
    print(json.dumps({k: v for k, v in out.items() if k not in ("denominators", "duplicates")}, indent=1))


if __name__ == "__main__":
    main()
