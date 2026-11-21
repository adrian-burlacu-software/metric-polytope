#!/usr/bin/env python3
"""Validate metricpoly.graphic.orbit_is_graphic against the canonical-key table it replaces.

 (a) n = 3..7: for every vertex orbit rep of m_n, orbit_is_graphic(x) == (canonical key of x is the key of some x_G);
     also every x_G (all connected graphs) passes, under a random group element.
 (b) n = 8: every x_G of the 11,117 connected graphs passes under a random group element; Deza reps that pass are
     re-checked against an x_G canonical key computed on the fly.
 (c) n = 9: 3,000 random connected graphs (seeded), x_G under a random group element, must pass; and
     3,000 random rows of Orbits.zip: positives cross-checked by canonical key against the reconstructed x_G.
Writes results/n9/graphic_test_validation.json.  Seed 20261121.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fractions import Fraction  # noqa: E402

from metricpoly import deza, group  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.dsl.prims import p_connected, p_gmetric, p_graphs, p_scale, p_triameter, _vertices  # noqa: E402
from metricpoly.dsl.values import Graph  # noqa: E402
from metricpoly.graphic import orbit_is_graphic, is_graph_metric  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402

SEED = 20261121


def xg(G):
    return p_scale(Fraction(2, int(p_triameter(G))), p_gmetric(G))


def graph_from_switched(x):
    """Return the x_G found by the test (as a Point), for cross-checking by canonical key."""
    a = np.asarray(x.nums, dtype=np.int64)
    F = group.switch_flips(x.n)
    for s in range(F.shape[0]):
        y = np.where(F[s], x.D - a, a)
        if is_graph_metric(y.tolist(), x.D, x.n):
            return Point.make(x.n, x.D, y.tolist())
    return None


def main():
    rng = np.random.default_rng(SEED)
    out = {"seed": SEED}
    t0 = time.time()
    for n in range(3, 8):
        gs = [G for G in p_graphs(n) if p_connected(G)]
        keys = set()
        bad_pos = 0
        for G in gs:
            x = xg(G)
            keys.add(group.canonical(x).key())
            p, s = group.random_element(n, rng)
            bad_pos += not orbit_is_graphic(group.apply(n, p, s, x))
        reps = _vertices(n)
        mism = sum(orbit_is_graphic(x) != (group.canonical(x).key() in keys) for x in reps)
        out[f"n{n}"] = {"graphs": len(gs), "graph_orbits": len(keys), "graph_images_failing": bad_pos,
                        "vertex_reps": len(reps), "mismatches": mism,
                        "graphic_vertex_orbits": sum(orbit_is_graphic(x) for x in reps)}
        print(n, out[f"n{n}"], f"{time.time() - t0:.0f}s", flush=True)
    # n = 8
    gs = [G for G in p_graphs(8) if p_connected(G)]
    bad = 0
    for G in gs:
        p, s = group.random_element(8, rng)
        bad += not orbit_is_graphic(group.apply(8, p, s, xg(G)))
    reps = _vertices(8)
    pos = [x for x in reps if orbit_is_graphic(x)]
    pos_bad = sum(group.canonical(graph_from_switched(x)).key() != group.canonical(x).key() for x in pos)
    out["n8"] = {"graphs": len(gs), "graph_images_failing": bad, "vertex_reps": len(reps),
                 "graphic_vertex_orbits": len(pos), "positives_failing_key_check": pos_bad}
    print(8, out["n8"], f"{time.time() - t0:.0f}s", flush=True)
    # n = 9 random graphs
    import networkx as nx
    bad = cnt = 0
    while cnt < 3000:
        g = nx.gnp_random_graph(9, float(rng.uniform(0.15, 0.9)), seed=int(rng.integers(1 << 31)))
        if not nx.is_connected(g):
            continue
        cnt += 1
        p, s = group.random_element(9, rng)
        bad += not orbit_is_graphic(group.apply(9, p, s, xg(Graph.make(9, list(g.edges())))))
    coords = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
    dens = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
    idx = sorted(rng.choice(len(coords), 3000, replace=False))
    pos9 = pos9_bad = 0
    for i in idx:
        x = Point.make(9, int(dens[i]), [int(v) for v in coords[i]])
        if orbit_is_graphic(x):
            pos9 += 1
            pos9_bad += group.canonical(graph_from_switched(x)).key() != group.canonical(x).key()
    out["n9"] = {"random_graphs": cnt, "graph_images_failing": bad, "orbit_rows_tested": len(idx),
                 "graphic_rows": pos9, "positives_failing_key_check": pos9_bad}
    print(9, out["n9"], f"{time.time() - t0:.0f}s", flush=True)
    ok = all(v.get("mismatches", 0) == 0 and v.get("graph_images_failing", 0) == 0
             and v.get("positives_failing_key_check", 0) == 0 for k, v in out.items() if k.startswith("n"))
    out["ok"] = ok
    atomic_write_json(ROOT / "results" / "n9" / "graphic_test_validation.json", out)
    print("OK" if ok else "FAILED", flush=True)


if __name__ == "__main__":
    main()
