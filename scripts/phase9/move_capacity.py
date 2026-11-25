#!/usr/bin/env python3
"""Counting argument (2026-11-25): how many m_9 orbits can the accepted moves produce from ALL of m_8?

Applies every accepted move (checkpoints/phase9/state.json) plus lift and radial to each of the 533 m_8 orbits (all of
them, reached or not: an upper bound on what moves from 8-node inputs can give), keeps outputs that are vertices of m_9,
counts distinct orbits per move and in total. Compared with the orbit count of m_9 and with the data ceiling from
vertex_structure_deza9all.json (orbits with an 8-node vertex restriction; non-primitive orbits).
Usage: python -u scripts/phase9/move_capacity.py [--workers 16]. Writes results/phase9/move_capacity.json."""
from __future__ import annotations
import argparse, json, multiprocessing as mp, sys, time
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
from metricpoly import core, group  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402
_W = {}


def _init():
    from common import interpreter
    I, _ = interpreter([])
    st = json.loads((ROOT / "checkpoints/phase9/state.json").read_text())
    _W.update(I=I, moves=[m for m in I.moves if m in st["moves"]])


def job(x):
    """Per move: number of outputs that are vertices of m_9 (orbit representatives as the interpreter returns them,
    not merged further: an upper bound on distinct orbits), and seconds."""
    I = _W["I"]
    out = {}
    for nm in _W["moves"]:
        t = time.time()
        try:
            pts = I.apply_move(I.moves[nm], [x], as_orbits=True)
            out[nm] = (len(pts), sum(1 for o in pts if o.n == 9 and core.is_feasible(o) and core.is_vertex(o)[0]),
                       round(time.time() - t, 1))
        except Exception as e:      # noqa: BLE001
            out[nm] = (0, 0, f"{type(e).__name__}")
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--limit", type=int, default=0); a = ap.parse_args()
    from metricpoly import deza
    t0 = time.time()
    V = deza.load_ext(8)
    if a.limit: V = V[:: max(1, len(V) // a.limit)]
    per, per_in, secs = defaultdict(lambda: [0, 0]), [], defaultdict(float)
    with mp.get_context("spawn").Pool(a.workers, initializer=_init) as pool:
        for i, o in enumerate(pool.imap_unordered(job, V, chunksize=2)):
            tot = 0
            for nm, (npts, nv, sec) in o.items():
                per[nm][0] += npts; per[nm][1] += nv; tot += nv
                if isinstance(sec, float): secs[nm] += sec
            per_in.append(tot)
            if (i + 1) % 50 == 0: print(f"  {i + 1}/{len(V)} inputs, {sum(per_in)} vertex outputs ({time.time() - t0:.0f} s)", flush=True)
    vs = json.loads((ROOT / "results/phase9/vertex_structure_deza9all.json").read_text())
    out = {"inputs": len(V), "vertex_outputs_total_upper_bound": sum(per_in),
           "per_move": {k: {"outputs": v[0], "vertex_outputs": v[1], "seconds": round(secs[k], 1)} for k, v in sorted(per.items())},
           "outputs_per_input_max": max(per_in), "outputs_per_input_mean": round(sum(per_in) / len(per_in), 1),
           "m9_orbits": vs["orbits"], "m9_with_8node_vertex_restriction": vs["largest_vertex_restriction"]["8"],
           "m9_non_primitive": vs["orbits"] - vs["primitive"], "seconds": round(time.time() - t0, 1)}
    print(json.dumps(out), flush=True)
    atomic_write_json(ROOT / "results/phase9/move_capacity.json", out)


if __name__ == "__main__":
    main()
