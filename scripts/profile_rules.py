#!/usr/bin/env python3
"""Time each generative rule per n (unbuffered), with a cProfile of the slowest call.
Usage: python -u scripts/profile_rules.py [max_n]"""
import cProfile
import pstats
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from metricpoly import group  # noqa: E402
from metricpoly.dsl.interp import Interpreter  # noqa: E402
from metricpoly.dsl.prims import p_vertex  # noqa: E402

max_n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
I = Interpreter()
I.load_file("rules/stdlib.mpr")
I.load_file("rules/literature.mpr")
I.finalize()
slowest = (0, None, None)
for name, r in I.rules.items():
    if r.kind != "generative":
        continue
    lo = r.meta.get("domain", (3,))[0]
    hi = (tuple(r.meta.get("domain", (3,))) + (99,))[1]
    for n in range(3, max_n + 1):
        if not (lo <= n <= hi):
            continue
        t = time.time()
        out = I.run_rule(r, n)
        dt_rule = time.time() - t
        t = time.time()
        vs = [p for p in out if p.n == n and p_vertex(p)]
        keys = {group.canonical(p).key() for p in vs}
        dt_check = time.time() - t
        print(f"{name:22s} n={n}: {len(out):5d} cand {len(vs):5d} vert {len(keys):3d} orbits | "
              f"rule {dt_rule:7.2f}s  check {dt_check:6.2f}s", flush=True)
        if dt_rule > slowest[0]:
            slowest = (dt_rule, name, n)
print("slowest:", slowest, flush=True)
if slowest[1]:
    I.memo.clear()
    pr = cProfile.Profile()
    pr.enable()
    I.run_rule(I.rules[slowest[1]], slowest[2])
    pr.disable()
    pstats.Stats(pr).sort_stats("cumulative").print_stats(18)
