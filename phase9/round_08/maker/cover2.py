# list all covers V = A u B, |A n B| = ov, with x|A = lam d_G and x|B = mu d_H in some frame (per piece)
import json, sys, itertools
from fractions import Fraction as F
from collections import Counter
UT = json.load(open('results/phase9/unreached_targets.json'))
def sgm(X, T):
    k=len(T); out=[]
    for S in range(1 << (k-1)):
        Ss={T[i+1] for i in range(k-1) if S>>i&1}
        N={(a,b):(1-X[a][b]) if ((a in Ss)!=(b in Ss)) else X[a][b] for a,b in itertools.combinations(T,2)}
        m=min(N.values())
        if m==0: continue
        A={e:N[e]/m for e in N}
        if any(v.denominator!=1 for v in A.values()): continue
        INF=99; d={(a,b):(0 if a==b else INF) for a in T for b in T}
        for (a,b),v in A.items():
            if v==1: d[(a,b)]=d[(b,a)]=1
        for w in T:
            for a in T:
                for b in T:
                    if d[(a,w)]+d[(w,b)]<d[(a,b)]: d[(a,b)]=d[(a,w)]+d[(w,b)]
        if all(d[e]==A[e] for e in A):
            E=sorted(e for e in A if A[e]==1)
            degs=sorted(sum(1 for e in E if v in e) for v in T)
            out.append((m, len(E), tuple(degs), Ss))
    return out
n0=int(sys.argv[1]); Ds={int(a) for a in sys.argv[2].split(',')}; ov=int(sys.argv[3])
summ=Counter()
for t in UT:
    if t['n']!=n0 or t['D'] not in Ds: continue
    n,D=n0,t['D']; it=iter(t['nums']); X=[[F(0)]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n): X[i][j]=X[j][i]=F(next(it),D)
    good={}
    for k in range(3,n):
        for T in itertools.combinations(range(n),k):
            g=sgm(X,list(T))
            if g: good[frozenset(T)]=g
    covers=[]
    for A in good:
        for B in good:
            if len(A)>=len(B) and len(A|B)==n and len(A&B)==ov and (len(A)>len(B) or sorted(A)<sorted(B)):
                for ga in good[A]:
                    for gb in good[B]:
                        covers.append((len(A),len(B),str(ga[0]),str(gb[0]),ga[1],ga[2],gb[1],gb[2]))
    cs=Counter((c[0],c[1],c[2],c[3]) for c in covers)
    print(t['id'],D,'covers',len(covers),dict(cs))
    for k in set((c[0],c[1],c[2],c[3],c[4],c[5],c[6],c[7]) for c in covers): summ[k]+=1
print('SUMMARY (#targets having cover type):')
for k,v in sorted(summ.items(),key=lambda kv:-kv[1]): print('  ',k,v)
