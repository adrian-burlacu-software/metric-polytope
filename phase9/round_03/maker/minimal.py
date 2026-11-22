import json, itertools, collections, sys, time, pickle
sys.path.insert(0,'.')
from metricpoly import group
from metricpoly.core import Point
from fractions import Fraction as F
from math import gcd
u=json.load(open('results/phase9/unreached_nodes.json')); U=set(u['keys'])
t=[r for r in json.load(open('results/phase9/unreached_targets.json')) if r['n']==int(sys.argv[1])]
if len(sys.argv)>2: t=t[:int(sys.argv[2])]
def restrict(r,T):
    n=r['n']; idx={}
    k=0
    for i in range(n):
        for j in range(i+1,n): idx[(i,j)]=r['nums'][k]; k+=1
    T=sorted(T); nums=[idx[(a,b)] for a,b in itertools.combinations(T,2)]
    return Point.make(len(T), r['D'], nums)
t0=time.time()
minimal=collections.Counter(); out=[]
for r in t:
    n=r['n']; unr={}
    for k in range(3,n+1):
        for T in itertools.combinations(range(n),k):
            unr[T]= group.canonical(restrict(r,T)).key() in U
    mins=[T for T,v in unr.items() if v and all(not unr[S] for S in itertools.combinations(T,len(T)-1) if len(S)>=3)]
    for T in mins:
        key=group.canonical(restrict(r,T)).key(); minimal[key]+=1
    out.append((r['id'],[len(T) for T in mins]))
print('time',time.time()-t0)
print(collections.Counter(len(T) for T in []))
sz=collections.Counter(k.split('|')[0] for k in minimal)
print('distinct minimal unreached keys by size',sz)
print('top',minimal.most_common(15))
print('targets by min-size of minimal piece',collections.Counter(min(s) for _,s in out))
pickle.dump((minimal,out),open('phase9/round_03/maker/minimal_%s.pkl'%sys.argv[1],'wb'))
