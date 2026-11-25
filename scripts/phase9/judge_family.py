#!/usr/bin/env python3
"""Judge for the family rounds (round 18): conditions on {1,2}-weighted minimal graphs vs being an extreme ray.

  python scripts/phase9/judge_family.py pools                 build non-ray pools (public + held-out) and k = 9 rays
  python scripts/phase9/judge_family.py judge phase9/round_18  judge maker claims and breaker candidates

Positives: results/phase9/family12/rays_k{5..8}.json (complete) and rays_k9.json (from the full m_9 run: the
simplest-alphabet switching of each orbit, so a sample of the k = 9 rays; every one re-checked exactly here).
Non-rays: seeded perturbations of the rays (one edge weight flipped, one edge removed or added), kept if connected,
minimal, weights in {1, 2} and exactly not a ray. nonrays_public_k*.json is given to the maker; nonrays_heldout_k*.json
is used only here.

A maker claim is a file phase9/round_NN/maker/NAME.py with KIND ("necessary" | "sufficient" | "iff"), STATEMENT (one
sentence, valid for every k) and claim(k, edges) -> bool. necessary: must be True on every ray. sufficient: must be
False on every non-ray (minimal, weights in {1,2}). iff: both. Breaker candidates (candidates.json: k, edges, claim,
how) are checked exactly; a ray on which a necessary claim is False, or a non-ray on which a sufficient claim is True,
breaks the claim. Selectivity is reported: for necessary claims the share of non-rays rejected, for sufficient
claims the share of rays accepted.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

import family12 as F  # noqa: E402
from metricpoly.jobs import atomic_write_json  # noqa: E402

OUT = F.OUT


def load(name):
    p = OUT / name
    return [(int(r["k"]), [tuple(e) for e in r["edges"]]) for r in json.loads(p.read_text())] if p.exists() else []


def perturb(k, edges, rng):
    E = {(min(a, b), max(a, b)): w for a, b, w in edges}
    t = int(rng.integers(0, 3))
    pairs = [(a, b) for a in range(k) for b in range(a + 1, k)]
    if t == 0:
        e = list(E)[int(rng.integers(0, len(E)))]
        E[e] = 3 - E[e]
    elif t == 1 and len(E) > k:
        del E[list(E)[int(rng.integers(0, len(E)))]]
    else:
        non = [p for p in pairs if p not in E]
        if not non:
            return None
        E[non[int(rng.integers(0, len(non)))]] = int(rng.integers(1, 3))
    return sorted((a, b, w) for (a, b), w in E.items())


def _pool_job(args):
    k, rays, seed, want = args
    rng = np.random.default_rng(seed)
    out, tries = [], 0
    while len(out) < want and tries < want * 60:
        tries += 1
        base = rays[int(rng.integers(0, len(rays)))]
        e = perturb(k, base, rng)
        for _ in range(int(rng.integers(0, 2))):             # sometimes a second perturbation
            e = perturb(k, e, rng) if e else None
        if not e:
            continue
        c = F.check(k, e)
        if c["connected"] and c["minimal"] and not c["ray"]:
            out.append((k, [list(t) for t in e]))
    return out


def pools():
    import multiprocessing as mp
    t0 = time.time()
    fam9 = ROOT / "results/phase9/graph_family_12_m9.json"
    if fam9.exists() and not (OUT / "rays_k9.json").exists():
        items = []
        for r in json.loads(fam9.read_text()):
            k, e = F.relabel([tuple(x) for x in r["edges"]])
            if k == 9:
                items.append((k, e))
        uniq = F.dedupe(items)
        with mp.get_context("spawn").Pool(12) as pool:
            ok = pool.starmap(F.check, uniq, chunksize=64)
        good = [{"k": k, "edges": e} for (k, e), c in zip(uniq, ok) if c["ray"]]
        atomic_write_json(OUT / "rays_k9.json", good)
        print(f"k = 9: {len(uniq)} distinct family graphs from the m_9 run, {len(good)} confirmed rays "
              f"({time.time() - t0:.0f} s)", flush=True)
    with mp.get_context("spawn").Pool(12) as pool:
        for k in (6, 7, 8, 9):
            rays = [e for _k, e in load(f"rays_k{k}.json")]
            if not rays:
                continue
            for name, seed, want in (("public", 1801, 1500), ("heldout", 1802, 1500)):
                parts = pool.map(_pool_job, [(k, rays, seed * 100 + j, want // 12 + 1) for j in range(12)])
                uniq = F.dedupe([x for p in parts for x in p])
                atomic_write_json(OUT / f"nonrays_{name}_k{k}.json", [{"k": kk, "edges": e} for kk, e in uniq])
                print(f"k = {k} {name}: {len(uniq)} distinct non-rays ({time.time() - t0:.0f} s)", flush=True)


def judge(rdir):
    t0 = time.time()
    rdir = ROOT / rdir
    pos = {k: load(f"rays_k{k}.json") for k in range(5, 10)}
    neg = {k: load(f"nonrays_heldout_k{k}.json") + load(f"nonrays_public_k{k}.json") for k in range(6, 10)}
    cands = []
    raw, seen = [], set()
    for fn_ in ("candidates.json", "new_rays.json"):          # every candidate is tested against every claim
        cf = rdir / "breaker" / fn_
        if cf.exists():
            for c in json.loads(cf.read_text()):
                sig = (int(c["k"]), tuple(sorted(tuple(x) for x in c["edges"])))
                if sig not in seen:
                    seen.add(sig)
                    raw.append(c)
    if raw:
        for c in raw:
            k, e = int(c["k"]), [tuple(x) for x in c["edges"]]
            v = F.check(k, e)
            ok12 = set(v["weights"]) <= {1, 2}
            cands.append(dict(c, verdict=v, in_scope=bool(v["connected"] and v["minimal"] and ok12)))
    res = []
    for f in sorted((rdir / "maker").glob("*.py")):
        spec = importlib.util.spec_from_file_location(f.stem, f)
        mod = importlib.util.module_from_spec(spec)
        row = {"file": f.name}
        try:
            spec.loader.exec_module(mod)
            kind, fn = mod.KIND, mod.claim
            row.update(name=getattr(mod, "NAME", f.stem), kind=kind, statement=mod.STATEMENT)
            t = time.time()
            per_k, viol = {}, []
            for k in sorted(pos):
                tp = sum(1 for kk, e in pos[k] if fn(kk, e))
                tn = [e for kk, e in neg.get(k, []) if fn(kk, e)]
                per_k[str(k)] = {"rays": len(pos[k]), "rays_true": tp, "nonrays": len(neg.get(k, [])),
                                 "nonrays_true": len(tn)}
                if kind in ("necessary", "iff") and tp < len(pos[k]):
                    bad = next(e for kk, e in pos[k] if not fn(kk, e))
                    viol.append({"k": k, "why": "a ray where the claim is False", "count": len(pos[k]) - tp,
                                 "edges": bad})
                if kind in ("sufficient", "iff") and tn:
                    viol.append({"k": k, "why": "a non-ray where the claim is True", "count": len(tn),
                                 "edges": tn[0]})
            for c in cands:
                if not c["in_scope"]:
                    continue
                val = bool(fn(int(c["k"]), [tuple(x) for x in c["edges"]]))
                if c["verdict"]["ray"] and not val and kind in ("necessary", "iff"):
                    viol.append({"k": c["k"], "why": "breaker: a ray where the claim is False", "edges": c["edges"]})
                if not c["verdict"]["ray"] and val and kind in ("sufficient", "iff"):
                    viol.append({"k": c["k"], "why": "breaker: a non-ray where the claim is True",
                                 "edges": c["edges"]})
            R = sum(v["rays"] for v in per_k.values())
            RT = sum(v["rays_true"] for v in per_k.values())
            N = sum(v["nonrays"] for v in per_k.values())
            NT = sum(v["nonrays_true"] for v in per_k.values())
            row.update(per_k=per_k, violations=viol, status="BROKEN" if viol else "HOLDS",
                       rays_accepted=round(RT / max(1, R), 4), nonrays_rejected=round(1 - NT / max(1, N), 4),
                       seconds=round(time.time() - t, 1))
        except Exception as e:      # noqa: BLE001
            row.update(status="ERROR", error=f"{type(e).__name__}: {e}")
        res.append(row)
        print(f"{row['file']}: {row.get('kind')} {row['status']} rays accepted {row.get('rays_accepted')} "
              f"non-rays rejected {row.get('nonrays_rejected')} ({row.get('seconds')} s)", flush=True)
    out = {"round": rdir.name, "positives": {str(k): len(v) for k, v in pos.items()},
           "nonrays": {str(k): len(v) for k, v in neg.items()}, "claims": res, "candidates": cands,
           "seconds": round(time.time() - t0, 1)}
    atomic_write_json(ROOT / "results/phase9" / f"{rdir.name}_family.json", out)
    lines = [f"# Phase 9 {rdir.name}: family {{1,2}} claims", "",
             f"Rays per k: {out['positives']}; non-rays per k: {out['nonrays']}. Judge time {out['seconds']} s.", "",
             "| file | kind | status | rays accepted | non-rays rejected | first violation |", "|---|---|---|---|---|---|"]
    for r in res:
        v = r.get("violations") or []
        first = (str(v[0]["k"]) + ": " + v[0]["why"]) if v else r.get("error", "")
        lines.append(f"| {r['file']} | {r.get('kind')} | {r['status']} | {r.get('rays_accepted')} | "
                     f"{r.get('nonrays_rejected')} | {first} |")
    lines += ["", "## Statements", ""]
    lines += [f"- **{r.get('name', r['file'])}** ({r.get('kind')}): {r.get('statement', '')}" for r in res]
    lines += ["", "## Breaker candidates", "", "| k | claim | in scope | ray | how |", "|---|---|---|---|---|"]
    lines += [f"| {c['k']} | {c.get('claim')} | {c['in_scope']} | {c['verdict']['ray']} | {c.get('how', '')} |"
              for c in cands]
    (ROOT / "results/phase9" / f"{rdir.name}_family.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1] == "pools":
        pools()
    else:
        judge(sys.argv[2])
