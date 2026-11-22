import json, itertools, collections
from fractions import Fraction as F
import networkx as nx
exec(open('phase9/round_03/maker/analyze.py').read().split('stats=')[0])
def best_switch(x,n=8):
    out=[]
    for m in range(1<<(n-1)):
        S={i for i in range(n) if m>>i&1}
        y=switch(x,S,n); out.append((len(set(y.values())),sorted(set(y.values())),S,y))
    b=min(o[0] for o in out); return [o for o in out if o[0]==b]
C=collections.Counter(); ex={}
for r in T8:
    x=mat(r); bs=best_switch(x)
    if bs[0][0]>4: continue
    sigs=set()
    for nd,vals,S,y in bs:
        # level graph degree sequences
        lg=[]
        for v in vals:
            G=nx.Graph();G.add_nodes_from(range(8));G.add_edges_from(p for p,w in y.items() if w==v and p[0]<p[1])
            lg.append((str(v),G.number_of_edges(),tuple(sorted(d for _,d in G.degree()))))
        sigs.add(tuple(lg))
    s=min(sigs)
    C[tuple(a for a,_,_ in s)]+=1
    ex.setdefault(tuple(a for a,_,_ in s),[]).append(s)
for k,v in sorted(C.items(),key=lambda z:-z[1]): print(v,k, ex[k][0])
