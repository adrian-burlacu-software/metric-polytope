#!/usr/bin/env python3
"""Adjacency-closure check of a published orbit list of m_n (n = 8: Deza's 533; n = 9: Orbits.zip, 1,056,367 rows).

For every listed orbit representative: tangent-cone extreme rays (exact cdd), each followed to the neighbouring vertex;
every neighbour COMPLETED (tight set, exact rank check) and canonicalised (metricpoly.canon_large: full group
switchings ⋊ S_n, validated). A neighbour orbit absent from the list is a MISS: it is verified exactly and saved.
Orbits whose walk exceeds the per-orbit timeout are FLAGGED (hard), set aside and reported.

Conclusion it supports: the vertex graph of m_n is connected, so if no listed orbit has a miss, every vertex outside the
list can only be adjacent to vertices of FLAGGED orbits; with no flags, the list is complete.

Parallel (19 workers), batches of BATCH orbits; each batch is written atomically to
checkpoints/phase10/closure_n{n}/batch_*.json and skipped on rerun (resumable). Workers return 12-byte hashes of the
neighbour keys plus the neighbour points; the main process holds only the hashes of the list keys.
Usage: python -u scripts/phase10/closure_check.py --n 8|9 [--workers 19] [--timeout 600] [--limit K]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np
import psutil

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from metricpoly import resguard  # noqa: E402
from metricpoly.jobs import atomic_write_json, code_version, git_head  # noqa: E402

BATCH = 500


def h(key: str) -> str:
    return hashlib.blake2b(key.encode(), digest_size=12).hexdigest()


def load_list(n):
    """[(row id, D, nums)] in lexicographic pair order."""
    if n == 9:
        co = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
        de = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
        return co, de
    from metricpoly import deza
    reps = list(deza.load_ext(n))
    return [x.nums for x in reps], [x.D for x in reps]


def _key_job(args):
    n, D, nums = args
    from metricpoly.canon_large import canonical_key
    from metricpoly.core import Point
    return h(canonical_key(Point.make(n, D, nums)))


def list_hashes(n, co, de, workers):
    if n == 9:                                    # reuse the keys from the n = 9 list check (same canonical form)
        ck = ROOT / "checkpoints" / "verify_n9_list"
        out = []
        for f in sorted(ck.glob("chunk_*.json")):
            out += [h(k) for k in json.loads(f.read_text())["keys"]]
        if len(out) == len(de):
            return out
    with mp.Pool(workers) as pool:
        return pool.map(_key_job, [(n, int(de[i]), [int(v) for v in co[i]]) for i in range(len(de))], chunksize=50)


def _walk(args):
    n, row, D, nums = args
    from metricpoly.canon_large import canonical_key
    from metricpoly.core import Point
    from metricpoly.ladder import rung
    R = rung(n - 1, n - 1)                        # top rung = m_n, edges in lexicographic pair order
    t = time.time()
    nb, nrays = R.neighbours(D, tuple(nums))
    found = {}
    nonvert = 0
    for Dy, y in nb:
        if not R.is_vertex(Dy, y):                # completion: full tight set + exact rank
            nonvert += 1
            continue
        k = canonical_key(Point.make(n, Dy, y))
        found.setdefault(h(k), (k, Dy, list(y)))
    return {"row": row, "rays": nrays, "nonvertex": nonvert, "nbr": found, "s": round(time.time() - t, 3)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=19)
    ap.add_argument("--timeout", type=float, default=600)
    ap.add_argument("--limit", type=int, default=0, help="only the first K rows (testing)")
    ap.add_argument("--defer-incidence", type=int, default=80,
                    help="n = 9: orbits with at least this many tight inequalities are not walked here but flagged "
                         "'deferred' for the hard-orbit step (A3); 0 = walk everything")
    ap.add_argument("--keep-partials", dest="prune_partials", action="store_false",
                    help="keep per-orbit neighbour detail after each batch (default: delete it; ~10-30 GB at n = 9)")
    args = ap.parse_args()
    n = args.n
    ck = ROOT / "checkpoints" / "phase10" / f"closure_n{n}"
    ck.mkdir(parents=True, exist_ok=True)
    out_dir = ROOT / "results" / "phase10"
    t0 = time.time()
    co, de = load_list(n)
    N = len(de) if not args.limit else min(args.limit, len(de))
    lh = list_hashes(n, co, de, args.workers)
    listset = set(lh)
    print(f"[closure n={n}] {len(de)} listed orbits, {len(listset)} distinct keys, checking {N}  ({time.time() - t0:.0f}s)",
          flush=True)
    deferred = {}
    if n == 9 and args.defer_incidence:
        inc = np.load(ROOT / "data/deza/orbits9/orbits9.npz")["incidence"]
        deferred = {int(r): int(inc[r]) for r in np.nonzero(inc[:N] >= args.defer_incidence)[0]}
        print(f"[closure n={n}] {len(deferred)} orbits with incidence >= {args.defer_incidence} deferred to the "
              f"hard-orbit step", flush=True)
    batches = [(b, list(range(b * BATCH, min((b + 1) * BATCH, N)))) for b in range((N + BATCH - 1) // BATCH)]
    for b, rows in batches:
        path = ck / f"batch_{b:05d}.json"
        if path.exists():
            part0 = ck / f"batch_{b:05d}.partial.jsonl"
            if args.prune_partials and part0.exists():
                part0.unlink()                                  # summary saved: the per-orbit detail is not needed
            continue
        resguard.require_disk()                                 # stop cleanly before starting a batch on a full disk
        tb = time.time()
        part = ck / f"batch_{b:05d}.partial.jsonl"           # per-orbit results as they finish (kept on interrupt)
        res = {}
        if part.exists():
            for line in part.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    x = json.loads(line)
                    res[x["row"]] = x
        for r in rows:
            if r not in res and r in deferred:
                res[r] = {"row": r, "flag": f"deferred: incidence {deferred[r]} >= {args.defer_incidence}",
                          "tight": deferred[r]}
        todo = [r for r in rows if r not in res]
        if todo:
            with mp.Pool(args.workers) as pool, open(part, "a", encoding="utf-8", newline="\n") as pf:
                asy = {r: pool.apply_async(_walk, ((n, r, int(de[r]), [int(v) for v in co[r]]),)) for r in todo}
                last = last_mem = time.time()
                while asy:
                    done_now = [r for r, a in asy.items() if a.ready()]
                    for r in done_now:
                        x = asy.pop(r).get()
                        res[r] = x
                        pf.write(json.dumps(x) + "\n")
                        pf.flush()
                        last = time.time()
                    # per-orbit timeout: once only stuck orbits remain (at most one per worker) and nothing has
                    # finished for `timeout` seconds, the remaining ones are hard
                    if asy and len(asy) <= args.workers and time.time() - last > args.timeout:
                        for r in list(asy):
                            res[r] = {"row": r, "flag": f"hard: no result within {args.timeout:.0f} s",
                                      "tight": int(len(__import__("metricpoly.ladder", fromlist=["rung"]).rung(
                                          n - 1, n - 1).tight(int(de[r]), tuple(int(v) for v in co[r]))))}
                            pf.write(json.dumps(res[r]) + "\n")
                            pf.flush()
                        asy.clear()
                    if not done_now:
                        time.sleep(0.5)
                    if time.time() - last > 2 * args.timeout:
                        pool.terminate()
                        raise SystemExit(f"stalled: nothing finished for {2 * args.timeout:.0f} s in batch {b}; "
                                         f"stopping (resumable). Pending rows: {sorted(asy)[:30]}")
                    if time.time() - last_mem > 10:
                        last_mem = time.time()
                        avail = psutil.virtual_memory().available / 2 ** 30
                        worst = max((resguard.private_gb(c.pid) for c in psutil.Process().children(recursive=True)),
                                    default=0.0)
                        if avail < 8 or worst > 12:
                            pool.terminate()
                            raise SystemExit(f"memory guard: {avail:.1f} GB available, largest worker {worst:.1f} GB; "
                                             f"stopping (resumable). Pending rows: {sorted(asy)[:30]}")
                    if not resguard.disk_ok():
                        pool.terminate()
                        resguard.require_disk()                 # raises LowDisk; finished orbits are in the partial
                pool.terminate()
        misses = {}
        for r, x in res.items():
            for hk, (k, Dy, y) in x.get("nbr", {}).items():
                if hk not in listset:
                    misses.setdefault(hk, {"key": k, "D": Dy, "nums": y, "found_from_row": r})
        rec = {"batch": b, "rows": [rows[0], rows[-1]], "walked": sum(1 for x in res.values() if "flag" not in x),
               "flagged": [x for x in res.values() if "flag" in x],
               "rays": {r: x["rays"] for r, x in res.items() if "rays" in x},
               "seconds": {r: x["s"] for r, x in res.items() if "s" in x},
               "nonvertex_neighbours": sum(x.get("nonvertex", 0) for x in res.values()),
               "misses": list(misses.values())}
        atomic_write_json(path, rec)
        if args.prune_partials:
            part.unlink(missing_ok=True)                        # the batch summary holds everything the report needs
        done = b + 1
        el = time.time() - t0
        print(f"[closure n={n}] batch {done}/{len(batches)}: walked {rec['walked']}, flagged {len(rec['flagged'])}, "
              f"misses {len(misses)}, {time.time() - tb:.0f}s; elapsed {el / 60:.1f} min", flush=True)
    # summary
    walked = flagged = nonv = 0
    misses, flags, rays = {}, [], []
    for b, _ in batches:
        rec = json.loads((ck / f"batch_{b:05d}.json").read_text())
        walked += rec["walked"]
        flags += rec["flagged"]
        nonv += rec["nonvertex_neighbours"]
        rays += list(rec["rays"].values())
        for m in rec["misses"]:
            misses.setdefault(m["key"], m)
    # exact verification of every miss
    from metricpoly.core import Point
    from metricpoly.dsl.prims import p_vertex
    for m in misses.values():
        m["verified_vertex"] = bool(p_vertex(Point.make(n, m["D"], m["nums"])))
    summ = {"n": n, "listed_orbits": len(de), "checked": N, "walked": walked, "flagged_hard": flags,
            "misses": list(misses.values()), "nonvertex_neighbours": nonv,
            "rays_mean": float(np.mean(rays)) if rays else None, "rays_max": int(max(rays)) if rays else None,
            "closed": not misses, "complete_if_no_flags": (not misses) and not flags,
            "code_version": code_version(), "git": git_head(), "seconds": round(time.time() - t0, 1)}
    atomic_write_json(out_dir / f"closure_n{n}{'_limit' + str(N) if args.limit else ''}.json", summ)
    print(json.dumps({k: v for k, v in summ.items() if k not in ("misses",)}, indent=1, default=str))
    print(f"misses: {len(misses)}")


if __name__ == "__main__":
    main()
