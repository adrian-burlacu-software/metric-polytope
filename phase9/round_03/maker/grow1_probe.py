import json, sys, collections, itertools, time
sys.path.insert(0,'.')
from metricpoly import group, core
from metricpoly.core import Point
from fractions import Fraction as F
R=json.load(open('checkpoints/phase9/reached.json'))
U=json.load(open('results/phase9/unreached_nodes.json')); UK=set(U['keys']); TK=set(U['target_keys'])
def parse(k):
    n,D,nums=k.split('|'); return Point.make(int(n),int(D),[int(v) for v in nums.split(',')])
def key(n,M):
    prs=core.pairs(n); q=Point.from_fractions(n,[M[i][j] for i,j in prs])
    if not core.is_feasible(q): return None
    return group.canonical(q).key()
hits=collections.defaultdict(set); t0=time.time()
for k in R:
    p=parse(k); n=p.n
    if n>=8: continue
    prs=core.pairs(n); base=[F(v,p.D) for v in p.nums]
    for m in range(1<<(n-1)):
        S={i for i in range(n) if m>>i&1}
        M=[[F(0)]*n for _ in range(n)]
        for a,(i,j) in zip(base,prs):
            v=(1-a if ((i in S)!=(j in S)) else a); M[i][j]=M[j][i]=v
        tau=max(M[a][b]+M[a][c]+M[b][c] for a,b,c in itertools.combinations(range(n),3))
        if tau==0: continue
        lam=F(2)/tau
        W=[[v*lam for v in row] for row in M]
        mc=max(max(r) for r in W)
        variants={}
        # radial of normalized
        al=mc/2
        variants['rad_norm']=[[*W[i],al] for i in range(n)]+[[al]*n+[F(0)]]
        # twin of normalized (each node)
        if False:
            for i in range(n):
                variants['twin_norm%d'%i]=[[*W[r],W[r][i]] for r in range(n)]+[[W[i][c] for c in range(n)]+[F(0)]]
        for name,Mx in variants.items():
            kk=key(n+1,Mx)
            if kk and kk in UK: hits[name.rstrip('0123456789')].add(kk)
print('time',time.time()-t0)
for nm,s in hits.items(): print(nm,len(s),collections.Counter(x.split('|')[0] for x in s),'targets',len(s&TK))
