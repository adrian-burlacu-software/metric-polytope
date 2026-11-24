# Lift closure from a 3-node dyadic seed, keeping only fiber vertices with denominator exactly 8 (canonical dedup).
# Reports orbits per level, how many level-k orbits are restrictions of D=8 targets, time.
import json, sys, time, itertools
sys.path.insert(0,'.')
from metricpoly.core import Point, pidx
from metricpoly import group
from metricpoly.dsl.prims import p_fiber_vertices, p_lift_partial, p_vertex
UT = json.load(open('results/phase9/unreached_targets.json'))
T=[t for t in UT if t['n']==8 and t['D']==8]
def restrict(p, keep):
    nums=[p.nums[pidx(p.n,keep[a],keep[b])] for a in range(len(keep)) for b in range(a+1,len(keep))]
    return Point.make(len(keep), p.D, nums)
sub={k:set() for k in range(3,9)}
for t in T:
    p=Point.make(8,8,t['nums'])
    for k in range(3,8):
        for S in itertools.combinations(range(8),k): sub[k].add(group.canonical(restrict(p,list(S))).key())
    sub[8].add(t['key'])
print({k:len(v) for k,v in sub.items()}, flush=True)
seeds=[Point.make(3,8,[3,3,4]),Point.make(3,8,[2,3,5])]
lev={3:{group.canonical(s).key():s for s in seeds}}
t0=time.time()
onlysub = len(sys.argv)>1   # oracle mode: keep only restrictions of targets (measures the needed part)
for k in range(4,9):
    nxt={}
    for y in lev[k-1].values():
        for z in p_fiber_vertices(p_lift_partial(y)):
            if z.D!=8: continue
            c=group.canonical(z); kk=c.key()
            if onlysub and kk not in sub[k]: continue
            nxt[kk]=c
    lev[k]=nxt
    print(k, 'orbits',len(nxt),'in target restrictions',len(set(nxt)&sub[k]),'of',len(sub[k]),'t',round(time.time()-t0,1), flush=True)
    if time.time()-t0>200: break
