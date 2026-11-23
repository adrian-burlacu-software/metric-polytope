import json, sys, itertools
from collections import Counter
n=int(sys.argv[1]); D=int(sys.argv[2])
L=[r for r in json.load(open(f'phase9/round_08/maker/dmet_n{n}.json')) if r['D']==D]
def apsp(n,E,w=None):
    INF=99; g=[[0 if i==j else INF for j in range(n)] for i in range(n)]
    for (i,j) in E: g[i][j]=g[j][i]=1
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if g[i][k]+g[k][j]<g[i][j]: g[i][j]=g[i][k]+g[k][j]
    return g
for r in L[:int(sys.argv[3])]:
    d=r['d']; m=min(d[i][j] for i in range(n) for j in range(i+1,n))
    E=[(i,j) for i in range(n) for j in range(i+1,n) if d[i][j]==m]
    g=apsp(n,E)
    print('id',r['id'],'min',m,'E',E)
    C=Counter((g[i][j],d[i][j]) for i in range(n) for j in range(i+1,n))
    print('  (d_Gmin, d) pairs:',dict(sorted(C.items())))
    for row in d: print('   ',row)
