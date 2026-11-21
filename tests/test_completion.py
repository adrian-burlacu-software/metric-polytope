"""Exact completion: correctness vs brute force, equivariance, box/LP path, switching classes."""
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from metricpoly import core, deza, group, pipeline, polyhedra  # noqa: E402
from metricpoly.completion import complete  # noqa: E402

SEED = 20261121


def test_all_facets_valid_on_full_vertex_set():
    for n in (4, 5, 6):
        V = polyhedra.enumerate_vertices(n)
        c = complete(n, V)
        assert len(c.valid_set()) == 4 * (n * (n - 1) * (n - 2) // 6)
        assert all(r.method == "max_over_generators" for r in c.results)


def test_partial_vset_matches_bruteforce():
    n = 5
    rng = np.random.default_rng(SEED)
    V = polyhedra.enumerate_vertices(n)
    for _ in range(20):
        W = [V[i] for i in rng.choice(len(V), 3, replace=False)]
        W.append(core.Point.make(n, 1, [1] * core.dim(n)))            # infeasible point
        c = complete(n, W)
        for r, q in zip(c.results, core.metric_inequalities(n)):
            mx = max(sum(Fraction(a) * x for a, x in zip(q.a, p.fractions())) for p in W)
            assert r.valid == (mx <= q.b) and r.max_value == mx


def test_rays():
    n = 4
    cut = core.Point.make(n, 1, [1, 1, 1, 0, 0, 0])
    ray = core.Point.make(n, 1, [1, 1, 0, 0, 1, 1])
    c = complete(n, [cut], [ray])
    for r, q in zip(c.results, core.metric_inequalities(n)):
        if sum(a * x for a, x in zip(q.a, ray.nums)) > 0:
            assert not r.valid and r.method == "ray_unbounded"


def test_box_lp_exact():
    n = 3
    # V outside the box: the box cuts conv(V); LP must find max over conv(V) ∩ box exactly
    V = [core.Point.make(3, 1, [0, 0, 0]), core.Point.make(3, 1, [2, 2, 2])]
    c = complete(n, V, box=True)
    # perimeter x12+x13+x23 <= 2: on the segment t*(2,2,2) ∩ box, max at t=1/2 -> 3
    per = [r for r, q in zip(c.results, core.metric_inequalities(3)) if q.kind == "perimeter"][0]
    assert per.method == "lp_exact" and per.max_value == 3 and not per.valid
    c2 = complete(n, V, box=False)
    per2 = [r for r, q in zip(c2.results, core.metric_inequalities(3)) if q.kind == "perimeter"][0]
    assert per2.max_value == 6


@pytest.mark.parametrize("n", [5, 6, 7])
def test_completion_equivariant(n):
    rng = np.random.default_rng(SEED)
    for x in deza.load_ext(n):
        for _ in range(3):
            p, s = group.random_element(n, rng)
            y = group.apply(n, p, s, x)
            act = group.ineq_action(n, p, s)
            sx = pipeline.exact_slacks(x)
            sy = pipeline.exact_slacks(y)
            assert x.D == y.D and (sy[act] == sx).all()


@pytest.mark.parametrize("n", [4, 5, 6])
def test_switch_canon_fast(n):
    for p in polyhedra.enumerate_vertices(n):
        assert group.switch_canon_fast(p) == group.switch_canon(p)


@pytest.mark.parametrize("n", [5, 6, 7, 8])
def test_canonical_with_element(n):
    rng = np.random.default_rng(SEED)
    R = deza.load_ext(n)
    for i in rng.choice(len(R), min(5, len(R)), replace=False):
        x = R[int(i)]
        c, p, s = group.canonical_with_element(x)
        assert c == group.canonical(x) == group.apply(n, p, s, x)


def test_switch_classes_are_blocks_of_orbits():
    # every orbit is a disjoint union of whole switching classes, of equal size 2^(n-1)/|K-stab|
    n = 6
    V = polyhedra.enumerate_vertices(n)
    cls = {}
    for p in V:
        cls.setdefault(group.switch_canon_fast(p), []).append(group.canonical(p).key())
    assert all(len(set(keys)) == 1 for keys in cls.values())
