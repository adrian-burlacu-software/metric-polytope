"""DSL tests: parser, primitives, interpreter semantics, symmetry policy, gluing spec = fast, closure, core freeze."""
import hashlib
import itertools
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from metricpoly import core, deza, group, polyhedra  # noqa: E402
from metricpoly.dsl import prims  # noqa: E402
from metricpoly.dsl.interp import DSLError, Interpreter  # noqa: E402
from metricpoly.dsl.registry import kernel_table  # noqa: E402
from metricpoly.dsl.sexpr import read, read_all, write  # noqa: E402
from metricpoly.dsl.values import Graph  # noqa: E402


@pytest.fixture(scope="module")
def I():
    it = Interpreter(params={"closure-max-n": 6})
    for f in ("stdlib.mpr", "literature.mpr", "blocks.mpr"):
        it.load_file(ROOT / "rules" / f)
    it.finalize()
    return it


def ev(I, src):
    return I.eval(read(src), I.globals)


# ------------------------------------------------------------------ parser
def test_roundtrip_all_rule_files():
    for f in (ROOT / "rules").glob("*.mpr"):
        forms = read_all(f.read_text(encoding="utf-8"))
        again = read_all("\n".join(write(x) for x in forms))
        assert forms == again


def test_atoms():
    assert read("(a 2/3 -1/6 4/2 #t :k {2 0 1})") == read("(a 2/3 -1/6 2 #t :k {0 1 2})")


# ------------------------------------------------------------------ primitives
def test_block_split_inverse(I):
    x = deza.load_ext(7)[8]
    A, M, B = prims.p_split(frozenset({0, 2, 5}), x)
    y = prims.p_block(A, M, B)
    # y is x relabelled so that {0,2,5} come first: same orbit
    assert group.canonical(y) == group.canonical(x)


def test_twin_is_trivial_extension(I):
    I.globals.vars["v5"] = deza.load_ext(5)[1]                     # anticut of m_5
    outs = ev(I, "(apply-move twin (list v5))")
    assert len(outs) == 10 and all(prims.p_vertex(p) for p in outs)


def test_graph_metric_and_graphic(I):
    assert ev(I, "(vertex? (graphic (K 5)))")                       # (2/3)1 = anticut
    assert not ev(I, "(vertex? (graphic (K 4)))")
    assert ev(I, "(triameter (path-graph 4))") == 6


def test_good_matches_definition():
    for n in range(2, 7):
        for E in itertools.islice(itertools.combinations(itertools.combinations(range(n), 2), n), 0, 200):
            G = Graph.make(n, E)
            assert prims.p_good(G) == prims.good_by_definition(G)


def test_adjacency_certified():
    V = polyhedra.enumerate_vertices(5)
    cuts = [p for p in V if p.D == 1]
    assert all(prims.p_adjacent(a, b) for a, b in itertools.combinations(cuts, 2))   # cuts form a clique
    for a, b in itertools.combinations(V[:12], 2):
        A, _ = core.ineq_matrix(5)
        import numpy as np
        T = np.intersect1d(core.tight_set(a), core.tight_set(b))
        assert prims.p_adjacent(a, b) == (core.exact_rank(A[T].tolist()) == 9)


def test_fiber_of_twin_contains_twin(I):
    I.globals.vars["v6"] = deza.load_ext(6)[2]
    fib = prims.p_fiber_vertices(prims.p_lift_partial(I.globals.vars["v6"]))
    assert ev(I, "(twin-of 0 0 v6)") in fib


def test_literature_examples_are_vertices(I):
    for name in ("lp-ex-2-14", "ddf-v7", "ddf-v8", "ddf-v9", "ddf-v10", "lp-ex-2-13", "dfmv-451", "dfmv-531", "di-2005"):
        assert ev(I, f"(vertex? {name})"), name


def test_lp_ex_2_14_has_no_vertex_projection(I):
    assert not ev(I, "(exists ((i (range 0 7))) (vertex? (restrict (all-but 7 i) lp-ex-2-14)))")


# ------------------------------------------------------------------ interpreter semantics
def test_recursion_must_decrease(I):
    J = Interpreter()
    J.load_source("(generative bad (n) (bad n))")
    J.finalize()
    with pytest.raises(DSLError):
        J.run_rule(J.rules["bad"], 4)


def test_unknown_name_rejected_at_load():
    J = Interpreter()
    J.load_source("(define (f x) (no-such-thing x))")
    with pytest.raises(DSLError):
        J.finalize()


def test_witness_reports_counterexample(I):
    v = I.run_rule(I.rules["projects-to-smaller-vertex"], 7)
    assert not v and "x" in v.witness["binding"]


def test_symmetry_policy_rejects_label_dependent_body():
    J = Interpreter()
    J.load_source("(generative lab (n) (for ((x (vertices n))) (where (= (entry x 0 1) 0)) x))")
    J.finalize()
    with pytest.raises(DSLError):
        J.run_rule(J.rules["lab"], 7)


def test_glue_fast_equals_spec(I):
    reps = {3: polyhedra.enumerate_vertices(3)[:1], 4: polyhedra.enumerate_vertices(4)[:1], 5: deza.load_ext(5)}
    for a, b in [(3, 4), (4, 4), (5, 3)]:
        for x1 in reps[a]:
            for x2 in reps[b]:
                for spec, fast in (("glue-spec", "glue"), ("glue-all-spec", "glue-all")):
                    s = {group.canonical(p).key() for p in I.apply_move_raw(I.moves[spec], [x1, x2])}
                    f = {group.canonical(p).key() for p in I.apply_move_raw(I.moves[fast], [x1, x2])}
                    assert s == f


def test_closure_saturates_and_matches_phase2(I):
    from metricpoly.dsl.closure import run_closure
    seeds = [prims.p_cut(3, frozenset()), ev(I, "(anticut 5 {})")]
    C = run_closure(I, seeds, [I.moves[m] for m in ("twin", "lift-fiber", "radial")], max_n=6, verbose=False)
    assert C.saturated
    for n in range(3, 7):
        assert C.keys(n) == {group.canonical(p).key() for p in polyhedra.enumerate_vertices(n)}


def test_block_rules_run(I):
    assert I.run_rule(I.rules["block-fractal-any"], 5)
    t = ev(I, "(decompose (anticut 5 {}) 3 #f)")
    assert t and t.label == "split"


def test_formula_rendering(I):
    from metricpoly.dsl.pretty import rule_formula
    for r in I.rules.values():
        assert rule_formula(r, "unicode") and rule_formula(r, "latex")


# ------------------------------------------------------------------ core freeze
FROZEN = ROOT / "tests" / "core_freeze.sha256"


def test_core_freeze():
    """Parser + kernel primitive table must not change when the DSL grows (extensions go to dsl/ext/)."""
    h = hashlib.sha256()
    h.update((ROOT / "metricpoly" / "dsl" / "sexpr.py").read_bytes())
    h.update(repr(sorted(kernel_table().items())).encode())
    digest = h.hexdigest()
    if not FROZEN.exists():
        FROZEN.write_text(digest + "\n")
    assert FROZEN.read_text().strip() == digest, "parser or kernel table changed: update deliberately"
