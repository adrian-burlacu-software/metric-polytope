# glue lam*d(K_{p,q}) and mu*d(K_{r,s}) at one node; fiber vertices; which hit unreached targets/nodes?
import sys, json, itertools, time
from fractions import Fraction as F
sys.path.insert(0,'scripts/phase9')
from common import ROOT, load_json, verify_vertex
from metricpoly import group
from metricpoly.core import Point
from metricpoly.dsl.prims import _fiber_vertices, p_glue
U=load_json(ROOT/'results/phase9/unreached_nodes.json'); UN=set(U['keys']); UT=set(U['target_keys'])
def kpq_metric(parts, lam):
    lab=[t for t,p in enumerate(parts) for _ in range(p)]; n=len(lab)
    return [[F(0) if i==j else (lam if lab[i]!=lab[j] else 2*lam) for j in range(n)] for i in range(n)], lab
def pt(M):
    n=len(M); return Point.from_fractions(n,[M[i][j] for i in range(n) for j in range(i+1,n)])
def perm_last(M,v):
    o=[i for i in range(len(M)) if i!=v]+[v]; return [[M[a][b] for b in o] for a in o]
def perm_first(M,v):
    o=[v]+[i for i in range(len(M)) if i!=v]; return [[M[a][b] for b in o] for a in o]
def run(P1, P2, lams, mus, verbose=False):
    hitsT=set(); hitsN=set(); allv=set(); nf=0
    for lam in lams:
        for mu in mus:
            M1,l1=kpq_metric(P1,lam); M2,l2=kpq_metric(P2,mu)
            for v1 in sorted(set(l1)):      # overlap node: one per part (symmetry)
                for v2 in sorted(set(l2)):
                    a=pt(perm_last(M1,l1.index(v1))); b=pt(perm_first(M2,l2.index(v2)))
                    Pp=p_glue(a,b,1); nf+=1
                    for x in _fiber_vertices(Pp):
                        if not verify_vertex(x)['vertex']: continue
                        k=group.canonical(x).key(); allv.add(k)
                        if k in UN: hitsN.add(k)
                        if k in UT:
                            hitsT.add(k)
                            if verbose: print('  HIT', P1,P2,lam,mu,v1,v2,x.D)
    return hitsT,hitsN,allv,nf
if __name__=='__main__':
    P1=tuple(int(a) for a in sys.argv[1].split(',')); P2=tuple(int(a) for a in sys.argv[2].split(','))
    taus=[int(a) for a in sys.argv[3].split(',')]
    t=time.time()
    for tau in taus:
        lams=[F(a,tau) for a in range(1,tau) if F(a,tau)*2<=1]
        T,N,A,nf=run(P1,P2,lams,lams,verbose=True)
        print('tau',tau,'fibers',nf,'vertex orbits',len(A),'unreached nodes',len(N),'targets',len(T),'sec',round(time.time()-t,1),flush=True)
