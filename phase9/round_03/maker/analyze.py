import json, itertools, collections, sys
from fractions import Fraction as F
import networkx as nx
t=json.load(open('results/phase9/unreached_targets.json'))
T8=[r for r in t if r['n']==8]
def mat(r):
    n=r['n'];x={};k=0
    for i in range(n):
        for j in range(i+1,n):
            x[(i,j)]=x[(j,i)]=F(r['nums'][k],r['D']);k+=1
    return x
def switch(x,S,n):
    return {p:(1-v if ((p[0] in S)!=(p[1] in S)) else v) for p,v in x.items()}
stats=collections.Counter(); ex={}
for r in T8:
    n=8;x=mat(r);best=None;found=[]
    for m in range(1<<(n-1)):
        S={i for i in range(n) if m>>i&1}
        y=switch(x,S,n)
        vals=sorted(set(y.values()))
        nd=len(vals)
        if best is None or nd<best: best=nd
        # affine graph metric test
        v1=vals[0]
        if v1==0: continue
        G=nx.Graph();G.add_nodes_from(range(n));G.add_edges_from(p for p,v in y.items() if v==v1 and p[0]<p[1])
        if nx.is_connected(G):
            d=dict(nx.all_pairs_shortest_path_length(G))
            # f(d) a function?
            f={}
            ok=True
            for p,v in y.items():
                k=d[p[0]][p[1]]
                if f.setdefault(k,v)!=v: ok=False;break
            if ok:
                lin = all(f[k]==f[1]*k for k in f)
                aff = len(f)<=2 or all(f[k+1]-f[k]==f[2]-f[1] for k in range(1,max(f)))
                found.append(('lin' if lin else 'aff' if aff else 'fun', max(f), tuple(sorted(f.items()))))
    kinds=set(f[0] for f in found)
    stats[('mindistinct',best)]+=1
    for k in kinds: stats[k]+=1
    if found: ex.setdefault(tuple(sorted(kinds)),[]).append((r['D'],found[0]))
print(stats)
for k,v in ex.items(): print(k,len(v),v[:4])
