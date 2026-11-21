#!/usr/bin/env python3
"""Phase 3: benchmark OLD vs NEW orbit pipeline on n <= 6 and verify identical results.

Variants (per n):
  old          : legacy completion (float LP per inequality, bug-fixed copy) on every vertex,
                 then naive canonical form min_pi switch_canon(pi.x) on every vertex.
  new          : switching classes (switch_canon_fast) -> positional dedupe (canonical) of class reps
                 -> exact completion of one representative per orbit.
  old_order_exact / new_order_legacy : ablations swapping the completion engine.
  vset_*       : completion of the whole vertex set as one V-set (the original script's use case).

Checks (stop on any failure): identical orbit dictionaries (keys and sizes) across variants;
legacy and exact completion agree on validity and tightness for every vertex; for every vertex, the
slack vector transported from its orbit representative equals its directly computed slack vector.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
import types
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from metricpoly import core, group, pipeline, polyhedra  # noqa: E402
from metricpoly.completion import complete  # noqa: E402
from metricpoly.jobs import Job, Progress, add_job_args, atomic_write_json, atomic_write_text  # noqa: E402

OUT = ROOT / "results" / "phase3"


def load_legacy():
    shim = types.ModuleType("cupy")
    shim.__dict__.update({k: getattr(np, k) for k in dir(np) if not k.startswith("__")})
    shim.asnumpy = np.asarray
    sys.modules.setdefault("cupy", shim)
    spec = importlib.util.spec_from_file_location("legacy_completion", ROOT / "legacy" / "completion_v4_baseline.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["legacy_completion"] = mod
    spec.loader.exec_module(mod)
    return mod


LEG = load_legacy()


def legacy_engine(p: core.Point):
    cat = LEG.gen_metric_catalog(p.n, LEG.default_variables(p.n), ["triangle", "perimeter"])
    res = LEG.classify_with_gpu_prefilter([tuple(float(f) for f in p.fractions())], [], cat, tol=1e-12)
    return [(r.is_redundant, bool(r.tight_generator_indices)) for r in res]


def exact_flags(p: core.Point):
    s = pipeline.exact_engine(p)
    return [(bool(v >= 0), bool(v == 0)) for v in s]


def timed(fn, repeat):
    best, out = None, None
    for _ in range(repeat):
        t0 = time.perf_counter()
        out = fn()
        dt = time.perf_counter() - t0
        best = dt if best is None else min(best, dt)
    return best, out


def task_n(n: int, repeat: int):
    V = polyhedra.enumerate_vertices(n)
    rec = {"n": n, "vertices": len(V), "repeat": repeat}

    t, old = timed(lambda: pipeline.run_old(V, legacy_engine, canon=group.canonical_via_switch_canon, keep=True), repeat)
    rec["old"] = {"seconds": t, **_summ(old)}
    t, new = timed(lambda: pipeline.run_new(V, pipeline.exact_engine), repeat)
    rec["new"] = {"seconds": t, **_summ(new)}
    t, a1 = timed(lambda: pipeline.run_old(V, pipeline.exact_engine, canon=group.canonical), repeat)
    rec["old_order_exact"] = {"seconds": t, **_summ(a1)}
    t, a2 = timed(lambda: pipeline.run_new(V, legacy_engine), repeat)
    rec["new_order_legacy"] = {"seconds": t, **_summ(a2)}

    # ---- verification
    checks = {}
    checks["orbits_identical_all_variants"] = old.orbits == new.orbits == a1.orbits == a2.orbits
    checks["orbit_count"] = len(new.orbits)
    checks["orbit_sizes"] = sorted(new.orbits.values())
    leg = old.per_orbit_completion["per_point"]
    checks["legacy_eq_exact_every_vertex"] = all(leg[i] == exact_flags(p) for i, p in enumerate(V))
    reps, comp = new.per_orbit_completion["reps"], new.per_orbit_completion["comp"]
    ok = True
    for i, p in enumerate(V):
        k = group.canonical(p).key()
        rep = reps[k]
        # comp[k] is D_rep * slack(rep); compare D-scaled exact ints via Fractions
        tr = pipeline.transported_slacks(p, rep, np.array([v / rep.D for v in comp[k]], dtype=object))
        direct = np.array([v / p.D for v in pipeline.exact_slacks(p)], dtype=object)
        ok &= bool((tr == direct).all())
    checks["transported_completion_eq_direct_every_vertex"] = ok
    rec["checks"] = checks

    # ---- whole V-set completion (original script's use case)
    cat = LEG.gen_metric_catalog(n, LEG.default_variables(n), ["triangle", "perimeter"])
    Vf = [tuple(float(f) for f in p.fractions()) for p in V]
    t_leg, rl = timed(lambda: LEG.classify_with_gpu_prefilter(Vf, [], cat), 1)
    t_ex, rx = timed(lambda: complete(n, V), max(1, repeat))
    rec["vset_legacy"] = {"seconds": t_leg, "valid": sum(r.is_redundant for r in rl), "lps": sum(r.lp_opt is not None for r in rl)}
    rec["vset_exact"] = {"seconds": t_ex, "valid": len(rx.valid_set()), "lps": 0}
    checks["vset_valid_sets_equal"] = [r.is_redundant for r in rl] == [r.valid for r in rx.results]
    # one tiny exact-LP case so the box/LP path is exercised: two cuts + a point outside the box
    W = V[:2] + [core.Point.make(n, 2, [3] + [1] * (core.dim(n) - 1))]
    rb = complete(n, W, box=True)
    rnb = complete(n, W, box=False)
    checks["box_lp_path_runs"] = all(r.method == "lp_exact" for r in rb.results)
    checks["box_never_less_valid_than_nobox"] = all(b.valid or not nb.valid for b, nb in zip(rb.results, rnb.results))
    return rec


def _summ(r: pipeline.PipelineResult):
    return {"orbits": len(r.orbits), "completions_run": r.completions_run,
            "canonicalisations_run": r.canonicalisations_run, "switch_classes": r.switch_classes,
            "stage_seconds": {k: round(v, 4) for k, v in r.timings.items()}}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_job_args(ap)
    ap.add_argument("--repeat", type=int, default=3)
    args = ap.parse_args()
    ns = [3, 4, 5, 6]
    job = Job("phase3_pipeline", {"n": ns, "repeat": args.repeat}, args.seed, resume=args.resume, force=args.force)
    prog = Progress("phase3", len(ns), every=0)
    for n in ns:
        if not job.is_done(f"n{n}"):
            job.record(f"n{n}", task_n(n, args.repeat if n < 6 else 1))
        prog.step(force=True)

    R = job.results()
    OUT.mkdir(parents=True, exist_ok=True)
    atomic_write_json(OUT / "benchmark.json", {"job_state": {k: job.state[k] for k in ("code_version", "git_head", "seed", "params")}, "results": R})
    md = ["# Phase 3: old vs new pipeline", "",
          f"code_version `{job.state['code_version']}`, git `{job.state['git_head']}`", "",
          "| n | vertices | orbits | switch classes | old: completions / s | new: completions / s | speedup | old-order+exact s | new-order+legacy s | all checks |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    bad = []
    for n in ns:
        r = R[f"n{n}"]
        c = r["checks"]
        allok = all(v for k, v in c.items() if isinstance(v, bool))
        if not allok:
            bad.append((n, c))
        md.append(f"| {n} | {r['vertices']} | {c['orbit_count']} | {r['new']['switch_classes']} | "
                  f"{r['old']['completions_run']} / {r['old']['seconds']:.3f} | {r['new']['completions_run']} / {r['new']['seconds']:.4f} | "
                  f"{r['old']['seconds'] / r['new']['seconds']:.0f}x | {r['old_order_exact']['seconds']:.3f} | "
                  f"{r['new_order_legacy']['seconds']:.4f} | {'PASS' if allok else 'FAIL'} |")
    md += ["", "Whole-vertex-set completion (original script's use case):", "",
           "| n | vertices | legacy float LP: s (LPs) | exact: s (LPs) | same valid set |", "|---|---|---|---|---|"]
    for n in ns:
        r = R[f"n{n}"]
        md.append(f"| {n} | {r['vertices']} | {r['vset_legacy']['seconds']:.3f} ({r['vset_legacy']['lps']}) | "
                  f"{r['vset_exact']['seconds']:.4f} ({r['vset_exact']['lps']}) | {r['checks']['vset_valid_sets_equal']} |")
    md += ["", "Stage timings (seconds):", ""]
    for n in ns:
        r = R[f"n{n}"]
        md.append(f"- n={n}: old {r['old']['stage_seconds']}; new {r['new']['stage_seconds']}")
    atomic_write_text(OUT / "benchmark.md", "\n".join(md) + "\n")
    print("\n".join(md))
    if bad:
        print("\nFAILED CHECKS:", json.dumps(bad, indent=1))
        sys.exit(1)


if __name__ == "__main__":
    main()
