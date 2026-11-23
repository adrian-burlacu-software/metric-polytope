# print targets in the global frame where x|A = lam d_G, x|B = mu d_H (1-node overlap); order A-K, K, B-K
import json, sys, itertools
from fractions import Fraction as F
sys.path.insert(0,'phase9/round_08/maker')
from cover2 import sgm, UT
n0=int(sys.argv[1]); D0=int(sys.argv[2]); want=(int(sys.argv[3]),int(sys.argv[4])); lim=int(sys.argv[5])
c=0
for t in UT:
    if t['n']!=n0 or t['D']!=D0: continue
    n,D=n0,D0; it=iter(t['nums']); X=[[F(0)]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n): X[i][j]=X[j][i]=F(next(it),D)
    done=False
    for A in itertools.combinations(range(n),want[0]):
        if done: break
        ga=sgm(X,list(A))
        if not ga: continue
        for k in A:
            B=[v for v in range(n) if v not in A]+[k]
            if len(B)!=want[1]: continue
            gb=sgm(X,sorted(B))
            if not gb: continue
            for a in ga:
                for b in gb:
                    S=set(a[3])|set(b[3]) if True else None
                    # combine: frame on A from a, on B from b; normalise so overlap node k not switched
                    SA=set(a[3]); SB=set(b[3])
                    if k in SA: SA=set(A)-SA
                    if k in SB: SB=set(B)-SB
                    S=SA|SB
                    Y=[[(1-X[i][j]) if ((i in S)!=(j in S)) else X[i][j] for j in range(n)] for i in range(n)]
                    order=[v for v in A if v!=k]+[k]+[v for v in B if v!=k]
                    print(t['id'],'lam',a[0],'mu',b[0],'A',A,'k',k)
                    for i in order: print('   ',[int(Y[i][j]*D) for j in order])
                    done=True; break
                if done: break
            if done: break
    c+=1
    if c>=lim: break
