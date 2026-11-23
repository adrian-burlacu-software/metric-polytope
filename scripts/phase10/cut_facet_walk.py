#!/usr/bin/env python3
"""Track B′ facet walk on CUT_n: expand every SMAPO facet class and check every neighbour is listed.

Per class (one JSONL checkpoint line): roots, number of ridges, neighbour class keys (as indices into the list when
listed), unlisted neighbours (with a representative), seconds. Classes with more than --max-roots roots are deferred
(reported, not expanded) unless --max-roots 0. A per-class time limit is enforced by running each class in a pool
with a watchdog: classes still unfinished when only they remain and nothing has finished for --timeout s are flagged.

Summary: listed-key check (all SMAPO representatives are facets with distinct keys), unlisted neighbours (a real one
disproves completeness of the list), deferred/flagged classes, triangle adjacency (Deza–Dutour conjecture: every
facet is adjacent to a triangle facet), and a negative control (drop a class that some expanded class reaches; the
walk must then report it unlisted).

Usage: python -u scripts/phase10/cut_facet_walk.py --n 7 [--workers 18] [--max-roots 0] [--timeout 600] [--limit K]
Writes results/phase10/cut_facet_walk_n{n}.json; checkpoint checkpoints/phase10/cut_facet_walk_n{n}.jsonl.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time

import psutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase10"))

from metricpoly import cutfacets as cf, resguard  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402


def load_classes(n):
    if n == 9:
        import cap_lemma_lp9 as c9
        return c9.read_classes()
    import cap_lemma_lp as cl
    return cl.parse_classes(n)


def _key(args):
    n, i, a, b = args
    R = cf.roots(n, a, b)
    return i, cf.canon(n, a, b, R), len(R), cf.is_facet(n, a, b)


def _expand(args):
    n, i, a, b = args
    t = time.time()
    R = cf.roots(n, a, b)
    rid = cf.ridges(n, a, b, R)
    nb = {}
    for h0, h in rid:
        aG, bG = cf.rotate(n, a, b, h0, h)
        if not cf.is_facet(n, aG, bG):
            return {"i": i, "error": "rotation not a facet"}
        nb.setdefault(cf.canon(n, aG, bG), [list(aG), bG])
    return {"i": i, "roots": len(R), "ridges": len(rid), "nbr": nb, "s": round(time.time() - t, 3)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=18)
    ap.add_argument("--max-roots", type=int, default=0, help="defer classes with more roots (0 = expand all)")
    ap.add_argument("--timeout", type=float, default=600)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--sym-roots", type=int, default=50,
                    help="classes with more roots are expanded one at a time with Normaliz ridges + Stab_Sn orbit "
                         "reduction (cutfacets.expand_sym), after the parallel phase")
    ap.add_argument("--sym-budget", type=float, default=None, help="Normaliz time budget per class (s)")
    ap.add_argument("--only", type=str, default="", help="comma-separated class indices (0-based) to expand")
    a = ap.parse_args()
    n = a.n
    t0 = time.time()
    resguard.require_disk()
    C = load_classes(n)
    ck = ROOT / "checkpoints" / "phase10" / f"cut_facet_walk_n{n}.jsonl"
    kc = ROOT / "checkpoints" / "phase10" / f"cut_facet_keys_n{n}.json"
    ck.parent.mkdir(parents=True, exist_ok=True)
    with mp.get_context("spawn").Pool(a.workers) as pool:
        if kc.exists():
            K = json.loads(kc.read_text())
        else:
            K = sorted(pool.imap_unordered(_key, [(n, i, c[0], c[1]) for i, c in enumerate(C)], chunksize=64))
            atomic_write_json(kc, K)
    keys = {k: i for i, k, _, _ in K}
    roots = {i: r for i, _, r, _ in K}
    print(f"[CUT_{n}] {len(C)} classes, {len(keys)} distinct keys, all facets {all(f for *_, f in K)} "
          f"({time.time() - t0:.0f} s)", flush=True)
    done = {}
    if ck.exists():
        for ln in ck.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(ln)
                done[r["i"]] = r
            except json.JSONDecodeError:
                pass
    idx = list(range(len(C)))
    if a.only:
        idx = [int(x) for x in a.only.split(",")]
    if a.limit:
        idx = idx[:a.limit]
    todo = [i for i in idx if i not in done]
    deferred = [i for i in todo if a.max_roots and roots[i] > a.max_roots]
    todo = [i for i in todo if i not in set(deferred)]
    big = [i for i in todo if roots[i] > a.sym_roots]
    todo = [i for i in todo if roots[i] <= a.sym_roots]
    print(f"  {len(done)} done, {len(todo)} to expand, {len(deferred)} deferred (roots > {a.max_roots})", flush=True)
    with mp.get_context("spawn").Pool(a.workers) as pool, open(ck, "a", encoding="utf-8") as fh:
        asy = {i: pool.apply_async(_expand, ((n, i, C[i][0], C[i][1]),)) for i in todo}
        last = tl = time.time()
        while asy:
            fin = [i for i, x in asy.items() if x.ready()]
            for i in fin:
                r = asy.pop(i).get()
                r["nbr"] = {k: (keys[k] if k in keys else v) for k, v in r.get("nbr", {}).items()}
                done[i] = r
                fh.write(json.dumps(r) + "\n")
                fh.flush()
                last = time.time()
            if asy and len(asy) <= a.workers and time.time() - last > a.timeout:
                for i in list(asy):
                    done[i] = {"i": i, "flag": f"no result within {a.timeout:.0f} s", "roots": roots[i]}
                    fh.write(json.dumps(done[i]) + "\n")
                asy.clear()
                pool.terminate()
            if psutil.virtual_memory().available < 8 * 2 ** 30 or max(
                    (resguard.private_gb(c.pid) for c in psutil.Process().children(recursive=True)), default=0) > 16:
                pool.terminate()
                raise SystemExit(f"memory guard: stopping (resumable); pending classes {sorted(asy)[:30]}")
            if time.time() - tl > 60:
                tl = time.time()
                print(f"  {len(done)} expanded, {len(asy)} pending, {time.time() - t0:.0f} s", flush=True)
                resguard.require_disk()
            if not fin:
                time.sleep(0.2)
    from metricpoly import adjdec
    with open(ck, "a", encoding="utf-8") as fh:
        for i in sorted(big, key=lambda i: roots[i]):
            print(f"  class {i}: {roots[i]} roots, symmetric expansion", flush=True)
            try:
                r = cf.expand_sym(n, C[i][0], C[i][1], threads=a.workers, budget=a.sym_budget,
                                  log=lambda m: print(m, flush=True))
                r["i"] = i
                r["method"] = "sym"
                r["nbr"] = {k: (keys[k] if k in keys else [list(v[0]), v[1]]) for k, v in r["nbr"].items()}
            except adjdec.NmzTimeout:
                r = {"i": i, "flag": "Normaliz budget or memory cap exceeded", "roots": roots[i]}
            done[i] = r
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            print(f"    -> {r.get('flag') or str(len(r['nbr'])) + ' neighbour classes, ' + str(r['s']) + ' s'}",
                  flush=True)
    # ------------------------------------------------------------- summary
    exp = [r for r in done.values() if "nbr" in r]
    unl = {}
    for r in exp:
        for k, v in r["nbr"].items():
            if not isinstance(v, int):
                unl.setdefault(k, {"key": k, "rep": v, "from_class": r["i"]})
    errors = [r for r in done.values() if "error" in r]
    flagged = [r for r in done.values() if "flag" in r]
    tri = next(i for i, (av, b) in enumerate(C) if sorted(map(abs, av))[-3:] == [1, 1, 1] and sum(map(abs, av)) == 3)
    adj_tri = {i for i in range(len(C)) if i == tri}
    for r in exp:
        if r["i"] == tri:
            adj_tri |= {v for v in r["nbr"].values() if isinstance(v, int)}
        elif tri in r["nbr"].values():
            adj_tri.add(r["i"])
    ctrl = None
    reach = {}
    for r in exp:
        for v in r["nbr"].values():
            if isinstance(v, int) and v != r["i"]:
                reach.setdefault(v, r["i"])
    # negative control: if class j were missing from the list, the walk would report it unlisted exactly when some
    # OTHER expanded class has j as a neighbour. Count the classes for which that holds (ideally all of them).
    ctrl = {"classes_reached_from_another_class": len(reach),
            "every_single_drop_detected": len(reach) == len(C),
            "undetectable_if_dropped": sorted(set(range(len(C))) - set(reach))[:50]}
    out = {"n": n, "classes": len(C), "distinct_keys": len(keys), "all_listed_are_facets": all(f for *_, f in K),
           "expanded": len(exp), "deferred": deferred, "flagged": flagged, "errors": len(errors),
           "unlisted_neighbours": list(unl.values()), "triangle_class": tri,
           "classes_adjacent_to_triangle": len(adj_tri), "all_adjacent_to_triangle": len(adj_tri) == len(C),
           "negative_control": ctrl, "max_class_s": max((r["s"] for r in exp), default=0),
           "sum_class_s": round(sum(r["s"] for r in exp), 1), "wall_s": round(time.time() - t0, 1)}
    out["PASS_closed"] = (out["all_listed_are_facets"] and len(keys) == len(C) and not unl and not errors
                          and not flagged and not deferred and len(exp) == len(C))
    tag = "" if not (a.limit or a.only) else "_partial"
    atomic_write_json(ROOT / "results" / "phase10" / f"cut_facet_walk_n{n}{tag}.json", out)
    print(json.dumps({k: v for k, v in out.items() if k not in ("unlisted_neighbours", "flagged")}), flush=True)
    print(f"unlisted neighbours: {len(unl)}, flagged {len(flagged)}", flush=True)


if __name__ == "__main__":
    main()
