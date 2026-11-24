# Columns used by star decompositions (orbit of X|C+a over the core), vs all D = 8 lift columns of the core.
# Also: does some pair (a,b) make X|C+a+b an endpoint of its 1-hole interval (staged construction)?
import json, sys, itertools
from collections import Counter
sys.path.insert(0,'.')
exec(open('phase9/round_13/maker/peel9.py').read().split("if __name__")[0])
from metricpoly.dsl.prims import _fiber_vertices
from metricpoly.dsl.values import Partial
from metricpoly.core import pairs
def lift(y): return _fiber_vertices(Partial.make(y.n+1,{(i,j):f for (i,j),f in zip(pairs(y.n),y.fractions())}))
Wk={'6|8|2,2,3,3,3,2,3,3,5,5,5,3,6,2,4':'w1','6|8|2,2,2,3,3,2,4,3,3,4,5,5,5,5,6':'w2'}
R=json.load(open('phase9/round_13/maker/tower.json'))
def P(k):
    n,D,r=k.split('|'); return Point.make(int(n),int(D),[int(a) for a in r.split(',')])
def stt(p):
    if p.n not in _A: _A[p.n]=ineq_matrix(p.n)[0]
    T=np.flatnonzero(slacks(p)==0)
    return p.n*(p.n-1)//2-exact_rank(_A[p.n][T].tolist()), len(T)
def interval_end(X, C, a, b):
    Y=restrict(X, list(C)+[a,b]); n=8
    v=Y.nums[pidx(8,6,7)]
    lo=max(abs(Y.nums[pidx(8,k,6)]-Y.nums[pidx(8,k,7)]) for k in range(6))
    hi=min(min(Y.nums[pidx(8,k,6)]+Y.nums[pidx(8,k,7)], 2*Y.D-Y.nums[pidx(8,k,6)]-Y.nums[pidx(8,k,7)]) for k in range(6))
    return v==lo or v==hi
used={'w1':Counter(),'w2':Counter()}; staged=Counter()
def star(X, tag):
    found=False
    for C in itertools.combinations(range(X.n),6):
        k=key(restrict(X,list(C)))
        if k not in Wk: continue
        rest=[a for a in range(X.n) if a not in C]
        ys=[restrict(X,list(C)+[a]) for a in rest]
        if all(peelable(y,6) for y in ys):
            found=True
            for y in ys: used[Wk[k]][key(y)]+=1
            if X.n==9: staged[(tag, Wk[k], any(interval_end(X,C,a,b) for a,b in itertools.permutations(rest,2)))]+=1
    return found
for nm in ('w1','w2'):
    for o in sorted(set(o for r in R[nm] for o in r['outs'])): star(P(o),'n8')
for t in UT:
    if t['n']==9 and t['D']==8 and isinstance(t['id'],int): star(Point.make(9,8,t['nums']),t['id'])
print('staged (n=9 star embeddings):',dict(staged))
for k,nm in Wk.items():
    cols=[z for z in lift(P(k)) if z.D==8]
    orb=Counter(key(z) for z in cols)
    print(nm,'D8 lift columns',len(cols),'orbits',len(orb),'used orbits',len(used[nm]),'covering columns',sum(orb[u] for u in used[nm]))
    for u,c in used[nm].most_common():
        print('   ',c,stt(P(u)),u)
