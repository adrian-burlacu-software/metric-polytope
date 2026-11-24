# For the n = 9 star targets: per pair of non-core nodes, is d(a,b) an endpoint of its interval over the core
# (lo/hi/inside)? Are the columns among those used by n = 8 star outputs? Deficiency of the 8-node restrictions.
import json, sys, itertools
from collections import Counter
sys.path.insert(0,'.')
src=open('phase9/round_13/maker/star2.py').read().split("used={")[0]
exec(src)
R=json.load(open('phase9/round_13/maker/tower.json'))
used8={'w1':set(),'w2':set()}
def emb(X):
    for C in itertools.combinations(range(X.n),6):
        k=key(restrict(X,list(C)))
        if k not in Wk: continue
        rest=[a for a in range(X.n) if a not in C]
        if all(peelable(restrict(X,list(C)+[a]),6) for a in rest): yield C,rest,Wk[k]
def pos(X,C,a,b):
    Y=restrict(X,list(C)+[a,b]); v=Y.nums[pidx(8,6,7)]
    lo=max(abs(Y.nums[pidx(8,k,6)]-Y.nums[pidx(8,k,7)]) for k in range(6))
    hi=min(min(Y.nums[pidx(8,k,6)]+Y.nums[pidx(8,k,7)], 2*Y.D-Y.nums[pidx(8,k,6)]-Y.nums[pidx(8,k,7)]) for k in range(6))
    return 'lo' if v==lo else 'hi' if v==hi else 'in(%d,%d,%d)'%(lo,v,hi)
for nm in ('w1','w2'):
    for o in sorted(set(o for r in R[nm] for o in r['outs'])):
        X=P(o)
        for C,rest,w in emb(X):
            if w==nm:
                for a in rest: used8[nm].add(key(restrict(X,list(C)+[a])))
print('n=8 used column orbits', {k:len(v) for k,v in used8.items()})
for t in UT:
    if not (t['n']==9 and t['D']==8 and isinstance(t['id'],int)): continue
    X=Point.make(9,8,t['nums'])
    for C,rest,w in emb(X):
        print(t['id'],w,'cols in used8:',[key(restrict(X,list(C)+[a])) in used8[w] for a in rest],
              'pairs:',[(pos(X,C,a,b), stt(restrict(X,list(C)+[a,b]))[0]) for a,b in itertools.combinations(rest,2)])
