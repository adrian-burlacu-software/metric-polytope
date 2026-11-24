# For y1, y2 (top 7-node restriction orbits): which 6-node restrictions w make y a one-node fiber vertex over w,
# and how many D=8 targets have a 6-node restriction in that w orbit with a full peel x -> y -> w.
import json, sys, itertools
from collections import defaultdict
sys.path.insert(0,'.')
sys.argv=[sys.argv[0]]
from metricpoly.core import Point, pidx
from metricpoly import group
exec(open('phase9/round_12/maker/peel.py').read().split("Dw=int")[0])
UT = json.load(open('results/phase9/unreached_targets.json'))
T=[t for t in UT if t['n']==8 and t['D']==8]
cov=defaultdict(set)
for t in T:
    x=Point.make(8,8,t['nums'])
    for u in range(8):
        if not peelable(x,u): continue
        y=restrict(x,[i for i in range(8) if i!=u])
        for v in range(7):
            if peelable(y,v):
                w=group.canonical(restrict(y,[i for i in range(7) if i!=v]))
                cov[w.key()].add(t['id'])
print('distinct w', len(cov))
left=set(t['id'] for t in T)
while left:
    k=max(cov,key=lambda k:len(cov[k]&left)); g=cov[k]&left
    if not g: break
    print(len(g), len(cov[k]), k); left-=g
