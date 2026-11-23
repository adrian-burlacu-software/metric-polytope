import json, sys, itertools
from collections import Counter
import networkx as nx
UT = json.load(open('results/phase9/unreached_targets.json'))
def mat(n, nums):
    M = [[0]*n for _ in range(n)]; it = iter(nums)
    for i in range(n):
        for j in range(i+1, n): M[i][j] = M[j][i] = next(it)
    return M
n0, D0 = int(sys.argv[1]), int(sys.argv[2]); Wwant = tuple(int(a) for a in sys.argv[3].split(','))
for t in UT:
    if t['n'] != n0 or t['D'] != D0: continue
    n, D = n0, D0; M = mat(n, t['nums']); res = []
    for S in range(1 << (n-1)):
        Ss = {i+1 for i in range(n-1) if S >> i & 1}
        N = [[(D - M[a][b]) if ((a in Ss) != (b in Ss)) else M[a][b] for b in range(n)] for a in range(n)]
        E = [(i, j, N[i][j]) for i, j in itertools.combinations(range(n), 2)
             if not any(q not in (i, j) and N[i][q] + N[q][j] == N[i][j] for q in range(n))]
        W = tuple(sorted(set(w for _, _, w in E)))
        if W == Wwant: res.append(E)
    for E in res[:1]:
        G = nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from((i, j) for i, j, _ in E)
        by = {w: [(i, j) for i, j, ww in E if ww == w] for w in Wwant}
        sub = {w: (nx.Graph(by[w]).number_of_nodes(), len(by[w]), sorted(d for _, d in nx.Graph(by[w]).degree())) for w in Wwant}
        print(t['id'], 'nsw', len(res), '#E', len(E), 'G6', nx.to_graph6_bytes(G, header=False).strip().decode(), 'deg', sorted(d for _, d in G.degree()), 'bip', nx.is_bipartite(G), 'sub', sub)
