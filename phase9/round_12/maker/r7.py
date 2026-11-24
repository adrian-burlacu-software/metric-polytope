import json, sys
from collections import Counter, defaultdict
sys.path.insert(0,'.')
from metricpoly.core import Point
from metricpoly import group
UT = json.load(open('results/phase9/unreached_targets.json'))
T = [t for t in UT if t['n']==8 and t['D']==8]
print(len(T))
def restrict(p, keep):
    n=p.n; idx={}
    k=0
    for i in range(n):
        for j in range(i+1,n): idx[(i,j)]=k; k+=1
    nums=[p.nums[idx[(keep[a],keep[b])]] for a in range(len(keep)) for b in range(a+1,len(keep))]
    return Point.make(len(keep), p.D, nums)
cnt=Counter(); per=defaultdict(set); Ds=Counter()
for t in T:
    p=Point.make(8,8,t['nums'])
    for v in range(8):
        r=group.canonical(restrict(p,[i for i in range(8) if i!=v]))
        cnt[r.key()]+=1; per[r.key()].add(t['id']); Ds[r.D]+=1
print('distinct 7-restr orbits', len(cnt), 'D', Ds)
for k,c in sorted(cnt.items(), key=lambda kv:-len(per[kv[0]]))[:15]:
    print(len(per[k]), c, k)
