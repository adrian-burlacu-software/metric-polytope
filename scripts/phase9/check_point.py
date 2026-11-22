#!/usr/bin/env python3
"""Agent tool (Phase 9): exact checks on candidate points.

Input JSON: a list of {"n": .., "D": .., "nums": [...]} (upper triangle, lexicographic pair order, x = nums / D)
or {"n": .., "coords": ["1/3", ...]}; optional "rule": name of a structural rule to test on that point.
Per point: feasibility, tight-set size, vertex (exact: all inequalities hold and tight rank = C(n,2)); for n <= 9 the
canonical orbit key, whether it is a Deza orbit (n <= 8: index), and whether it is a currently unreached node/target;
with a rule: whether the rule FAILS on the point (= counterexample, if the point is a vertex).
Usage: python scripts/phase9/check_point.py FILE.json [--rule NAME]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, eval_structural_on, interpreter, load_json, point_from_json, verify_vertex  # noqa: E402

from metricpoly import deza, group  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--rule")
    ap.add_argument("--extra", nargs="*", default=[], help="extra .mpr files to load (e.g. a proposal)")
    args = ap.parse_args()
    items = load_json(args.file)
    if isinstance(items, dict):
        items = [items]
    I, _ = interpreter(args.extra)
    unr_path = ROOT / "results/phase9/unreached_nodes.json"
    U = load_json(unr_path) if unr_path.exists() else {"keys": [], "target_keys": []}
    unreached, unr_targets = set(U["keys"]), set(U["target_keys"])
    idx = {}
    out = []
    for it in items:
        x = point_from_json(it)
        r = verify_vertex(x)
        if x.n <= 9:
            k = group.canonical(x).key()
            r["key"] = k
            if x.n <= 8:
                if x.n not in idx:
                    idx[x.n] = {group.canonical(p).key(): i + 1 for i, p in enumerate(deza.load_ext(x.n))}
                r["deza_orbit"] = idx[x.n].get(k)
            r["unreached_node"] = k in unreached
            r["unreached_target"] = k in unr_targets
        rule = args.rule or it.get("rule")
        if rule and rule in I.rules and I.rules[rule].kind == "structural" and r["vertex"]:
            try:
                r["rule"] = rule
                r["rule_fails_here"] = not eval_structural_on(I, rule, x)
            except Exception as ex:
                r["rule_error"] = f"{type(ex).__name__}: {ex}"[:300]
        out.append(r)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
