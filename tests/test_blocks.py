"""Fast block engine == DSL specification (rules/blocks.mpr) on existence of decompositions."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from metricpoly import blocks, deza, polyhedra  # noqa: E402
from metricpoly.dsl.interp import Interpreter  # noqa: E402
from metricpoly.dsl.prims import p_fiber_vertices, p_lift_partial  # noqa: E402
from metricpoly.dsl.sexpr import read  # noqa: E402


@pytest.fixture(scope="module")
def I():
    it = Interpreter()
    for f in ("stdlib.mpr", "literature.mpr", "blocks.mpr"):
        it.load_file(ROOT / "rules" / f)
    it.finalize()
    return it


def spec(I, x, X, bv):
    I.globals.vars["_x"] = x
    return bool(I.eval(read(f"(decompose _x {X} {'#t' if bv else '#f'})"), I.globals))


def points():
    rng = np.random.default_rng(20261121)
    pts = list(polyhedra.enumerate_vertices(5))
    V6 = polyhedra.enumerate_vertices(6)
    pts += [V6[i] for i in rng.choice(len(V6), 25, replace=False)]
    pts += list(deza.load_ext(6))
    # non-vertex points: fiber vertices over the m5 anticut
    pts += [p for p in p_fiber_vertices(p_lift_partial(deza.load_ext(5)[1]))][:10]
    return pts


def test_engine_equals_spec(I):
    E = blocks.Engine()
    for x in points():
        Mx = blocks.matrix(x)
        for bv in (False, True):
            for X in range(4):
                assert E.can(Mx, x.D, X, bv) == spec(I, x, X, bv), (x, X, bv)


def test_class_predicates_switching_invariant():
    from metricpoly.dsl.prims import p_switch
    E = blocks.Engine()
    for x in deza.load_ext(7):
        for S in (frozenset({1}), frozenset({2, 5}), frozenset({3, 4, 6})):
            y = p_switch(S, x)
            for bv in (False, True):
                a = next((X for X in range(4) if E.can(blocks.matrix(x), x.D, X, bv)), None)
                b = next((X for X in range(4) if E.can(blocks.matrix(y), y.D, X, bv)), None)
                assert a == b


def test_build_is_consistent():
    E = blocks.Engine()
    for x in deza.load_ext(7):
        r = E.analyse(x)
        assert r["free"]["Xstar"] is not None          # level 3 always decomposes without the vertex condition
        t = r["free"]["tree"]
        assert sorted(t["T"] + t["Tbar"]) == list(range(1, 8))
