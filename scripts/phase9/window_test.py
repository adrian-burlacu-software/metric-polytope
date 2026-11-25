#!/usr/bin/env python3
"""Period test for local-pattern families (rules of family_scan.py with all three profiles extended "near").

Such a family has, for every large t, the same distances at bounded offsets, so the submetric on a window of m
consecutive positions (2m points) does not depend on t once t >= 2m + 2r + 3. If the window submetric is itself an
extreme ray for some m, the family's locality is at most 2m for every larger t (the window proves everything inside
it and the closure then spreads by symmetry); this is what happens for K^(2) at m = 13. A family whose windows are
never rays, while the cyclic metrics are, is a candidate for locality growing linearly with t.
Reports the nullity (dimension of the solution space of the tight system) of the window submetric for several m.

  python scripts/phase9/window_test.py --key t0_7_t_11_13 --m 8 12 16 20
"""
from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

from family_extend import build, extend  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402
from vertex_structure import rank_mod_p  # noqa: E402


def nullity(d):
    k = len(d)
    idx = {}
    for i, j in itertools.combinations(range(k), 2):
        idx[(i, j)] = idx[(j, i)] = len(idx) // 2
    N = k * (k - 1) // 2
    rows = []
    for a, b, c in itertools.combinations(range(k), 3):
        for (i, j, m) in ((a, b, c), (a, c, b), (b, c, a)):
            if d[i, j] == d[i, m] + d[j, m]:
                r = np.zeros(N, dtype=np.int64)
                r[idx[(i, j)]] = 1
                r[idx[(i, m)]] = -1
                r[idx[(j, m)]] = -1
                rows.append(r)
    return N - (rank_mod_p(np.array(rows)) if rows else 0)


def job(args):
    k, fA, fB, h, r, ms = args
    out = {}
    for m in ms:
        t = 2 * m + 2 * r + 5
        r2 = (t - 1) // 2
        d = build(t, extend(list(fA), r, r2, "near", 1), extend(list(fB), r, r2, "near", 1), extend(list(h), r, r2, "near", 0))
        W = list(range(m)) + [t + i for i in range(m)]
        dw = d[np.ix_(W, W)]
        n = len(W)
        ok = all(not (dw > dw[:, x:x + 1] + dw[x:x + 1, :]).any() for x in range(n))
        if not ok:
            out[m] = None
            continue
        from locality_fast import locality_fast
        L, prof = locality_fast(n, dw.tolist(), None, levels=[4, n])
        out[m] = (prof.get(4), prof.get(4), prof.get(n))      # classes after level 4, after level 6, with the whole window
    return k, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", default="t0_7_t_11_13")
    ap.add_argument("--m", type=int, nargs="+", default=[8, 12, 16])
    ap.add_argument("--workers", type=int, default=14)
    a = ap.parse_args()
    t0 = time.time()
    j = json.loads((ROOT / "results/phase9/family_scan.json").read_text())
    rules = [x for x in j[a.key] if x["modes"] == ["near", "near", "near"]]
    r = len(rules[0]["fA"])
    items = [(k, x["fA"], x["fB"], x["h"], r, a.m) for k, x in enumerate(rules)]
    print(f"{len(items)} local-pattern rules", flush=True)
    res = {}
    with mp.get_context("spawn").Pool(a.workers) as pool:
        for k, out in pool.imap_unordered(job, items, chunksize=4):
            res[k] = out
    c = Counter(tuple(res[k][m] for m in a.m) for k in res)
    print("classes (level 4, level 6, whole window) for m =", a.m, flush=True)
    for key, v in sorted(c.items(), key=lambda kv: -kv[1])[:25]:
        print("  ", key, "x", v, flush=True)
    good = [k for k in res if all(res[k][m] is not None and res[k][m][2] is not None and res[k][m][2] == res[k][m][1] > 1 for m in a.m)]
    print(f"{len(good)} rules whose windows force nothing beyond the 6-point merges ({time.time() - t0:.0f} s)", flush=True)
    for k in good[:20]:
        x = rules[k]
        print("   fA", x["fA"], "fB", x["fB"], "h", x["h"], "L0", x["L0"], "nullity", [res[k][m] for m in a.m], flush=True)
    atomic_write_json(ROOT / "results/phase9/window_test.json",
                      {"key": a.key, "m": a.m, "rules": [dict(rules[k], window_nullity={str(m): res[k][m] for m in a.m}) for k in sorted(res)]})


if __name__ == "__main__":
    main()
