"""Breaker round 01: vectorized scans of Deza's n = 9 representatives for structural-rule violations (filters only;
every hit is re-checked exactly with scripts/phase9/check_point.py)."""
import itertools, json, sys
import numpy as np
from math import comb
n = 9
P = list(itertools.combinations(range(n), 2)); pid = {p: k for k, p in enumerate(P)}
C = np.load("data/deza/orbits9/coords.npy", mmap_mode="r"); Dn = np.load("data/deza/orbits9/den.npy", mmap_mode="r")
T = list(itertools.combinations(range(n), 3))
ij = np.array([pid[(a, b)] for a, b, c in T]); ik = np.array([pid[(a, c)] for a, b, c in T]); jk = np.array([pid[(b, c)] for a, b, c in T])
out = {"den2": [], "lift_fail": [], "ext_den_cand": [], "inc_fail": [], "third_ff": [], "nonff_noncut": 0, "int_noncut": []}
N = C.shape[0]; CH = 100000
for s in range(0, N, CH):
    X = np.asarray(C[s:s + CH], dtype=np.int64); D = np.asarray(Dn[s:s + CH], dtype=np.int64)[:, None]
    rows = np.arange(s, s + len(X))
    out["den2"] += rows[D[:, 0] == 2].tolist()
    integral = D[:, 0] == 1
    has01 = ((X == 0) | (X == D)).any(1)
    ff = ~has01
    out["nonff_noncut"] += int((has01 & ~integral).sum())
    # tight counts
    a, b, c = X[:, ij], X[:, ik], X[:, jk]
    tight = ((a == b + c).sum(1) + (b == a + c).sum(1) + (c == a + b).sum(1) + (a + b + c == 2 * D).sum(1))
    nt = comb(n, 3)
    bad = (tight > 3 * nt) | ((tight == 3 * nt) & ~integral) | ((~integral) & has01 & (tight > 2 * nt)) | (ff & (tight > nt))
    out["inc_fail"] += rows[bad].tolist()
    out["third_ff"] += rows[(D[:, 0] == 3) & ff].tolist()
    # restriction denominators
    for i in range(n):
        keep = [k for k, p in enumerate(P) if i not in p]
        g = np.gcd.reduce(np.concatenate([X[:, keep], D], 1), axis=1)
        d = D[:, 0] // g
        lf = (2 * d) % D[:, 0] != 0
        out["lift_fail"] += [(int(r), i) for r in rows[lf]]
        ec = (D[:, 0] != d) & (D[:, 0] != 2 * d) & (d != 1)
        out["ext_den_cand"] += [(int(r), i) for r in rows[ec]]
    print(s, {k: (len(v) if isinstance(v, list) else v) for k, v in out.items()}, file=sys.stderr, flush=True)
out["third_ff_count"] = len(out["third_ff"])
json.dump(out, open("phase9/round_01/breaker/scan9_out.json", "w"))
print({k: (len(v) if isinstance(v, list) else v) for k, v in out.items()})
