#!/usr/bin/env python3
"""Upper bounds for the linear locality of C_t from chosen families of sets (exact rational arithmetic).

The level-s linear closure (linear_locality.py) uses all sets of at most s points. Any subfamily of sets, and any
subset of the exchanges between them, gives a sound derivation, hence an upper bound: if a single class remains,
L_lin(C_t) <= s. C_t is invariant under the rotation i -> i + 1, and so is the closure; a merge found for two pairs
is therefore applied to all their rotations.

Stage 1 (two-term merges, cheap): four-point sets {A_i, A_i+1, A_k, A_k+1}, {A_i, A_i', A_j, B_j} and their
three-point subsets, which merge the A-pairs at distance 1 or >= 3 into one class and the pairs A_i B_j (i far
from j) into one class per j, as in the proof of Theorem 4.
Stage 2 (exchange): sets given by --scheme:
  windows w      : W_j = all points at positions [0, w) or [j, j + w)                       (4w points)
  bstate m       : W_j = {B_0..B_3} + {B_j..B_j+m-1} + one far A,  plus local sets           (5 + m points)
  bblocks m      : W_j = {B_0..B_m-1} + {B_j..B_j+m-1}                                       (2m points)
plus, with --local q, all sets of the points at q consecutive positions (2q points).

  python scripts/phase9/linear_family.py --t 13 15 --scheme windows --w 2 3 4
Output results/phase9/linear_family.json (appended)
"""
import argparse
import itertools
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
from linear_locality import nullspace, restrict  # noqa: E402
from family_C import metric  # noqa: E402


class Closure:
    def __init__(self, t):
        self.t = t
        self.n = 2 * t
        self.d = metric(t).tolist()
        self.pairs = list(itertools.combinations(range(self.n), 2))
        self.pid = {p: i for i, p in enumerate(self.pairs)}
        self.parent = list(range(len(self.pairs)))
        rot = lambda x, k: (x + k) % t if x < t else t + (x - t + k) % t
        self.rot = [[self.key(rot(a, k), rot(b, k)) for a, b in self.pairs] for k in range(t)]

    def key(self, a, b):
        return self.pid[(a, b) if a < b else (b, a)]

    def find(self, x):
        p = self.parent
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x

    def merge(self, x, y):
        """Merge the classes of pairs x, y and of all their rotations. Returns True if something changed."""
        ch = False
        for k in range(self.t):
            a, b = self.find(self.rot[k][x]), self.find(self.rot[k][y])
            if a != b:
                self.parent[b] = a
                ch = True
        return ch

    def classes(self):
        return len({self.find(i) for i in range(len(self.pairs))})

    def space(self, W):
        d, key, find = self.d, self.key, self.find
        vs = sorted({find(key(a, b)) for a, b in itertools.combinations(W, 2)})
        ix = {v: i for i, v in enumerate(vs)}
        rows = []
        for a, b in itertools.combinations(W, 2):
            for m in W:
                if m != a and m != b and d[a][b] == d[a][m] + d[m][b]:
                    r = [Fraction(0)] * len(vs)
                    r[ix[find(key(a, b))]] += d[a][b]
                    r[ix[find(key(a, m))]] -= d[a][m]
                    r[ix[find(key(m, b))]] -= d[m][b]
                    rows.append(r)
        return [vs, ix, nullspace(rows, len(vs))]

    def merges(self, fam):
        done = False
        for vs, ix, B in fam:
            if not B:
                continue
            cols = {}
            for j, v in enumerate(vs):
                cols.setdefault(tuple(row[j] for row in B), []).append(v)
            for grp in cols.values():
                for v in grp[1:]:
                    done |= self.merge(grp[0], v)
        return done

    def two_term(self, sets):
        while self.merges([self.space(W) for W in sets]):
            pass

    def exchange(self, sets, max_rounds=50):
        """Linear closure on the given sets (all pairs of sets sharing >= 2 variables exchange)."""
        rounds = 0
        while True:
            rounds += 1
            fam = [self.space(W) for W in sets]
            if self.merges(fam):
                continue
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
            if not self.merges(fam) or rounds >= max_rounds:
                return rounds, [len(f[2]) for f in fam]


def A(i, t): return i % t
def B(i, t): return t + i % t


def stage1_sets(t):
    s = set()
    for i in range(1):                                  # rotations are applied by merge()
        for k in range(t):
            W = {A(i, t), A(i + 1, t), A(k, t), A(k + 1, t)}
            if len(W) >= 3:
                s.add(tuple(sorted(W)))
        for i2 in range(t):
            for j in range(t):
                W = {A(i, t), A(i2, t), A(j, t), B(j, t)}
                if len(W) >= 3:
                    s.add(tuple(sorted(W)))
    return sorted(s)


def local_sets(t, q):
    return [tuple(sorted([A(i, t) for i in range(a, a + q)] + [B(i, t) for i in range(a, a + q)])) for a in range(t)]


def scheme_sets(t, scheme, par):
    out = set()
    if scheme == "windows":
        for j in range(t):
            pos = set(range(par)) | {(j + k) % t for k in range(par)}
            out.add(tuple(sorted([A(i, t) for i in pos] + [B(i, t) for i in pos])))
    elif scheme == "bstate":
        for j in range(t):
            pos = [(j + k) % t for k in range(par)]
            far = [x for x in range(t) if all(min((x - p) % t, (p - x) % t) >= 3 for p in list(range(4)) + pos)]
            if not far:
                continue
            out.add(tuple(sorted({B(i, t) for i in range(4)} | {B(p, t) for p in pos} | {A(far[0], t)})))
    elif scheme == "bblocks":                           # B-points only: start block and moving block of par positions
        for j in range(t):
            out.add(tuple(sorted({B(i, t) for i in range(par)} | {B(j + k, t) for k in range(par)})))
    return sorted(out)


def run(t, scheme, par, local):
    t0 = time.time()
    C = Closure(t)
    C.two_term(stage1_sets(t))
    c1 = C.classes()
    sets = scheme_sets(t, scheme, par)
    if local:
        sets = sorted(set(sets) | set(local_sets(t, local)))
    size = max(len(W) for W in sets)
    rounds, dims = C.exchange(sets)
    # stage 3: two-term merges on small sets again (stage-1 sets, four-point subsets of one local window, and the
    # sets {A_0, B_0, A_j, B_j}), alternating with the exchange until nothing changes
    small = set(stage1_sets(t))
    if local:
        small |= {tuple(c) for c in itertools.combinations(local_sets(t, local)[0], 4)}
    small |= {tuple(sorted({A(0, t), B(0, t), A(j, t), B(j, t)})) for j in range(1, t)}
    small = sorted(small)
    for _ in range(6):
        before = C.classes()
        C.two_term(small)
        if C.classes() == 1 or C.classes() == before:
            break
        r2, dims = C.exchange(sets)
        rounds += r2
    return {"t": t, "scheme": scheme, "par": par, "local": local, "sets": len(sets), "max_points": size,
            "classes_after_stage1": c1, "classes_final": C.classes(), "proved": C.classes() == 1,
            "final_dims": [min(dims), max(dims)], "rounds": rounds, "seconds": round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t", type=int, nargs="+", default=[13])
    ap.add_argument("--scheme", default="windows")
    ap.add_argument("--par", type=int, nargs="+", default=[2, 3, 4])
    ap.add_argument("--local", type=int, default=0)
    a = ap.parse_args()
    path = ROOT / "results/phase9/linear_family.json"
    out = json.loads(path.read_text()) if path.exists() else []
    for par in a.par:
        for t in a.t:
            r = run(t, a.scheme, par, a.local)
            out.append(r)
            print(r, flush=True)
            path.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
