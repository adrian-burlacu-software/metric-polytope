import json, sys, itertools
UT = json.load(open('results/phase9/unreached_targets.json'))
def mat(n, nums):
    M = [[0]*n for _ in range(n)]; it = iter(nums)
    for i in range(n):
        for j in range(i+1, n): M[i][j] = M[j][i] = next(it)
    return M
n0, D0, cnt = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
k = 0
for t in UT:
    if t['n'] != n0 or t['D'] != D0: continue
    n, D = t['n'], t['D']; M = mat(n, t['nums'])
    # switch to minimize sum: try all S containing node 0? n small
    best = None
    for S in range(1 << (n-1)):
        Sset = {i+1 for i in range(n-1) if S >> i & 1}
        N = [[ (D - M[i][j]) if ((i in Sset) != (j in Sset)) else M[i][j] for j in range(n)] for i in range(n)]
        s = sorted((N[i][j] for i in range(n) for j in range(i+1,n)))
        key = (sum(s), s)
        if best is None or key < best[0]: best = (key, N)
    N = best[1]
    print('id', t['id'], 'D', D, 'values', sorted(set(N[i][j] for i in range(n) for j in range(i+1,n))))
    for r in N: print('  ', ' '.join('%2d' % v for v in r))
    k += 1
    if k >= cnt: break
