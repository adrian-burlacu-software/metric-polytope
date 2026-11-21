#!/usr/bin/env python3
"""Phase 6: catalog of middle-region types.

A middle region of a vertex x is a cross block x[T, U] for disjoint nonempty node sets T, U (all of them, not only
T ∪ U = V, so a pattern of shape r×c can first appear at any n >= r + c). Types = canonical form up to row/column
permutations, sign flips and transpose (metricpoly/middles.py). Per type: shape, denominator, first n, number of
orbits containing it per n, and expressibility (constant; one-step block rule from smaller types; recursive with
constant / structured off-diagonals). Atom = not constant and not one-step expressible.

Also: top-level middle types (T ∪ U = V) of n = 8 orbits compared between reachable and unreachable orbits
(detour-depth DP) within the same denominator; and the types carried by m7 #12.
Usage: python -u scripts/phase6_middles.py [--resume] [--force]
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from metricpoly import blocks, deza, middles  # noqa: E402
from metricpoly.jobs import Job, Progress, add_job_args, atomic_write_json, atomic_write_text  # noqa: E402

OUT = ROOT / "results" / "phase6"


def block_pairs(n):
    for kt in range(1, n):
        for T in itertools.combinations(range(n), kt):
            rest = [v for v in range(n) if v not in T]
            for ku in range(1, len(rest) + 1):
                for U in itertools.combinations(rest, ku):
                    if T[0] < U[0]:
                        yield T, U


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_job_args(ap)
    args = ap.parse_args()
    job = Job("phase6_middles", {"n": [3, 4, 5, 6, 7, 8]}, args.seed, resume=args.resume, force=args.force)
    OUT.mkdir(parents=True, exist_ok=True)
    for n in range(3, 9):
        task = f"types_n{n}"
        if job.is_done(task):
            continue
        reps = deza.load_ext(n)
        path = OUT / f"types_n{n}.jsonl"
        tmp = path.with_suffix(".jsonl.tmp")
        prog = Progress(task, len(reps), every=50)
        t = time.time()
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            for i, x in enumerate(reps, 1):
                Mx = blocks.matrix(x)
                occ, top = Counter(), Counter()
                for T, U in block_pairs(n):
                    k = middles.canonical_type(Mx[np.ix_(T, U)], x.D)
                    occ[k] += 1
                    if len(T) + len(U) == n:
                        top[k] += 1
                f.write(json.dumps({"orbit": i, "D": x.D, "occ": occ, "top": top}) + "\n")
                prog.step()
        tmp.replace(path)
        job.record(task, {"seconds": round(time.time() - t, 1)})
    if not job.is_done("classify"):
        types = set()
        for n in range(3, 9):
            for line in open(OUT / f"types_n{n}.jsonl", encoding="utf-8"):
                types.update(json.loads(line)["occ"])
        prog = Progress("classify", len(types), every=30)
        cls = {}
        for k in sorted(types):
            cls[k] = middles.classify(k)
            prog.step()
        atomic_write_json(OUT / "classification.json", cls)
        job.record("classify", {"types": len(types)})
    report(job)


def report(job):
    cls = json.load(open(OUT / "classification.json", encoding="utf-8"))
    per_n = {n: [json.loads(l) for l in open(OUT / f"types_n{n}.jsonl", encoding="utf-8")] for n in range(3, 9)}
    first, orbits_with, occ_tot = {}, defaultdict(Counter), defaultdict(Counter)
    for n in range(3, 9):
        for rec in per_n[n]:
            for k, c in rec["occ"].items():
                first.setdefault(k, n)
                orbits_with[k][n] += 1
                occ_tot[k][n] += c
    md = ["# Phase 6: middle-region catalog", "",
          f"code_version `{job.state['code_version']}`, git `{job.state['git_head']}`", "",
          "Middle region = cross block x[T, U], T and U disjoint nonempty node sets; type = canonical form up to "
          "row/column permutations, sign flips and transpose. Atom = neither constant up to flips nor one-step "
          "expressible (a bi-split whose two off-diagonal blocks are constant up to flips). 'recursive' = built "
          "entirely by the block rule from constant pieces (const: constant off-diagonals; structured: off-diagonals "
          "at most two-valued up to complement).", "",
          "## Per n", "",
          "| n | orbits | distinct types | new types (first seen at n) | new constant | new one-step expressible | new recursive (const) | new recursive (structured) | **new atoms** |",
          "|---|---|---|---|---|---|---|---|---|"]
    summary = {}
    for n in range(3, 9):
        present = {k for rec in per_n[n] for k in rec["occ"]}
        new = [k for k in present if first[k] == n]
        c = Counter()
        for k in new:
            f = cls[k]
            c["const"] += f["const"]
            c["one"] += f["one_step"] and not f["const"]
            c["rc"] += f["recursive_const"]
            c["rs"] += f["recursive_structured"]
            c["atom"] += not f["const"] and not f["one_step"]
        md.append(f"| {n} | {len(per_n[n])} | {len(present)} | {len(new)} | {c['const']} | {c['one']} | {c['rc']} | "
                  f"{c['rs']} | {c['atom']} |")
        summary[n] = {"distinct": len(present), "new": len(new), **c}
    md += ["", "## Most frequent middle types per n (share of orbits containing the type)", ""]
    for n in range(3, 9):
        N = len(per_n[n])
        top = sorted(((orbits_with[k][n], k) for k in orbits_with if orbits_with[k][n]), reverse=True)[:8]
        md.append(f"- n = {n}: " + "; ".join(f"`{k}` {100 * c / N:.0f}% (first n={first[k]}"
                                               f"{', atom' if not cls[k]['const'] and not cls[k]['one_step'] else ''})"
                                               for c, k in top))
    # ---- reachable vs unreachable at n = 8 within denominator
    reach = {r["orbit"]: r["depth"] for r in json.load(open(ROOT / "results" / "phase4c" / "detour_depth2.json",
                                                                encoding="utf-8"))["raw"]["detour@8"]["rows"]}
    md += ["", "## n = 8: middle types of reachable vs unreachable orbits, same denominator", "",
           "Top-level types (T ∪ U = V) and all cross-block types. 'exclusive' = present in ≥ 3 orbits of one group "
           "and in no orbit of the other group (same denominator).", "",
           "| den | group | orbits | distinct top types | top types exclusive (≥3 orbits) | distinct block types | block types exclusive (≥3 orbits) | new-at-8 atoms per orbit (mean) |",
           "|---|---|---|---|---|---|---|---|"]
    comp = {}
    for D in (6, 7, 8, 10, 14):
        grp = {"reachable": [r for r in per_n[8] if r["D"] == D and reach[r["orbit"]] is not None],
               "UNREACHABLE": [r for r in per_n[8] if r["D"] == D and reach[r["orbit"]] is None]}
        if not grp["reachable"] or not grp["UNREACHABLE"]:
            continue
        cnt = {g: (Counter(k for r in rows for k in r["top"]), Counter(k for r in rows for k in r["occ"]))
               for g, rows in grp.items()}
        for g, rows in grp.items():
            other = "UNREACHABLE" if g == "reachable" else "reachable"
            ex_top = [k for k, c in cnt[g][0].items() if c >= 3 and cnt[other][0][k] == 0]
            ex_blk = [k for k, c in cnt[g][1].items() if c >= 3 and cnt[other][1][k] == 0]
            atoms = [sum(1 for k in r["occ"] if first[k] == 8 and not cls[k]["const"] and not cls[k]["one_step"])
                     for r in rows]
            md.append(f"| {D} | {g} | {len(rows)} | {len(cnt[g][0])} | {len(ex_top)} | {len(cnt[g][1])} | "
                      f"{len(ex_blk)} | {sum(atoms) / len(atoms):.1f} |")
            comp[f"{D}:{g}"] = {"orbits": len(rows), "exclusive_top": ex_top[:50], "exclusive_blocks": ex_blk[:50],
                                "mean_new_atoms": sum(atoms) / len(atoms)}
    # ---- m7 #12
    r12 = next(r for r in per_n[7] if r["orbit"] == 12)
    others7 = [r for r in per_n[7] if r["orbit"] != 12]
    only12 = [k for k in r12["occ"] if all(k not in r["occ"] for r in others7)]
    new7_12 = [k for k in r12["occ"] if first[k] == 7]
    md += ["", "## m7 #12", "",
           f"Distinct block types: {len(r12['occ'])}; first seen at n = 7: {len(new7_12)} "
           f"(atoms: {sum(1 for k in new7_12 if not cls[k]['const'] and not cls[k]['one_step'])}); "
           f"carried by #12 and by no other m7 orbit: {len(only12)}.", ""]
    for k in sorted(only12, key=lambda k: (-len(k), k))[:12]:
        M, D = middles.decode(k)
        f = cls[k]
        md.append(f"- `{k}` = (1/{D})·{M.tolist()}  "
                  f"{'atom' if not f['const'] and not f['one_step'] else ('one-step expressible' if f['one_step'] else 'constant')}"
                  f"{', recursive(structured)' if f['recursive_structured'] else ''}")
    per7 = [(r["orbit"], sum(1 for k in r["occ"] if first[k] == 7 and not cls[k]["const"] and not cls[k]["one_step"]),
             sum(1 for k in r["occ"] if all(k not in o["occ"] for o in per_n[7] if o["orbit"] != r["orbit"])))
            for r in per_n[7]]
    md += ["", "Per m7 orbit: (orbit, new atoms at n=7 it carries, types carried by it alone): " + str(per7)]
    catalog = {k: {"first_n": first[k], "orbits_with": dict(orbits_with[k]), "occurrences": dict(occ_tot[k]), **cls[k]}
               for k in first}
    atomic_write_json(OUT / "catalog.json", catalog)
    atomic_write_json(OUT / "report.json", {"per_n": summary, "n8_comparison": comp, "m7_12_only": only12})
    atomic_write_text(OUT / "report.md", "\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
