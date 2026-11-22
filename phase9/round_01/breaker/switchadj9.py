"""switch-class-nonadjacent at n = 9, filter: for every Deza representative x and every switching S (x_S != x), count
inequalities tight at both x and r_S(x); adjacency needs >= C(n,2) - 1 = 35 common tight ones. Usage: scan LO HI."""
import itertools, json, sys
import numpy as np
n = 9
lo, hi = int(sys.argv[1]), int(sys.argv[2])
P = list(itertools.combinations(range(n), 2)); pid = {p: k for k, p in enumerate(P)}
T = list(itertools.combinations(range(n), 3))
ij = np.array([pid[(a, b)] for a, b, c in T]); ik = np.array([pid[(a, c)] for a, b, c in T]); jk = np.array([pid[(b, c)] for a, b, c in T])
X = np.load("data/deza/orbits9/coords.npy", mmap_mode="r")[lo:hi].astype(np.int64)
D = np.load("data/deza/orbits9/den.npy", mmap_mode="r")[lo:hi].astype(np.int64)[:, None]
keep = D[:, 0] > 1
X, D = X[keep], D[keep]; rows = np.arange(lo, hi)[keep]
a, b, c = X[:, ij], X[:, ik], X[:, jk]      # x_ab, x_ac, x_bc for triple (a,b,c)
# bits: 1 = t_c (x_ab <= x_ac + x_bc), 2 = t_b (x_ac <= ...), 4 = t_a (x_bc <= ...), 8 = perimeter
M = ((a == b + c) * 1 + (b == a + c) * 2 + (c == a + b) * 4 + (a + b + c == 2 * D) * 8).astype(np.uint8)
def perm(m, case):  # tight mask of r_S(x) at a triple, in x's labels; case: which node is cut off (0=a,1=b,2=c) or -1
    bit = lambda k: (m >> k) & 1
    tc, tb, ta, p = bit(0), bit(1), bit(2), bit(3)
    if case == -1: return m
    if case == 0: ta, p, tb, tc = p, ta, tc, tb
    if case == 1: tb, p, ta, tc = p, tb, tc, ta
    if case == 2: tc, p, ta, tb = p, tc, tb, ta
    return tc | tb << 1 | ta << 2 | p << 3
LUT = np.array([[perm(m, cs) for m in range(16)] for cs in (-1, 0, 1, 2)], dtype=np.uint8)
POP = np.array([bin(m).count("1") for m in range(16)], dtype=np.uint8)
hits = []
FF = ~((X == 0) | (X == D)).any(1)
VEC = []
for (u, v, w) in T:
    e = np.zeros((4, 36), int)
    pab, pac, pbc = pid[(u, v)], pid[(u, w)], pid[(v, w)]
    e[0, [pab, pac, pbc]] = [1, -1, -1]; e[1, [pab, pac, pbc]] = [-1, 1, -1]; e[2, [pab, pac, pbc]] = [-1, -1, 1]
    e[3, [pab, pac, pbc]] = [1, 1, 1]
    VEC.append(e)
for s in range(1, 2 ** (n - 1)):
    S = [(s >> k) & 1 for k in range(n - 1)] + [0]
    cases = []
    for (u, v, w) in T:
        su, sv, sw = S[u], S[v], S[w]
        cases.append(-1 if su == sv == sw else (0 if sv == sw else (1 if su == sw else 2)))
    cases = np.array(cases) + 1
    Y = LUT[cases[None, :], M]
    common = POP[M & Y].sum(1, dtype=np.int32)
    h = np.where(common >= 35)[0]
    for r in h:
        if FF[r]:
            Z = (M[r] & Y[r])
            G = np.concatenate([VEC[k][[b for b in range(4) if (Z[k] >> b) & 1]] for k in range(len(T))])
            rk = np.linalg.matrix_rank(G.astype(float))
            if rk >= 35:
                hits.append((int(rows[r]), s, int(common[r]), int(rk)))
json.dump(hits, open(f"phase9/round_01/breaker/switchadj9_{lo}.json", "w"))
print(lo, hi, len(hits), hits[:10])
