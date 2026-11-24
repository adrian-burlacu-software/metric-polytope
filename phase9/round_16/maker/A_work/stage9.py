# For n=9 targets (D given): one-node covers A (6 nodes, co-P_6 at a/D) + B (4 nodes, H at b/D).
# Report v's position on the complement path P_6, H type and v's degree in H, and which u in B-v pass the stage test
# (x|(V-u) is a vertex of its glue fiber with known pairs inside A and inside B-u).
import json, sys, itertools
from fractions import Fraction as F
from collections import Counter, defaultdict
import networkx as nx
sys.path.insert(0, 'phase9/round_11/maker'); sys.path.insert(0, 'phase9/round_16/maker/A_work')
from stage import fiber_vertex
from cov9 import load
D = int(sys.argv[1]); fn = sys.argv[2]
data = {r['id']: r for r in json.load(open(fn))}
X9 = {tid: X for tid, d, X in load(9, {D})}
tot = defaultdict(set)
for tid, rec in data.items():
    g = {frozenset(T): L for T, L in rec['goods']}
    Xf = [[F(X9[tid][i][j], D) for j in range(9)] for i in range(9)]
    for A in g:
        if len(A) != 6: continue
        for B in g:
            if len(B) != 4 or len(A & B) != 1 or len(A | B) != 9: continue
            v = next(iter(A & B))
            for SA, ma, ea, da, EA in g[A]:
                GA = nx.Graph(); GA.add_nodes_from(A); GA.add_edges_from(map(tuple, EA))
                P = nx.complement(GA)
                degs = sorted(d for _, d in P.degree())
                if degs != [1, 1, 2, 2, 2, 2] or not nx.is_connected(P): continue
                ends = [a for a in P if P.degree(a) == 1]
                pos = nx.shortest_path_length(P, ends[0], v); pos = min(pos, 5 - pos)
                for SB, mb, eb, db, EB in g[B]:
                    GB = nx.Graph(); GB.add_nodes_from(B); GB.add_edges_from(map(tuple, EB))
                    htype = (mb, tuple(sorted(d for _, d in GB.degree())), GB.degree(v))
                    oks = []
                    for u in sorted(B - {v}):
                        W = [i for i in range(9) if i != u]
                        known = {(a, b) for a, b in itertools.combinations(W, 2) if (a in A and b in A) or (a in B and b in B)}
                        ok, nh = fiber_vertex(Xf, W, known)
                        if ok: oks.append((GB.degree(u), nx.shortest_path_length(GB, v, u)))
                    key = (ma, pos, htype, tuple(sorted(oks)))
                    tot[key].add(tid)
                    print(tid, key, flush=True)
print('SUMMARY')
for k, s in sorted(tot.items(), key=lambda kv: -len(kv[1])): print(len(s), k, sorted(s))
allt = set().union(*tot.values()) if tot else set()
print('targets with co-P6 cover:', len(allt))
