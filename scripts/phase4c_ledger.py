#!/usr/bin/env python3
"""Phase 4c: run every literature rule against verified data and seed the rule ledger (rules.md).

Data: full vertex sets n <= 6 (cdd, Phase 2); Deza orbit representatives n = 7, 8.
Each (rule, n) is one checkpointed task. Counterexamples are saved to results/ledger/counterexamples/.

Usage: python -u scripts/phase4c_ledger.py [--max-n 7] [--only RULE ...] [--resume] [--force]
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
from metricpoly.dsl.interp import Interpreter, Verdict  # noqa: E402
from metricpoly.dsl.pretty import rule_formula  # noqa: E402
from metricpoly.dsl.prims import p_vertex  # noqa: E402
from metricpoly.jobs import Job, add_job_args, atomic_write_json, atomic_write_text  # noqa: E402

OUT = ROOT / "results" / "ledger"
CEX = OUT / "counterexamples"
FILES = ["stdlib.mpr", "literature.mpr", "mutations.mpr", "fractal.mpr"]

# Model mutation from the literature (Phase 7 will verify it on data/deza/raw/1221_counterexamples.txt).
LITERATURE_MUTATIONS = [{
    "id": "M0", "rule": "dominating-set",
    "statement": "Every vertex of m_n is adjacent to a cut (Laurent–Poljak 1992).",
    "holds": "n <= 8 (Deza et al., complete m_8)", "breaks_at": 9,
    "evidence": "Deza–Indik 2007: 1,221 known orbits of m_9 vertices not adjacent to any cut; "
                "example (1/9)(2,2,3,3,4,4,5,5,4,3,5,6,6,3,3,5,5,2,4,3,5,6,3,3,6,6,5,3,2,6,6,3,3,5,3,4).",
    "status": "LITERATURE — not yet verified in code (Phase 7)"}]


def in_domain(rule, n):
    d = tuple(rule.meta.get("domain", (3,)))
    return d[0] <= n <= (d[1] if len(d) > 1 else 99)


def deza_index(n):
    return {group.canonical(p).key(): i for i, p in enumerate(deza.load_ext(n), 1)}


def enc(v):
    if isinstance(v, core.Point):
        return {"n": v.n, "coords": v.strs(), "deza_orbit": deza_index(v.n).get(group.canonical(v).key())
                if 3 <= v.n <= 8 else None}
    if isinstance(v, frozenset):
        return sorted(v)
    if isinstance(v, (list, tuple)):
        return [enc(x) for x in v]
    if isinstance(v, dict):
        return {k: enc(x) for k, x in v.items()}
    return v if isinstance(v, (int, str, bool, type(None))) else str(v)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_job_args(ap)
    ap.add_argument("--max-n", type=int, default=7)
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args()
    params = {"max_n": args.max_n, "files": FILES, "only": args.only}
    job = Job(f"phase4c_ledger_n{args.max_n}" + ("_" + "_".join(args.only) if args.only else ""), params, args.seed,
              resume=args.resume, force=args.force)
    I = Interpreter(seed=args.seed)
    for f in FILES:
        I.load_file(ROOT / "rules" / f)
    I.finalize()
    CEX.mkdir(parents=True, exist_ok=True)
    for name, rule in I.rules.items():
        if args.only and name not in args.only:
            continue
        for n in range(3, args.max_n + 1):
            if not in_domain(rule, n) or (rule.kind == "generative" and n > 8):
                continue
            task = f"{name}@{n}"
            if job.is_done(task):
                continue
            t = time.time()
            try:
                val = I.run_rule(rule, n)
                err = None
            except Exception as ex:          # recorded, not hidden
                val, err = None, f"{type(ex).__name__}: {ex}"
            dt = round(time.time() - t, 2)
            rec = {"rule": name, "kind": rule.kind, "n": n, "seconds": dt, "error": err}
            if err is None and rule.kind == "structural":
                rec["holds"] = bool(val)
                if not val and isinstance(val, Verdict) and val.witness:
                    w = enc(val.witness.get("values", {}))
                    path = CEX / f"{name}_n{n}.json"
                    atomic_write_json(path, {"rule": name, "n": n, "witness": w,
                                             "binding": val.witness.get("binding"), "rule_source": rule.source})
                    rec["counterexample"] = str(path.relative_to(ROOT).as_posix())
                    rec["witness"] = w
            elif err is None:
                idx = deza_index(n) if n <= 8 else {}
                vs = [p for p in val if isinstance(p, core.Point) and p.n == n and p_vertex(p)]
                keys = {group.canonical(p).key() for p in vs}
                rec.update({"candidates": len(val), "vertices": len(vs),
                            "orbits": sorted(idx.get(k, "?") for k in keys) if idx else len(keys),
                            "non_vertex_candidates": len(val) - len(vs)})
            print(f"[{task}] {dt}s " + (f"ERROR {err}" if err else
                  (f"holds={rec['holds']}" if rule.kind == "structural" else f"orbits={rec['orbits']}")), flush=True)
            job.record(task, rec)
    write_ledger(I, job, args)


def write_ledger(I, job, args):
    R = job.results()
    md = ["# Rule ledger", "",
          "Every rule is DSL source in `rules/*.mpr`; this file is generated by `scripts/phase4c_ledger.py`.",
          f"Data: n <= 6 full vertex sets (cdd), n = 7, 8 Deza orbit representatives. code_version "
          f"`{job.state['code_version']}`, git `{job.state['git_head']}`.", "",
          "Status legend: holds for every tested n / **BREAKS** at the first failing n (counterexample saved) / "
          "error = rule could not be evaluated.", ""]
    for kind in ("structural", "generative"):
        md += [f"## {kind.capitalize()} rules", ""]
        for name, rule in I.rules.items():
            if rule.kind != kind:
                continue
            recs = sorted((v for k, v in R.items() if v.get("rule") == name), key=lambda r: r["n"])
            if not recs:
                continue
            md += [f"### `{name}`", "", f"- English: {rule.meta.get('doc', '')}",
                   f"- Source: {rule.meta.get('source', '')}", f"- Formula: `{rule_formula(rule)}`"]
            if kind == "structural":
                ok = [r["n"] for r in recs if r.get("holds") is True]
                bad = [r for r in recs if r.get("holds") is False]
                errs = [r for r in recs if r.get("error")]
                md.append(f"- Holds for n = {ok or '—'}")
                if bad:
                    b = bad[0]
                    md.append(f"- **BREAKS at n = {b['n']}**; counterexample `{b.get('counterexample')}`: "
                              f"`{json.dumps(b.get('witness'))[:400]}`")
                for e in errs:
                    md.append(f"- error at n = {e['n']}: {e['error'][:300]}")
            else:
                for r in recs:
                    if r.get("error"):
                        md.append(f"- n = {r['n']}: error {r['error'][:200]}")
                    else:
                        md.append(f"- n = {r['n']}: {r['candidates']} candidates, {r['vertices']} vertices, "
                                  f"Deza orbits {r['orbits']}")
            md += ["", "```lisp", rule.source, "```", ""]
    # ---------------------------------------------------------------- mutation log
    fixes = {r.meta["fixes"]: r for r in I.rules.values() if "fixes" in r.meta}
    log = list(LITERATURE_MUTATIONS)
    k = 1
    for name, rule in I.rules.items():
        if rule.kind != "structural":
            continue
        bad = sorted((v for v in R.values() if v.get("rule") == name and v.get("holds") is False), key=lambda r: r["n"])
        if not bad:
            continue
        ok = sorted(v["n"] for v in R.values() if v.get("rule") == name and v.get("holds") is True)
        entry = {"id": f"M{k}", "rule": name, "statement": rule.meta.get("doc", ""), "source": rule.meta.get("source"),
                 "holds": ok, "breaks_at": bad[0]["n"], "counterexample": bad[0].get("counterexample"),
                 "witness": bad[0].get("witness"), "status": "VERIFIED in code"}
        if name in fixes:
            fx = fixes[name]
            entry["extension"] = {"rule": fx.name, "level": fx.meta.get("level"), "source": fx.source}
            checked = [r for r in I.rules.values() if r.kind == "structural" and r.meta.get("source", "").startswith(
                fx.meta.get("source", "").split()[0]) and r.name != name]
            entry["extension"]["rechecked_by"] = {
                c.name: {str(v["n"]): v.get("holds") for v in R.values() if v.get("rule") == c.name} for c in checked}
        log.append(entry)
        k += 1
    md += ["## Mutation log", "",
           "A mutation = a rule that holds up to some n and breaks at the next tested n. Literature entries are "
           "marked as such until verified.", ""]
    for e in log:
        md.append(f"### {e['id']}: `{e['rule']}` breaks at n = {e['breaks_at']}")
        md.append(f"- Statement: {e['statement']}")
        md.append(f"- Holds for: {e['holds']}")
        md.append(f"- Status: {e['status']}")
        if e.get("evidence"):
            md.append(f"- Evidence: {e['evidence']}")
        if e.get("counterexample"):
            md.append(f"- Counterexample file: `{e['counterexample']}`")
        if e.get("extension"):
            x = e["extension"]
            md.append(f"- DSL extension (level {x['level']}): `{x['rule']}`; recheck: {x['rechecked_by']}")
            md += ["", "```lisp", x["source"], "```"]
        md.append("")
    OUT.mkdir(parents=True, exist_ok=True)
    atomic_write_json(OUT / "mutations.json", log)
    atomic_write_json(OUT / "ledger.json", R)
    atomic_write_text(ROOT / "rules.md", "\n".join(md) + "\n")
    print(f"wrote rules.md ({len(R)} task records)")


if __name__ == "__main__":
    main()
