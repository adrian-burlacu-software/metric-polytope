# Hypothesis "star over the core": a target X contains a copy of the core w on a 6-set C, and for every other node a,
# X|C+a is a vertex of the one-node fiber over X|C (a D = 8 lift column of w). Then X is a vertex of the glue of
# these columns (holes = pairs among the non-core nodes). Check for n = 8 tower outputs and n = 9 dyadic targets.
import json, sys, itertools
sys.path.insert(0,'.')
exec(open('phase9/round_13/maker/peel9.py').read().split("if __name__")[0])
W={'6|8|2,2,3,3,3,2,3,3,5,5,5,3,6,2,4':'w1','6|8|2,2,2,3,3,2,4,3,3,4,5,5,5,5,6':'w2'}
R=json.load(open('phase9/round_13/maker/tower.json'))
def P(k):
    n,D,r=k.split('|'); return Point.make(int(n),int(D),[int(a) for a in r.split(',')])
def star(X):
    res=set()
    for C in itertools.combinations(range(X.n),6):
        k=key(restrict(X,list(C)))
        if k not in W: continue
        rest=[a for a in range(X.n) if a not in C]
        if all(peelable(restrict(X,list(C)+[a]),6) for a in rest): res.add(W[k])
    return res
for nm in ('w1','w2'):
    outs=sorted(set(o for r in R[nm] for o in r['outs']))
    ok=sum(1 for o in outs if nm in star(P(o)))
    print('n=8 outputs of',nm,len(outs),'star over',nm,':',ok)
T=[t for t in UT if t['n']==9 and t['D']==8 and isinstance(t['id'],int)]
for t in T: print(9,t['id'],star(Point.make(9,8,t['nums'])))
