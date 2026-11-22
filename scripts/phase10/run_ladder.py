#!/usr/bin/env python3
"""Phase 10: edge-by-edge ladder from m_{nK} to m_{nK+1} (rungs G_0 .. G_nK; see metricpoly/ladder.py).

Rung 0 = m_{nK} with an isolated extra node: seeded from Deza's m_{nK} orbit representatives.
Per rung k >= 1:
  1. SEED: lift every orbit representative of rung k-1 through the new edge e = (k-1, w): for every constraint of rung k
     containing e, solve for x_e making it tight; keep the candidate if it is feasible and its completed tight set has
     full rank (a vertex of P_k).
  2. WALK: breadth-first over orbits in parallel waves. For each orbit representative: tangent-cone extreme rays
     (exact cdd), each followed to the neighbour; every neighbour is COMPLETED (tight set + exact rank check) and then
     canonicalised under Aut(G_k) with switchings. New orbits join the next wave. Closure = a wave adds nothing.
  3. HARD orbits: an orbit whose neighbour enumeration exceeds ORBIT_TIMEOUT is set aside (flagged), reported
     separately, and NOT walked.
Per rung records: orbits, vertices (sum of orbit sizes), denominators, seconds, flagged orbits.
Checkpoints: checkpoints/phase10/ladder_n{nK+1}/rung_{k}.jsonl (one orbit per line, with a 'walked' flag) and
state.json (params, code version); --resume refuses on a code/param change unless --force.
Usage: python -u scripts/phase10/run_ladder.py --nK 7 [--workers 19] [--resume] [--force] [--rungs 0-7]
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from metricpoly import deza  # noqa: E402
from metricpoly.core import pairs  # noqa: E402
from metricpoly.jobs import atomic_write_json, code_version, git_head  # noqa: E402
from metricpoly.ladder import rung  # noqa: E402

ORBIT_TIMEOUT = 600


def _walk(args):
    nK, k, D, nums = args
    R = rung(nK, k)
    t = time.time()
    nb, nrays = R.neighbours(D, tuple(nums))
    found = {}
    nonvert = 0
    for Dy, y in nb:
        if not R.is_vertex(Dy, y):                 # completion: full tight set + exact rank
            nonvert += 1
            continue
        key = R.canonical_key(Dy, y)
        if key not in found:
            found[key] = (Dy, list(y))
    return {"rays": nrays, "nonvertex": nonvert, "found": found, "s": round(time.time() - t, 3)}


def _info(args):
    nK, k, D, nums = args
    R = rung(nK, k)
    return R.orbit_size(D, tuple(nums)), len(R.tight(D, tuple(nums)))


class RungStore:
    def __init__(self, path: Path):
        self.path = path
        self.orbits = {}                            # key -> {"D", "nums", "walked", "flag"}
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    d = json.loads(line)
                    self.orbits[d["key"]] = d

    def add(self, key, D, nums, how):
        if key in self.orbits:
            return False
        self.orbits[key] = {"key": key, "D": D, "nums": list(nums), "walked": False, "how": how}
        return True

    def save(self):
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            for d in self.orbits.values():
                f.write(json.dumps(d) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.path)


def seed_rung0(nK, store):
    R = rung(nK, 0)
    order = {e: t for t, e in enumerate(pairs(nK))}
    for x in deza.load_ext(nK):
        nums = tuple(x.nums[order[e]] for e in R.edges)
        assert R.is_vertex(x.D, nums)
        store.add(R.canonical_key(x.D, nums), x.D, nums, "Deza m_%d rep" % nK)


def seed_from(nK, k, prev: RungStore, store):
    """Lift every rung-(k-1) representative through the new edge (k-1, w)."""
    Rp, R = rung(nK, k - 1), rung(nK, k)
    e_new = (k - 1, R.w)
    te = R.eidx[e_new]
    rows = [i for i in range(len(R.b)) if R.A[i, te] != 0]
    added = 0
    for d in prev.orbits.values():
        D = d["D"]
        old = dict(zip(Rp.edges, d["nums"]))
        for i in rows:
            c = int(R.A[i, te])
            rest = sum(int(R.A[i, t]) * old[e] for t, e in enumerate(R.edges) if e != e_new and R.A[i, t])
            val = Fraction(int(R.b[i]) * D - rest, c * D)            # x_e making row i tight
            den = D * val.denominator // __import__("math").gcd(D, val.denominator)
            nums = tuple(int(Fraction(old[e], D) * den) if e != e_new else int(val * den) for e in R.edges)
            if R.is_vertex(den, nums):
                added += store.add(R.canonical_key(den, nums), den, nums, f"lift of rung {k - 1}")
    return added


def walk_rung(nK, k, store, workers, log):
    t0 = time.time()
    wave = 0
    flagged = []
    while True:
        todo = [d for d in store.orbits.values() if not d["walked"] and not d.get("flag")]
        if not todo:
            break
        wave += 1
        with mp.Pool(workers) as pool:                  # one pool per wave: a hung hard orbit dies with it
            asy = [(d, pool.apply_async(_walk, ((nK, k, d["D"], d["nums"]),))) for d in todo]
            new = 0
            rays = []
            deadline = time.time() + ORBIT_TIMEOUT * (1 + len(todo) / workers)
            stuck = False
            for d, a in asy:
                try:
                    r = a.get(timeout=max(1.0, min(deadline - time.time(), ORBIT_TIMEOUT * 2)))
                except mp.TimeoutError:
                    d["flag"] = f"hard: neighbour enumeration > {ORBIT_TIMEOUT} s"
                    flagged.append(d["key"])
                    stuck = True
                    continue
                d["walked"] = True
                d["rays"] = r["rays"]
                rays.append(r["rays"])
                if r["nonvertex"]:
                    d["nonvertex_neighbours"] = r["nonvertex"]
                for key, (Dy, y) in r["found"].items():
                    new += store.add(key, Dy, y, f"walk wave {wave}")
            pool.terminate()
        store.save()
        log(f"[rung {k}] wave {wave}: walked {len(todo) - len([d for d in todo if d.get('flag')])}, new {new}, "
            f"total {len(store.orbits)}, mean rays {sum(rays) / max(1, len(rays)):.0f}, {time.time() - t0:.0f}s")
    return flagged, time.time() - t0


def summarise(nK, k, store, workers, secs, flagged):
    with mp.Pool(workers) as pool:
        res = pool.map(_info, [(nK, k, d["D"], d["nums"]) for d in store.orbits.values()], chunksize=8)
    sizes = [s for s, _ in res]
    return {"rung": k, "orbits": len(store.orbits), "vertices": int(sum(sizes)),
            "denominators": dict(sorted(Counter(d["D"] for d in store.orbits.values()).items())),
            "max_incidence": max(t for _, t in res), "seconds": round(secs, 1),
            "flagged_hard": flagged, "group_order": rung(nK, k).group_order}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nK", type=int, default=7)
    ap.add_argument("--workers", type=int, default=19)
    ap.add_argument("--rungs", default=None, help="e.g. 0-7")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    nK = args.nK
    ck = ROOT / "checkpoints" / "phase10" / f"ladder_n{nK + 1}"
    ck.mkdir(parents=True, exist_ok=True)
    params = {"nK": nK, "orbit_timeout": ORBIT_TIMEOUT}
    stp = ck / "state.json"
    state = json.loads(stp.read_text()) if stp.exists() else None
    cv = code_version()
    if state and args.resume:
        if (state["code_version"] != cv or state["params"] != params) and not args.force:
            raise SystemExit(f"refusing to resume: code {state['code_version']} -> {cv} or params changed (use --force)")
    elif state and not args.resume:
        bak = ck.with_name(ck.name + ".bak-" + time.strftime("%Y%m%d-%H%M%S"))
        ck.rename(bak)
        ck.mkdir(parents=True)
        state = None
    state = state or {"params": params, "summary": {}}
    state.update(code_version=cv, git=git_head())
    out = ROOT / "results" / "phase10" / f"ladder_n{nK + 1}.json"
    logf = open(ROOT / "results" / "phase10" / f"ladder_n{nK + 1}.log", "a", encoding="utf-8")

    def log(msg):
        print(msg, flush=True)
        logf.write(msg + "\n")
        logf.flush()

    lo, hi = (0, nK) if not args.rungs else map(int, args.rungs.split("-"))
    prev = None
    for k in range(0, hi + 1):
        store = RungStore(ck / f"rung_{k}.jsonl")
        if k < lo or str(k) in state["summary"]:
            prev = store
            continue
        t0 = time.time()
        if k == 0:
            if not store.orbits:
                seed_rung0(nK, store)
                store.save()
            for d in store.orbits.values():         # rung 0 = m_nK itself: orbits are given, no walk needed
                d["walked"] = True
            store.save()
            flagged, secs = [], time.time() - t0
        else:
            if not store.orbits:
                n_seed = seed_from(nK, k, prev, store)
                store.save()
                log(f"[rung {k}] seeded {n_seed} orbits from rung {k - 1} ({time.time() - t0:.0f}s)")
            flagged, secs = walk_rung(nK, k, store, args.workers, log)
        summ = summarise(nK, k, store, args.workers, secs, flagged)
        state["summary"][str(k)] = summ
        atomic_write_json(stp, state)
        atomic_write_json(out, state)
        log(f"[rung {k}] DONE: {summ['orbits']} orbits, {summ['vertices']} vertices, denominators "
            f"{summ['denominators']}, {summ['seconds']} s, flagged {len(flagged)}")
        prev = store
    logf.close()


if __name__ == "__main__":
    main()
