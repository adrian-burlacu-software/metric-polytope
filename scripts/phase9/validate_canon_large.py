#!/usr/bin/env python3
"""Validate metricpoly.canon_large (seed 20261122):
 (1) n = 3..6 all vertices, n = 7, 8 Deza reps: number of distinct keys == number of orbits (n <= 6: Deza counts)
 (2) invariance: 5 random group images of every n = 7, 8 rep and of 300 random n = 9 rows give the same key
 (3) agreement with the lexmin canonical form: on 3,000 random points (restrictions of n = 9 rows to random 5..9 node
     subsets, plus their random images), key equality <=> lexmin-key equality, checked over all pairs with equal
     (n, D) inside each size class
 (4) timing at n = 10..20 on round-2/3 breaker vertices
Writes results/phase9/canon_large_validation.json
"""
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from metricpoly import deza, group  # noqa: E402
from metricpoly.canon_large import canonical_key, random_image  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.dsl.prims import p_vertices  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402

rng = np.random.default_rng(20261122)
out = {}
t = time.time()
expect = {3: 1, 4: 1, 5: 2, 6: 3}
for n in range(3, 7):
    ks = {canonical_key(x) for x in p_vertices(n)}
    out[f"n{n}_orbits"] = [len(ks), expect[n]]
for n in (7, 8):
    reps = list(deza.load_ext(n))
    ks = [canonical_key(x) for x in reps]
    bad = sum(canonical_key(random_image(x, rng)) != k for x, k in zip(reps, ks) for _ in range(5))
    out[f"n{n}_orbits"] = [len(set(ks)), len(reps)]
    out[f"n{n}_image_mismatch"] = bad
print(out, round(time.time() - t, 1), flush=True)
coords = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
dens = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
rows = rng.choice(len(coords), 300, replace=False)
bad9 = 0
for r in rows:
    x = Point.make(9, int(dens[r]), [int(v) for v in coords[r]])
    k = canonical_key(x)
    bad9 += sum(canonical_key(random_image(x, rng)) != k for _ in range(5))
out["n9_image_mismatch"] = bad9
# (3) agreement with lexmin canonical form on restrictions
sys.path.insert(0, str(ROOT / "scripts"))
import detour_depth2 as d2  # noqa: E402
pts = []
for r in rng.choice(len(coords), 600, replace=False):
    x = Point.make(9, int(dens[r]), [int(v) for v in coords[r]])
    M = d2.matrix(x)
    k = int(rng.integers(5, 10))
    T = sorted(rng.choice(9, k, replace=False).tolist())
    y = d2.restrict(M, x.D, T)
    pts += [y, random_image(y, rng)]
    for _ in range(3):                    # near-duplicates: images of a few earlier points
        if pts:
            pts.append(random_image(pts[int(rng.integers(len(pts)))], rng))
classes_new, classes_old = defaultdict(set), defaultdict(set)
for i, p in enumerate(pts):
    classes_new[canonical_key(p)].add(i)
    classes_old[group.canonical(p).key()].add(i)
part_new = {frozenset(v) for v in classes_new.values()}
part_old = {frozenset(v) for v in classes_old.values()}
out["agreement_points"] = len(pts)
out["agreement_orbits"] = len(part_old)
out["partitions_identical"] = part_new == part_old
print({k: v for k, v in out.items()}, round(time.time() - t, 1), flush=True)
# (4) timing at large n
tim = {}
for f in ["phase9/round_02/breaker/candidates.json", "phase9/round_03/breaker/candidates.json"]:
    for c in json.loads((ROOT / f).read_text()):
        x = Point.make(c["n"], c["D"], c["nums"])
        t0 = time.time()
        k = canonical_key(x)
        k2 = canonical_key(random_image(x, rng))
        tim.setdefault(c["n"], []).append(time.time() - t0)
        out.setdefault("large_image_mismatch", 0)
        out["large_image_mismatch"] += k != k2
out["large_seconds_per_two_keys_median"] = {n: round(float(np.median(v)), 3) for n, v in sorted(tim.items())}
out["seconds"] = round(time.time() - t, 1)
atomic_write_json(ROOT / "results/phase9/canon_large_validation.json", out)
print(out, flush=True)
