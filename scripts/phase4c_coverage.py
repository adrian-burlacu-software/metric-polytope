#!/usr/bin/env python3
"""Phase 4c coverage report: which orbits of m_n (n = 3..max_n) do the literature rules reach?

Experiment B (absolute): seeds = outputs of the *data-free* generative rules (they do not read our vertex lists),
closed under all moves until nothing new appears. Shortest derivations come from the BFS provenance.
Experiment A (tower): for each n, seeds = every verified orbit of every smaller size + the base pieces of size n,
closed up to size n. Orbits of m_n not reached are new at n relative to everything smaller.

Usage: python -u scripts/phase4c_coverage.py [--max-n 7] [--glue-cap 99] [--resume] [--force]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from metricpoly import core, deza, group  # noqa: E402
from metricpoly.dsl.closure import run_closure  # noqa: E402
from metricpoly.dsl.interp import Interpreter  # noqa: E402
from metricpoly.dsl.prims import p_vertex, p_vertices  # noqa: E402
from metricpoly.jobs import Job, add_job_args, atomic_write_json, atomic_write_text  # noqa: E402

OUT = ROOT / "results" / "phase4c"
DATA_FREE = ["gen-cuts", "gen-anticuts", "gen-graphic", "gen-multipartite", "gen-avis-paths", "gen-rays",
             "gen-tree-suspension", "gen-sporadic"]
MOVES = ["twin", "dup", "radial", "radial2", "radial3", "lift-fiber", "glue-all"]


def in_domain(rule, n):
    d = tuple(rule.meta.get("domain", (3,)))
    return d[0] <= n <= (d[1] if len(d) > 1 else 99)


def deza_table(n):
    reps = deza.load_ext(n)
    G = group.group_order(n)
    rows = {}
    for i, p in enumerate(reps, 1):
        k = group.canonical(p).key()
        rows[k] = {"index": i, "rep": p, "denominator": p.D, "orbit_size": G // group.stabilizer_size(p),
                   "incidence": int(len(core.tight_set(p)))}
    return rows


def fmt_point(p):
    return f"(1/{p.D})·(" + " ".join(map(str, p.nums)) + ")" if p.D > 1 else "(" + " ".join(map(str, p.nums)) + ")"


def derivation(C, n, k, depth=0):
    if depth > 40:
        return "…"
    pv = C.orbits[n][k]["prov"]
    if pv["move"] == "seed":
        return pv.get("seed_rule", "seed")
    parts = []
    for pk in pv["parents"]:
        pn = next(m for m, d in C.orbits.items() if pk in d)
        parts.append(derivation(C, pn, pk, depth + 1))
    return f"{pv['move']}(" + ", ".join(parts) + ")"


def label_of(n, k, tables):
    t = tables.get(n, {}).get(k)
    return f"m{n}#{t['index']}" if t else f"m{n}:?"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_job_args(ap)
    ap.add_argument("--max-n", type=int, default=7)
    ap.add_argument("--glue-cap", type=int, default=99, help="max overlap k for gluing (99 = uncapped)")
    args = ap.parse_args()
    params = {"max_n": args.max_n, "glue_cap": args.glue_cap, "moves": MOVES, "base_rules": DATA_FREE}
    job = Job(f"phase4c_coverage_n{args.max_n}", params, args.seed, resume=args.resume, force=args.force)
    I = Interpreter(seed=args.seed, params={"glue-cap": args.glue_cap})
    I.load_file(ROOT / "rules" / "stdlib.mpr")
    I.load_file(ROOT / "rules" / "literature.mpr")
    I.finalize()
    tables = {n: deza_table(n) for n in range(3, args.max_n + 1)}
    R = job.results()

    # ---- 1. base pieces
    if not job.is_done("base"):
        base = {}
        for name in DATA_FREE:
            rule = I.rules[name]
            for n in range(3, args.max_n + 1):
                if not in_domain(rule, n):
                    continue
                t = time.time()
                out = [p for p in I.run_rule(rule, n) if p.n == n and p_vertex(p)]
                keys = sorted({group.canonical(p).key() for p in out})
                base.setdefault(name, {})[str(n)] = {"orbits": [label_of(n, k, tables) for k in keys],
                                                    "keys": keys, "seconds": round(time.time() - t, 2)}
                print(f"[base] {name}@{n}: {len(keys)} orbits {[label_of(n, k, tables) for k in keys]}", flush=True)
        job.record("base", base)
        R = job.results()
    base = R["base"]
    seeds, labels = [], []
    for name, per_n in base.items():
        for n, d in per_n.items():
            for k in d["keys"]:
                _, D, nums = k.split("|")
                seeds.append(core.Point(int(n), int(D), tuple(int(v) for v in nums.split(","))))
                labels.append(f"{name}@{n}")
    moves = [I.moves[m] for m in MOVES]

    # ---- 2. experiment B (absolute closure)
    if not job.is_done("closure_abs"):
        t = time.time()
        C = run_closure(I, seeds, moves, max_n=args.max_n, max_rounds=100, checkpoint=f"cov-abs-n{args.max_n}-cap{args.glue_cap}",
                        seed_labels=labels)
        job.record("closure_abs", {"closure": C.to_json(), "seconds": round(time.time() - t, 1), "modes": I.log[-200:]})
        R = job.results()

    # ---- 3. experiment A (tower)
    for n in range(4, args.max_n + 1):
        task = f"closure_tower_{n}"
        if job.is_done(task):
            continue
        tseeds, tlabels = [], []
        for m in range(3, n):
            for k, row in tables[m].items():
                tseeds.append(row["rep"])
                tlabels.append(f"m{m}#{row['index']}")
        for s, lab in zip(seeds, labels):
            if s.n == n:
                tseeds.append(s)
                tlabels.append(lab)
        t = time.time()
        C = run_closure(I, tseeds, moves, max_n=n, max_rounds=100, checkpoint=f"cov-tower-n{n}-cap{args.glue_cap}",
                        seed_labels=tlabels)
        job.record(task, {"closure": C.to_json(), "seconds": round(time.time() - t, 1)})
        R = job.results()

    report(job, R, tables, args)


def report(job, R, tables, args):
    from metricpoly.dsl.closure import Closure
    Cabs = Closure.from_json(R["closure_abs"]["closure"])
    out = {"params": job.state["params"], "code_version": job.state["code_version"], "git": job.state["git_head"],
           "closure_abs": {"saturated": Cabs.saturated, "rounds": Cabs.rounds, "seconds": R["closure_abs"]["seconds"]},
           "per_n": {}}
    md = ["# Phase 4c coverage report", "",
          f"code_version `{job.state['code_version']}`, git `{job.state['git_head']}`, seed {job.state['seed']}", "",
          f"Base pieces: data-free generative rules {', '.join(DATA_FREE)}.",
          f"Moves: {', '.join(MOVES)}. Gluing overlap cap: "
          f"{'none (uncapped)' if args.glue_cap >= 99 else args.glue_cap}.",
          f"Absolute closure: saturated = {Cabs.saturated} after {Cabs.rounds} rounds "
          f"({R['closure_abs']['seconds']} s).", "",
          "| n | Deza orbits | reached (absolute: base pieces + moves) | reached (tower: all smaller orbits + moves) | not reached (absolute) | not reached (tower) |",
          "|---|---|---|---|---|---|"]
    detail = []
    for n in range(3, args.max_n + 1):
        tab = tables[n]
        reached = Cabs.keys(n) & set(tab)
        extra = Cabs.keys(n) - set(tab)
        if n >= 4:
            Ct = Closure.from_json(R[f"closure_tower_{n}"]["closure"])
            treached = Ct.keys(n) & set(tab)
            tsat = Ct.saturated
        else:
            treached, tsat = set(tab), True
        miss = sorted((k for k in tab if k not in reached), key=lambda k: tab[k]["index"])
        tmiss = sorted((k for k in tab if k not in treached), key=lambda k: tab[k]["index"])
        md.append(f"| {n} | {len(tab)} | {len(reached)} | {len(treached)} | "
                  f"{', '.join('#' + str(tab[k]['index']) for k in miss) or '—'} | "
                  f"{', '.join('#' + str(tab[k]['index']) for k in tmiss) or '—'} |")
        per = {"deza_orbits": len(tab), "reached_abs": len(reached), "reached_tower": len(treached),
               "tower_saturated": tsat, "extra_keys_not_in_deza": sorted(extra),
               "not_reached_abs": [], "not_reached_tower": [], "derivations": {}}
        detail += ["", f"## n = {n}", ""]
        detail += ["Shortest derivations (absolute closure):", "", "| orbit | denominator | orbit size | derivation |",
                   "|---|---|---|---|"]
        for k in sorted(reached, key=lambda k: tab[k]["index"]):
            d = derivation(Cabs, n, k)
            per["derivations"][f"#{tab[k]['index']}"] = d
            detail.append(f"| #{tab[k]['index']} | {tab[k]['denominator']} | {tab[k]['orbit_size']} | `{d}` |")
        for kind, lst in (("absolute", miss), ("tower", tmiss)):
            if not lst:
                continue
            detail += ["", f"Not reached ({kind}):", "", "| orbit | representative | denominator | orbit size | incidence |",
                       "|---|---|---|---|---|"]
            for k in lst:
                row = tab[k]
                rec = {"index": row["index"], "rep": fmt_point(row["rep"]), "denominator": row["denominator"],
                       "orbit_size": row["orbit_size"], "incidence": row["incidence"]}
                per["not_reached_abs" if kind == "absolute" else "not_reached_tower"].append(rec)
                detail.append(f"| #{row['index']} | {rec['rep']} | {row['denominator']} | {row['orbit_size']} | {row['incidence']} |")
        if extra:
            detail += ["", f"**Warning**: closure produced {len(extra)} orbit(s) at n={n} not in Deza's list (bug?)."]
        out["per_n"][str(n)] = per
    md += ["", "Orbit numbers #i are Deza's (data/deza/raw/metric_n.ext order).",
           f"Gluing cap: {'not applied — gluing ran uncapped for every pair, so every unreached orbit is a confirmed non-reach for this move set' if args.glue_cap >= 99 else f'k <= {args.glue_cap}; unreached orbits are CANDIDATES until the uncapped rerun'}."]
    md += detail
    OUT.mkdir(parents=True, exist_ok=True)
    atomic_write_json(OUT / f"coverage_n{args.max_n}.json", out)
    atomic_write_text(OUT / f"coverage_n{args.max_n}.md", "\n".join(md) + "\n")
    print("\n".join(md[:20]))


if __name__ == "__main__":
    main()
