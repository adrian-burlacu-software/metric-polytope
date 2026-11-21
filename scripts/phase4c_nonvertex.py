#!/usr/bin/env python3
"""Can m7 orbit #12 be reached if intermediate points may be non-vertices?

All 7 single-node projections of #12 are non-vertices of m6 (so vertex-only lifting can never reach it).
Here: closure up to n = 6 keeping every FEASIBLE point (non-vertex mode), seeded with every feasible candidate of
the data-free base rules; then check whether any projection orbit of #12 is reached, and if so lift it.

Usage: python -u scripts/phase4c_nonvertex.py [--rounds 3] [--resume] [--force]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from metricpoly import deza, group  # noqa: E402
from metricpoly.dsl.closure import run_closure  # noqa: E402
from metricpoly.dsl.interp import Interpreter  # noqa: E402
from metricpoly.dsl.prims import p_feasible, p_restrict, p_vertex  # noqa: E402
from metricpoly.jobs import Job, add_job_args, atomic_write_json  # noqa: E402

BASE = ["gen-cuts", "gen-anticuts", "gen-graphic", "gen-multipartite", "gen-avis-paths", "gen-rays",
        "gen-tree-suspension"]                       # gen-sporadic excluded (it has no n <= 6 points anyway)
UNARY = ["twin", "dup", "radial", "radial2", "radial3", "lift-fiber"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_job_args(ap)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--target", type=int, default=12)
    args = ap.parse_args()
    params = {"rounds": args.rounds, "base": BASE, "moves": UNARY, "target": args.target}
    job = Job("phase4c_nonvertex", params, args.seed, resume=args.resume, force=args.force)
    I = Interpreter(seed=args.seed)
    I.load_file(ROOT / "rules" / "stdlib.mpr")
    I.load_file(ROOT / "rules" / "literature.mpr")
    I.finalize()

    x = deza.load_ext(7)[args.target - 1]
    proj = {}
    for i in range(7):
        r = p_restrict(frozenset(set(range(7)) - {i}), x)
        proj.setdefault(group.canonical(r).key(), []).append(i + 1)

    seeds, labels = [], []
    for name in BASE:
        rule = I.rules[name]
        d = tuple(rule.meta.get("domain", (3,)))
        for n in range(max(3, d[0]), min(6, d[1] if len(d) > 1 else 6) + 1):
            for p in I.run_rule(rule, n):
                if p.n == n and p_feasible(p):
                    seeds.append(p)
                    labels.append(f"{name}@{n}")
    print(f"{len(seeds)} feasible seed points", flush=True)
    t = time.time()
    C = run_closure(I, seeds, [I.moves[m] for m in UNARY], max_n=6, max_rounds=args.rounds, only_vertices=False,
                    checkpoint=f"nonvertex-r{args.rounds}", seed_labels=labels)
    hit = {k: v for k, v in proj.items() if k in C.keys(6)}
    rec = {"orbits_per_n": {n: len(d) for n, d in C.orbits.items()}, "saturated": C.saturated,
           "truncated": C.truncated_reason, "seconds": round(time.time() - t, 1),
           "projection_orbits": {k: v for k, v in proj.items()}, "projections_reached": hit}
    print(rec["orbits_per_n"], "saturated", C.saturated, "projections reached:", hit, flush=True)

    if hit:                                          # final step: lift each reached projection, look for #12
        target_key = group.canonical(x).key()
        found = []
        for k in hit:
            y = C.orbits[6][k]["rep"]
            for z in I.apply_move(I.moves["lift-fiber"], [y], as_orbits=True):
                if p_vertex(z) and group.canonical(z).key() == target_key:
                    found.append(k)
                    break
        rec["lift_reaches_target_from"] = found
        rec["derivations"] = {k: C.orbits[6][k]["prov"] for k in hit}
        print("lift-fiber reaches #%d from projections:" % args.target, found, flush=True)
    job.record("result", rec)
    atomic_write_json(ROOT / "results" / "phase4c" / f"nonvertex_m7_{args.target}.json", rec)


if __name__ == "__main__":
    main()
