"""Shared helpers for the Phase 9 judge and the agents' tools (exact verification only)."""
from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from metricpoly import core  # noqa: E402
from metricpoly.core import Point  # noqa: E402
from metricpoly.dsl.interp import Interpreter  # noqa: E402
from metricpoly.dsl.prims import DomainList, p_feasible, p_vertex  # noqa: E402
from metricpoly.dsl.registry import REGISTRY  # noqa: E402

BASE_FILES = ["stdlib.mpr", "literature.mpr", "mutations.mpr", "fractal.mpr", "phase7.mpr", "phase8.mpr"]
ACCEPTED = ROOT / "rules" / "phase9_accepted.mpr"


def interpreter(extra_files=(), seed=20261122):
    I = Interpreter(seed=seed)
    for f in BASE_FILES:
        I.load_file(ROOT / "rules" / f)
    if ACCEPTED.exists() and ACCEPTED.read_text(encoding="utf-8").strip():
        I.load_file(ACCEPTED)
    names = []
    for f in extra_files:
        names += I.load_file(Path(f))
    I.finalize()
    return I, names


def point_from_json(d) -> Point:
    if "nums" in d:
        return Point.make(int(d["n"]), int(d.get("D", 1)), [int(v) for v in d["nums"]])
    from fractions import Fraction
    return Point.from_fractions(int(d["n"]), [Fraction(str(v)) for v in d["coords"]])


def verify_vertex(x: Point) -> dict:
    """Exact: every triangle/perimeter inequality holds and the tight set has full rank C(n,2)."""
    s = core.slacks(x)
    feas = bool((s >= 0).all())
    tight = int((s == 0).sum())
    return {"feasible": feas, "tight": tight, "dim": len(core.pairs(x.n)),
            "vertex": bool(feas and p_vertex(x)), "D": x.D, "n": x.n}


class only_vertices:
    """Context manager: (vertices n) returns just the given point(s) for size n (other sizes unchanged), marked as a
    partial list, so a structural rule can be evaluated on a candidate counterexample."""

    def __init__(self, pts):
        self.pts = pts
        self.n = pts[0].n

    def __enter__(self):
        self.old = REGISTRY["vertices"]
        old_fn, pts, n = self.old.fn, self.pts, self.n

        def fn(m):
            if int(m) == n:
                L = DomainList(pts)
                L.kind, L.n, L.complete = "all", n, False
                return L
            return old_fn(m)
        REGISTRY["vertices"] = dataclasses.replace(self.old, fn=fn)
        return self

    def __exit__(self, *a):
        REGISTRY["vertices"] = self.old


def eval_structural_on(I, rule_name, x: Point):
    """True/False: does the structural rule hold when the vertex set of size x.n is just {x}?"""
    rule = I.rules[rule_name]
    I.memo.clear()
    with only_vertices([x]):
        v = I.run_rule(rule, x.n)
    I.memo.clear()
    return bool(v)


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))
