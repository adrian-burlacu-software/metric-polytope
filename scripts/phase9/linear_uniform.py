#!/usr/bin/env python3
"""Finite checks for the bound on the linear locality of C_t that is uniform in t (exact rational arithmetic).

Notation: pi is the partition of Theorem 4 (one class 'alpha' of the A-pairs at distance 1 or >= 3, one class (j)
of the pairs A_i B_j with |i - j| >= 3 for each j, singletons). In the normalised variables u the recurrence (REC)
reads
        u_(i) + 2 u_(i+3) + u_(i+4) = 4 u_alpha .                                  (REC_i)

U1  (REC is derived locally). Sets: the windows [a, a + q) of q consecutive positions (2q points), a in [-r, r].
    Starting from the solution spaces of T_W(pi) and exchanging between these windows only, (REC_0) holds on the
    space of the window [0, q). Reported for several (q, r) and for two values of t (the computation does not
    depend on t once t >= 2r + q + 2, since the union of the windows is then isometric to a segment of C_infinity).
U2  (the end game is local). If u_(j) = u_alpha for all j, the three-point sets merge everything: checked by running
    two-term merges on all three-point sets from the partition pi with all (j) merged into alpha.
U3  (the whole scheme, as a program). linear_family.py --scheme state --local 5.

  python scripts/phase9/linear_uniform.py
Output results/phase9/linear_uniform.json
"""
import itertools
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
from linear_locality import restrict  # noqa: E402
from linear_family import Closure, A, B  # noqa: E402


def with_pi(t):
    C = Closure(t)
    for k in range(3, t - 2):
        C.merge(C.key(A(0, t), A(1, t)), C.key(A(0, t), A(k, t)))
    for i in range(3, t - 2):
        C.merge(C.key(A(3, t), B(0, t)), C.key(A(i, t), B(0, t)))
    assert C.classes() == (t * t + 13 * t + 2) // 2
    return C


def window(t, a, q):
    return tuple(sorted([A(i, t) for i in range(a, a + q)] + [B(i, t) for i in range(a, a + q)]))


def consistent(C, sets):
    fam = [C.space(W) for W in sets]
    nb = [[j for j in range(len(fam)) if j != i and len(set(fam[i][0]) & set(fam[j][0])) >= 2] for i in range(len(fam))]
    queue, inq = list(range(len(fam))), [True] * len(fam)
    while queue:
        i = queue.pop()
        inq[i] = False
        for j in nb[i]:
            ci, cj = restrict(fam[i], fam[j])
            if cj and not inq[j]:
                queue.append(j); inq[j] = True
            if ci and not inq[i]:
                queue.append(i); inq[i] = True
    return fam


def holds(C, S, rel):
    """rel: list of (pair, coefficient); True if sum coef * u_class(pair) = 0 on the space S."""
    vs, ix, basis = S
    cols = [(ix[C.find(C.key(*p))], c) for p, c in rel]
    return all(sum(c * row[j] for j, c in cols) == 0 for row in basis)


def rec(t, i):
    """(REC_i) in class variables, with representatives inside the window [i, i + 5)."""
    return [((A(i + 3, t), B(i, t)), 1), ((A(i, t), B(i + 3, t)), 2), ((A(i, t), B(i + 4, t)), 1),
            ((A(i, t), A(i + 1, t)), -4)]


def u1(t, q, r):
    C = with_pi(t)
    sets = [window(t, a, q) for a in range(-r, r + 1)]
    fam = consistent(C, sets)
    S = fam[r]
    # sanity: the relation is true on d (all u equal) and its variables are in the window
    return {"t": t, "q": q, "r": r, "dim_window_0": len(S[2]), "REC_0_holds": holds(C, S, rec(t, 0))}


def u2(t):
    C = with_pi(t)
    for j in range(t):
        C.merge(C.key(A(0, t), A(1, t)), C.key(A(3, t), B(0, t)))
    before = C.classes()
    # three-point sets up to rotation: one point at position 0
    pts = range(2 * t)
    sets = [tuple(sorted({x, y, z})) for x in (A(0, t), B(0, t)) for y, z in itertools.combinations(pts, 2) if len({x, y, z}) == 3]
    C.two_term(sorted(set(sets)))
    return {"t": t, "classes_before": before, "classes_after_three_point_merges": C.classes()}


def main():
    out = {"U1": [], "U2": []}
    t0 = time.time()
    for q, r in [(5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (6, 0), (6, 1), (6, 2)]:
        for t in (31, 41):
            x = u1(t, q, r)
            out["U1"].append(x)
            print(x, f"({time.time() - t0:.0f} s)", flush=True)
    for t in (19, 21, 31):
        x = u2(t)
        out["U2"].append(x)
        print(x, f"({time.time() - t0:.0f} s)", flush=True)
    (ROOT / "results/phase9/linear_uniform.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
