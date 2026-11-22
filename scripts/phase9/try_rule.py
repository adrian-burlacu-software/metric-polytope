#!/usr/bin/env python3
"""Agent tool (Phase 9): load a proposal .mpr on top of the current rule set and report what each rule does.

  generative rule : per n in --ns, number of points, exact feasibility, vertices, distinct orbits, and how many orbits
                    hit the CURRENT unreached nodes (results/phase9/unreached_nodes.json; n <= 9)
  move            : applies the move to --probe random reached/unreached node representatives; reports output sizes,
                    feasibility and vertex counts
  structural rule : evaluates it for each n in --ns (exhaustive vertex sets n <= 6, Deza reps n = 7, 8)
--emit OUT.json writes every feasible generated point (used by the judge). Never trust a point without this check.
Usage: python scripts/phase9/try_rule.py FILE.mpr [--ns 3-9] [--emit out.json] [--probe 20]
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, interpreter, load_json, verify_vertex  # noqa: E402

from metricpoly import group  # noqa: E402
from metricpoly.core import Point  # noqa: E402


def parse_ns(s):
    a, _, b = s.partition("-")
    return list(range(int(a), int(b or a) + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--ns", default="3-9")
    ap.add_argument("--emit")
    ap.add_argument("--probe", type=int, default=20)
    args = ap.parse_args()
    I, names = interpreter([args.file])
    unr_path = ROOT / "results/phase9/unreached_nodes.json"
    unreached = set(load_json(unr_path)["keys"]) if unr_path.exists() else set()
    unr_targets = set(load_json(unr_path)["target_keys"]) if unr_path.exists() else set()
    report, emitted = {}, []
    for name in names:
        if name in I.rules:
            rule = I.rules[name]
            rep = {"kind": rule.kind}
            for n in parse_ns(args.ns):
                lo_hi = rule.meta.get("domain", (3,))
                if n < lo_hi[0] or (len(lo_hi) > 1 and n > lo_hi[1]):
                    continue
                t = time.time()
                try:
                    val = I.run_rule(rule, n)
                except Exception as ex:
                    rep[n] = {"error": f"{type(ex).__name__}: {ex}"[:300]}
                    continue
                if rule.kind == "structural":
                    rep[n] = {"holds": bool(val), "seconds": round(time.time() - t, 2)}
                    continue
                pts = [p for p in val if isinstance(p, Point) and p.n == n]
                feas = [p for p in pts if verify_vertex(p)["feasible"]]
                verts = [p for p in feas if verify_vertex(p)["vertex"]]
                keys = {group.canonical(p).key() for p in feas} if n <= 9 else set()
                rep[n] = {"points": len(pts), "feasible": len(feas), "vertices": len(verts),
                          "orbits": len(keys), "hits_unreached_nodes": len(keys & unreached),
                          "hits_unreached_targets": len(keys & unr_targets), "seconds": round(time.time() - t, 2)}
                emitted += [{"rule": name, "n": p.n, "D": p.D, "nums": list(p.nums)} for p in feas]
            report[name] = rep
        elif name in I.moves:
            mv = I.moves[name]
            rng = random.Random(1)
            pool = []
            for n in (5, 6, 7):
                from metricpoly.dsl.prims import p_vertices
                pool += list(p_vertices(n))
            rep = {"kind": "move", "grow": mv.meta.get("grow")}
            outs = tot = feas = verts = 0
            t = time.time()
            for x in rng.sample(pool, min(args.probe, len(pool))):
                try:
                    o = I.apply_move(mv, [x])
                except Exception as ex:
                    rep["error"] = f"{type(ex).__name__}: {ex}"[:300]
                    break
                tot += 1
                outs += len(o)
                feas += sum(verify_vertex(p)["feasible"] for p in o)
                verts += sum(verify_vertex(p)["vertex"] for p in o)
            rep.update({"probed_inputs": tot, "outputs": outs, "feasible": feas, "vertices": verts,
                        "seconds": round(time.time() - t, 2)})
            report[name] = rep
    print(json.dumps(report, indent=1, default=str))
    if args.emit:
        Path(args.emit).write_text(json.dumps(emitted), encoding="utf-8")


if __name__ == "__main__":
    main()
