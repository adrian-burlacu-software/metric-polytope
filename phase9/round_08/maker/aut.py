# automorphism group size of the integer metric d (backtracking), plus orbit structure
import json, sys
from collections import Counter
def auts(d):
    n=len(d); res=[]
    prof=[tuple(sorted(r)) for r in d]
    def bt(p):
        k=len(p)
        if k==n: res.append(tuple(p)); return
        for c in range(n):
            if c in p or prof[c]!=prof[k]: continue
            if all(d[k][i]==d[c][p[i]] for i in range(k)):
                p.append(c); bt(p); p.pop()
    bt([]); return res
def orbits(n,A):
    par=list(range(n))
    def f(a):
        while par[a]!=a: a=par[a]
        return a
    for p in A:
        for i in range(n): par[f(i)]=f(p[i])
    return sorted(Counter(f(i) for i in range(n)).values())
if __name__=='__main__':
    for fn in sys.argv[1:]:
        for r in json.load(open(fn)):
            A=auts(r['d']); print(r['id'],'D',r['D'],'|Aut|',len(A),'orbits',orbits(len(r['d']),A))
