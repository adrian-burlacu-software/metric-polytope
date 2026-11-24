"""Round 16 C: current group-C targets (unreached, some reached restriction >=3 nodes, no missing odd prime) and their
frontier pairs (Y reached, Z = Y + v unreached, both restrictions of the target). Saves C_work/frontC.pkl."""
import json, sys, pickle, collections
from fractions import Fraction as F
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import detour_depth2 as d2
exec(open('phase9/round_04/maker/frontier_load.py').read())
def oddp(d):
    out=set(); p=3
    while d%2==0: d//=2
    while d>1:
        while d%p==0: out.add(p); d//=p
        p+=2
    return out
def kden(k): return int(k.split('|')[1])
C=[]; pairs={}
for tid,tg in enumerate(targets):
    n0=tg.n; full=(1<<n0)-1
    if tkeys[tid][full] not in TK: continue
    Rk=[m for m in range(1,full) if bin(m).count('1')>=3 and tkeys[tid][m] in R]
    if not Rk: continue
    s=max(bin(m).count('1') for m in Rk); rp=set()
    for m in Rk: rp|=oddp(kden(tkeys[tid][m]))
    miss=oddp(tg.D)-rp
    C.append(dict(tid=tid,n=n0,D=tg.D,s=s,miss=sorted(miss)))
    if miss: continue
    M=d2.matrix(tg); X=[[F(int(M[a,b]),tg.D) for b in range(n0)] for a in range(n0)]
    for m in Rk:
        for v in range(n0):
            if m>>v&1: continue
            Zk=tkeys[tid][m|(1<<v)]
            if Zk in R: continue
            key=(tkeys[tid][m],Zk)
            if key in pairs: pairs[key][2].add(tid); continue
            Ys=[a for a in range(n0) if m>>a&1]
            Y=[[X[a][q] for q in Ys] for a in Ys]; b=tuple(X[v][a] for a in Ys)
            pairs[key]=(Y,b,{tid})
print(collections.Counter((c['n'],c['D'],c['s'],tuple(c['miss'])) for c in C))
print('groupC', len(C), 'no-miss', sum(1 for c in C if not c['miss']), 'pairs', len(pairs),
      collections.Counter(len(p[1]) for p in pairs.values()))
pickle.dump(dict(C=C,pairs=pairs),open('phase9/round_16/maker/C_work/frontC.pkl','wb'))
