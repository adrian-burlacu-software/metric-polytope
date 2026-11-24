"""For each frontier pair (Y, b): is b on a segment or triangle of special fiber columns (tw/an/dp/ad of node i)?
Record kinds, index pattern, weights. Also b's minimal face dim."""
import pickle, collections, itertools, sys
from fractions import Fraction as F
P=pickle.load(open('phase9/round_16/maker/C_work/frontC.pkl','rb')); pairs=P['pairs']; C={c['tid']:c for c in P['C']}
def specials(Y,m):
    S=[]
    for i in range(m):
        tw=[F(0) if j==i else Y[i][j] for j in range(m)]
        dl=min(min(2*Y[i][j],2-2*Y[i][j]) for j in range(m) if j!=i)
        dp=list(tw); dp[i]=dl
        S+= [(('tw',i),tuple(tw)),(('an',i),tuple(1-t for t in tw)),(('dp',i),tuple(dp)),(('ad',i),tuple(1-t for t in dp))]
    S.append((('h',-1),tuple([F(1,2)]*m)))
    seen={}; 
    for k,v in S: seen.setdefault(v,k)
    return [(k,v) for v,k in seen.items()]
def solve2(b,P,Q,R):
    # b-R = a(P-R)+c(Q-R)
    u=[p-r for p,r in zip(P,R)]; w=[q-r for q,r in zip(Q,R)]; t=[x-r for x,r in zip(b,R)]
    m=len(b)
    for i in range(m):
        for j in range(i+1,m):
            det=u[i]*w[j]-u[j]*w[i]
            if det:
                a=(t[i]*w[j]-t[j]*w[i])/det; c=(u[i]*t[j]-u[j]*t[i])/det
                if all(a*u[k]+c*w[k]==t[k] for k in range(m)): return a,c
                return None
    return None
def pat(ks):
    idx=[i for _,i in ks]; d={}
    return ''.join(str(d.setdefault(i,len(d))) if i>=0 else 'h' for i in idx)
st=collections.Counter(); tg_hit=collections.defaultdict(set)
for key,(Y,b,tids) in pairs.items():
    m=len(b); S=specials(Y,m); found=False
    for (k1,P),(k2,Q) in itertools.combinations(S,2):
        r=solve2(b,P,Q,Q) if False else None
    # segments
    seg=[]
    for (k1,P),(k2,Q) in itertools.combinations(S,2):
        dif=[q-p for p,q in zip(P,Q)]; nz=[i for i,x in enumerate(dif) if x]
        if not nz: continue
        t=(b[nz[0]]-P[nz[0]])/dif[nz[0]]
        if 0<t<1 and all(P[i]+t*dif[i]==b[i] for i in range(m)): seg.append((k1,k2,t))
    if seg:
        st['seg']+=1; continue
    tri=[]
    for (k1,P),(k2,Q),(k3,R) in itertools.combinations(S,3):
        s=solve2(b,P,Q,R)
        if s and s[0]>0 and s[1]>0 and s[0]+s[1]<1:
            ws=(s[0],s[1],1-s[0]-s[1]); ks=(k1,k2,k3)
            o=sorted(zip(ks,ws),key=lambda z:(z[0][0],z[1]))
            kinds='-'.join(k[0] for k,_ in o); wts='/'.join(str(w) for _,w in o)
            tri.append((kinds,pat([k for k,_ in o]),wts))
    if tri:
        st['tri']+=1
        for t in set(tri): st[t]+=1
        for t in tids: tg_hit[t].add(key)
    else: st['none']+=1
for k,v in sorted(st.items(),key=lambda z:-z[1])[:60]: print(v,k)
print('targets with a triangle frontier pair', len(tg_hit), collections.Counter((C[t]['D'],C[t]['s']) for t in tg_hit))
