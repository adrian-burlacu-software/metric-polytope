"""For unreached targets: weights (in units 1/D) of the non-redundant edges (ij with no k: x_ik + x_kj = x_ij)."""
import json, collections, itertools
UT = json.load(open('results/phase9/unreached_targets.json'))
def mat(n, nums):
    M = [[0] * n for _ in range(n)]; it = iter(nums)
    for i in range(n):
        for j in range(i + 1, n): M[i][j] = M[j][i] = next(it)
    return M
out = collections.Counter(); ex = {}
for t in UT:
    n, D = t['n'], t['D']; M = mat(n, t['nums'])
    W = set(); nz0 = any(M[i][j] == 0 for i in range(n) for j in range(i+1, n))
    for i, j in itertools.combinations(range(n), 2):
        if not any(k not in (i, j) and M[i][k] + M[k][j] == M[i][j] for k in range(n)): W.add(M[i][j])
    key = (n, D, len(W)); out[key] += 1
    ex.setdefault((n, D), []).append(sorted(W))
for n in (8, 9):
    for D in sorted(set(k[1] for k in out if k[0] == n)):
        print(n, D, {k[2]: v for k, v in out.items() if k[:2] == (n, D)}, ex[(n, D)][:4])
