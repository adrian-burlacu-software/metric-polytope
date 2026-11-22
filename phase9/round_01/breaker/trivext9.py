"""non-fully-fractional-is-trivial-ext at n = 9 (filter): every non-cut Deza rep with a 0/1 coordinate x_ij must have
x restricted to [9] minus j (or minus i) a vertex of m_8 (and j a twin/antitwin of i)."""
import itertools
import numpy as np
n = 9
P = list(itertools.combinations(range(n), 2))
C = np.load("data/deza/orbits9/coords.npy"); Dn = np.load("data/deza/orbits9/den.npy")
def is_vertex(m, nodes, x, D):
    pid = {p: k for k, p in enumerate(itertools.combinations(range(m), 2))}
    val = {}
    for a, b in itertools.combinations(range(m), 2):
        u, v = nodes[a], nodes[b]
        val[(a, b)] = x[P.index((min(u, v), max(u, v)))]
    rowsA = []
    for a, b, c in itertools.combinations(range(m), 3):
        p, q, r = pid[(a, b)], pid[(a, c)], pid[(b, c)]
        xa, xb, xc = val[(a, b)], val[(a, c)], val[(b, c)]
        for coef, lhs in (([1, -1, -1], xa - xb - xc), ([-1, 1, -1], xb - xa - xc), ([-1, -1, 1], xc - xa - xb), ([1, 1, 1], xa + xb + xc - 2 * D)):
            if lhs == 0:
                e = np.zeros(len(pid)); e[[p, q, r]] = coef; rowsA.append(e)
    return np.linalg.matrix_rank(np.array(rowsA)) == len(pid)
bad = 0; tot = 0
for r in range(len(C)):
    x, D = C[r].astype(int), int(Dn[r])
    if D == 1: continue
    z = [k for k, v in enumerate(x) if v == 0 or v == D]
    if not z: continue
    tot += 1
    i, j = P[z[0]]
    ok = all(x[P.index(tuple(sorted((i, k))))] in (x[P.index(tuple(sorted((j, k))))], D - x[P.index(tuple(sorted((j, k))))]) for k in range(n) if k not in (i, j))
    ok = ok and is_vertex(8, [k for k in range(n) if k != j], x, D)
    if not ok:
        bad += 1; print("BAD", r)
print("checked", tot, "bad", bad)
