# detail of one-node covers: per target, list (G iso class via canonical edge string, deg of v in G), (H class, deg v in H), scales
import json, sys, itertools
from collections import Counter, defaultdict
import networkx as nx
f = sys.argv[1]; ov = int(sys.argv[2]); minA = int(sys.argv[3]) if len(sys.argv) > 3 else 0
data = json.load(open(f))
def wl(T, E):
    G = nx.Graph(); G.add_nodes_from(T); G.add_edges_from(E)
    return nx.weisfeiler_lehman_graph_hash(G, iterations=4)[:8], G
summ = Counter(); per = defaultdict(set)
names = {}
for rec in data:
    g = {frozenset(T): L for T, L in rec['goods']}
    for A in g:
        for B in g:
            if len(A | B) == 9 and len(A & B) == ov and len(A) >= len(B) and A != B and len(A) >= minA:
                if len(A) == len(B) and sorted(A) > sorted(B): continue
                v = sorted(A & B)
                for SA, ma, ea, da, EA in g[A]:
                    for SB, mb, eb, db, EB in g[B]:
                        ha, GA = wl(sorted(A), [tuple(e) for e in EA]); hb, GB = wl(sorted(B), [tuple(e) for e in EB])
                        names.setdefault(ha, (len(A), len(EA), tuple(da), [tuple(e) for e in nx.convert_node_labels_to_integers(GA).edges()]))
                        names.setdefault(hb, (len(B), len(EB), tuple(db), [tuple(e) for e in nx.convert_node_labels_to_integers(GB).edges()]))
                        key = (ha, ma, tuple(GA.degree(u) for u in v), hb, mb, tuple(GB.degree(u) for u in v))
                        per[key].add(rec['id'])
for k, s in sorted(per.items(), key=lambda kv: -len(kv[1]))[:20]:
    print(len(s), k, sorted(s)[:12])
print()
used = {k[0] for k in per} | {k[3] for k in per}
for h in used: print(h, names[h])
