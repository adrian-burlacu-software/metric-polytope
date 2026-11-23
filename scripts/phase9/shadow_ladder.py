#!/usr/bin/env python3
"""Shadow ladder of the unreached Phase 9 targets (docs/ladder_semantics.md, Definition 1 along a target's own ladder).

For an unreached target x of m_n, a new node w, and an attachment order of the other nodes: the rung-k shadow of x is
x on G_k (the other nodes complete, w joined to N_k = the first k of them). Its pieces are x|(V \\ w) and x|(N_k ∪ w),
both restrictions of x, i.e. engine nodes with exact verdicts (checkpoints/phase9/reached.json; sets of <= 2 nodes
count as reached). The shadow at rung k is reached iff x|(V \\ w) and every x|(N_j ∪ w), j <= k, are reached (a chain:
the attachment grows one edge per rung). For each w the best order is found by a DP over the subsets containing w:
    good(S) = |S| <= 2, or (S reached and good(S \\ v) for some v in S \\ w)
k_w(x) = max |S| - 1 over good S ≠ V (0..n-2), and -1 if x|(V \\ w) itself is unreached.
The target's break rung is b(x) = max_w k_w(x) + 1: the first rung of the best ladder that is not reached
(b = n - 1 means every partial attachment is fine and only the last edge fails).
Also reported per target: the minimal unreached restrictions that block the best ladders (aim points for new rules).

Usage: python -u scripts/phase9/shadow_ladder.py [--n 8]
Writes results/phase9/shadow_ladder_n{n}.json.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

from metricpoly import group  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8)
    a = ap.parse_args()
    import detour_depth2 as d2
    from judge import targets
    t0 = time.time()
    reached = set(json.loads((ROOT / "checkpoints/phase9/reached.json").read_text()))
    T = [(o, x) for m, o, x in targets() if m == a.n]
    rows = []
    for o, x in T:
        M = d2.matrix(x)
        n = x.n
        full = (1 << n) - 1
        key = {}
        for size in range(3, n + 1):
            for S in itertools.combinations(range(n), size):
                key[sum(1 << v for v in S)] = group.canonical(d2.restrict(M, x.D, S)).key()
        if key[full] in reached:
            continue
        R = {m for m, k in key.items() if k in reached}

        def ok(m):
            return bin(m).count("1") <= 2 or m in R

        per_w, goods, blockers = {}, {}, Counter()
        for w in range(n):
            bw = 1 << w
            if not ok(full & ~bw):
                per_w[w] = -1
                continue
            good = {bw}
            best = 0
            frontier = [bw]
            for size in range(2, n):                         # S ∋ w, |S| = size, S ≠ V
                nxt = []
                for S in itertools.combinations([v for v in range(n) if v != w], size - 1):
                    m = bw | sum(1 << v for v in S)
                    if any((m & ~(1 << v)) in good for v in S):
                        if ok(m):
                            good.add(m)
                            nxt.append(m)
                            best = size - 1
                if not nxt:
                    break
                frontier = nxt
            per_w[w] = best
            goods[w] = good
        b = max(per_w.values()) + 1
        # blockers: minimal unreached sets S ∋ w (S ≠ V) one node above a good set, on the best ladders
        for w, kw in per_w.items():
            if kw + 1 != b or kw < 0:
                continue
            bw = 1 << w
            for S in itertools.combinations([v for v in range(n) if v != w], kw + 1):
                m = bw | sum(1 << v for v in S)
                if m == full or ok(m):
                    continue
                if any((m & ~(1 << v)) in goods[w] for v in S):
                    blockers[key[m]] += 1
        top = max((bin(m).count("1") for m in R if m != full), default=0)
        odd = sorted({q for q in range(3, x.D + 1, 2) if x.D % q == 0 and all(q % r for r in range(3, int(q ** .5) + 1, 2))})
        rows.append({"orbit": o, "D": x.D, "odd_primes": odd, "largest_reached_restriction": top,
                     "reached_restrictions_by_size": dict(sorted(Counter(bin(m).count("1") for m in R).items())),
                     "break_rung": b, "k_w": per_w,
                     "blockers": [{"key": k, "count": c} for k, c in blockers.most_common(10)]})
    hist = Counter(r["break_rung"] for r in rows)
    allb = Counter()
    for r in rows:
        for bl in r["blockers"]:
            allb[bl["key"]] += 1
    prof = Counter(r["largest_reached_restriction"] for r in rows)
    by_top = {}
    for r in rows:
        g = by_top.setdefault(r["largest_reached_restriction"], {"D": Counter(), "odd_primes": Counter()})
        g["D"][r["D"]] += 1
        g["odd_primes"][",".join(map(str, r["odd_primes"])) or "none"] += 1
    out = {"n": a.n, "unreached_targets": len(rows), "break_rung_histogram": dict(sorted(hist.items())),
           "largest_reached_restriction_histogram": dict(sorted(prof.items())),
           "by_largest_reached": {k: {"D": dict(sorted(v["D"].items())), "odd_primes": dict(v["odd_primes"])}
                                  for k, v in sorted(by_top.items())},
           "top_blockers": [{"key": k, "targets": c, "nodes": int(k.split("|")[0]), "D": int(k.split("|")[1])}
                            for k, c in allb.most_common(40)],
           "rows": rows, "seconds": round(time.time() - t0, 1)}
    atomic_write_json(ROOT / "results" / "phase9" / f"shadow_ladder_n{a.n}.json", out)
    print(json.dumps({k: out[k] for k in ("n", "unreached_targets", "break_rung_histogram",
                                          "largest_reached_restriction_histogram", "seconds")}))
    for k, v in out["by_largest_reached"].items():
        print(f"  largest reached restriction {k}: D {v['D']}  odd primes {v['odd_primes']}")
    print("top blockers (key prefix, targets):")
    for b in out["top_blockers"][:15]:
        print(f"  {b['nodes']} nodes, D={b['D']}: {b['targets']} targets   {b['key'][:70]}")


if __name__ == "__main__":
    main()
