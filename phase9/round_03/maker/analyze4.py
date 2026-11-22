exec(open('phase9/round_03/maker/analyze.py').read().split('stats=')[0])
from math import gcd, lcm
from functools import reduce
import networkx as nx
def trunc_test(y,n):
    L=reduce(lcm,[v.denominator for v in y.values()],1)
    d={p:int(v*L) for p,v in y.items()}
    g=reduce(gcd,[v for v in d.values()]); d={p:v//g for p,v in d.items()}
    if 0 in d.values(): return None
    c=max(d.values())
    G=nx.Graph(); G.add_nodes_from(range(n))
    for (i,j),v in d.items():
        if i<j and v<c: G.add_edge(i,j,weight=v)
    sp=dict(nx.all_pairs_dijkstra_path_length(G))
    for (i,j),v in d.items():
        if i<j and min(c,sp[i].get(j,10**9))!=v: return None
    # essential edges
    ess=[(i,j,v) for (i,j),v in d.items() if i<j and v<c and not any(d[(i,k)]+d[(k,j)]==v for k in range(n) if k not in (i,j))]
    H=nx.Graph(); H.add_nodes_from(range(n)); H.add_weighted_edges_from(ess)
    return c, len(ess), nx.is_forest(H), tuple(sorted(collections.Counter(w for *_,w in ess).items())), nx.number_connected_components(H)
stats=collections.Counter(); per=collections.defaultdict(set)
for r in T8:
    x=mat(r); res=set()
    for m in range(1<<7):
        S={i for i in range(8) if m>>i&1}
        t=trunc_test(switch(x,S,8),8)
        if t: res.add(t)
    if res:
        stats['trunc']+=1
        b=min(res,key=lambda t:(not t[2], t[0], t[1]))
        stats[('forest' if any(t[2] for t in res) else 'nonforest')]+=1
        per[(r['D'],b[0],b[3])].add(r['id'])
print(stats)
for k,v in sorted(per.items(),key=lambda z:-len(z[1])): print(k,len(v))
