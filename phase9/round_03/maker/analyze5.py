exec(open('phase9/round_03/maker/analyze.py').read().split('stats=')[0])
import networkx as nx, sys
which=sys.argv[1] if len(sys.argv)>1 else '8'
def test(y,n):
    v1=min(y.values())
    if v1==0: return None
    c=max(y.values())/v1
    if c.denominator!=1: return None
    G=nx.Graph(); G.add_nodes_from(range(n)); G.add_edges_from(p for p,v in y.items() if v==v1 and p[0]<p[1])
    sp=dict(nx.all_pairs_shortest_path_length(G))
    for (i,j),v in y.items():
        if i<j and v1*min(c,sp[i].get(j,10**9))!=v: return None
    return int(c), G.number_of_edges(), nx.number_connected_components(G)
def allswitch(rows,n):
    hits=collections.Counter(); ids=[]
    for r in rows:
        x=mat(r); res=set()
        for m in range(1<<(n-1)):
            S={i for i in range(n) if m>>i&1}
            t=test(switch(x,S,n),n)
            if t: res.add(t)
        if res: hits[min(res)]+=1; ids.append(r['id'])
    return hits,ids
h,ids=allswitch(T8,8); print(sum(h.values()),h)
