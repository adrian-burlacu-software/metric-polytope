# Peel chains: x (n nodes) -> x - v is "peelable" if x is a vertex of the one-node fiber over x - v
# (tight rows of x restricted to the hole columns (v,*) have rank n-1). Find, per target, the smallest
# restriction z reachable by peel steps, and collect bottom orbits.
import json, sys, itertools
from collections import Counter, defaultdict
sys.path.insert(0,'.')
from metricpoly.core import Point, pidx, ineq_matrix, slacks, exact_rank
from metricpoly import group
import numpy as np
UT = json.load(open('results/phase9/unreached_targets.json'))
def restrict(p, keep):
    nums=[p.nums[pidx(p.n,keep[a],keep[b])] for a in range(len(keep)) for b in range(a+1,len(keep))]
    return Point.make(len(keep), p.D, nums)
def peelable(p, v):
    A,_=ineq_matrix(p.n); T=np.flatnonzero(slacks(p)==0)
    cols=[pidx(p.n,min(v,j),max(v,j)) for j in range(p.n) if j!=v]
    return exact_rank(A[T][:,cols].tolist())==p.n-1
Dw=int(sys.argv[1]) if len(sys.argv)>1 else 8
T=[t for t in UT if t['n']==8 and t['D']==Dw]
bottoms=defaultdict(set); minsize=Counter()
memo={}
def down(p):
    # return set of canonical keys of minimal-size... we return all reachable restrictions keys with sizes
    k=group.canonical(p).key()
    if k in memo: return memo[k]
    res={k:p}
    for v in range(p.n):
        if peelable(p,v):
            q=restrict(p,[i for i in range(p.n) if i!=v])
            res.update(down(q))
    memo[k]=res; return res
for t in T:
    p=Point.make(8,Dw,t['nums']); R=down(p)
    m=min(int(k.split('|')[0]) for k in R)
    minsize[m]+=1
    for k,q in R.items():
        if int(k.split('|')[0])==m: bottoms[k].add(t['id'])
print('min peel size', sorted(minsize.items()))
for k,ids in sorted(bottoms.items(), key=lambda kv:-len(kv[1]))[:20]:
    print(len(ids), k)
