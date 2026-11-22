#!/usr/bin/env python3
"""Computer checks for docs/denominator_lemma.md (Phase 8a). These are CHECKS, not part of the proof.

 C3  For every connected graph G on k <= 9 nodes: tau(G) <= 2(k-1) (Lemma 3), equality attained; den(x_G) | tau(G).
 C4  n = 9 design-A sample: every orbit found derivable (detours allowed) satisfies the Theorem 4 bound
     (every odd prime power p^e exactly dividing den(x) has p^e <= 2n - 3 = 15).
 C5  EXACT count over all 1,056,367 rows of Orbits.zip: orbits whose denominator violates the bound, i.e. orbits
     that Theorem 4 proves non-derivable (no sampling involved). Also n = 8 (533 orbits).
Writes results/phase8/denominator_bound.json.
"""
from __future__ import annotations

import gzip
import itertools
import math
import json
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from metricpoly import deza  # noqa: E402
from metricpoly.dsl.prims import p_connected, p_gmetric, p_graphs, p_triameter  # noqa: E402
from metricpoly.dsl.values import Graph  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402


def odd_prime_powers(d: int):
    out, p = [], 3
    while d % 2 == 0:
        d //= 2
    while p * p <= d:
        if d % p == 0:
            e = 1
            while d % p == 0:
                d //= p
                e *= p
            out.append(e)
        p += 2
    if d > 1:
        out.append(d)
    return out


def bound_ok(den: int, n: int) -> bool:
    return all(q <= 2 * n - 3 for q in odd_prime_powers(den))


def main():
    t0 = time.time()
    out = {}
    # C3: tau bound, exhaustive
    c3 = {}
    for k in range(3, 10):
        if k <= 8:
            gs = [G for G in p_graphs(k) if p_connected(G)]
        else:
            gs = [Graph.make(9, E) for E in json.loads((ROOT / "data/generated/graphs9.json").read_text())]
            gs = [G for G in gs if p_connected(G)]
        taus = Counter()
        bad_den = 0
        for G in gs:
            d = p_gmetric(G)
            tau = int(p_triameter(G))
            taus[tau] += 1
            D = 1
            for v in d.nums:
                D = D * Fraction(2 * v, tau).denominator // math.gcd(D, Fraction(2 * v, tau).denominator)
            bad_den += tau % D != 0
        c3[k] = {"graphs": len(gs), "max_tau": max(taus), "bound_2(k-1)": 2 * (k - 1),
                 "holds": max(taus) <= 2 * (k - 1), "attained": max(taus) == 2 * (k - 1),
                 "den_divides_tau_violations": bad_den, "tau_histogram": dict(sorted(taus.items()))}
        print("C3", k, {a: b for a, b in c3[k].items() if a != "tau_histogram"}, f"{time.time() - t0:.0f}s", flush=True)
    out["C3_tau_bound"] = c3
    # C4: n = 9 sample, derivable orbits satisfy the bound
    recs = [json.loads(l) for l in gzip.open(ROOT / "results/n9/orbits_A.jsonl.gz", "rt") if l.strip()]
    der = [r for r in recs if r["depth_detour"] is not None]
    out["C4_n9_sample"] = {"orbits": len(recs), "derivable": len(der),
                           "derivable_violating_bound": sum(not bound_ok(r["D"], 9) for r in der),
                           "sample_orbits_violating_bound": sum(not bound_ok(r["D"], 9) for r in recs)}
    print("C4", out["C4_n9_sample"], flush=True)
    # C5: exact population counts
    den = np.load(ROOT / "data/deza/orbits9/den.npy")
    cnt = Counter(int(d) for d in den)
    excl = {d: c for d, c in cnt.items() if not bound_ok(d, 9)}
    out["C5_n9_population"] = {"orbits": int(len(den)), "excluded_by_theorem": int(sum(excl.values())),
                               "excluded_share": sum(excl.values()) / len(den),
                               "excluded_by_denominator": dict(sorted(excl.items())),
                               "all_denominators": dict(sorted(cnt.items()))}
    n8 = Counter(x.D for x in deza.load_ext(8))
    out["C5_n8"] = {"orbits": sum(n8.values()), "excluded_by_theorem": sum(c for d, c in n8.items() if not bound_ok(d, 8))}
    print("C5", {k: v for k, v in out["C5_n9_population"].items() if k != "all_denominators"}, out["C5_n8"], flush=True)
    out["ok"] = bool(all(v["holds"] and v["den_divides_tau_violations"] == 0 for v in c3.values())
                 and out["C4_n9_sample"]["derivable_violating_bound"] == 0)
    atomic_write_json(ROOT / "results/phase8/denominator_bound.json", out)
    print("OK" if out["ok"] else "FAILED", f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
