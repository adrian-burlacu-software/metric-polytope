#!/usr/bin/env python3
"""Validate metricpoly.reach_large.reachable_bu and recheck the large-n breaker orbits with the accepted moves.
 (a) 40 seeded n = 8 targets (20 reached / 20 unreached in the current main state): bottom-up WITH the accepted moves
     must agree with the engine's verdict
 (b) the 80 large-n orbits of rounds 2-3, bottom-up WITHOUT user moves: must agree with the judged verdicts
 (c) the same 80 orbits WITH the accepted moves: the new verdicts (written to results/phase9/recheck_large.json)
Budget 60 s per search, 19 workers (worst case about 6 minutes).
"""
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

from metricpoly.core import Point  # noqa: E402

_W = {}
BUDGET = 60.0


def _init():
    from common import interpreter
    I, _ = interpreter([])
    _W["I"] = I
    _W["moves"] = [(name, int(mv.grow)) for name, mv in I.moves.items()
                   if name in json.loads((ROOT / "checkpoints/phase9/state.json").read_text())["moves"]]


def _apply(name, p):
    from metricpoly import core
    I = _W["I"]
    try:
        return [o for o in I.apply_move(I.moves[name], [p], as_orbits=True) if core.is_feasible(o)]
    except Exception:
        return []


def _job(args):
    tag, meta, x, use_moves = args
    from metricpoly.reach_large import reachable_bu
    t = time.time()
    v, st = reachable_bu(x, _W["moves"] if use_moves else [], _apply, budget=BUDGET)
    return {"tag": tag, **meta, "verdict": v, "stats": st, "s": round(time.time() - t, 1)}


def main():
    from judge import CK, targets
    from phase9_round import load_state
    from metricpoly.reach import Engine
    rng = np.random.default_rng(20261122)
    eng = Engine(CK / "engine")
    reached, st = load_state()
    T = targets()
    ids8 = [i for i, (n, o, _) in enumerate(T) if n == 8]
    r8 = [i for i in ids8 if eng.target_key(i) in reached]
    u8 = [i for i in ids8 if eng.target_key(i) not in reached]
    pick = [int(i) for i in rng.choice(r8, 20, replace=False)] + [int(i) for i in rng.choice(u8, 20, replace=False)]
    jobs = [("a", {"n": 8, "id": int(T[i][1]), "engine": eng.target_key(i) in reached}, T[i][2], True) for i in pick]
    large = []
    for rnd in ("round_02", "round_03"):
        for c in json.loads((ROOT / f"phase9/{rnd}/breaker/candidates.json").read_text()):
            large.append(({"round": rnd, "n": c["n"], "D": c["D"]}, Point.make(c["n"], c["D"], c["nums"])))
    jobs += [("b", m, x, False) for m, x in large if x.n <= 11]
    jobs += [("c", m, x, True) for m, x in large]
    t0 = time.time()
    part = ROOT / "checkpoints/phase9/recheck_large.jsonl"          # incremental; rerun skips finished jobs
    done = {}
    if part.exists():
        for line in part.read_text(encoding="utf-8").splitlines():
            d = json.loads(line)
            done[d["job"]] = d
    todo = [(j, jb) for j, jb in enumerate(jobs) if j not in done]
    with mp.Pool(19, initializer=_init) as pool, open(part, "a", encoding="utf-8") as f:
        for j, r in zip([j for j, _ in todo], pool.imap(_job, [jb for _, jb in todo], chunksize=1)):
            r["job"] = j
            f.write(json.dumps(r, default=str) + chr(10))
            f.flush()
            done[j] = r
    res = [done[j] for j in range(len(jobs))]
    A = [r for r in res if r["tag"] == "a"]
    B = [r for r in res if r["tag"] == "b"]
    C = [r for r in res if r["tag"] == "c"]
    out = {"moves": st["moves"], "budget_s": BUDGET, "seconds": round(time.time() - t0, 1),
           "a_n8_agree_with_engine": sum(1 for r in A if r["verdict"] == r["engine"]), "a_checked": len(A),
           "a_undecided": sum(1 for r in A if r["verdict"] is None),
           "a_disagree": [r for r in A if r["verdict"] is not None and r["verdict"] != r["engine"]],
           "b_without_moves_unreachable": sum(1 for r in B if r["verdict"] is False), "b_checked": len(B),
           "b_other": [r for r in B if r["verdict"] is not False],
           "c_with_moves": {str(v): sum(1 for r in C if r["verdict"] is v) for v in (True, False, None)},
           "c_rows": C}
    from metricpoly.jobs import atomic_write_json
    atomic_write_json(ROOT / "results/phase9/recheck_large.json", out)
    print(json.dumps({k: v for k, v in out.items() if k != "c_rows"}, indent=1, default=str))


if __name__ == "__main__":
    main()
