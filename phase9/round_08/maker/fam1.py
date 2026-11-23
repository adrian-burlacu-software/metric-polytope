# test: d = a*d_G + b*delta_S + c*(J-I)  (a>=1, b>=0 or negative, c in -2..3), any S, G any connected graph
import json, sys, itertools
from fractions import Fraction as F
def is_graph_metric(g):
    n=len(g); INF=99
    for i in range(n):
        for j in range(i+1,n):
            if g[i][j].denominator!=1 or g[i][j]<1: return False
    h=[[0 if i==j else (1 if g[i][j]==1 else INF) for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if h[i][k]+h[k][j]<h[i][j]: h[i][j]=h[i][k]+h[k][j]
    return all(h[i][j]==g[i][j] for i in range(n) for j in range(n))
res={}
if __name__=='__main__':
 for fn in sys.argv[1:]:
  for r in json.load(open(fn)):
    d=r['d']; n=len(d); hits=[]
    for S in range(1<<(n-1)):
        s=S<<1
        cut=[[1 if ((s>>i&1)!=(s>>j&1)) else 0 for j in range(n)] for i in range(n)]
        for b in range(-3,4):
            if S==0 and b!=0: continue
            for c in range(-3,4):
                for a in (1,2,3):
                    g=[[F(d[i][j]-b*cut[i][j]-(c if i!=j else 0),a) for j in range(n)] for i in range(n)]
                    if is_graph_metric(g): hits.append((a,b,c,S))
    print(r['id'],r['D'],len(hits),hits[:4])
