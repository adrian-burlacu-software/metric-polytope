#!/usr/bin/env python3
"""n = 9 sample study on Deza's 1,056,367 orbit representatives (Orbits.zip).

Design (seeded, saved to results/n9/sample_<design>.json):
  U  : 10,000 orbits uniformly at random (without replacement) from all rows
  A  : denominator strata — den <= 5 census; each den 6..21 its own stratum (2,000 each); 22–25 pooled; 26–43 pooled
  B  : as A with 1,000 per stratum
  C  : coarse strata  <=8, 9–11, 12–14, 15–17, >=18  (2,000 each)
Per orbit: exact vertex test, incidence, canonical key, stabilizer -> orbit size, adjacent to some cut, block
decomposition X* (free / vertex blocks), derivation depth (detour / vertex-only, uniform base incl. all graph metrics
on 9 nodes), middle types (count, new vs the n <= 8 catalog, new atoms).
Parallel (--workers), one atomic JSONL file per chunk in checkpoints/n9_sample_<design>/, resumable.
Usage: python -u scripts/n9_sample.py --design A [--workers 19] [--draw-only] [--report-only]
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import multiprocessing as mp
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from metricpoly.jobs import ROOT as _R, atomic_write_json, atomic_write_text, code_version, git_head  # noqa: E402

NPZ = ROOT / "data" / "deza" / "orbits9" / "orbits9.npz"
COORDS = ROOT / "data" / "deza" / "orbits9" / "coords.npy"
DENS = ROOT / "data" / "deza" / "orbits9" / "den.npy"
BASE = ROOT / "results" / "n9" / "base_keys.json"
OUT = ROOT / "results" / "n9"
SEED = 20261121
PER = {"A": 2000, "B": 1000, "C": 2000}


def strata_of(design, den):
    if design == "C":
        return ("<=8" if den <= 8 else "9-11" if den <= 11 else "12-14" if den <= 14 else "15-17" if den <= 17 else ">=18")
    if den <= 5:
        return "<=5"
    if den <= 21:
        return str(den)
    return "22-25" if den <= 25 else "26-43"


def ensure_arrays():
    if not COORDS.exists():
        z = np.load(NPZ)
        np.save(COORDS, z["coords"])
        np.save(DENS, z["den"])


def draw(design):
    ensure_arrays()
    den = np.load(DENS)
    N = len(den)
    rng = np.random.default_rng(SEED)
    uniform = np.sort(rng.choice(N, 10_000, replace=False))
    lab = np.array([strata_of(design, int(d)) for d in den])
    strata = {}
    for s in sorted(set(lab.tolist()), key=lambda s: (len(s), s)):
        idx = np.flatnonzero(lab == s)
        k = len(idx) if (design in "AB" and s == "<=5") else min(PER[design], len(idx))
        pick = np.sort(rng.choice(idx, k, replace=False))
        strata[s] = {"population": int(len(idx)), "sampled": int(k), "rows": pick.tolist()}
    zsha = hashlib.sha256((ROOT / "data" / "deza" / "orbits9" / "Orbits.zip").read_bytes()).hexdigest()
    rows = sorted(set(uniform.tolist()) | {r for s in strata.values() for r in s["rows"]})
    d = {"design": design, "seed": SEED, "orbits_zip_sha256": zsha, "population": int(N),
         "uniform": uniform.tolist(), "strata": strata, "rows": rows}
    atomic_write_json(OUT / f"sample_{design}.json", d)
    return d


# ======================================================================= worker
_W = {}


def _init():
    from metricpoly import blocks, group
    import detour_depth2 as d2
    group.perm_src(9)
    base = {int(n): set(v) for n, v in json.loads(BASE.read_text()).items()}
    cat = json.loads((ROOT / "results" / "phase6" / "catalog.json").read_text(encoding="utf-8"))
    _W.update(coords=np.load(COORDS, mmap_mode="r"), den=np.load(DENS, mmap_mode="r"), engine=blocks.Engine(),
              dpF=d2.DP(base, vertex_mode=False), dpV=d2.DP(base, vertex_mode=True), old_types=set(cat), cls={})


def _pairs9():
    for kt in range(1, 9):
        for T in itertools.combinations(range(9), kt):
            rest = [v for v in range(9) if v not in T]
            for ku in range(1, len(rest) + 1):
                for U in itertools.combinations(rest, ku):
                    if T[0] < U[0]:
                        yield T, U


def analyse_row(r):
    from metricpoly import blocks, core, group, middles
    from metricpoly.core import Point
    from metricpoly.dsl.prims import p_adjacent, p_cuts, p_vertex
    x = Point.make(9, int(_W["den"][r]), [int(v) for v in _W["coords"][r]])
    out = {"row": int(r), "D": x.D, "vertex": p_vertex(x), "incidence": int(len(core.tight_set(x)))}
    out["key"] = group.canonical(x).key()
    st = group.stabilizer_size(x)
    out["orbit_size"] = group.group_order(9) // st
    out["adj_cut"] = any(p_adjacent(x, c) for c in p_cuts(9))
    E = _W["engine"]
    Mx = blocks.matrix(x)
    for bv, name in ((False, "free"), (True, "vb")):
        out[f"X_{name}"] = next((X for X in range(4) if E.can(Mx, x.D, X, bv)), None)
    dF, _ = _W["dpF"].point_depth(x)
    dV, _ = _W["dpV"].point_depth(x)
    out["depth_detour"] = None if dF == math.inf else int(dF)
    out["depth_vertex"] = None if dV == math.inf else int(dV)
    types = {middles.canonical_type(Mx[np.ix_(T, U)], x.D) for T, U in _pairs9()}
    new = [k for k in types if k not in _W["old_types"]]
    atoms = 0
    for k in new:
        if k not in _W["cls"]:
            M, D = middles.decode(k)
            _W["cls"][k] = (not blocks.is_const_up_to_flips(M, D)) and not middles.one_step_expressible(M, D)
        atoms += _W["cls"][k]
    out.update(types=len(types), new_types=len(new), new_atoms=atoms,
               new_atoms_old_den=sum(1 for k in new if _W["cls"][k] and int(k.split("|")[1]) <= 15))
    return out


def analyse_chunk(args):
    cid, rows, ckdir = args
    path = Path(ckdir) / f"chunk_{cid:05d}.jsonl"
    if path.exists():
        return cid, len(rows), 0.0
    t = time.time()
    lines = [json.dumps(analyse_row(r)) for r in rows]
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    return cid, len(rows), time.time() - t


def run(design, workers, chunk=25):
    sample = json.loads((OUT / f"sample_{design}.json").read_text())
    ckdir = ROOT / "checkpoints" / f"n9_sample_{design}"
    ckdir.mkdir(parents=True, exist_ok=True)
    state = {"design": design, "code_version": code_version(), "git": git_head(), "seed": SEED,
             "orbits_zip_sha256": sample["orbits_zip_sha256"], "rows": len(sample["rows"])}
    st_path = ckdir / "state.json"
    if st_path.exists():
        old = json.loads(st_path.read_text())
        if old["code_version"] != state["code_version"] and not os.environ.get("N9_FORCE"):
            raise SystemExit(f"checkpoint code version {old['code_version']} != {state['code_version']} "
                             "(set N9_FORCE=1 to resume anyway)")
    atomic_write_json(st_path, state)
    rows = sample["rows"]
    tasks = [(i, rows[i * chunk:(i + 1) * chunk], str(ckdir)) for i in range((len(rows) + chunk - 1) // chunk)]
    todo = [t for t in tasks if not (ckdir / f"chunk_{t[0]:05d}.jsonl").exists()]
    print(f"[n9 {design}] {len(rows)} orbits, {len(tasks)} chunks, {len(tasks) - len(todo)} already done", flush=True)
    t0, done = time.time(), 0
    with mp.Pool(workers, initializer=_init) as pool:
        for cid, k, dt in pool.imap_unordered(analyse_chunk, todo):
            done += k
            el = time.time() - t0
            rate = done / el
            left = sum(len(t[1]) for t in todo) - done
            print(f"[n9 {design}] {done}/{sum(len(t[1]) for t in todo)} orbits  {rate:.1f}/s  "
                  f"elapsed {el / 60:.1f} min  eta {left / rate / 60:.1f} min", flush=True)


# ======================================================================= report
def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h


def report(design):
    sample = json.loads((OUT / f"sample_{design}.json").read_text())
    ckdir = ROOT / "checkpoints" / f"n9_sample_{design}"
    R = {}
    for f in sorted(ckdir.glob("chunk_*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                R[rec["row"]] = rec
    missing = [r for r in sample["rows"] if r not in R]
    feats = {
        "not adjacent to any cut (dominating set fails)": lambda r: not r["adj_cut"],
        "fractal: constant middles (X*=const)": lambda r: r["X_free"] == 0,
        "fractal: structured middles (X* <= 2val)": lambda r: r["X_free"] is not None and r["X_free"] <= 2,
        "fractal: blocks are vertices (any level)": lambda r: r["X_vb"] is not None,
        "derivable with detours": lambda r: r["depth_detour"] is not None,
        "derivable vertex-only": lambda r: r["depth_vertex"] is not None,
        "carries a new atom (vs n<=8)": lambda r: r["new_atoms"] > 0,
        "carries a new atom with denominator <= 15": lambda r: r["new_atoms_old_den"] > 0,
    }
    U = [R[r] for r in sample["uniform"] if r in R]
    md = ["# n = 9 sample study", "",
          f"Design {design}; seed {sample['seed']}; Orbits.zip sha256 `{sample['orbits_zip_sha256'][:16]}…`; "
          f"population {sample['population']:,} orbits; analysed {len(R):,} distinct orbits; missing {len(missing)}.", "",
          "All analysed points were checked: exact vertex " + str(all(r["vertex"] for r in R.values())) + ".", "",
          "## Uniform sample (10,000 orbits): estimates with 95% intervals", "",
          "| property | orbit-weighted: share [95% CI] | vertex-weighted (by orbit size): share [95% bootstrap CI] |",
          "|---|---|---|"]
    rng = np.random.default_rng(SEED)
    w = np.array([r["orbit_size"] for r in U], dtype=float)
    out = {"uniform": {}, "strata": {}, "comparisons": {}}
    for name, f in feats.items():
        v = np.array([f(r) for r in U], dtype=float)
        p, lo, hi = wilson(int(v.sum()), len(v))
        pw = float((w * v).sum() / w.sum())
        boots = []
        for _ in range(1000):
            idx = rng.integers(0, len(v), len(v))
            boots.append((w[idx] * v[idx]).sum() / w[idx].sum())
        blo, bhi = np.percentile(boots, [2.5, 97.5])
        md.append(f"| {name} | {100 * p:.2f}% [{100 * lo:.2f}, {100 * hi:.2f}] | {100 * pw:.2f}% [{100 * blo:.2f}, {100 * bhi:.2f}] |")
        out["uniform"][name] = {"p": p, "ci": [lo, hi], "p_vertex_weighted": pw, "ci_vw": [float(blo), float(bhi)]}
    md += ["", "## Per denominator stratum (orbit-weighted within stratum)", "",
           "| stratum | population | sampled | " + " | ".join(feats) + " |", "|---" * (3 + len(feats)) + "|"]
    strat_est = defaultdict(float)
    for s, info in sample["strata"].items():
        rows = [R[r] for r in info["rows"] if r in R]
        cells = []
        for name, f in feats.items():
            k = sum(1 for r in rows if f(r))
            p, lo, hi = wilson(k, len(rows))
            cells.append(f"{100 * p:.1f}% ±{100 * (hi - lo) / 2:.1f}")
            strat_est[name] += info["population"] / sample["population"] * p
            out["strata"].setdefault(s, {})[name] = {"p": p, "ci": [lo, hi], "n": len(rows)}
        md.append(f"| {s} | {info['population']:,} | {len(rows):,} | " + " | ".join(cells) + " |")
    md += ["", "Stratified overall estimate (Σ N_h/N · p_h) vs uniform-sample estimate:", ""]
    for name in feats:
        md.append(f"- {name}: stratified {100 * strat_est[name]:.2f}%  vs uniform {100 * out['uniform'][name]['p']:.2f}%")
    # within-stratum comparisons: reachable (detour) vs unreachable
    md += ["", "## Within-denominator: derivable vs not derivable (detours allowed)", "",
           "Mean new atoms per orbit and share with structured decomposition; one-sided permutation test "
           "(20,000 permutations) on new atoms with denominator <= 15, Holm-corrected across strata.", "",
           "| stratum | derivable n | not n | mean new atoms (der / not) | mean new atoms den<=15 (der / not) | structured X* (der / not) | p (raw) | p (Holm) |",
           "|---|---|---|---|---|---|---|---|"]
    tests = []
    for s, info in sample["strata"].items():
        rows = [R[r] for r in info["rows"] if r in R]
        a = [r for r in rows if r["depth_detour"] is not None]
        b = [r for r in rows if r["depth_detour"] is None]
        if len(a) < 20 or len(b) < 20:
            md.append(f"| {s} | {len(a)} | {len(b)} | — | — | — | (group < 20) | |")
            continue
        va = np.array([r["new_atoms_old_den"] for r in a], float)
        vb = np.array([r["new_atoms_old_den"] for r in b], float)
        allv, lab = np.concatenate([va, vb]), np.r_[np.zeros(len(va)), np.ones(len(vb))].astype(bool)
        obs = allv[lab].mean() - allv[~lab].mean()
        cnt = 0
        for _ in range(20000):
            pl = rng.permutation(lab)
            cnt += allv[pl].mean() - allv[~pl].mean() >= obs
        p = (cnt + 1) / 20001
        sa = np.mean([r["X_free"] is not None and r["X_free"] <= 2 for r in a])
        sb = np.mean([r["X_free"] is not None and r["X_free"] <= 2 for r in b])
        tests.append([s, p, len(a), len(b), np.mean([r["new_atoms"] for r in a]), np.mean([r["new_atoms"] for r in b]),
                      va.mean(), vb.mean(), sa, sb])
    order = sorted(range(len(tests)), key=lambda i: tests[i][1])
    m = len(tests)
    holm, running = [0.0] * m, 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * tests[i][1]))
        holm[i] = running
    for i, t in enumerate(tests):
        md.append(f"| {t[0]} | {t[2]} | {t[3]} | {t[4]:.1f} / {t[5]:.1f} | {t[6]:.2f} / {t[7]:.2f} | "
                  f"{100 * t[8]:.0f}% / {100 * t[9]:.0f}% | {t[1]:.4f} | {holm[i]:.4f} |")
        out["comparisons"][t[0]] = {"p": t[1], "p_holm": holm[i], "n_der": t[2], "n_not": t[3]}
    atomic_write_json(OUT / f"report_{design}.json", out)
    atomic_write_text(OUT / f"report_{design}.md", "\n".join(md) + "\n")
    print("\n".join(md))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--design", choices=["A", "B", "C"], default="A")
    ap.add_argument("--workers", type=int, default=19)
    ap.add_argument("--draw-only", action="store_true")
    ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args()
    if not a.report_only:
        if not (OUT / f"sample_{a.design}.json").exists():
            d = draw(a.design)
            print(f"drew design {a.design}: {len(d['rows'])} distinct orbits "
                  f"({len(d['uniform'])} uniform + strata {[(s, v['sampled']) for s, v in d['strata'].items()]})")
        if a.draw_only:
            return
        run(a.design, a.workers)
    report(a.design)


if __name__ == "__main__":
    main()
