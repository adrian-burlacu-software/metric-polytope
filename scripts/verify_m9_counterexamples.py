#!/usr/bin/env python3
"""Verify Deza–Indik's 1,221 m_9 counterexample orbits to the Laurent–Poljak dominating-set conjecture.

Per point: exact vertex test; incidence equals the file's value; adjacent to NONE of the 2^8 = 256 cuts
(certified rank: adjacency <=> rank of the common tight set = C(9,2) - 1); canonical form (orbits distinct).
Also checks that the arXiv:math/0512493 Proposition 2.1 vertex is among them.
Usage: python -u scripts/verify_m9_counterexamples.py [--resume] [--force]
"""
from __future__ import annotations

import argparse
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from metricpoly import core, deza, group  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.dsl.prims import p_adjacent, p_cuts, p_vertex  # noqa: E402
from metricpoly.jobs import Job, Progress, add_job_args, atomic_write_json  # noqa: E402

DI_2005 = Point.make(9, 9, [2, 2, 3, 3, 4, 4, 5, 5, 4, 3, 5, 6, 6, 3, 3, 5, 5, 2, 4, 3, 5, 6, 3, 3, 6, 6, 5, 3, 2, 6,
                            6, 3, 3, 5, 3, 4])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    add_job_args(ap)
    args = ap.parse_args()
    job = Job("verify_m9_cex", {"file": "1221_counterexamples.txt"}, args.seed, resume=args.resume, force=args.force)
    rows = deza.load_counterexamples()
    cuts = p_cuts(9)
    prog = Progress("m9", len(rows), every=30)
    for i, (x, inc, adj) in enumerate(rows, 1):
        task = f"cex{i}"
        if job.is_done(task):
            prog.step()
            continue
        v = p_vertex(x)
        icd = int(len(core.tight_set(x)))
        adj_cuts = sum(1 for c in cuts if p_adjacent(x, c))
        key = group.canonical(x).key()
        job.record(task, {"i": i, "vertex": v, "incidence": icd, "incidence_file": inc, "adjacency_file": adj,
                          "adjacent_cuts": adj_cuts, "D": x.D, "key": key})
        prog.step()
    R = [v for k, v in job.results().items() if k.startswith("cex")]
    di_key = group.canonical(DI_2005).key()
    out = {"points": len(R), "all_vertices": all(r["vertex"] for r in R),
           "incidence_matches_file": all(r["incidence"] == r["incidence_file"] for r in R),
           "adjacent_to_no_cut": all(r["adjacent_cuts"] == 0 for r in R),
           "distinct_orbits": len({r["key"] for r in R}),
           "arxiv_2005_example_included": di_key in {r["key"] for r in R},
           "arxiv_2005_example_is_vertex_not_adjacent_to_cut": p_vertex(DI_2005) and not any(p_adjacent(DI_2005, c) for c in cuts),
           "incidence_histogram": dict(sorted(Counter(r["incidence"] for r in R).items())),
           "denominators": dict(sorted(Counter(r["D"] for r in R).items()))}
    atomic_write_json(ROOT / "results" / "phase7" / "m9_counterexamples.json", out)
    print(out)


if __name__ == "__main__":
    main()
