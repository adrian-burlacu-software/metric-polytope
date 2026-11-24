# Level-8 sets of the D = 8 towers over w1, w2 (orbits), by deficiency; time of 8-hole fibers on a sample.
import json, sys, time, pickle, random
sys.path.insert(0,'.')
exec(open('phase9/round_13/maker/tower.py').read().split("if __name__")[0])
def dfc(p):
    inc,rk=stats(p); return p.n*(p.n-1)//2-rk
from collections import Counter
res={}
for name,k in W.items():
    t=time.time(); w=P(k); print(name,'core def',dfc(w))
    L7=up([w]); L8=up(L7); t8=time.time()-t
    c=Counter(dfc(z) for z in L8)
    print(name,'L8 orbits',len(L8),'by def',sorted(c.items()),'time %.1f'%t8, flush=True)
    res[name]={z.key():dfc(z) for z in L8}
json.dump(res,open('phase9/round_13/maker/level8.json','w'))
random.seed(1); smp=random.sample(list(res['w1']),10)
t=time.time(); n9=0
for k in smp: n9+=sum(1 for z in lift(P(k)) if z.D==8)
print('10 8-hole fibers %.1f s, D8 children %d'%(time.time()-t,n9))
