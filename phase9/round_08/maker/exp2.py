import sys, time
from fractions import Fraction as F
sys.path.insert(0,'phase9/round_08/maker'); sys.path.insert(0,'scripts/phase9')
from exp1 import *
from metricpoly.dsl.prims import _fiber_vertices, p_glue
P1=(2,3);P2=(2,2)
for lam,mu in [(F(4,13),F(5,13))]:
    M1,l1=kpq_metric(P1,lam); M2,l2=kpq_metric(P2,mu)
    for v1 in sorted(set(l1)):
        t=time.time()
        a=pt(perm_last(M1,l1.index(v1))); b=pt(perm_first(M2,l2.index(0)))
        vs=_fiber_vertices(p_glue(a,b,1)); t1=time.time()-t
        ks=set(); T=set(); N=set(); nv=0
        for x in vs:
            if not verify_vertex(x)['vertex']: continue
            nv+=1; k=group.canonical(x).key(); ks.add(k)
            if k in UN: N.add(k)
            if k in UT: T.add(k)
        print('overlap part',v1,'fiber verts',len(vs),'cdd s',round(t1,1),'m8 vertices',nv,'orbits',len(ks),'unr nodes',len(N),'targets',len(T),'total s',round(time.time()-t,1),flush=True)
