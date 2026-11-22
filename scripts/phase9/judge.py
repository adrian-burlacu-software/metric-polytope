#!/usr/bin/env python3
"""Phase 9 judge: the only arbiter. Agents' claims count only after this script confirms them.

  init                : targets = all m_7 and m_8 orbit reps + a seeded random 1,000 of the n = 9 uniform sample
                        (design A); baseline reachability with the current rule set (uniform base; lift, radial 1-3,
                        gluing); validated against the Phase 4c DP (n = 8) and the design-A records (n = 9).
  round R [--budget S]: evaluates phase9/round_R/maker/*.mpr (new rules) and phase9/round_R/breaker/*.json
                        (candidate points), writes results/phase9/round_R.{json,md}, appends accepted rules to
                        rules/phase9_accepted.mpr.
Usage: python -u scripts/phase9/judge.py init | round 1 [--budget 300] [--workers 19]
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from metricpoly import deza, group  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.graphic import orbit_is_graphic  # noqa: E402
from metricpoly.jobs import atomic_write_json, atomic_write_text, code_version, git_head  # noqa: E402
from metricpoly.reach import Engine  # noqa: E402

SEED = 20261122
OUT = ROOT / "results" / "phase9"
CK = ROOT / "checkpoints" / "phase9"
N9_TARGETS = 1000


def load_base():
    b = json.loads((ROOT / "results/n9/base_keys.json").read_text())
    return {int(n): set(v) for n, v in b.items() if not n.startswith("_")}


def make_is_base(base, extra=None):
    extra = extra or set()
    cache = {}

    def is_base(k):
        if k in cache:
            return cache[k]
        n = int(k.split("|")[0])
        v = k in base.get(n, ()) or k in extra
        if not v and n == 9:
            D = int(k.split("|")[1])
            v = orbit_is_graphic(Point.make(9, D, [int(t) for t in k.split("|")[2].split(",")]))
        cache[k] = v
        return v
    return is_base


def targets():
    T = [(7, i + 1, x) for i, x in enumerate(deza.load_ext(7))] + [(8, i + 1, x) for i, x in enumerate(deza.load_ext(8))]
    samp = json.loads((ROOT / "results/n9/sample_A.json").read_text())
    rng = np.random.default_rng(SEED)
    rows = sorted(int(r) for r in rng.choice(samp["uniform"], N9_TARGETS, replace=False))
    coords = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
    dens = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
    T += [(9, r, Point.make(9, int(dens[r]), [int(v) for v in coords[r]])) for r in rows]
    return T


def summarize(eng, T, reached):
    out = {}
    for n in (7, 8, 9):
        ids = [i for i, (m, o, _) in enumerate(T) if m == n and isinstance(o, int)]   # breaker-added points excluded
        r = sum(1 for i in ids if eng.target_key(i) in reached)
        out[n] = {"targets": len(ids), "reached": r, "unreached": len(ids) - r,
                  "unreached_fraction": (len(ids) - r) / len(ids)}
    return out


def cmd_init(args):
    T = targets()
    eng = Engine(CK / "engine", workers=args.workers)
    eng.add_targets([x for _, _, x in T])
    t = time.time()
    reached, _ = eng.run(make_is_base(load_base()))
    summ = summarize(eng, T, reached)
    # validation against earlier, independent computations
    d2 = json.loads((ROOT / "results/phase4c/detour_depth2.json").read_text())["raw"]
    want8 = {r["orbit"] for r in d2["detour@8"]["rows"] if r["depth"] is not None}
    got8 = {o for i, (n, o, _) in enumerate(T) if n == 8 and eng.target_key(i) in reached}
    recs = {json.loads(l)["row"]: json.loads(l) for l in gzip.open(ROOT / "results/n9/orbits_A.jsonl.gz", "rt")}
    want9 = {o for n, o, _ in T if n == 9 and recs[o]["depth_detour"] is not None}
    got9 = {o for i, (n, o, _) in enumerate(T) if n == 9 and eng.target_key(i) in reached}
    val = {"n8_equal_to_phase4c_DP": got8 == want8, "n8_diff": sorted(got8 ^ want8),
           "n9_equal_to_designA": got9 == want9, "n9_diff": sorted(got9 ^ want9)}
    base = {"seed": SEED, "code_version": code_version(), "git": git_head(), "summary": summ, "validation": val,
            "seconds": round(time.time() - t, 1),
            "reached_targets": {f"{n}:{o}": reached[eng.target_key(i)] for i, (n, o, _) in enumerate(T)
                                if eng.target_key(i) in reached},
            "n9_rows": [o for n, o, _ in T if n == 9]}
    OUT.mkdir(parents=True, exist_ok=True)
    atomic_write_json(OUT / "baseline.json", base)
    atomic_write_json(CK / "reached.json", {k: list(v) if isinstance(v, tuple) else v for k, v in reached.items()})
    print(json.dumps({"summary": summ, "validation": val}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["init", "round", "state"])
    ap.add_argument("round_no", nargs="?", type=int)
    ap.add_argument("--budget", type=float, default=300)
    ap.add_argument("--workers", type=int, default=19)
    ap.add_argument("--round-cap", type=float, default=1800)   # 30 min per round (user decision 2026-11-22, back from 1 h)
    ap.add_argument("--dry-run", action="store_true", help="evaluate but change no state (testing)")
    args = ap.parse_args()
    if args.cmd == "init":
        cmd_init(args)
    elif args.cmd == "state":                      # (re)write agent-facing state files from the current reached set
        from phase9_round import load_state, write_state
        reached, st = load_state()
        write_state(Engine(CK / "engine", workers=args.workers), targets(), reached, st)
    else:
        from phase9_round import cmd_round  # noqa: E402
        cmd_round(args)


if __name__ == "__main__":
    main()
