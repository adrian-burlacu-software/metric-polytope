# For each n = 9 dyadic target: the 6-node (and 7-node) restrictions reachable by peel chains (each step: the larger
# point is a vertex of the one-node fiber over the smaller). Do the n = 9 targets sit on towers over w1, w2?
import json, sys
from collections import defaultdict
sys.path.insert(0,'.')
sys.argv=[sys.argv[0]]+sys.argv[1:]
exec(open('phase9/round_13/maker/peel9.py').read().split("if __name__")[0])
W={'6|8|2,2,3,3,3,2,3,3,5,5,5,3,6,2,4':'w1','6|8|2,2,2,3,3,2,4,3,3,4,5,5,5,5,6':'w2'}
lim=int(sys.argv[1]) if len(sys.argv)>1 else 6
memo2={}
def downto(p):
    k=key(p)
    if k in memo2: return memo2[k]
    res={k}
    if p.n>lim:
        for v in range(p.n):
            if peelable(p,v): res|=downto(restrict(p,[i for i in range(p.n) if i!=v]))
    memo2[k]=res; return res
for Dw in (8,16):
    T=[t for t in UT if t['n']==9 and t['D']==Dw and isinstance(t['id'],int)]
    cov=defaultdict(set)
    for t in T:
        R=downto(Point.make(9,Dw,t['nums']))
        for k in R:
            if int(k.split('|')[0])==lim: cov[k].add(t['id'])
    print('D',Dw,'targets',len(T),'distinct',lim,'-node peel-cores',len(cov))
    for k in W:
        if k in cov: print('  ',W[k],'covers',len(cov[k]))
    left=set(t['id'] for t in T)
    while left:
        k=max(cov,key=lambda k:len(cov[k]&left)); g=cov[k]&left
        if not g: print('  uncovered',len(left)); break
        print('  ',len(g),len(cov[k]),k,W.get(k,'')); left-=g
