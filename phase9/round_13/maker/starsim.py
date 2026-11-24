# Python simulation of gen-dyadic-star (01) at n = 9: candidate counts, vertices, unreached-target hits,
# with and without the m_8-pair column pruning. Integers are 8x distances.
import json, sys, itertools, time
sys.path.insert(0,'.')
from metricpoly.core import Point, pidx, is_vertex, pairs
from metricpoly import group
from metricpoly.dsl.prims import _fiber_vertices
from metricpoly.dsl.values import Partial
UT=json.load(open('results/phase9/unreached_targets.json'))
TK={t['key']:t['id'] for t in UT if t['n']==9}
UN=set(json.load(open('results/phase9/unreached_nodes.json'))['keys'])
cores=['6|8|2,2,3,3,3,2,3,3,5,5,5,3,6,2,4','6|8|2,2,2,3,3,2,4,3,3,4,5,5,5,5,6']
def P(k):
    n,D,r=k.split('|'); return Point.make(int(n),int(D),[int(a) for a in r.split(',')])
def mat(p):
    M=[[0]*p.n for _ in range(p.n)]
    for (i,j),v in zip(pairs(p.n),p.nums): M[i][j]=M[j][i]=v
    return M
def feas_new(M):  # triangles/perimeters involving last node
    m=len(M)-1
    for i in range(m):
        for j in range(i+1,m):
            a,b,c=M[m][i],M[m][j],M[i][j]
            if a>b+c or b>a+c or c>a+b or a+b+c>16: return False
    return True
def topoint(M):
    n=len(M); return Point.make(n,8,[M[i][j] for i,j in pairs(n)])
def run(core, prune, K=3):
    w=P(core); W=mat(w)
    cols=[]
    for z in _fiber_vertices(Partial.make(7,{(i,j):f for (i,j),f in zip(pairs(6),w.fractions())})):
        if z.D==8:
            c=[z.nums[pidx(7,k,6)] for k in range(6)]
            if sum(c)<=24: cols.append(c)
    lo=lambda a,b:max(abs(x-y) for x,y in zip(a,b)); hi=lambda a,b:min(min(x+y,16-x-y) for x,y in zip(a,b))
    def ext(M,sel,c):
        for vals in itertools.product(*[(lo(b,c),hi(b,c)) for b in sel]):
            N=[r[:]+[x] for r,x in zip(M,c+list(vals))]; N.append(c+list(vals)+[0])
            if feas_new(N): yield N
    def level(cs,k):
        S=[(W,[],-1)]
        for _ in range(k):
            S=[(N,sel+[cs[i]],i) for M,sel,l in S for i in range(l+1,len(cs)) for N in ext(M,sel,cs[i])]
        return S
    uc=cols
    if prune:
        V2=[sel for M,sel,_ in level(cols,2) if is_vertex(topoint(M))[0]]
        uc=[a for a in cols if any(a in s for s in V2)]
    t=time.time(); S=level(uc,K); nf=len(S)
    V=[topoint(M) for M,_,_ in S]; V=[p for p in V if is_vertex(p)[0]]
    keys=set(group.canonical(p).key() for p in V)
    hitsT=sorted(TK[k] for k in keys if k in TK); hitsN=sum(1 for k in keys if k in UN)
    print(core[:12],'prune',prune,'cols',len(cols),'used',len(uc),'feasible cands',nf,'vertices',len(V),'orbits',len(keys),'hits nodes',hitsN,'targets',hitsT,'%.1fs'%(time.time()-t),flush=True)
for c in cores:
    run(c, True)
for c in cores:
    run(c, False)
