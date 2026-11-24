# For n = 9 D = 8 targets: all peel chains X -> x8 -> y7 -> w (w = w1 or w2 up to symmetry), with deficiency
# def = C(k,2) - tight rank and incidence of x8 and y7. Which filter on intermediates keeps at least one chain?
import json, sys, itertools
from collections import defaultdict, Counter
sys.path.insert(0,'.')
exec(open('phase9/round_13/maker/peel9.py').read().split("if __name__")[0])
W={'6|8|2,2,3,3,3,2,3,3,5,5,5,3,6,2,4':'w1','6|8|2,2,2,3,3,2,4,3,3,4,5,5,5,5,6':'w2'}
def stats(p):
    if p.n not in _A: _A[p.n]=ineq_matrix(p.n)[0]
    T=np.flatnonzero(slacks(p)==0)
    return p.n*(p.n-1)//2-exact_rank(_A[p.n][T].tolist()), len(T)
out={}
T=[t for t in UT if t['n']==9 and t['D']==8 and isinstance(t['id'],int)]
for t in T:
    X=Point.make(9,8,t['nums']); chains=[]
    for u in range(9):
        x8=restrict(X,[i for i in range(9) if i!=u])
        s8=None
        for v in range(8):
            if not peelable(x8,v): continue
            y7=restrict(x8,[i for i in range(8) if i!=v]); s7=None
            for w in range(7):
                if not peelable(y7,w): continue
                k=key(restrict(y7,[i for i in range(7) if i!=w]))
                if k in W:
                    s8=s8 or stats(x8); s7=s7 or stats(y7)
                    chains.append((W[k],s8,s7,key(x8),key(y7)))
    print(t['id'],len(chains),'best (def8,def7):',sorted(set((c[0],c[1][0],c[2][0]) for c in chains))[:6])
    out[t['id']]=chains
json.dump(out,open('phase9/round_13/maker/chains9.json','w'))
