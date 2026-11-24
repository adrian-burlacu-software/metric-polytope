"""From prefilter14.json, compute for each kept row the max float rank of its 9 restrictions to m_8 and pick the
rows with the lowest max rank (furthest from a lift), spread over the D values. Usage: pick14b.py OUT N MAXRANK [D ...]"""
import json, sys
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent
ROOT = H.parents[2]
sys.path.insert(0, str(ROOT))
from metricpoly.core import ineq_matrix, pairs
A, b = ineq_matrix(8); A = np.asarray(A, float); b = np.asarray(b, float)
C = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
P = pairs(9); subs = [[i for i, (a, c) in enumerate(P) if k not in (a, c)] for k in range(9)]
pf = json.load(open(H / "prefilter14.json"))
out, N, MR = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ONLY = set(sys.argv[4:])  # optional D filter
excl = set()
for f in H.glob("rows14*.txt"):
    excl |= {int(x) for x in f.read_text().split()}
per = {}
for D, rows in pf.items():
    if ONLY and D not in ONLY: continue
    sc = []
    for r in rows:
        if r in excl: continue
        x = np.asarray(C[r], float); m = 0
        for s in subs:
            T = A[np.abs(b * int(D) - A @ x[s]) < 1e-9]
            m = max(m, int(np.linalg.matrix_rank(T)) if len(T) else 0)
        if m <= MR: sc.append((m, r))
    sc.sort(); per[D] = [r for _, r in sc]
    print(D, len(sc), sc[:5])
pick, i = [], 0
while len(pick) < N and any(i < len(v) for v in per.values()):
    for D in per:
        if i < len(per[D]) and len(pick) < N: pick.append(per[D][i])
    i += 1
open(H / out, "w").write(" ".join(map(str, pick)))
print(pick)
