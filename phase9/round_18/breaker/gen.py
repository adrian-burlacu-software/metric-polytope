#!/usr/bin/env python3
"""Breaker round 18: generate new rays (k = 9, 10, 11) of the {1,2} family and near-miss non-rays.
Usage: gen.py SEED SECONDS  -> pool_rays_SEED.json, pool_nonrays_SEED.json (lists of {k, edges, how})."""
import sys, json, random, time, itertools, warnings
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
import family12 as F
import networkx as nx
warnings.simplefilter("ignore")
HERE = Path(__file__).resolve().parent
DATA = ROOT / "results/phase9/family12"


def norm(edges):
    return sorted((min(a, b), max(a, b), int(w)) for a, b, w in edges)


def load(name):
    return [(j["k"], norm(j["edges"])) for j in json.loads((DATA / name).read_text())]


def whash(edges):
    G = F.nxgraph(edges)
    return nx.weisfeiler_lehman_graph_hash(G, edge_attr="w", iterations=4)


def add_node(k, edges, rng):
    n = rng.randint(2, k)
    S = rng.sample(range(k), n)
    mode = rng.random()
    return k + 1, edges + [(s, k, 1 if mode < .4 else 2 if mode < .55 else rng.choice((1, 2))) for s in S]


def twin(k, edges, rng):
    v = rng.randrange(k)
    new = [(a if a != v else k, b if b != v else k, w) for a, b, w in edges if v in (a, b)]
    r = rng.random()
    if r < .25:      # true twin joined by an edge
        new.append((v, k, rng.choice((1, 2))))
    elif r < .45 and len(new) > 2:   # drop one neighbour
        new.pop(rng.randrange(len(new)))
    elif r < .6:     # reweight one edge of the copy
        i = rng.randrange(len(new)); a, b, w = new[i]; new[i] = (a, b, 3 - w)
    return k + 1, edges + new


def subdivide(k, edges, rng):
    i = rng.randrange(len(edges))
    a, b, w = edges[i]
    w1, w2 = rng.choice(((1, 1), (1, 1), (1, 2), (2, 1), (2, 2)))
    return k + 1, edges[:i] + edges[i + 1:] + [(a, k, w1), (k, b, w2)]


def split_node(k, edges, rng):
    """split node v into v, v' joined by an edge, neighbours distributed."""
    v = rng.randrange(k)
    out = []
    for a, b, w in edges:
        if v in (a, b):
            o = b if a == v else a
            r = rng.random()
            if r < .4: out.append((v, o, w))
            elif r < .8: out.append((k, o, w))
            else: out += [(v, o, w), (k, o, w)]
        else:
            out.append((a, b, w))
    out.append((v, k, rng.choice((1, 2))))
    return k + 1, out


def glue(k1, e1, k2, e2, rng):
    """glue two graphs along m nodes (random identification)."""
    m = rng.choice((2, 2, 3, 3, 4))
    if m > min(k1, k2): return None
    A = rng.sample(range(k1), m); B = rng.sample(range(k2), m)
    lab = dict(zip(B, A)); nxt = k1
    for v in range(k2):
        if v not in lab:
            lab[v] = nxt; nxt += 1
    D = {}
    for a, b, w in e1: D[(a, b)] = w
    for a, b, w in e2:
        x, y = sorted((lab[a], lab[b]))
        D[(x, y)] = min(w, D.get((x, y), 9))
    return nxt, [(a, b, w) for (a, b), w in D.items()]


def perturb(k, edges, rng):
    r = rng.random(); e = list(edges)
    if r < .3:
        i = rng.randrange(len(e)); a, b, w = e[i]; e[i] = (a, b, 3 - w); how = "flip weight of one edge"
    elif r < .55:
        e.pop(rng.randrange(len(e))); how = "delete one edge"
    elif r < .8:
        have = {(a, b) for a, b, _ in e}
        non = [p for p in itertools.combinations(range(k), 2) if p not in have]
        if not non: return None
        a, b = rng.choice(non); e.append((a, b, rng.choice((1, 2)))); how = "add one edge"
    else:
        i = rng.randrange(len(e)); a, b, w = e[i]
        c = rng.randrange(k)
        if c in (a, b) or any({x, y} == {a, c} for x, y, _ in e): return None
        e[i] = (min(a, c), max(a, c), w); how = "move one end of an edge"
    return k, e, how


def random_graph(k, rng):
    r = rng.random()
    if r < .3:      # random multipartite-like
        parts = [rng.randrange(rng.randint(2, 4)) for _ in range(k)]
        p = rng.uniform(.6, 1)
        e = [(a, b, 1) for a, b in itertools.combinations(range(k), 2) if parts[a] != parts[b] and rng.random() < p]
        how = "random subgraph of a complete multipartite graph, weights 1"
    elif r < .5:
        p = rng.uniform(.3, .7)
        e = [(a, b, 1) for a, b in itertools.combinations(range(k), 2) if rng.random() < p]
        how = "random graph G(k,p), weights 1"
    elif r < .75:
        p = rng.uniform(.3, .8); q = rng.uniform(.1, .9)
        e = [(a, b, 1 if rng.random() < q else 2) for a, b in itertools.combinations(range(k), 2) if rng.random() < p]
        how = "random graph with random weights in {1,2}"
    else:           # weight-1 graph plus all remaining pairs at weight 2 where minimal: 'distance-2 completion'
        p = rng.uniform(.2, .6)
        e = [(a, b, 1) if rng.random() < p else (a, b, 2) for a, b in itertools.combinations(range(k), 2)]
        how = "complete graph with random weights in {1,2} (reduced to its minimal graph)"
    return k, e, how


def structured():
    out = []
    def add(G, how, wfun=None):
        G = nx.convert_node_labels_to_integers(G)
        out.append((G.number_of_nodes(), [(a, b, 1 if wfun is None else wfun(a, b)) for a, b in G.edges()], how))
    for k in (9, 10, 11):
        for r in range(1, 4 ** (k // 2)):       # weighted circulants: each jump absent / 1 / 2
            jumps = {}
            x = r
            for j in range(1, k // 2 + 1):
                if x % 3: jumps[j] = x % 3
                x //= 3
            if r >= 3 ** (k // 2): break
            e = {}
            for j, w in jumps.items():
                for v in range(k):
                    a, b = sorted((v, (v + j) % k)); e[(a, b)] = w
            out.append((k, [(a, b, w) for (a, b), w in e.items()], f"weighted circulant C_{k}{jumps}"))
        for parts in itertools.combinations_with_replacement(range(1, k), 2):
            pass
        def partitions(n, m=1):
            if n == 0: yield []; return
            for i in range(m, n + 1):
                for p in partitions(n - i, i): yield [i] + p
        for p in partitions(k):
            if len(p) >= 2:
                G = nx.complete_multipartite_graph(*p)
                add(G, f"complete multipartite K{p}")
                # minus a perfect-ish matching between the first two parts, and weight-2 inside parts
                H = G.copy()
                part = nx.get_node_attributes(G, "subset")
                add(nx.complete_graph(k), f"K{p} with weight 2 inside parts", lambda a, b, part=part: 1 if part[a] != part[b] else 2)
                add(nx.complete_graph(k), f"K{p} with weight 1 inside parts, 2 across", lambda a, b, part=part: 2 if part[a] != part[b] else 1)
    named = {"petersen": nx.petersen_graph(), "grotzsch": nx.mycielski_graph(4), "paley9": nx.paley_graph(9).to_undirected(),
             "rook3x3": nx.cartesian_product(nx.complete_graph(3), nx.complete_graph(3)),
             "prism5": nx.circular_ladder_graph(5), "mobius5": nx.circulant_graph(10, [1, 5]),
             "johnson52": nx.complement(nx.petersen_graph()), "K5xK2": nx.cartesian_product(nx.complete_graph(5), nx.complete_graph(2)),
             "K33xK2?": nx.cartesian_product(nx.complete_bipartite_graph(2, 3), nx.complete_graph(2)),
             "wheel9": nx.wheel_graph(9), "wheel10": nx.wheel_graph(10), "wheel11": nx.wheel_graph(11),
             "mycielski_C5_minus": nx.mycielski_graph(4), "paley11_und": nx.circulant_graph(11, [1, 3, 4, 5, 9]),
             "K3xK3_compl": nx.complement(nx.cartesian_product(nx.complete_graph(3), nx.complete_graph(3))),
             "tensor_K3_K3": nx.tensor_product(nx.complete_graph(3), nx.complete_graph(3)),
             "tensor_K5_K2": nx.tensor_product(nx.complete_graph(5), nx.complete_graph(2)),
             "strong_C5_K2": nx.strong_product(nx.cycle_graph(5), nx.complete_graph(2)),
             "lex_C5_2K1": nx.lexicographic_product(nx.cycle_graph(5), nx.empty_graph(2)),
             "lex_P5_2K1": nx.lexicographic_product(nx.path_graph(5), nx.empty_graph(2)),
             "lex_C3_3K1": nx.lexicographic_product(nx.cycle_graph(3), nx.empty_graph(3)),
             "grid3x3": nx.grid_2d_graph(3, 3), "K33_subdiv": None}
    for name, G in named.items():
        if G is None: continue
        add(G, f"named graph {name}, weights 1")
        C = nx.complement(G)
        if nx.is_connected(C): add(C, f"complement of {name}, weights 1")
        K = nx.convert_node_labels_to_integers(G)
        es = set(map(frozenset, K.edges()))
        add(nx.complete_graph(K.number_of_nodes()), f"{name} at weight 1, non-edges at weight 2", lambda a, b, es=es: 1 if frozenset((a, b)) in es else 2)
        add(nx.complete_graph(K.number_of_nodes()), f"{name} at weight 2, non-edges at weight 1", lambda a, b, es=es: 2 if frozenset((a, b)) in es else 1)
    return out


def main():
    seed, secs = int(sys.argv[1]), float(sys.argv[2])
    rng = random.Random(seed)
    base = {k: [e for _, e in load(f"rays_k{k}.json")] for k in (6, 7, 8, 9)}
    known9 = {}
    for e in base[9]:
        known9.setdefault((len(e), whash(e)), []).append(e)
    em = nx.algorithms.isomorphism.numerical_edge_match("w", 0)
    seen = {}       # (k, len, hash) -> list of graphs (rays found in this run)
    rays, nonrays = [], []
    cnt = {}

    def is_new(k, e):
        key = (k, len(e), whash(e))
        G = F.nxgraph(e)
        if k == 9:
            for e2 in known9.get(key[1:], []):
                if nx.is_isomorphic(G, F.nxgraph(e2), edge_match=em): return False
        for G2 in seen.setdefault(key, []):
            if nx.is_isomorphic(G, G2, edge_match=em): return False
        seen[key].append(G)
        return True

    def consider(k, e, how, want_non=False):
        if not 9 <= k <= 11: return None
        d = F.metric(k, e)
        if (d >= F.INF).any(): return None
        e = [tuple(x) for x in F.minimal_edges(k, d)]       # reduce to the minimal graph
        if not {w for _, _, w in e} <= {1, 2}: return None
        c = F.check(k, e)
        if not (c["connected"] and c["minimal"]): return None
        tag = how.split(":")[0]
        if c["ray"]:
            if is_new(k, e):
                rays.append({"k": k, "edges": [list(x) for x in e], "how": how})
                cnt[(k, tag)] = cnt.get((k, tag), 0) + 1
                return e
        elif want_non or rng.random() < .02:
            nonrays.append({"k": k, "edges": [list(x) for x in e], "how": how})
        return None

    if seed == 0:
        for k, e, how in structured():
            consider(k, e, how, want_non=True)
    t0 = time.time()
    work = {9: [], 10: [], 11: []}
    while time.time() - t0 < secs:
        r = rng.random()
        kk = rng.choice((8, 8, 9, 9, 9, 10, 10))
        pool = base.get(kk, []) + work.get(kk, []) if kk <= 9 else work[kk]
        if kk == 9 and work[9] and rng.random() < .5: pool = work[9]
        if not pool: continue
        e = rng.choice(pool)
        if r < .25: k2, e2 = add_node(kk, e, rng); how = f"add node: new node joined to a random set of a k={kk} ray"
        elif r < .45: k2, e2 = twin(kk, e, rng); how = f"twin: copy a node of a k={kk} ray (with variations)"
        elif r < .58: k2, e2 = subdivide(kk, e, rng); how = f"subdivide: subdivide an edge of a k={kk} ray"
        elif r < .68: k2, e2 = split_node(kk, e, rng); how = f"split: split a node of a k={kk} ray into two adjacent nodes"
        elif r < .78:
            ka = rng.choice((6, 7, 8)); kb = rng.choice((5, 6, 7)) if True else 0
            if kb == 5: eb = [(a, b, 1) for a in range(2) for b in range(2, 5)] + [(0, 1, 2)]; kb = 5
            else: eb = rng.choice(base[kb])
            g = glue(ka, rng.choice(base[ka]), kb, eb, rng)
            if g is None: continue
            k2, e2 = g; how = f"glue: glue a k={ka} ray and a k={kb} ray along a few nodes"
        elif r < .9:
            k2, e2, how = random_graph(rng.choice((9, 10, 11)), rng); how = "random: " + how
        else:
            if kk < 9: continue
            p = perturb(kk, e, rng)
            if p is None: continue
            k2, e2, h = p; how = f"perturb: {h} of a k={kk} ray"
            got = consider(k2, e2, how, want_non=True)
            if got: work[k2].append(got)
            continue
        got = consider(k2, e2, how)
        if got: work[k2].append(got)
    (HERE / f"pool_rays_{seed}.json").write_text(json.dumps(rays))
    (HERE / f"pool_nonrays_{seed}.json").write_text(json.dumps(nonrays))
    for key in sorted(cnt): print(key, cnt[key])
    print("rays", len(rays), "nonrays", len(nonrays))


if __name__ == "__main__":
    main()
