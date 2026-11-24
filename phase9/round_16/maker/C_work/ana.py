"""Group C (partly reached) targets: odd primes of D vs odd primes present in reached restrictions."""
import json, sys, pickle, collections
from fractions import Fraction as F
from math import gcd
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
res=collections.Counter(); C=[]
for tid,tg in enumerate(targets):
    n0=tg.n; full=(1<<n0)-1
    if tkeys[tid][full] not in TK: continue
    Rk=[m for m in range(1,full) if bin(m).count('1')>=3 and tkeys[tid][m] in R]
    if not Rk: continue
    s=max(bin(m).count('1') for m in Rk)
    rp=set()
    for m in Rk: rp|=oddp(kden(tkeys[tid][m]))
    tp=oddp(tg.D)
    miss=tp-rp
    res[(n0,tg.D,s,tuple(sorted(rp)),tuple(sorted(miss)))]+=1
    C.append(dict(tid=tid,n=n0,D=tg.D,s=s,rp=sorted(rp),miss=sorted(miss)))
for k,v in sorted(res.items()): print(k,v)
json.dump(C,open('phase9/round_14/maker/groupC.json','w'))
print(len(C), 'missing-prime targets', sum(1 for c in C if c['miss']), 'missing only 3', sum(1 for c in C if c['miss']==[3]))
