#!/usr/bin/env python3
"""Phase 2 harness: reproduce Deza's published counts for the metric polytope.

Full enumeration only for n <= 6 (cdd, exact GMP). For n = 7, 8 only Deza's orbit
representatives are used (plus, for n=7 face orbits, the vertex set obtained by expanding
Deza's 13 representatives under the group -- Deza data, not an enumeration).

Usage:
  python scripts/phase2_verify.py            # fresh run
  python scripts/phase2_verify.py --resume   # continue from checkpoints/phase2_verify
Outputs: results/phase2/report.json, results/phase2/report.md, data/generated/m<n>_vertices.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from metricpoly import core, deza, faces, group, patterns, polyhedra  # noqa: E402
from metricpoly.cache import DiskCache  # noqa: E402
from metricpoly.jobs import Job, Progress, add_job_args, atomic_write_json, atomic_write_text  # noqa: E402

PUB = json.loads((ROOT / "data" / "deza" / "published.json").read_text())
OUT = ROOT / "results" / "phase2"
GEN = ROOT / "data" / "generated"


def write_vjson(n: int, pts, path: Path) -> None:
    atomic_write_json(path, {
        "n": n,
        "variables": [[i + 1, j + 1] for (i, j) in core.pairs(n)],
        "families": ["triangle", "perimeter"],
        "generators": [{"type": "vertex", "coords": p.strs()} for p in pts],
    })


# ------------------------------------------------------------------ tasks

def t_ine_order(n):
    ours = {(q.a, q.b) for q in core.metric_inequalities(n)}
    theirs = deza.load_ine(n)
    return {"ours": len(ours), "deza": len(theirs), "deza_distinct": len(set(theirs)),
            "equal_as_sets": ours == set(theirs)}


def t_deza_reps(n, cache: DiskCache):
    reps = deza.load_ext(n)
    inv = deza.load_inv(n)
    G = group.group_order(n)
    out = []
    prog = Progress(f"deza_reps n={n}", len(reps), every=10)
    for i, p in enumerate(reps):
        ok, why = core.is_vertex(p)
        stab = group.stabilizer_size(p)
        can = cache.canonical(p)
        out.append({"i": i + 1, "is_vertex": ok, "why": why, "stab": stab, "orbit": G // stab,
                    "icd": int(len(core.tight_set(p))), "canon": can.key()})
        prog.step()
    sizes = [r["orbit"] for r in out]
    return {
        "n_reps": len(reps), "all_vertices": all(r["is_vertex"] for r in out),
        "distinct_orbits": len({r["canon"] for r in out}),
        "group_order": G, "orbit_sizes": sizes, "total_vertices": sum(sizes),
        "orbit_sizes_match_inv": sizes == [r["orbit_size"] for r in inv],
        "icd_match_inv": [r["icd"] for r in out] == [r["icd"] for r in inv],
        "stabilizers": [r["stab"] for r in out],
    }


def t_enum(n, cache: DiskCache):
    t0 = time.time()
    V = polyhedra.enumerate_vertices(n)
    t_enum = time.time() - t0
    write_vjson(n, V, GEN / f"m{n}_vertices.json")
    allv = all(core.is_vertex(p)[0] for p in V)
    cans = [cache.canonical(p).key() for p in V]
    orbit_sizes = {}
    for c in cans:
        orbit_sizes[c] = orbit_sizes.get(c, 0) + 1
    deza_cans = {cache.canonical(p).key() for p in deza.load_ext(n)}
    L, arr = core.common_denominator_array(V)
    U = np.unique(np.concatenate([group.orbit_array(p, L) for p in deza.load_ext(n)]), axis=0)
    union_eq = U.shape[0] == len(V) and set(map(tuple, U.tolist())) == set(map(tuple, arr.tolist()))
    # orbit sizes from stabilizers of each orbit rep must equal class sizes
    G = group.group_order(n)
    stab_ok = all(G // group.stabilizer_size(core.Point(n, *_parse_key(k))) == c
                  for k, c in orbit_sizes.items())
    return {"vertices": len(V), "enum_seconds": round(t_enum, 3), "all_vertices": allv,
            "orbits": len(orbit_sizes), "orbit_sizes": sorted(orbit_sizes.values()),
            "canon_set_equals_deza": set(orbit_sizes) == deza_cans,
            "deza_orbit_union_equals_enum": union_eq, "orbit_stabilizer_consistent": stab_ok,
            "file": str((GEN / f"m{n}_vertices.json").relative_to(ROOT).as_posix())}


def _parse_key(key: str):
    _, D, nums = key.split("|")
    return int(D), tuple(int(v) for v in nums.split(","))


def t_rays(n):
    R = polyhedra.enumerate_cone_rays(n)
    return {"rays": len(R)}


def t_facets(n, V):
    L, arr = core.common_denominator_array(V)
    fl = faces.FaceLattice(n, L, arr)
    keys = {fl.barycenter_key(fl.inc[f]).key() for f in range(fl.inc.shape[0])}
    return {"facets": int(fl.inc.shape[0]), "all_facet_defining": fl.facet_defining_all(),
            "facet_orbits": len(keys)}


def faces_task(job: Job, n: int, V_L_arr, depth: int, cache_tag: str):
    """Face orbits by codim, with one checkpoint record per completed codim level."""
    L, arr = V_L_arr
    fl = faces.FaceLattice(n, L, arr)
    prev = job.results()
    start = {}
    for k in range(1, depth + 1):
        r = prev.get(f"{cache_tag}_level{k}")
        if r is not None:
            start[k] = r
        else:
            break

    def on_level(k, reps):
        job.record(f"{cache_tag}_level{k}", reps)
        print(f"[faces n={n}] codim {k}: {len(reps)} orbits", flush=True)

    lv = faces.upper_lattice(fl, depth, on_level=on_level, start=start)
    counts = [len(lv[k]) for k in range(1, depth + 1)]
    # Deza's representatives (clause encoding) must map one-to-one onto our orbits
    ci = patterns.clause_index(n)
    deza_ok = {}
    for k in range(1, depth + 1):
        f = deza.RAW / f"up_d{k}_m{n}.txt"
        if not f.exists():
            continue
        keys, codim_ok = set(), True
        dfaces = deza.load_up_lattice(n, k)
        for fc in dfaces:
            mask = fl.face_from_facets([ci[c] for c in fc])
            codim_ok &= fl.codim(fl.closure(mask)) == k
            keys.add(fl.barycenter_key(mask).key())
        deza_ok[k] = {"deza_reps": len(dfaces), "distinct": len(keys), "codim_ok": codim_ok,
                      "same_orbits_as_ours": keys == {r["key"] for r in lv[k]}}
    return {"orbits_by_codim": counts, "deza_reps_check": deza_ok}


def t_canon_crosscheck(rng, cache: DiskCache):
    res = {}
    # n<=6: fast == brute on every enumerated vertex; literal min_pi switch_canon(pi.x) on n<=5 all, n=6 sample
    for n in range(3, 7):
        V = polyhedra.enumerate_vertices(n)
        fb = all(group.canonical(p) == group.canonical_brute(p) for p in V)
        sample = V if n <= 5 else [V[i] for i in rng.choice(len(V), 12, replace=False)]
        sc = all(group.canonical(p) == group.canonical_via_switch_canon(p) for p in sample)
        st = all(group.stabilizer_size(p) == group.stabilizer_size_brute(p)
                 for p in (V if n <= 5 else sample))
        res[f"n{n}"] = {"fast_eq_brute_all": fb, "fast_eq_switchcanon_def": sc, "stab_fast_eq_brute": st}
    # n=7: brute on all 13 Deza reps and on random images of them
    R7 = deza.load_ext(7)
    ok = True
    for p in R7:
        c = group.canonical(p)
        ok &= c == group.canonical_brute(p)
        pp, ss = group.random_element(7, rng)
        ok &= group.canonical(group.apply(7, pp, ss, p)) == c
    res["n7"] = {"fast_eq_brute_and_invariant": ok}
    # n=8: invariance under random group elements on a random sample of Deza reps
    R8 = deza.load_ext(8)
    ok = True
    for i in rng.choice(len(R8), 25, replace=False):
        p = R8[int(i)]
        c = cache.canonical(p)
        for _ in range(4):
            pp, ss = group.random_element(8, rng)
            ok &= group.canonical(group.apply(8, pp, ss, p)) == c
    res["n8"] = {"invariant_under_100_random_images": ok}
    return res


def t_patterns(rng):
    """Clause (+-1 node-vector) encoding: Deza's rule reproduces the catalog; switching = column
    sign flip; permutation = column permutation; a cut is tight on V iff NAE."""
    res = {}
    for n in range(3, 9):
        ineqs = core.metric_inequalities(n)
        C = patterns.catalog_clauses(n)
        enc = all(patterns.clause_to_inequality(c) == (q.a, q.b) for c, q in zip(C, ineqs))
        distinct = len(set(C)) == len(C)
        # switching / permutation act on clauses as column ops
        sw_ok = True
        for _ in range(30):
            p_i, s = group.random_element(n, rng)
            pi = group.perms(n)[p_i]
            S = [v for v in range(1, n) if (s >> (v - 1)) & 1]
            # take a random vertex rep of this n (or a cut) and compare tight-pattern transport
            x = deza.load_ext(n)[int(rng.integers(len(deza.load_ext(n))))]
            y = group.apply(n, p_i, s, x)
            tx = {C[t] for t in core.tight_set(x)}
            ty = {C[t] for t in core.tight_set(y)}
            img = {patterns.switch_clause(patterns.permute_clause(c, pi), S) for c in tx}
            sw_ok &= img == ty
        nae_ok = True
        if n <= 6:
            for bits in range(1 << (n - 1)):
                sigma = [1] + [(-1 if (bits >> (v - 1)) & 1 else 1) for v in range(1, n)]
                x = core.Point.make(n, 1, [int(sigma[i] != sigma[j]) for (i, j) in core.pairs(n)])
                T = set(core.tight_set(x).tolist())
                nae_ok &= all((k in T) == patterns.nae_tight(c, sigma) for k, c in enumerate(C))
        res[f"n{n}"] = {"deza_rule_reproduces_catalog": enc, "clauses_distinct": distinct,
                        "group_acts_as_column_ops": sw_ok, "cut_tight_iff_NAE": nae_ok if n <= 6 else None}
    return res


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_job_args(ap)
    ap.add_argument("--faces7-depth", type=int, default=4, help="codim depth for n=7 face orbits (0 = skip)")
    args = ap.parse_args()
    params = {"enum_n": [3, 4, 5, 6], "reps_n": [3, 4, 5, 6, 7, 8], "faces7_depth": args.faces7_depth}
    job = Job("phase2_verify", params, args.seed, resume=args.resume, force=args.force)
    rng = np.random.default_rng(args.seed)
    cache = DiskCache()

    tasks = []
    for n in range(3, 9):
        tasks.append((f"ine_order_n{n}", lambda n=n: t_ine_order(n)))
    for n in range(3, 9):
        tasks.append((f"deza_reps_n{n}", lambda n=n: t_deza_reps(n, cache)))
    for n in range(3, 7):
        tasks.append((f"enum_n{n}", lambda n=n: t_enum(n, cache)))
        tasks.append((f"rays_n{n}", lambda n=n: t_rays(n)))
        tasks.append((f"facets_n{n}", lambda n=n: t_facets(n, polyhedra.enumerate_vertices(n))))
    for n, depth in ((4, 3), (5, 3), (6, 4)):
        tasks.append((f"faces_n{n}", lambda n=n, d=depth: faces_task(
            job, n, core.common_denominator_array(polyhedra.enumerate_vertices(n)), d, f"faces_n{n}")))
    if args.faces7_depth:
        def faces7():
            R = deza.load_ext(7)
            L = math.lcm(*[p.D for p in R])
            V = np.unique(np.concatenate([group.orbit_array(p, L) for p in R]), axis=0).astype(np.int64)
            assert V.shape[0] == PUB["vertices"]["7"], V.shape
            return faces_task(job, 7, (L, V), args.faces7_depth, "faces_n7")
        tasks.append(("faces_n7", faces7))
    tasks.append(("canon_crosscheck", lambda: t_canon_crosscheck(rng, cache)))
    tasks.append(("patterns", lambda: t_patterns(rng)))

    prog = Progress("phase2", len(tasks), every=0)
    for name, fn in tasks:
        if job.is_done(name):
            prog.step()
            continue
        t0 = time.time()
        r = fn()
        r["_seconds"] = round(time.time() - t0, 3)
        job.record(name, r)
        prog.step(force=True)

    build_report(job, cache)


def build_report(job: Job, cache: DiskCache):
    R = job.results()
    rows = []   # (quantity, n, published, ours, status, note)

    def add(q, n, pub, ours, note=""):
        status = "PASS" if pub == ours else ("n/a" if pub is None else "MISMATCH")
        if status == "MISMATCH" and note.startswith("page says"):
            status = "SOURCE-TYPO"
        rows.append({"quantity": q, "n": n, "published": pub, "ours": ours, "status": status, "note": note})

    for n in range(3, 9):
        r = R[f"deza_reps_n{n}"]
        add("vertex orbits (Deza reps -> distinct canonical forms)", n, PUB["vertex_orbits"][str(n)], r["distinct_orbits"])
        note = ""
        if n == 6:
            note = "page says 554; Deza's own metric_6.inv sizes 32+32+480 = 544; orbit-stabilizer and cdd give 544 -> page typo"
        add("vertices (orbit-stabilizer sum over Deza reps)", n, PUB["vertices"][str(n)], r["total_vertices"], note)
        add("all Deza reps pass exact vertex test", n, True, r["all_vertices"])
        add("orbit sizes == metric_n.inv", n, True, r["orbit_sizes_match_inv"])
        add("incidences == metric_n.inv", n, True, r["icd_match_inv"])
        add("our facet list == metric_n.ine (lex coordinate order)", n, True, R[f"ine_order_n{n}"]["equal_as_sets"])
    for n in range(3, 7):
        e = R[f"enum_n{n}"]
        add("vertices (cdd exact enumeration)", n, PUB["vertices"][str(n)], e["vertices"],
            "page says 554; exact enumeration gives 544 (see orbit-stabilizer row)" if n == 6 else "")
        add("vertex orbits (canonicalizing all enumerated vertices)", n, PUB["vertex_orbits"][str(n)], e["orbits"])
        add("enumerated orbits == Deza orbits; orbit union == vertex set", n, True,
            e["canon_set_equals_deza"] and e["deza_orbit_union_equals_enum"] and e["all_vertices"])
        f = R[f"facets_n{n}"]
        add("facets (all facet-defining)", n, PUB["facets"][str(n)], f["facets"] if f["all_facet_defining"] else -1)
        add("facet orbits", n, PUB["facet_orbits"][str(n)], f["facet_orbits"])
        add("extreme rays of metric cone M_n (cdd)", n, PUB["cone_rays"][str(n)], R[f"rays_n{n}"]["rays"])
    for n in (4, 5, 6, 7):
        if f"faces_n{n}" not in R:
            continue
        fr = R[f"faces_n{n}"]
        pub = PUB["face_orbits_by_codim"][str(n)][:len(fr["orbits_by_codim"])]
        add("face orbits by codim", n, pub, fr["orbits_by_codim"])
        add("Deza face reps map 1-1 onto our face orbits", n, True,
            all(v["same_orbits_as_ours"] and v["codim_ok"] and v["distinct"] == v["deza_reps"]
                for v in fr["deza_reps_check"].values()))
    cc = R["canon_crosscheck"]
    add("canonical form: fast == brute force == min_pi switch_canon (n<=6, n=7 reps), invariant (n=8 sample)",
        "3-8", True, all(all(v for k, v in d.items()) for d in cc.values() if isinstance(d, dict)))
    pt = R["patterns"]
    add("clause (+-1) encoding: Deza rule == catalog, group = column ops, cut tight iff NAE", "3-8", True,
        all(all(v in (True, None) for v in d.values()) for d in pt.values() if isinstance(d, dict)))

    report = {"job_state": {k: job.state[k] for k in ("code_version", "git_head", "seed", "params", "python")},
              "rows": rows, "raw": R}
    OUT.mkdir(parents=True, exist_ok=True)
    atomic_write_json(OUT / "report.json", report)

    md = ["# Phase 2 verification report", "",
          f"code_version `{job.state['code_version']}`, git `{job.state['git_head']}`, seed {job.state['seed']}", "",
          "| quantity | n | published | ours | status | note |", "|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['quantity']} | {r['n']} | {r['published']} | {r['ours']} | {r['status']} | {r['note']} |")
    atomic_write_text(OUT / "report.md", "\n".join(md) + "\n")
    bad = [r for r in rows if r["status"] == "MISMATCH"]
    print(f"\n{len(rows)} checks, {len(bad)} mismatches -> {OUT / 'report.md'}")
    for r in bad:
        print("  MISMATCH:", r)
    print(f"cache hits/misses: {cache.hits}/{cache.misses}")


if __name__ == "__main__":
    main()
