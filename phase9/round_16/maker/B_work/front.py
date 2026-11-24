"""Track B: D=15/21 partly reached n=9 targets. Frontier pairs (Y reached, Z = Y+v unreached), with den/odd primes."""
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
rows=[]; stat=collections.Counter(); pairs=collections.Counter()
FP=[]
for tid,tg in enumerate(targets):
    n0=tg.n; full=(1<<n0)-1
    if n0!=9 or tkeys[tid][full] not in TK or tg.D not in (15,21): continue
    Rk=[m for m in range(1,full) if bin(m).count('1')>=3 and tkeys[tid][m] in R]
    if not Rk: continue
    s=max(bin(m).count('1') for m in Rk)
    rp=set()
    for m in Rk: rp|=oddp(kden(tkeys[tid][m]))
    P=oddp(tg.D)-{3}
    # frontier pairs: Y reached (>=3), Z=Y+v unreached; record whether Z carries the prime p
    fr=[]
    for m in Rk:
        for v in range(n0):
            if m>>v&1: continue
            Zk=tkeys[tid][m|(1<<v)]
            if Zk in R: continue
            zp=oddp(kden(Zk))
            fr.append((bin(m).count('1'), tkeys[tid][m], Zk, v, m, bool(zp&P)))
    fp=[f for f in fr if f[5]]
    stat[(tg.D, s, tuple(sorted(rp)), len(fp)>0)]+=1
    for f in fp:
        pairs[(f[1],f[2])]+=1
        FP.append(dict(tid=tid,D=tg.D,s=f[0],Y=f[1],Z=f[2],v=f[3],m=f[4]))
for k,v in sorted(stat.items()): print('D,s,reached-primes,has-prime-frontier', k, v)
print('distinct prime-introducing frontier pairs', len(pairs))
c=collections.Counter((p[0].split('|')[0],p[0].split('|')[1],p[1].split('|')[1]) for p in pairs)
for k,v in sorted(c.items()): print(' Y size,Y D,Z D',k,v)
json.dump(FP,open('phase9/round_16/maker/B_work/fp.json','w'))
