#!/usr/bin/env python3
"""Evaluate Phase 9 reachability rung by rung on the Phase 10 ladder (docs/ladder_semantics.md, Definition 1).

For every vertex orbit y of rung k of the ladder m_nK -> m_{nK+1} (checkpoints/phase10/ladder_n{nK+1}/rung_k.jsonl):
  k < nK : pieces y|K (nK nodes) and y|(N ∪ w) (k + 1 nodes; <= 2 nodes counts as reached); y is reached iff both are
  k = nK : y itself (P_nK = m_{nK+1}: Phase 9 proper)
Three rule sets, all exact:
  detour  - ledger rule all-moves-cover: uniform base, lift / radial 1-3 / uncapped glue, non-vertex intermediates
            allowed (detour_depth2.DP, vertex_mode False)
  vertex  - ledger rule all-moves-cover-vertex-only: same with every point of the chain a vertex (DP, vertex_mode
            True); a piece that is not a vertex is unreached
  main    - the current Phase 9 main track: detour + accepted moves of checkpoints/phase9/state.json
            (reach_large.reachable_bu; None = undecided within the budget)
Rung k is covered for a rule set iff every orbit is reached; the break rung is the smallest uncovered k.

--validate: before the ladder, reachable_bu with the accepted moves is compared with the engine's own verdicts on
random engine nodes (reached and unreached; checkpoints/phase9/reached.json, results/phase9/unreached_nodes.json).

Usage: python -u scripts/phase9/ladder_eval.py --nK 6 [--validate 40] [--budget 60] [--workers 16]
Writes results/phase9/ladder_eval_n{nK+1}.json.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

from metricpoly.core import Point  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402
from metricpoly.ladder import rung  # noqa: E402

_W = {}


def _init(max_n):
    from common import interpreter
    import detour_depth2 as d2
    I, _ = interpreter([])
    st = json.loads((ROOT / "checkpoints/phase9/state.json").read_text())
    _W["I"] = I
    _W["moves"] = [(name, int(mv.grow)) for name, mv in I.moves.items() if name in st["moves"]]
    from metricpoly.dsl.interp import Interpreter
    J = Interpreter(seed=20261122)
    for f in ("stdlib.mpr", "literature.mpr"):
        J.load_file(ROOT / "rules" / f)
    J.finalize()
    B = d2.base_keys(J, d2.UNIFORM, max_n)
    _W["dp"] = {"detour": d2.DP(B, False), "vertex": d2.DP(B, True)}


def _apply(name, p):
    from metricpoly import core
    I = _W["I"]
    try:
        return [o for o in I.apply_move(I.moves[name], [p], as_orbits=True) if core.is_feasible(o)]
    except Exception:
        return []


def _verdicts(args):
    x, budget, modes = args
    from metricpoly.reach_large import reachable_bu
    import detour_depth2 as d2
    out = {}
    t = time.time()
    if "detour" in modes:
        out["detour"] = _W["dp"]["detour"].point_depth(x)[0] != d2.INF
    if "vertex" in modes:
        out["vertex"] = _W["dp"]["vertex"].point_depth(x)[0] != d2.INF
    if "main" in modes:
        v, _ = reachable_bu(x, _W["moves"], _apply, budget=budget)
        out["main"] = v
    out["s"] = round(time.time() - t, 2)
    return out


def sub(vals, D, T):
    T = sorted(T)
    return Point.make(len(T), D, [vals[(T[a], T[b])] for a in range(len(T)) for b in range(a + 1, len(T))])


def is_vertex(x: Point) -> bool:
    from common import verify_vertex
    return bool(verify_vertex(x)["vertex"])


def parse_key(k: str) -> Point:
    n, D, nums = k.split("|")
    return Point.make(int(n), int(D), [int(v) for v in nums.split(",")])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nK", type=int, required=True)
    ap.add_argument("--budget", type=float, default=60)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--validate", type=int, default=0, help="engine nodes per class (reached / unreached) to compare")
    ap.add_argument("--validate-max-n", type=int, default=None, help="largest node size in the validation sample "
                    "(default nK + 1, the largest piece size)")
    a = ap.parse_args()
    nK = a.nK
    t0 = time.time()
    lad = ROOT / "checkpoints" / "phase10" / f"ladder_n{nK + 1}"
    rungs = sorted(int(p.stem.split("_")[1]) for p in lad.glob("rung_*.jsonl"))
    out = {"nK": nK, "rungs_available": rungs, "budget_s": a.budget}
    with mp.get_context("spawn").Pool(a.workers, initializer=_init, initargs=(max(nK + 1, a.validate_max_n or 0),)) as pool:
        if a.validate:
            reached = json.loads((ROOT / "checkpoints/phase9/reached.json").read_text())
            unr = json.loads((ROOT / "results/phase9/unreached_nodes.json").read_text())["keys"]
            rng = np.random.default_rng(20261123)
            vmax = a.validate_max_n or nK + 1
            rk = sorted(k for k in reached if 5 <= int(k.split("|")[0]) <= vmax)
            uk = sorted(k for k in unr if 5 <= int(k.split("|")[0]) <= vmax)
            pick = [(k, True) for k in rng.choice(rk, a.validate, replace=False)] + \
                   [(k, False) for k in rng.choice(uk, min(a.validate, len(uk)), replace=False)]
            res = []
            for j, r in enumerate(pool.imap(_verdicts, [(parse_key(k), a.budget, ("main",)) for k, _ in pick])):
                res.append(r)
                print(f"  validate {j + 1}/{len(pick)}: n={pick[j][0].split('|')[0]} engine={pick[j][1]} "
                      f"bu={r['main']} {r['s']} s ({time.time() - t0:.0f} s)", flush=True)
            agree = sum(1 for (k, e), r in zip(pick, res) if r["main"] == e)
            und = sum(1 for r in res if r["main"] is None)
            dis = [{"key": k, "engine": e, "bu": r["main"]} for (k, e), r in zip(pick, res)
                   if r["main"] is not None and r["main"] != e]
            out["validation"] = {"checked": len(pick), "agree": agree, "undecided": und, "disagree": dis}
            print(f"validation: {agree}/{len(pick)} agree, {und} undecided, {len(dis)} disagree "
                  f"({time.time() - t0:.0f} s)", flush=True)
            if dis:
                atomic_write_json(ROOT / "results" / "phase9" / f"ladder_eval_n{nK + 1}.json", out)
                raise SystemExit("bottom-up search disagrees with the engine: stopping")
        # pieces
        jobs, rows = [], []
        for k in rungs:
            R = rung(nK, k)
            w = nK
            for ln in (lad / f"rung_{k}.jsonl").read_text(encoding="utf-8").splitlines():
                r = json.loads(ln)
                vals = dict(zip(R.edges, r["nums"]))
                if k < nK:
                    pcs = [("K", sub(vals, r["D"], range(nK)))]
                    if k + 1 >= 3:
                        pcs.append(("Nw", sub(vals, r["D"], list(range(k)) + [w])))
                else:
                    pcs = [("full", sub(vals, r["D"], range(nK + 1)))]
                row = {"rung": k, "key": r["key"], "D": r["D"], "pieces": {}}
                for name, x in pcs:
                    row["pieces"][name] = {"n": x.n, "D": x.D, "nums": list(x.nums), "vertex": is_vertex(x)}
                    jobs.append((len(rows), name, x))
                rows.append(row)
        print(f"{len(rows)} rung orbits, {len(jobs)} pieces ({time.time() - t0:.0f} s)", flush=True)
        res = pool.map(_verdicts, [(x, a.budget, ("detour", "vertex", "main")) for _, _, x in jobs], chunksize=1)
    for (ri, name, _), v in zip(jobs, res):
        rows[ri]["pieces"][name].update(v)
    summ = {}
    for mode in ("detour", "vertex", "main"):
        per = {}
        for k in rungs:
            rr = [r for r in rows if r["rung"] == k]
            st = []
            for r in rr:
                vs = []
                for p in r["pieces"].values():
                    v = p[mode]
                    if mode == "vertex" and not p["vertex"]:
                        v = False
                    vs.append(v)
                st.append(False if any(v is False for v in vs) else (None if any(v is None for v in vs) else True))
            per[k] = {"orbits": len(rr), "reached": st.count(True), "unreached": st.count(False),
                      "undecided": st.count(None)}
        brk = next((k for k in rungs if per[k]["unreached"]), None)
        summ[mode] = {"per_rung": per, "break_rung": brk,
                      "undecided_somewhere": any(per[k]["undecided"] for k in rungs)}
    out.update(rows=rows, summary=summ, seconds=round(time.time() - t0, 1))
    atomic_write_json(ROOT / "results" / "phase9" / f"ladder_eval_n{nK + 1}.json", out)
    for mode, s in summ.items():
        print(mode, "break rung:", s["break_rung"], {k: (v["reached"], v["unreached"], v["undecided"])
                                                     for k, v in s["per_rung"].items()}, flush=True)
    print(f"done in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
