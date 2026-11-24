# For each D=8 target and each switching with non-redundant weights in {2,3}: iso type of the weight-2 graph
# (components) and number of weight-3 edges. Print a compact summary per target.
import json, sys, itertools
from collections import Counter, defaultdict
import networkx as nx
UT = json.load(open('results/phase9/unreached_targets.json'))
def mat(n, nums):
    M = [[0]*n for _ in range(n)]; it = iter(nums)
    for i in range(n):
        for j in range(i+1, n): M[i][j] = M[j][i] = next(it)
    return M
def comps(G):
    out=[]
    for c in nx.connected_components(G):
        H=G.subgraph(c)
        out.append((len(c),H.number_of_edges()))
    return tuple(sorted(out,reverse=True))
types=defaultdict(set); none=[]
for t in UT:
    if t['n']!=8 or t['D']!=8: continue
    n,D=8,8; M=mat(n,t['nums']); seen=set()
    for S in range(1<<(n-1)):
        Ss={i+1 for i in range(n-1) if S>>i&1}
        N=[[(D-M[a][b]) if ((a in Ss)!=(b in Ss)) else M[a][b] for b in range(n)] for a in range(n)]
        E=[(i,j,N[i][j]) for i,j in itertools.combinations(range(n),2) if not any(q not in (i,j) and N[i][q]+N[q][j]==N[i][j] for q in range(n))]
        if set(w for _,_,w in E)<={2,3}:
            G=nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from((i,j) for i,j,w in E if w==2)
            ty=(comps(G), sum(1 for e in E if e[2]==3))
            seen.add(ty)
    if not seen: none.append(t['id'])
    for ty in seen: types[ty].add(t['id'])
print('no {2,3} frame:', none)
for ty,ids in sorted(types.items(), key=lambda kv:-len(kv[1]))[:25]: print(len(ids), ty)
