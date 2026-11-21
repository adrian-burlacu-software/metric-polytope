"""Orbit pipelines: OLD order (complete + canonicalise every point) vs NEW order
(switching classes -> positional dedupe of class reps -> complete one rep per orbit).

Why NEW is correct: the switching group K is normal in G = K x| S_n, so G/K ~ S_n acts on the set of
switching classes, and G-orbits of points = S_n-orbits of K-classes. The class of x is keyed by
switch_canon(x) (lexmin over K); the orbit of a class is keyed by canonical(rep) (lexmin over G),
which is the same for every member of the class. Completion commutes with G (catalog is G-invariant,
slacks are preserved), so completing one representative per orbit determines every member's completion.
"""
from __future__ import annotations

import time
from fractions import Fraction
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Sequence

import numpy as np

from .core import Point, ineq_matrix
from .group import canonical, canonical_via_switch_canon, canonical_with_element, ineq_action, switch_canon_fast

Engine = Callable[[Point], np.ndarray]     # point -> slack vector (b - a.x) per catalog inequality, as Fractions/floats


@dataclass
class PipelineResult:
    orbits: Dict[str, int]                         # canonical key -> orbit size (within the input set)
    completions_run: int
    canonicalisations_run: int
    switch_classes: int = 0
    timings: Dict[str, float] = field(default_factory=dict)
    per_orbit_completion: Dict[str, object] = field(default_factory=dict)


def run_old(points: Sequence[Point], engine: Engine, canon: Callable[[Point], Point] = canonical_via_switch_canon,
            keep: bool = False) -> PipelineResult:
    t = {}
    t0 = time.perf_counter()
    comps = [engine(p) for p in points]
    t["complete"] = time.perf_counter() - t0
    t0 = time.perf_counter()
    keys = [canon(p).key() for p in points]
    t["canonicalise"] = time.perf_counter() - t0
    orbits: Dict[str, int] = {}
    for k in keys:
        orbits[k] = orbits.get(k, 0) + 1
    r = PipelineResult(orbits, len(points), len(points), timings=t)
    if keep:
        r.per_orbit_completion = {"per_point": comps, "keys": keys}
    return r


def run_new(points: Sequence[Point], engine: Engine) -> PipelineResult:
    t = {}
    t0 = time.perf_counter()
    classes: Dict[Point, List[int]] = {}
    for i, p in enumerate(points):
        classes.setdefault(switch_canon_fast(p), []).append(i)
    t["switch_classes"] = time.perf_counter() - t0
    t0 = time.perf_counter()
    orbits: Dict[str, int] = {}
    reps: Dict[str, Point] = {}
    for sc, members in classes.items():
        k = canonical(sc).key()
        orbits[k] = orbits.get(k, 0) + len(members)
        reps.setdefault(k, sc)
    t["positional_dedupe"] = time.perf_counter() - t0
    t0 = time.perf_counter()
    comp = {k: engine(r) for k, r in reps.items()}
    t["complete"] = time.perf_counter() - t0
    r = PipelineResult(orbits, len(reps), len(classes), switch_classes=len(classes), timings=t,
                       per_orbit_completion={"reps": reps, "comp": comp})
    return r


def transported_slacks(x: Point, rep: Point, rep_slack: np.ndarray) -> np.ndarray:
    """Slack vector of x obtained from its orbit representative's slack vector via the group:
    if g_x.x = c = g_r.rep then slack(x, f) = slack(c, g_x f) = slack(rep, g_r^-1 g_x f)."""
    cx, px, sx = canonical_with_element(x)
    cr, pr, sr = canonical_with_element(rep)
    assert cx == cr
    ax = ineq_action(x.n, px, sx)          # f -> g_x f
    ar = ineq_action(x.n, pr, sr)          # f -> g_r f
    inv_r = np.empty_like(ar)
    inv_r[ar] = np.arange(ar.size)
    return rep_slack[inv_r[ax]]


def exact_slacks(p: Point) -> np.ndarray:
    A, b = ineq_matrix(p.n)
    return (b * p.D - A @ p.array())       # = D * slack, exact ints


def exact_engine(p: Point):
    """Exact completion of the single-point V-set {p}: returns the slack vector scaled by p.D."""
    from .completion import complete
    c = complete(p.n, [p])
    b = ineq_matrix(p.n)[1]
    return np.array([(Fraction(int(b[r.index])) - r.max_value) * p.D for r in c.results], dtype=object)
