# For targets of given D at n=8: find one-node covers x^S|A = (a/D) d_G, x^S|B = (b/D) d_H (|A|=5 K23-type, |B|=4)
# and print the cross entries (numerators) by (d_G(a,v), d_H(v,b)).
import json, sys, itertools
from fractions import Fraction as F
from collections import Counter, defaultdict
def apsp(T, A):
    INF=99; d={(a,b):(0 if a==b else INF) for a in T for b in T}
    for (a,b),v in A.items():
        if v==1: d[(a,b)]=d[(b,a)]=1
    for w in T:
        for a in T:
            for b in T:
                if d[(a,w)]+d[(w,b)]<d[(a,b)]: d[(a,b)]=d[(a,w)]+d[(w,b)]
    return d
def piece(X, T, lam, degs):
    A={(a,b):X[a][b]/lam for a,b in itertools.combinations(T,2)}
    if any(v.denominator!=1 for v in A.values()): return None
    d=apsp(T,A)
    if any(d[e]!=A[e] for e in A): return None
    E=[e for e in A if A[e]==1]
    if sorted(sum(1 for e in E if v in e) for v in T)!=degs: return None
    return d
def load(n, D, src):
    out=[]
    if src=='dmet':
        for t in json.load(open('phase9/round_08/maker/dmet_n8.json')):
            if t['D']==D: out.append((t['id'], [[F(2*v,D) for v in r] for r in t['d']]))
    else:
        for t in json.load(open('results/phase9/unreached_targets.json')):
            if t['n']==n and t['D']==D:
                it=iter(t['nums']); X=[[F(0)]*n for _ in range(n)]
                for i in range(n):
                    for j in range(i+1,n): X[i][j]=X[j][i]=F(next(it),D)
                out.append((t['id'],X))
    return out
def sw(X, S):
    n=len(X); return [[X[i][j] if ((i in S)==(j in S)) or i==j else 1-X[i][j] for j in range(n)] for i in range(n)]
if __name__=='__main__':
    D=int(sys.argv[1]); la=F(int(sys.argv[2]),D); mu=F(int(sys.argv[3]),D)
    dA=eval(sys.argv[4]); dB=eval(sys.argv[5]); src=sys.argv[6]; nA=len(dA); nB=len(dB)
    for tid,X in load(8,D,src):
        n=len(X); found=Counter(); pat=defaultdict(Counter)
        for v in range(n):
            rest=[i for i in range(n) if i!=v]
            for Ar in itertools.combinations(rest,nA-1):
                Br=[i for i in rest if i not in Ar]
                if len(Br)!=nB-1: continue
                A=list(Ar)+[v]; B=[v]+Br
                for m in range(1<<(n-1)):
                    S={rest[i] for i in range(n-1) if m>>i&1}
                    Y=sw(X,S)
                    gA=piece(Y,A,la,dA)
                    if not gA: continue
                    gB=piece(Y,B,mu,dB)
                    if not gB: continue
                    degv=sum(1 for a in Ar if gA[(a,v)]==1)
                    key=('degvA',degv,'degvB',sum(1 for b in Br if gB[(v,b)]==1))
                    found[key]+=1
                    for a in Ar:
                        for b in Br:
                            pat[(key,gA[(a,v)],gB[(v,b)])][Y[a][b]*D]+=1
        print(tid, dict(found))
        for k in sorted(pat): print('   ',k,dict(pat[k]))
