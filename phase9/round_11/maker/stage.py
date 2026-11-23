# For each target and one-node cover (A,B,v,S): which single nodes u can be dropped so that x|W (W = V-u) is a
# vertex of its own glue fiber (known = pairs inside A-u or inside B-u)? Then x = vertex of the 2nd-stage fiber.
import sys, itertools
from fractions import Fraction as F
from collections import Counter
sys.path.insert(0,'phase9/round_11/maker')
from cross import load, sw, piece
def rank(rows):
    M=[r[:] for r in rows]; r=0
    if not M: return 0
    m=len(M[0])
    for c in range(m):
        p=next((i for i in range(r,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        for i in range(len(M)):
            if i!=r and M[i][c]!=0:
                f=M[i][c]/M[r][c]; M[i]=[a-f*b for a,b in zip(M[i],M[r])]
        r+=1
    return r
def fiber_vertex(Y, W, known):
    holes=[(a,b) for a,b in itertools.combinations(W,2) if (a,b) not in known]
    hi={h:k for k,h in enumerate(holes)}
    rows=[]
    for i,j,k in itertools.combinations(W,3):
        e=[(i,j),(i,k),(j,k)]
        for t in range(3):
            co={e[t]:1}; 
            for s in range(3):
                if s!=t: co[e[s]]=-1
            if sum(c*Y[a][b] for (a,b),c in co.items())==0: rows.append(co)
        if Y[i][j]+Y[i][k]+Y[j][k]==2: rows.append({p:1 for p in e})
    R=[[r.get(h,0) for h in holes] for r in rows]
    return rank([[F(v) for v in r] for r in R])==len(holes), len(holes)
if __name__=='__main__':
    D=int(sys.argv[1]); la=F(int(sys.argv[2]),D); mu=F(int(sys.argv[3]),D)
    dA=eval(sys.argv[4]); dB=eval(sys.argv[5]); src=sys.argv[6]; nA=len(dA); nB=len(dB)
    tot=Counter()
    for tid,X in load(8,D,src):
        n=len(X); res=Counter(); ncov=0
        for v in range(n):
            rest=[i for i in range(n) if i!=v]
            for Ar in itertools.combinations(rest,nA-1):
                Br=[i for i in rest if i not in Ar]
                if len(Br)!=nB-1: continue
                A=list(Ar)+[v]; B=[v]+Br
                for m in range(1<<(n-1)):
                    S={rest[i] for i in range(n-1) if m>>i&1}
                    Y=sw(X,S); gA=piece(Y,A,la,dA)
                    if not gA: continue
                    gB=piece(Y,B,mu,dB)
                    if not gB: continue
                    ncov+=1
                    cv=('vA',sum(1 for a in Ar if gA[(a,v)]==1))
                    for u in rest:
                        W=[i for i in range(n) if i!=u]
                        known={(a,b) for a,b in itertools.combinations(W,2) if (a in A and b in A) or (a in B and b in B)}
                        ok,nh=fiber_vertex(Y,W,known)
                        role=('A',gA[(u,v)]) if u in A else ('B',gB[(v,u)])
                        if ok: res[(cv,role)]+=1
        print(tid,'covers',ncov,dict(res),flush=True)
        for k in res: tot[k]+=1
    print('TOTAL #targets with drop type:',dict(tot))
