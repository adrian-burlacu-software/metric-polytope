"""third-valued-is-graphic at n = 9: test every Deza (1/3,2/3) fully fractional representative against all switchings
(filter; hits re-checked with check_point.py)."""
import itertools, json
import numpy as np
n = 9
P = list(itertools.combinations(range(n), 2))
C = np.load("data/deza/orbits9/coords.npy", mmap_mode="r")
rows = json.load(open("phase9/round_01/breaker/scan9_out.json"))["third_ff"]
bad = []
for r in rows:
    x = np.asarray(C[r], dtype=int)  # values 1 or 2 (D = 3)
    ok = False
    for m in range(2 ** (n - 1)):
        S = [(m >> k) & 1 for k in range(n - 1)] + [0]
        y = np.array([3 - v if S[a] != S[b] else v for v, (a, b) in zip(x, P)])
        A = np.zeros((n, n), bool)
        for v, (a, b) in zip(y, P):
            if v == 1: A[a, b] = A[b, a] = True
        A2 = (A.astype(int) @ A.astype(int)) > 0
        if not all(A[a, b] or A2[a, b] for a, b in P):  # diameter <= 2 (=> connected)
            continue
        if any(not (A[a, b] or A[a, c] or A[b, c]) for a, b, c in itertools.combinations(range(n), 3)):
            ok = True; break
    if not ok:
        bad.append(r)
print(len(rows), "bad:", len(bad), bad[:20])
json.dump(bad, open("phase9/round_01/breaker/third9_bad.json", "w"))
