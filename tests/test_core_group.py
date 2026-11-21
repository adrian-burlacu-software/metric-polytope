"""Unit tests: exact vertex test, group action, canonical forms, stabilizers, clause patterns."""
import math
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from metricpoly import core, deza, group, patterns, polyhedra  # noqa: E402

SEED = 20261121


def cut(n, S):
    return core.Point.make(n, 1, [int((i in S) != (j in S)) for (i, j) in core.pairs(n)])


# ------------------------------------------------------------ core

def test_pair_order_is_lex():
    assert core.pairs(4) == ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))


@pytest.mark.parametrize("n", range(3, 9))
def test_catalog_size(n):
    assert len(core.metric_inequalities(n)) == 4 * math.comb(n, 3)


def test_vertex_test_accepts_and_rejects():
    n = 5
    assert core.is_vertex(cut(n, {0, 2}))[0]
    assert core.is_vertex(core.Point.make(n, 3, [2] * 10))[0]          # all-2/3 vertex
    mid = core.Point.from_fractions(n, [(Fraction(a) + b) / 2 for a, b in
                                        zip(cut(n, {0}).nums, cut(n, {1}).nums)])
    ok, why = core.is_vertex(mid)
    assert not ok and "rank" in why                                     # feasible, not a vertex
    assert not core.is_vertex(core.Point.make(n, 1, [1] * 10))[0]       # violates perimeter


def test_point_normalisation():
    p = core.Point.make(3, 6, [2, 4, 0])
    assert (p.D, p.nums) == (3, (1, 2, 0))


# ------------------------------------------------------------ group

@pytest.mark.parametrize("n", range(3, 7))
def test_group_tables(n):
    assert len(group.perms(n)) * group.switch_flips(n).shape[0] == group.group_order(n)
    # every switching row is a distinct cut
    F = group.switch_flips(n)
    assert len({r.tobytes() for r in F}) == F.shape[0]


@pytest.mark.parametrize("n", range(3, 7))
def test_action_preserves_vertices_and_is_faithful_on_orbits(n):
    rng = np.random.default_rng(SEED + n)
    for p in deza.load_ext(n):
        for _ in range(10):
            q = group.apply(n, *group.random_element(n, rng), p)
            assert core.is_vertex(q)[0]


@pytest.mark.parametrize("n", range(3, 7))
def test_canonical_fast_equals_brute_and_definition(n):
    rng = np.random.default_rng(SEED)
    V = polyhedra.enumerate_vertices(n)
    sample = V if n <= 5 else [V[i] for i in rng.choice(len(V), 10, replace=False)]
    for p in sample:
        c = group.canonical(p)
        assert c == group.canonical_brute(p)
        assert c == group.canonical_via_switch_canon(p)


@pytest.mark.parametrize("n", [6, 7, 8])
def test_canonical_invariant_under_group(n):
    rng = np.random.default_rng(SEED)
    R = deza.load_ext(n)
    for i in rng.choice(len(R), min(len(R), 6), replace=False):
        p = R[int(i)]
        c = group.canonical(p)
        for _ in range(3):
            assert group.canonical(group.apply(n, *group.random_element(n, rng), p)) == c


def test_canonical_handles_half_ties():
    # barycentre of two cuts has many coordinates 1/2: exercises tie branching
    n = 6
    a, b = cut(n, {0, 1}), cut(n, {2})
    p = core.Point.from_fractions(n, [Fraction(x + y, 2) for x, y in zip(a.nums, b.nums)])
    assert group.canonical(p) == group.canonical_brute(p)
    assert group.stabilizer_size(p) == group.stabilizer_size_brute(p)


@pytest.mark.parametrize("n", range(3, 7))
def test_orbit_stabilizer(n):
    for p in deza.load_ext(n):
        assert group.orbit_array(p).shape[0] * group.stabilizer_size(p) == group.group_order(n)


# ------------------------------------------------------------ clause patterns

@pytest.mark.parametrize("n", range(3, 9))
def test_clause_encoding_matches_catalog(n):
    for c, q in zip(patterns.catalog_clauses(n), core.metric_inequalities(n)):
        assert patterns.clause_to_inequality(c) == (q.a, q.b)


def test_switching_turns_triangle_into_perimeter():
    V = patterns.normalize_clause([1, 1, -1, 0])          # x01 - x02 - x12 <= 0
    assert patterns.switch_clause(V, [2]) == (1, 1, 1, 0)   # perimeter


def test_pattern_determines_vertex():
    # solving the tight system recovers the vertex exactly (n=6, all three orbit reps)
    import sympy
    for p in deza.load_ext(6):
        A, b = core.ineq_matrix(6)
        T = core.tight_set(p)
        M = sympy.Matrix(A[T].tolist())
        rhs = sympy.Matrix(b[T].tolist())
        sol = (M.T * M).LUsolve(M.T * rhs)
        assert [Fraction(int(s.p), int(s.q)) for s in sol] == p.fractions()


# ------------------------------------------------------------ deza parsers

def test_up_lattice_padding():
    f = deza.load_up_lattice(4, 1)
    assert f == [[(1, 1, 1, 0)]]
