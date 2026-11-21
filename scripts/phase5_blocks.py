#!/usr/bin/env python3
"""Phase 5: block / fractal decomposition of every orbit representative, n = 3..8.

Per point: minimal middle-class level X* (0 const-up-to-flips, 1 twin, 2 two-valued mod complement, 3 any) for which a
full recursive decomposition exists — free blocks and blocks-must-be-vertices — the tree at X* (balanced splits
preferred, middles bi-split recursively with class labels), and the raw top-level middle of every split.
Groups at n = 8: reachable vs unreachable (detour-depth DP with all moves), and vertex-only reachable vs not.
m7 #12 is reported on its own.

Outputs: results/phase5/decomp_n<n>.jsonl, results/phase5/report.{md,json}
Usage: python -u scripts/phase5_blocks.py [--resume] [--force]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from metricpoly import blocks, deza  # noqa: E402
from metricpoly.jobs import Job, Progress, add_job_args, atomic_write_json, atomic_write_text  # noqa: E402

OUT = ROOT / "results" / "phase5"
LV = {0: "const", 1: "twin", 2: "2val", 3: "any", None: "none"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_job_args(ap)
    args = ap.parse_args()
    job = Job("phase5_blocks", {"n": [3, 4, 5, 6, 7, 8]}, args.seed, resume=args.resume, force=args.force)
    OUT.mkdir(parents=True, exist_ok=True)
    E = blocks.Engine()
    for n in range(3, 9):
        task = f"n{n}"
        if job.is_done(task):
            continue
        reps = deza.load_ext(n)
        path = OUT / f"decomp_n{n}.jsonl"
        tmp = path.with_suffix(".jsonl.tmp")
        prog = Progress(task, len(reps), every=20)
        t = time.time()
        summary = []
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            for i, x in enumerate(reps, 1):
                r = E.analyse(x)
                r.update({"n": n, "orbit": i, "rep": x.strs()})
                f.write(json.dumps(r) + "\n")
                f.flush()
                summary.append({"orbit": i, "D": x.D,
                                "free": {k: r["free"].get(k) for k in ("Xstar", "top_split", "nontrivial_top_split_exists", "tree_depth")},
                                "vblocks": {k: r["vblocks"].get(k) for k in ("Xstar", "top_split", "nontrivial_top_split_exists", "tree_depth")},
                                "top_middle_levels": dict(Counter(m["level"] for m in r["top_middles"]))})
                prog.step()
        tmp.replace(path)
        job.record(task, {"rows": summary, "seconds": round(time.time() - t, 1)})
    report(job)


def group_stats(rows):
    c = Counter()
    for r in rows:
        c[("free", LV[r["free"]["Xstar"]])] += 1
        c[("vblocks", LV[r["vblocks"]["Xstar"]])] += 1
        if r["free"]["nontrivial_top_split_exists"]:
            c[("free", "nontrivial top split")] += 1
    tops = Counter()
    for r in rows:
        for lv, k in r["top_middle_levels"].items():
            tops[LV[int(lv)]] += k
    depth = Counter(r["free"]["tree_depth"] for r in rows)
    return c, tops, depth


def fmt_row(name, rows):
    c, tops, depth = group_stats(rows)
    N = len(rows)
    pct = lambda k: f"{c[k]} ({100 * c[k] / N:.0f}%)" if N else "—"
    tt = sum(tops.values())
    return (f"| {name} | {N} | " + " | ".join(pct(("free", l)) for l in ("const", "twin", "2val", "any")) + " | "
            + pct(("free", "nontrivial top split")) + " | "
            + " | ".join(pct(("vblocks", l)) for l in ("const", "twin", "2val", "any", "none")) + " | "
            + ", ".join(f"{l} {100 * tops[l] / tt:.0f}%" for l in ("const", "twin", "2val", "any")) + " |")


def render_tree(t, ind=0):
    pad = "  " * ind
    if t["node"] == "leaf":
        return [f"{pad}leaf {t['nodes']}"]
    if t["node"] == "split":
        lines = [f"{pad}split T={t['T']} | T̄={t['Tbar']}  middle level {LV[t['level']]}  "
                 f"middle = (1/{t['D']})·{t['middle']}"]
        lines += [f"{pad}  A:"] + render_tree(t["A"], ind + 2)
        lines += [f"{pad}  M:"] + render_mid(t["M"], ind + 2)
        lines += [f"{pad}  B:"] + render_tree(t["B"], ind + 2)
        return lines
    return render_mid(t, ind)


def render_mid(m, ind):
    pad = "  " * ind
    if m["node"] == "mleaf":
        return [f"{pad}mleaf {m['shape'][0]}x{m['shape'][1]} level {LV[m['level']]}"]
    lines = [f"{pad}msplit rows {m['R']} cols {m['C']}  off-diagonal levels {[LV[l] for l in m['levels']]}"]
    for ch in m["children"]:
        lines += render_mid(ch, ind + 1)
    return lines


def report(job):
    R = job.results()
    reach = json.load(open(ROOT / "results" / "phase4c" / "detour_depth2.json", encoding="utf-8"))["raw"]
    hdr = ["| group | orbits | X* free: const | twin | 2val | any | nontrivial top split at X* | "
           "X* vertex-blocks: const | twin | 2val | any | none | top-level middle levels (all splits) |",
           "|" + "---|" * 13]
    md = ["# Phase 5: block / fractal decomposition", "",
          f"code_version `{job.state['code_version']}`, git `{job.state['git_head']}`", "",
          "X* = smallest middle class for which a full recursive decomposition exists "
          "(const = constant up to flips, twin, 2val = two-valued up to complement, any). "
          "'free': blocks arbitrary; 'vertex-blocks': every block must be a vertex of its own metric polytope "
          "('none' = no decomposition at any level). With free blocks 'any' always succeeds (peeling), so the "
          "informative columns are const/twin/2val and whether a non-peeling top split exists.", "", "## By n", ""] + hdr
    for n in range(3, 9):
        md.append(fmt_row(f"n = {n}", R[f"n{n}"]["rows"]))
    rows8 = {r["orbit"]: r for r in R["n8"]["rows"]}
    det = {r["orbit"]: r["depth"] for r in reach["detour@8"]["rows"]}
    ver = {r["orbit"]: r["depth"] for r in reach["vertex@8"]["rows"]}
    groups = {
        "n = 8, reachable with detours": [rows8[o] for o in rows8 if det[o] is not None],
        "n = 8, UNREACHABLE (the 266)": [rows8[o] for o in rows8 if det[o] is None],
        "n = 8, vertex-only reachable": [rows8[o] for o in rows8 if ver[o] is not None],
        "n = 8, vertex-only unreachable": [rows8[o] for o in rows8 if ver[o] is None],
    }
    md += ["", "## n = 8 by reachability", ""] + hdr + [fmt_row(k, v) for k, v in groups.items()]
    rows7 = {r["orbit"]: r for r in R["n7"]["rows"]}
    md += ["", "## n = 7, orbit by orbit", "", "| orbit | den | X* free | top split | nontrivial top split | X* vertex-blocks | tree depth |",
           "|---|---|---|---|---|---|---|"]
    for o in range(1, 14):
        r = rows7[o]
        mark = " **← #12**" if o == 12 else ""
        md.append(f"| #{o}{mark} | {r['D']} | {LV[r['free']['Xstar']]} | {r['free']['top_split']} | "
                  f"{r['free']['nontrivial_top_split_exists']} | {LV[r['vblocks']['Xstar']]} | {r['free']['tree_depth']} |")
    rec12 = next(json.loads(l) for l in open(OUT / "decomp_n7.jsonl", encoding="utf-8") if json.loads(l)["orbit"] == 12)
    md += ["", "## m7 #12 on its own", "", f"representative: {' '.join(rec12['rep'])}", "",
           f"X* free = {LV[rec12['free']['Xstar']]}, X* vertex-blocks = {LV[rec12['vblocks']['Xstar']]}", "",
           "Top-level middle levels over all 63 splits: "
           + str(dict(Counter(LV[m['level']] for m in rec12["top_middles"]))), "", "Tree at X* (free blocks):", "```"]
    md += render_tree(rec12["free"]["tree"]) + ["```"]
    out = {k: {"n": len(v), "stats": {f"{a}:{b}": c for (a, b), c in group_stats(v)[0].items()}} for k, v in groups.items()}
    atomic_write_json(OUT / "report.json", {"groups_n8": out, "raw": R})
    atomic_write_text(OUT / "report.md", "\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
