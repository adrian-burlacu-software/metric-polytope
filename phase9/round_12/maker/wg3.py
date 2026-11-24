# For each D=8 target: all switchings in which x = (1/8) shortest-path metric of a weighted graph with weights {2,3};
# print the weighted graph with fewest edges, and the matrix.
import json, sys, itertools
import networkx as nx
UT = json.load(open('results/phase9/unreached_targets.json'))
def mat(n, nums):
    M = [[0]*n for _ in range(n)]; it = iter(nums)
    for i in range(n):
        for j in range(i+1, n): M[i][j] = M[j][i] = next(it)
    return M
ids = [int(a) for a in sys.argv[1:]]
for t in UT:
    if t['n']!=8 or t['D']!=8: continue
    if ids and t['id'] not in ids: continue
    n,D=8,8; M=mat(n,t['nums']); best=None
    nsw=0
    for S in range(1<<(n-1)):
        Ss={i+1 for i in range(n-1) if S>>i&1}
        N=[[(D-M[a][b]) if ((a in Ss)!=(b in Ss)) else M[a][b] for b in range(n)] for a in range(n)]
        E=[(i,j,N[i][j]) for i,j in itertools.combinations(range(n),2) if not any(q not in (i,j) and N[i][q]+N[q][j]==N[i][j] for q in range(n))]
        W=set(w for _,_,w in E)
        if W<= {2,3}:
            nsw+=1
            if best is None or len(E)<len(best[0]): best=(E,N,Ss)
    if best is None: print(t['id'],'none'); continue
    E,N,Ss=best
    print(t['id'], 'nsw',nsw,'S',sorted(Ss),'w2',[(i,j) for i,j,w in E if w==2],'w3',[(i,j) for i,j,w in E if w==3])
