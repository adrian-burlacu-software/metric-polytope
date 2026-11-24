# Recompute round 12's D = 8 tower in Python: level 7 over w1, w2; stats of the level-7 points (incidence, tight rank,
# vertex?) and which ones have m_8-vertex children (the 53 / 31 outputs). Saves phase9/round_13/maker/tower.json.
import json, sys, time, pickle
sys.path.insert(0,'.')
from metricpoly.core import Point, pidx, ineq_matrix, slacks, exact_rank, is_vertex, pairs
from metricpoly import group
from metricpoly.dsl.prims import _fiber_vertices
from metricpoly.dsl.values import Partial
import numpy as np
W={'w1':'6|8|2,2,3,3,3,2,3,3,5,5,5,3,6,2,4','w2':'6|8|2,2,2,3,3,2,4,3,3,4,5,5,5,5,6'}
def P(k):
    n,D,r=k.split('|'); return Point.make(int(n),int(D),[int(a) for a in r.split(',')])
def lift(y):
    return _fiber_vertices(Partial.make(y.n+1,{(i,j):f for (i,j),f in zip(pairs(y.n),y.fractions())}))
def up(L, D=8):
    out={}
    for y in L:
        for z in lift(y):
            if z.D==D:
                c=group.canonical(z); out.setdefault(c.key(),c)
    return list(out.values())
_A={}
def stats(p):
    if p.n not in _A: _A[p.n]=ineq_matrix(p.n)[0]
    s=slacks(p); T=np.flatnonzero(s==0)
    return len(T), exact_rank(_A[p.n][T].tolist())
if __name__=='__main__':
    res={}
    for name,k in W.items():
        t=time.time(); w=P(k)
        L7=up([w]); t7=time.time()-t
        rows=[]
        for y in L7:
            ch=[z for z in lift(y) if z.D==8]
            outs=set(group.canonical(z).key() for z in ch if is_vertex(z)[0])
            inc,rk=stats(y)
            rows.append(dict(key=y.key(),inc=inc,rank=rk,vertex=rk==21,nchild8=len(ch),outs=sorted(outs)))
        allout=set(o for r in rows for o in r['outs'])
        print(name,'L7',len(L7),'t7 %.1f'%t7,'total %.1f'%(time.time()-t),'outputs',len(allout))
        res[name]=rows
    json.dump(res,open('phase9/round_13/maker/tower.json','w'))
