# Peel the n = 9 dyadic targets (D = 8, 16): which one-node deletions are peel steps (target is a fiber vertex over
# the restriction), whether the restriction is unreached, and the minimal peel size.
import json, sys, time
from collections import Counter, defaultdict
sys.path.insert(0,'.')
from metricpoly.core import Point, pidx, ineq_matrix, slacks, exact_rank
from metricpoly import group
import numpy as np
UT=json.load(open('results/phase9/unreached_targets.json'))
UN=set(json.load(open('results/phase9/unreached_nodes.json'))['keys'])
def restrict(p, keep):
    nums=[p.nums[pidx(p.n,keep[a],keep[b])] for a in range(len(keep)) for b in range(a+1,len(keep))]
    return Point.make(len(keep), p.D, nums)
_A={}
def peelable(p,v):
    if p.n not in _A: _A[p.n]=ineq_matrix(p.n)[0]
    A=_A[p.n]; T=np.flatnonzero(slacks(p)==0)
    cols=[pidx(p.n,min(v,j),max(v,j)) for j in range(p.n) if j!=v]
    return exact_rank(A[T][:,cols].tolist())==p.n-1
def key(p): return group.canonical(p).key()
memo={}
def down(p):
    k=key(p)
    if k in memo: return memo[k]
    res={k}
    for v in range(p.n):
        if peelable(p,v): res|=down(restrict(p,[i for i in range(p.n) if i!=v]))
    memo[k]=res; return res
if __name__=='__main__':
    for Dw in (8,16):
        T=[t for t in UT if t['n']==9 and t['D']==Dw and isinstance(t['id'],int)]
        ms=Counter(); botc=Counter()
        for t in T:
            X=Point.make(9,Dw,t['nums'])
            info=[]
            for v in range(9):
                y=restrict(X,[i for i in range(9) if i!=v]); ky=key(y)
                info.append((v, peelable(X,v), y.D, ky in UN))
            R=down(X); m=min(int(k.split('|')[0]) for k in R)
            ms[m]+=1
            pe=[(v,d,u) for v,pp,d,u in info if pp]
            print(Dw,t['id'],'peel->',[(v,d,'U' if u else 'R') for v,d,u in pe],'nonpeel D',[d for v,pp,d,u in info if not pp],'minpeel',m)
        print('D',Dw,'min peel sizes',sorted(ms.items()))
