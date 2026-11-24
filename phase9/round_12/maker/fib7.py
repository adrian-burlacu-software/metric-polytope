# For each 7-node restriction orbit y of the 49 D=8 targets: m_8 vertices of the fiber over y, which targets they hit.
import json, sys, time
from collections import Counter, defaultdict
sys.path.insert(0,'.')
from metricpoly.core import Point
from metricpoly import group
from metricpoly.dsl.prims import p_fiber_vertices, p_lift_partial, p_vertex
UT = json.load(open('results/phase9/unreached_targets.json'))
T = [t for t in UT if t['n']==8 and t['D']==8]
tk = {t['key']:t['id'] for t in UT}
def restrict(p, keep):
    from metricpoly.core import pidx
    nums=[p.nums[pidx(p.n,keep[a],keep[b])] for a in range(len(keep)) for b in range(a+1,len(keep))]
    return Point.make(len(keep), p.D, nums)
ys={}
for t in T:
    p=Point.make(8,8,t['nums'])
    for v in range(8):
        r=group.canonical(restrict(p,[i for i in range(8) if i!=v])); ys[r.key()]=r
t0=time.time(); res={}
for k,y in ys.items():
    hits=set(); nv=0; nf=0
    for z in p_fiber_vertices(p_lift_partial(y)):
        nf+=1
        if p_vertex(z):
            nv+=1; c=group.canonical(z).key()
            if c in tk: hits.add(tk[c])
    res[k]=dict(nf=nf,nv=nv,hits=sorted(hits))
print('time',time.time()-t0)
json.dump(res,open('phase9/round_12/maker/fib7.json','w'))
# greedy cover
left=set(t['id'] for t in T); chosen=[]
while left:
    k=max(res,key=lambda k:len(left&set(res[k]['hits'])))
    g=left&set(res[k]['hits'])
    if not g: break
    chosen.append((k,sorted(g),res[k]['nf'],res[k]['nv'])); left-=g
for c in chosen: print(c)
print('uncovered',left)
