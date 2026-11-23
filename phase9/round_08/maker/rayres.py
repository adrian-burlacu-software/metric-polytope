# for targets: which k-node restrictions (in some switching frame) lie on an extreme ray of MET_k (tight triangles rank C(k,2)-1)?
import json, sys, itertools
from fractions import Fraction as F
from collections import Counter
import sympy
UT = json.load(open('results/phase9/unreached_targets.json'))
def rank(rows):
    if not rows: return 0
    return sympy.Matrix(rows).rank()
def tri_rank(X, T):
    k=len(T); P=[(a,b) for a in range(k) for b in range(a+1,k)]; idx={p:i for i,p in enumerate(P)}
    rows=[]
    for a,b,c in itertools.combinations(range(k),3):
        for (i,j),o in (((a,b),c),((a,c),b),((b,c),a)):
            # x_ij <= x_io + x_jo tight
            if X[T[i]][T[j]] == X[T[i]][T[o]] + X[T[j]][T[o]]:
                r=[0]*len(P); r[idx[(i,j)]]=1; r[idx[tuple(sorted((i,o)))]]=-1; r[idx[tuple(sorted((j,o)))]]=-1; rows.append(r)
    return rank(rows), len(P)
n0=int(sys.argv[1]); Ds={int(a) for a in sys.argv[2].split(',')}; k=int(sys.argv[3])
tot=Counter()
for t in UT:
    if t['n']!=n0 or t['D'] not in Ds: continue
    n,D=n0,t['D']; it=iter(t['nums']); X0=[[F(0)]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n): X0[i][j]=X0[j][i]=F(next(it),D)
    hits=[]
    for T in itertools.combinations(range(n),k):
        for S in range(1<<(k-1)):
            Ss={T[i+1] for i in range(k-1) if S>>i&1}
            X=[[ (1-X0[a][b]) if ((a in Ss)!=(b in Ss)) else X0[a][b] for b in range(n)] for a in range(n)]
            r,m=tri_rank(X,T)
            if r==m-1: hits.append((T,S))
    print(t['id'],D,'rays among',k,'-restrictions:',len(hits), hits[:3], flush=True)
