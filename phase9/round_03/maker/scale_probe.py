import json, sys, collections, itertools
sys.path.insert(0,'.')
from metricpoly import group, core
from metricpoly.core import Point
from fractions import Fraction as F
R=json.load(open('checkpoints/phase9/reached.json'))
U=json.load(open('results/phase9/unreached_nodes.json')); UK=set(U['keys']); TK=set(U['target_keys'])
print('reached by size',collections.Counter(k.split('|')[0] for k in R))
def parse(k):
    n,D,nums=k.split('|'); return Point.make(int(n),int(D),[int(v) for v in nums.split(',')])
def fr(p): return [F(v,p.D) for v in p.nums]
hits=collections.Counter(); hitkeys=set()
for k in R:
    p=parse(k); n=p.n; prs=core.pairs(n); base=fr(p)
    for m in range(1<<(n-1)):
        S={i for i in range(n) if m>>i&1}
        v=[(1-a if ((i in S)!=(j in S)) else a) for a,(i,j) in zip(base,prs)]
        idx={pr:a for pr,a in zip(prs,v)}
        tau=max(idx[(a,b)]+idx[(a,c)]+idx[(b,c)] for a,b,c in itertools.combinations(range(n),3))
        if tau==0 or tau==2: continue
        w=[a*2/tau for a in v]
        q=Point.from_fractions(n,w)
        if not core.is_feasible(q): continue
        key=group.canonical(q).key()
        if key in UK and key not in hitkeys:
            hitkeys.add(key); hits[n]+=1
print('normalize one-step new unreached nodes by size',hits, 'targets',len(hitkeys&TK))
json.dump(sorted(hitkeys),open('phase9/round_03/maker/scale_hits.json','w'))
