exec(open('phase9/round_03/maker/analyze2.py').read().split('C=collections')[0])
cnt=collections.Counter()
for r in T8:
    x=mat(r); bs=best_switch(x)
    vals=[str(v) for v in bs[0][1]]
    if ','.join(vals)!='2/9,4/9,2/3': continue
    sigs=[]
    for nd,vals,S,y in bs:
        G1=nx.Graph();G1.add_nodes_from(range(8));G1.add_edges_from(p for p,w in y.items() if w==F(2,9) and p[0]<p[1])
        G2=nx.Graph();G2.add_nodes_from(range(8));G2.add_edges_from(p for p,w in y.items() if w==F(4,9) and p[0]<p[1])
        U=nx.compose(G1,G2)
        # is G2 = pairs at distance 2 in G1 plus extra?
        d1=dict(nx.all_pairs_shortest_path_length(G1))
        two=sum(1 for i,j in G2.edges() if d1[i].get(j)==2)
        sigs.append((G1.number_of_edges(),G2.number_of_edges(),two,nx.is_forest(G1),sorted(len(c) for c in nx.connected_components(U))))
    cnt[str(min(sigs))]+=1
for k,v in cnt.most_common(): print(v,k)
