#!/usr/bin/env python3
"""Recheck all large-n breaker orbits of earlier rounds against the CURRENT accepted moves (checkpoints/phase9/state.json).
Bottom-up search (n <= 12) with hard per-orbit timeouts; denominator-lemma flag. Writes results/phase9/recheck_rounds_<tag>.json.
Usage: python -u scripts/phase9/recheck_rounds.py --rounds 2 3 4 --tag after_r05
"""
import argparse, json, multiprocessing as mp, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
import phase9_round as P
from metricpoly.core import Point
from metricpoly.jobs import atomic_write_json
from metricpoly.dsl.ext.phase8_prims import p_den_bound_ok

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--rounds", nargs="+", type=int); ap.add_argument("--tag"); a = ap.parse_args()
    items = []
    for r in a.rounds:
        for c in json.loads((ROOT / f"phase9/round_{r:02d}/breaker/candidates.json").read_text()):
            items.append(({"round": r, "n": c["n"], "D": c["D"], "how": c.get("how", "")[:80],
                           "bound_violated": not p_den_bound_ok(c["D"], c["n"])}, Point.make(c["n"], c["D"], c["nums"])))
    t0 = time.time()
    with mp.Pool(19, initializer=P._large_init) as pool:
        jobs = [pool.apply_async(P._large_reach, (x,)) for _, x in items]
        out = []
        hard = time.time() + P.LARGE_BUDGET * (1 + len(items) / 19) + 60
        for (m, x), jb in zip(items, jobs):
            try:
                v, stats, s = jb.get(timeout=max(1.0, hard - time.time()))
            except mp.TimeoutError:
                v, stats, s = None, {"hard_timeout": True}, None
            out.append({**m, "verdict": v, "stats": stats, "s": s})
        pool.terminate()
    st = json.loads((ROOT / "checkpoints/phase9/state.json").read_text())
    summ = {}
    for r in out:
        key = f"round {r['round']}"
        d = summ.setdefault(key, {"total": 0, "reachable": 0, "unreachable": 0, "undecided": 0, "undecided_but_bound_violated": 0})
        d["total"] += 1
        d[{True: "reachable", False: "unreachable", None: "undecided"}[r["verdict"]]] += 1
        if r["verdict"] is None and r["bound_violated"]:
            d["undecided_but_bound_violated"] += 1
    res = {"moves": st["moves"], "seconds": round(time.time() - t0, 1), "summary": summ, "rows": out}
    atomic_write_json(ROOT / f"results/phase9/recheck_rounds_{a.tag}.json", res)
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))

if __name__ == "__main__":
    main()
