"""Kernel primitives of the rule DSL (exact arithmetic throughout).

Each primitive is registered with a signature, Unicode/LaTeX formula templates and an equivariance tag:
  'G'     : commutes with the full group (permutations and switchings) as a map on orbits
  'Sn'    : commutes with permutations only
  'label' : depends on labels (closure must expand inputs or quantify internally)
  'n/a'   : not point-valued
"""
from __future__ import annotations

import itertools
import math
from fractions import Fraction
from pathlib import Path
from functools import lru_cache
from typing import List, Sequence

import numpy as np

from .. import core, deza, group, patterns, polyhedra
from ..core import Point, dim, pairs, pidx
from .registry import primitive
from .values import Graph, Mid, Partial, Q, Tree


class DomainList(list):
    """A list that remembers whether it holds all vertices ('all') or orbit representatives ('reps')."""
    kind = "all"
    n = None
    complete = True          # False: a partial list (a failing forall is a valid counterexample; a pass proves nothing)


def _pt_from_matrix(n: int, get) -> Point:
    return Point.from_fractions(n, [Q(get(i, j)) for (i, j) in pairs(n)])


def _nodes(S, n=None) -> frozenset:
    if isinstance(S, frozenset):
        return S
    if isinstance(S, (set, list, tuple, range)):
        return frozenset(int(v) for v in S)
    raise TypeError(f"expected node set, got {type(S).__name__}")


# ======================================================================= points

@primitive("const", 2, "Nat Rat -> Point", "{1}·𝟙_{0}", r"{1}\,\mathbb{1}_{{{0}}}", "Sn")
def p_const(n, q):
    return Point.from_fractions(n, [Q(q)] * dim(n))


@primitive("cut", 2, "Nat Nodes -> Point", "δ({1})", r"\delta({1})", "label")
def p_cut(n, S):
    S = _nodes(S)
    return Point.make(n, 1, [int((i in S) != (j in S)) for (i, j) in pairs(n)])


@primitive("entry", 3, "Point Nat Nat -> Rat", "{0}_{{{1}{2}}}", r"{0}_{{{1}{2}}}")
def p_entry(x, i, j):
    if i == j:
        return Fraction(0)
    return Fraction(x.nums[pidx(x.n, i, j)], x.D)


@primitive("size", 1, "Point -> Nat", "|{0}|", r"|{0}|")
def p_size(x):
    return x.n


@primitive("maxc", 1, "Point -> Rat", "δ({0})", r"\delta({0})")
def p_maxc(x):
    return Fraction(max(x.nums), x.D)


@primitive("scale", 2, "Rat Point -> Point", "{0}·{1}", r"{0}\,{1}", "Sn")
def p_scale(q, x):
    return Point.from_fractions(x.n, [Q(q) * f for f in x.fractions()])


@primitive("affine", 3, "Rat Rat (Point|Mid) -> (Point|Mid)", "{0}·{2}+{1}", r"{0}{2}+{1}", "Sn")
def p_affine(a, b, x):
    a, b = Q(a), Q(b)
    if isinstance(x, Mid):
        return Mid.make([[a * v + b for v in r] for r in x.data])
    return Point.from_fractions(x.n, [a * f + b for f in x.fractions()])


# ======================================================================= blocks

@primitive("block", 3, "Point Mid Point -> Point", "[{0} {1}; {1}ᵀ {2}]",
           r"\begin{{pmatrix}}{0}&{1}\\{1}^\top&{2}\end{{pmatrix}}", "Sn")
def p_block(A, M, B):
    a = A.n if isinstance(A, Point) else A
    b = B.n if isinstance(B, Point) else B
    if M.rows != a or M.cols != b:
        raise ValueError(f"block: middle is {M.rows}x{M.cols}, blocks are {a} and {b}")
    n = a + b

    def get(i, j):
        if i < a and j < a:
            return p_entry(A, i, j)
        if i >= a and j >= a:
            return p_entry(B, i - a, j - a)
        if i < a:
            return M[i, j - a]
        return M[j, i - a]
    return _pt_from_matrix(n, get)


@primitive("restrict", 2, "Nodes Point -> Point", "{1}|_{0}", r"{1}|_{{{0}}}", "Sn")
def p_restrict(T, x):
    T = sorted(_nodes(T))
    if any(not (0 <= t < x.n) for t in T):
        raise ValueError("restrict: node out of range")
    return _pt_from_matrix(len(T), lambda i, j: p_entry(x, T[i], T[j]))


@primitive("split", 2, "Nodes Point -> (Point Mid Point)", "split_{0}({1})", r"\mathrm{{split}}_{{{0}}}({1})", "Sn")
def p_split(T, x):
    T = sorted(_nodes(T))
    U = [v for v in range(x.n) if v not in set(T)]
    A = p_restrict(T, x)
    B = p_restrict(U, x)
    M = Mid.make([[p_entry(x, i, j) for j in U] for i in T]) if T and U else Mid(len(T), len(U), tuple(() for _ in T))
    return (A, M, B)


@primitive("col", 2, "Point Nat -> Mid", "{0}_{{{1}·}}", r"{0}_{{{1}\cdot}}")
def p_col(x, i):
    return Mid.make([[p_entry(x, j, i)] for j in range(x.n)])


@primitive("mcol", 2, "Mid Nat -> Mid", "{0}_{{·{1}}}", r"{0}_{{\cdot {1}}}")
def p_mcol(M, j):
    return Mid.make([[M[i, j]] for i in range(M.rows)])


@primitive("mconst", 3, "Nat Nat Rat -> Mid", "{2}·𝟙_{{{0}×{1}}}", r"{2}\,\mathbb{{1}}_{{{0}\times{1}}}")
def p_mconst(k, l, q):
    return Mid.make([[Q(q)] * l for _ in range(k)])


@primitive("mset", 4, "Mid Nat Nat Rat -> Mid", "{0}[{1},{2}↦{3}]", r"{0}[{1},{2}\mapsto {3}]")
def p_mset(M, i, j, q):
    rows = [list(r) for r in M.data]
    rows[i][j] = Q(q)
    return Mid.make(rows)


@primitive("mhcat", (1, None), "Mid... -> Mid", "[{0}]", r"[{0}]")
def p_mhcat(*Ms):
    if len({M.rows for M in Ms}) != 1:
        raise ValueError("mhcat: row counts differ")
    return Mid.make([sum((list(M.data[i]) for M in Ms), []) for i in range(Ms[0].rows)])


@primitive("mvcat", (1, None), "Mid... -> Mid", "[{0}]", r"[{0}]")
def p_mvcat(*Ms):
    if len({M.cols for M in Ms}) != 1:
        raise ValueError("mvcat: column counts differ")
    return Mid.make([list(r) for M in Ms for r in M.data])


@primitive("mvcat-list", 1, "List<Rat> -> Mid", "({0})ᵀ", r"({0})^\top")
def p_mvcat_list(lst):
    return Mid.make([[Q(v)] for v in lst])


@primitive("rows", 1, "Mid -> Nat", "rows({0})", r"\mathrm{{rows}}({0})")
def p_rows(M):
    return M.rows


@primitive("cols", 1, "Mid -> Nat", "cols({0})", r"\mathrm{{cols}}({0})")
def p_cols(M):
    return M.cols


@primitive("mvalues", 1, "Mid -> List<Rat>", "vals({0})", r"\mathrm{{vals}}({0})")
def p_mvalues(M):
    return M.values()


@primitive("mflip", 3, "Nodes Nodes Mid -> Mid", "{2}^{{{0},{1}}}", r"{2}^{{{0},{1}}}")
def p_mflip(S1, S2, M):
    S1, S2 = _nodes(S1), _nodes(S2)
    return Mid.make([[(1 - M[i, j]) if ((i in S1) != (j in S2)) else M[i, j] for j in range(M.cols)]
                     for i in range(M.rows)])


@primitive("mrestrict", 3, "Nodes Nodes Mid -> Mid", "{2}[{0},{1}]", r"{2}[{0},{1}]")
def p_mrestrict(R, C, M):
    R, C = sorted(_nodes(R)), sorted(_nodes(C))
    return Mid(len(R), len(C), tuple(tuple(M[i, j] for j in C) for i in R))


@primitive("msplit", 3, "Nodes Nodes Mid -> (Mid Mid Mid Mid)", "msplit_{{{0},{1}}}({2})",
           r"\mathrm{{msplit}}_{{{0},{1}}}({2})")
def p_msplit(R, C, M):
    R, C = _nodes(R), _nodes(C)
    Rb = frozenset(range(M.rows)) - R
    Cb = frozenset(range(M.cols)) - C
    return (p_mrestrict(R, C, M), p_mrestrict(R, Cb, M), p_mrestrict(Rb, C, M), p_mrestrict(Rb, Cb, M))


@primitive("tree", (1, None), "Str Any... -> Tree", "{0}", r"{0}")
def p_tree(label, *parts):
    kids = tuple(p for p in parts if isinstance(p, Tree))
    payload = tuple(_freeze(p) for p in parts if not isinstance(p, Tree))
    return Tree(str(label), payload, kids)


def _freeze(v):
    if isinstance(v, list):
        return tuple(_freeze(x) for x in v)
    return v


# ======================================================================= symmetry

@primitive("switch", 2, "Nodes Point -> Point", "r_{{δ({0})}}({1})", r"r_{{\delta({0})}}({1})", "G")
def p_switch(S, x):
    S = _nodes(S)
    fr = x.fractions()
    return Point.from_fractions(x.n, [(1 - f) if ((i in S) != (j in S)) else f
                                      for f, (i, j) in zip(fr, pairs(x.n))])


@primitive("perm", 2, "Perm Point -> Point", "π_{0}·{1}", r"\pi_{{{0}}}\cdot {1}", "G")
def p_perm(p, x):
    p = tuple(p)
    inv = [0] * x.n
    for i, v in enumerate(p):
        inv[v] = i
    return _pt_from_matrix(x.n, lambda a, b: p_entry(x, inv[a], inv[b]))


@primitive("move-last", 2, "Tuple Point -> Point", "{1}", r"{1}")
def p_move_last(t, x):
    t = list(t)
    rest = [v for v in range(x.n) if v not in set(t)]
    order = rest + t                         # new label k <- old node order[k]
    return _pt_from_matrix(x.n, lambda a, b: p_entry(x, order[a], order[b]))


@primitive("move-first", 2, "Tuple Point -> Point", "{1}", r"{1}")
def p_move_first(t, x):
    t = list(t)
    rest = [v for v in range(x.n) if v not in set(t)]
    order = t + rest
    return _pt_from_matrix(x.n, lambda a, b: p_entry(x, order[a], order[b]))


@primitive("canon", 1, "Point -> Point", "canon({0})", r"\mathrm{{canon}}({0})", "G")
def p_canon(x):
    return group.canonical(x)


@primitive("orbit-key", 1, "Point -> Str", "[{0}]", r"[{0}]")
def p_orbit_key(x):
    return group.canonical(x).key()


@primitive("switch-class", 1, "Point -> List<Point>", "K·{0}", r"K\cdot {0}", "G")
def p_switch_class(x):
    out, seen = [], set()
    for s in range(1 << (x.n - 1)):
        S = frozenset(v for v in range(1, x.n) if (s >> (v - 1)) & 1)
        y = p_switch(S, x)
        if y not in seen:
            seen.add(y)
            out.append(y)
    return out


@primitive("pattern", 1, "Point -> Pattern", "pattern({0})", r"\mathrm{{pattern}}({0})")
def p_pattern(x):
    return [tuple(int(v) for v in r) for r in patterns.pattern(x)]


@primitive("mid-canon", 1, "Mid -> Str", "[{0}]_mid", r"[{0}]_{{\mathrm{{mid}}}}")
def p_mid_canon(M):
    """Canonical form of a middle under row perms, column perms and mflip (switching restricted to M).
    Brute force over flips; rows/cols sorted after each flip choice (sorting = optimal perm for lexmin)."""
    best = None
    for s1 in range(1 << M.rows):
        S1 = frozenset(i for i in range(M.rows) if (s1 >> i) & 1)
        # given S1, each column j independently chooses flip t_j to minimise; but rows sort jointly:
        # brute force S2 too for small sizes
        for s2 in range(1 << M.cols):
            S2 = frozenset(j for j in range(M.cols) if (s2 >> j) & 1)
            F = p_mflip(S1, S2, M)
            key = _lexmin_rowcol(F)
            if best is None or key < best:
                best = key
    return f"{M.rows}x{M.cols}|" + ";".join(",".join(str(v) for v in r) for r in best)


def _lexmin_rowcol(M: Mid):
    """Lexmin of row-and-column permutations, by alternating sorts until stable (heuristic), then exact
    for small sizes via column permutations."""
    rows = [tuple(r) for r in M.data]
    best = None
    for cp in itertools.permutations(range(M.cols)) if M.cols <= 6 else [tuple(range(M.cols))]:
        R = sorted(tuple(r[c] for c in cp) for r in rows)
        t = tuple(R)
        if best is None or t < best:
            best = t
    return best


# ======================================================================= graphs

@primitive("graph", 2, "Nat List<Tuple> -> Graph", "G", "G")
def p_graph(n, edges):
    return Graph.make(n, edges)


@primitive("order", 1, "Graph -> Nat", "|V({0})|", r"|V({0})|")
def p_order(G):
    return G.n


@primitive("edges", 1, "Graph -> List<Tuple>", "E({0})", r"E({0})")
def p_edges(G):
    return [tuple(e) for e in G.sorted_edges()]


@primitive("neighbors", 2, "Graph Nat -> List<Nat>", "N_{0}({1})", r"N_{{{0}}}({1})")
def p_neighbors(G, i):
    return sorted(G.adj()[i])


def _bfs(G: Graph, s: int):
    adj = G.adj()
    dist = {s: 0}
    frontier = [s]
    while frontier:
        nxt = []
        for u in frontier:
            for w in adj[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    nxt.append(w)
        frontier = nxt
    return dist


@primitive("connected?", 1, "Graph -> Bool", "{0} connected", r"{0}\ \text{{connected}}")
def p_connected(G):
    return G.n <= 1 or len(_bfs(G, 0)) == G.n


@primitive("gmetric", 1, "Graph -> Point", "d_{{{0}}}", r"d_{{{0}}}", "Sn")
def p_gmetric(G):
    if not p_connected(G):
        raise ValueError("gmetric: graph is disconnected")
    D = [_bfs(G, s) for s in range(G.n)]
    return Point.make(G.n, 1, [D[i][j] for (i, j) in pairs(G.n)])


@primitive("triameter", 1, "Graph -> Nat", "τ({0})", r"\tau({0})")
def p_triameter(G):
    d = p_gmetric(G)
    return max(p_entry(d, i, j) + p_entry(d, i, k) + p_entry(d, j, k)
               for i, j, k in itertools.combinations(range(G.n), 3))


@primitive("complement", 1, "Graph -> Graph", "̅{0}", r"\overline{{{0}}}")
def p_complement(G):
    return Graph.make(G.n, [e for e in itertools.combinations(range(G.n), 2) if e not in G.edges])


@primitive("gminus", 2, "Graph Graph -> Graph", "{0}−{1}", r"{0}-{1}")
def p_gminus(G, H):
    if G.n != H.n:
        raise ValueError("gminus: different node sets")
    return Graph(G.n, G.edges - H.edges)


@primitive("gunion", 2, "Graph Graph -> Graph", "{0}∪{1}", r"{0}\cup{1}")
def p_gunion(G, H):
    if G.n != H.n:
        raise ValueError("gunion: different node sets")
    return Graph(G.n, G.edges | H.edges)


@primitive("level-graph", 2, "Point Rat -> Graph", "Γ_{1}({0})", r"\Gamma_{{{1}}}({0})")
def p_level_graph(x, q):
    q = Q(q)
    return Graph.make(x.n, [(i, j) for (i, j) in pairs(x.n) if p_entry(x, i, j) == q])


@primitive("good?", 1, "Graph -> Bool", "good({0})", r"\mathrm{{good}}({0})")
def p_good(G):
    """DDF96 'good': exists spanning E' with |E'| = |N| and nonsingular node-edge incidence.
    Implemented as: every connected component contains an odd cycle (tests compare with the definition)."""
    adj = G.adj()
    color = {}
    for s in range(G.n):
        if s in color:
            continue
        color[s] = 0
        stack, odd = [s], False
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if w not in color:
                    color[w] = 1 - color[u]
                    stack.append(w)
                elif color[w] == color[u]:
                    odd = True
        if not odd:
            return False
    return True


def good_by_definition(G: Graph) -> bool:
    """Literal DDF96 definition (exponential; for tests only)."""
    E = G.sorted_edges()
    for sub in itertools.combinations(E, G.n):
        M = [[0] * G.n for _ in range(G.n)]
        for c, (i, j) in enumerate(sub):
            M[i][c] = 1
            M[j][c] = 1
        if core.exact_rank(M) == G.n:
            return True
    return False


# ======================================================================= lists, numbers

@primitive("list", (0, None), "Any... -> List", "({0})", r"({0})")
def p_list(*xs):
    return list(xs)


@primitive("tuple", (0, None), "Any... -> Tuple", "({0})", r"({0})")
def p_tuple(*xs):
    return tuple(xs)


@primitive("concat", (0, None), "List... -> List", "{0}", r"{0}")
def p_concat(*ls):
    return [v for l in ls for v in l]


@primitive("concat-all", 1, "List<List> -> List", "⋃{0}", r"\bigcup {0}")
def p_concat_all(ls):
    return [v for l in ls for v in l]


@primitive("len", 1, "List -> Nat", "|{0}|", r"|{0}|")
def p_len(l):
    return len(l)


@primitive("nth", 2, "List Nat -> Any", "{0}[{1}]", r"{0}_{{{1}}}")
def p_nth(l, i):
    return l[i]


@primitive("fst", 1, "Tuple -> Any", "{0}₁", r"{0}_1")
def p_fst(t):
    return t[0]


@primitive("snd", 1, "Tuple -> Any", "{0}₂", r"{0}_2")
def p_snd(t):
    return t[1]


@primitive("elems", 1, "Nodes -> List", "{0}", r"{0}")
def p_elems(S):
    return sorted(S)


@primitive("nodes", 1, "List -> Nodes", "{{{0}}}", r"\{{{0}\}}")
def p_nodes_(l):
    return _nodes(l)


@primitive("sum", 1, "List<Rat> -> Rat", "Σ{0}", r"\sum {0}")
def p_sum(l):
    return sum(l, 0)


@primitive("distinct", 1, "List -> List", "distinct({0})", r"\mathrm{{distinct}}({0})")
def p_distinct(l):
    out, seen = [], set()
    for v in l:
        k = _hashable(v)
        if k not in seen:
            seen.add(k)
            out.append(v)
    return out


def _hashable(v):
    if isinstance(v, list):
        return tuple(_hashable(x) for x in v)
    return v


@primitive("orbits", 1, "List<Point> -> List<Point>", "{0}/G", r"{0}/G")
def p_orbits(l):
    out, seen = [], set()
    for v in l:
        k = group.canonical(v).key()
        if k not in seen:
            seen.add(k)
            out.append(v)
    return out


@primitive("in", 2, "Any (List|Nodes) -> Bool", "{0}∈{1}", r"{0}\in{1}")
def p_in(v, coll):
    return v in coll


@primitive("card", 1, "(List|Nodes) -> Nat", "|{0}|", r"|{0}|")
def p_card(c):
    return len(c)


@primitive("binom", 2, "Nat Nat -> Nat", "C({0},{1})", r"\binom{{{0}}}{{{1}}}")
def p_binom(n, k):
    return math.comb(n, k)


@primitive("mod", 2, "Nat Nat -> Nat", "{0} mod {1}", r"{0}\bmod {1}")
def p_mod(a, b):
    return a % b


def _num_binop(name, f, uni, tex):
    primitive(name, (1, None), "Rat... -> Rat", uni, tex)(f)


def _add(*xs):
    return sum(xs, 0)


def _sub(a, *xs):
    return -a if not xs else a - sum(xs, 0)


def _mul(*xs):
    r = 1
    for v in xs:
        r = r * v
    return r


def _div(a, b):
    return Fraction(a) / Fraction(b)


_num_binop("+", _add, "({0})", r"({0})")
_num_binop("-", _sub, "({0})", r"({0})")
_num_binop("*", _mul, "({0})", r"({0})")
primitive("/", 2, "Rat Rat -> Rat", "{0}/{1}", r"\frac{{{0}}}{{{1}}}")(_div)
primitive("min", (1, None), "Rat... -> Rat", "min({0})", r"\min({0})")(lambda *xs: min(xs))
primitive("max", (1, None), "Rat... -> Rat", "max({0})", r"\max({0})")(lambda *xs: max(xs))


def _eq(a, b):
    return _hashable(a) == _hashable(b)


primitive("=", 2, "Any Any -> Bool", "{0}={1}", r"{0}={1}")(_eq)
primitive("<", 2, "Rat Rat -> Bool", "{0}<{1}", r"{0}<{1}")(lambda a, b: a < b)
primitive("<=", 2, "Rat Rat -> Bool", "{0}≤{1}", r"{0}\le{1}")(lambda a, b: a <= b)
primitive(">", 2, "Rat Rat -> Bool", "{0}>{1}", r"{0}>{1}")(lambda a, b: a > b)
primitive(">=", 2, "Rat Rat -> Bool", "{0}≥{1}", r"{0}\ge{1}")(lambda a, b: a >= b)
primitive("not", 1, "Bool -> Bool", "¬{0}", r"\neg {0}")(lambda a: not a)


# ======================================================================= domains

@primitive("range", 2, "Nat Nat -> List<Nat>", "[{0},{1})", r"[{0},{1})")
def p_range(a, b):
    return list(range(a, b))


@primitive("subsets", (1, 2), "Nat [Nat] -> List<Nodes>", "2^[{0}]", r"2^{{[{0}]}}")
def p_subsets(n, k=None):
    if k is None:
        return [frozenset(c) for r in range(n + 1) for c in itertools.combinations(range(n), r)]
    return [frozenset(c) for c in itertools.combinations(range(n), k)]


@primitive("perms", 1, "Nat -> List<Perm>", "S_{0}", r"S_{{{0}}}")
def p_perms(n):
    return [tuple(p) for p in itertools.permutations(range(n))]


@primitive("arrangements", 2, "Nat Nat -> List<Tuple>", "[{0}]^{{({1})}}", r"[{0}]^{{\underline{{{1}}}}}")
def p_arrangements(n, k):
    return [tuple(p) for p in itertools.permutations(range(n), k)]


@primitive("switchings", 1, "Nat -> List<Nodes>", "K_{0}", r"K_{{{0}}}")
def p_switchings(n):
    return [frozenset(v for v in range(1, n) if (s >> (v - 1)) & 1) for s in range(1 << (n - 1))]


@primitive("partitions", 1, "Nat -> List<List<Nat>>", "Par({0})", r"\mathrm{{Par}}({0})")
def p_partitions(n):
    out = []

    def rec(rem, mx, acc):
        if rem == 0:
            out.append(list(acc))
            return
        for k in range(min(rem, mx), 0, -1):
            rec(rem - k, k, acc + [k])
    rec(n, n, [])
    return out


@lru_cache(maxsize=None)
def _atlas():
    import networkx as nx
    return nx.graph_atlas_g()


GRAPHS8 = Path(__file__).resolve().parent.parent.parent / "data" / "generated" / "graphs8.json"
N_GRAPHS = {8: (12346, 11117)}          # OEIS A000088 / A001349: all / connected graphs on 8 nodes


def _graphs8():
    """All non-isomorphic graphs on 8 nodes: extend every 7-node atlas graph by a node with every neighbour set,
    deduplicate exactly (WL hash buckets + nx.is_isomorphic). Cached in data/generated/graphs8.json."""
    import json
    import networkx as nx
    if GRAPHS8.exists():
        return [Graph.make(8, e) for e in json.loads(GRAPHS8.read_text())]
    buckets = {}
    reps = []
    for g in _atlas():
        if g.number_of_nodes() != 7:
            continue
        for mask in range(1 << 7):
            h = nx.Graph(g)
            h.add_node(7)
            h.add_edges_from((7, j) for j in range(7) if (mask >> j) & 1)
            key = (tuple(sorted(d for _, d in h.degree())), nx.weisfeiler_lehman_graph_hash(h, iterations=3))
            lst = buckets.setdefault(key, [])
            if not any(nx.is_isomorphic(h, o) for o in lst):
                lst.append(h)
                reps.append(h)
    conn = sum(1 for h in reps if nx.is_connected(h))
    if (len(reps), conn) != N_GRAPHS[8]:
        raise RuntimeError(f"graph generation mismatch: {len(reps)} graphs, {conn} connected; expected {N_GRAPHS[8]}")
    from ..jobs import atomic_write_text
    atomic_write_text(GRAPHS8, json.dumps([sorted(h.edges()) for h in reps]))
    return [Graph.make(8, h.edges()) for h in reps]


@primitive("graphs", (1, 2), "Nat [:connected] -> List<Graph>", "𝒢_{0}", r"\mathcal{{G}}_{{{0}}}")
def p_graphs(n, flag=None):
    import networkx as nx
    if n > 8:
        raise ValueError("graphs: available for n <= 8 (atlas n <= 7, generated n = 8)")
    if n == 8:
        gs = _graphs8()
        if flag is not None and str(flag) == ":connected":
            gs = [G for G in gs if p_connected(G)]
        return gs
    out = []
    for g in _atlas():
        if g.number_of_nodes() != n:
            continue
        if flag is not None and str(flag) == ":connected" and not nx.is_connected(g):
            continue
        out.append(Graph.make(n, g.edges()))
    return out


@primitive("trees", 1, "Nat -> List<Graph>", "𝒯_{0}", r"\mathcal{{T}}_{{{0}}}")
def p_trees(n):
    import networkx as nx
    if n == 1:
        return [Graph.make(1, [])]
    return [Graph.make(n, t.edges()) for t in nx.nonisomorphic_trees(n)]


@lru_cache(maxsize=None)
def _vertices(n: int):
    if n <= 6:
        lst = DomainList(polyhedra.enumerate_vertices(n))
        lst.kind = "all"
    elif n in (7, 8):
        lst = DomainList(deza.load_ext(n))
        lst.kind = "reps"
    elif n == 9:
        # PARTIAL: Deza–Indik's 1,221 orbit representatives of m_9 vertices not adjacent to any cut
        lst = DomainList(p for p, _inc, _adj in deza.load_counterexamples())
        lst.kind = "reps"
        lst.complete = False
    else:
        raise ValueError(f"vertices: no data for n={n} (n <= 6 enumerated, 7-8 Deza reps, 9 partial)")
    lst.n = n
    return lst


@primitive("vertices", 1, "Nat -> List<Point>", "V(m_{0})", r"V(m_{{{0}}})")
def p_vertices(n):
    return _vertices(n)


@primitive("cuts", 1, "Nat -> List<Point>", "Cut_{0}", r"\mathrm{{Cut}}_{{{0}}}")
@lru_cache(maxsize=None)
def p_cuts(n):
    return DomainList(p_cut(n, S) for S in p_switchings(n))


@primitive("cone-rays", 1, "Nat -> List<Point>", "R(M_{0})", r"R(M_{{{0}}})")
def p_cone_rays(n):
    if n > 6:
        raise ValueError("cone-rays: enumerated for n <= 6 only")
    return polyhedra.enumerate_cone_rays(n)


# ======================================================================= verification

@primitive("feasible?", 1, "Point -> Bool", "{0}∈m_n", r"{0}\in m_n")
def p_feasible(x):
    return core.is_feasible(x)


@lru_cache(maxsize=200_000)
def _is_vertex(x: Point) -> bool:
    """Exact: feasible and tight set of full rank (certified mod-p rank, exact fallback)."""
    s = core.slacks(x)
    if (s < 0).any():
        return False
    A, _ = core.ineq_matrix(x.n)
    return certified_rank_is(A[np.flatnonzero(s == 0)], dim(x.n))


@primitive("vertex?", 1, "Point -> Bool", "{0}∈V(m_n)", r"{0}\in V(m_n)")
def p_vertex(x):
    return _is_vertex(x)


@primitive("incidence", 1, "Point -> Nat", "Icd({0})", r"\mathrm{{Icd}}({0})")
def p_incidence(x):
    return int(len(core.tight_set(x)))


@primitive("denominator", 1, "Point -> Nat", "den({0})", r"\mathrm{{den}}({0})")
def p_denominator(x):
    return x.D


@primitive("integral?", 1, "Point -> Bool", "{0}∈ℤ", r"{0}\in\mathbb{{Z}}")
def p_integral(x):
    return x.D == 1


@primitive("fully-fractional?", 1, "Point -> Bool", "{0} fully fractional", r"{0}\ \text{{fully fractional}}")
def p_fully_fractional(x):
    return all(0 < v < x.D for v in x.nums)


_P1, _P2 = 2_147_483_629, 2_147_483_587     # primes < 2^31


def _rank_mod_p(M: np.ndarray, p: int) -> int:
    A = np.mod(M.astype(np.int64), p)
    r = 0
    rows, cols = A.shape
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if A[i, c] != 0:
                piv = i
                break
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        inv = pow(int(A[r, c]), p - 2, p)
        A[r] = (A[r] * inv) % p
        for i in range(rows):
            if i != r and A[i, c] != 0:
                A[i] = (A[i] - A[i, c] * A[r]) % p
        r += 1
        if r == rows:
            break
    return r


def certified_rank_is(M_rows: np.ndarray, target: int) -> bool:
    """Exact test rank_Q(M) == target, given rank_Q(M) <= target is known a priori."""
    if M_rows.shape[0] < target:
        return False
    if _rank_mod_p(M_rows, _P1) == target or _rank_mod_p(M_rows, _P2) == target:
        return True                              # rank_Q >= rank_p = target, and rank_Q <= target
    return core.exact_rank(M_rows.tolist()) == target


@primitive("adjacent?", 2, "Point Point -> Bool", "{0}~{1}", r"{0}\sim{1}")
def p_adjacent(x, y):
    """x, y distinct vertices: adjacent iff the common tight set has rank C(n,2)-1."""
    if x == y:
        return False
    A, _ = core.ineq_matrix(x.n)
    T = np.intersect1d(core.tight_set(x), core.tight_set(y))
    return certified_rank_is(A[T], dim(x.n) - 1)


@primitive("perimeter", 2, "Point Nodes -> Rat", "per_{1}({0})", r"\mathrm{{per}}_{{{1}}}({0})")
def p_perimeter(x, T):
    a, b, c = sorted(T)
    return p_entry(x, a, b) + p_entry(x, a, c) + p_entry(x, b, c)


# ======================================================================= partial points

@primitive("lift-partial", 1, "Point -> Partial", "{0}⊕?", r"{0}\oplus ?")
def p_lift_partial(v):
    return Partial.make(v.n + 1, {(i, j): p_entry(v, i, j) for (i, j) in pairs(v.n)})


@primitive("glue-partial", 3, "Point Point Nat -> Partial", "{0}⊕_{2}{1}", r"{0}\oplus_{{{2}}}{1}")
def p_glue(x1, x2, k):
    a, b = x1.n, x2.n
    n = a + b - k
    off = a - k
    known = {}
    for (i, j) in pairs(a):
        known[(i, j)] = p_entry(x1, i, j)
    for (i, j) in pairs(b):
        key = (i + off, j + off)
        v = p_entry(x2, i, j)
        if key in known and known[key] != v:
            raise ValueError("glue: points disagree on the overlap")
        known[key] = v
    return Partial.make(n, known)


@lru_cache(maxsize=50_000)
def _fiber_vertices(P: Partial):
    n = P.n
    known = P.as_dict()
    holes = P.holes()
    hidx = {h: k for k, h in enumerate(holes)}
    rows = []
    for q in core.metric_inequalities(n):
        rhs = Fraction(q.b)
        coef = [Fraction(0)] * len(holes)
        for e, a in enumerate(q.a):
            if not a:
                continue
            pr = pairs(n)[e]
            if pr in hidx:
                coef[hidx[pr]] += a
            else:
                rhs -= a * known[pr]
        if all(c == 0 for c in coef):
            if rhs < 0:
                return ()
            continue
        rows.append([rhs] + [-c for c in coef])
    full = lambda ys: Point.from_fractions(n, [known[p] if p in known else ys[hidx[p]] for p in pairs(n)])
    if not holes:
        return (full([]),)
    import cdd
    import cdd.gmp
    mat = cdd.gmp.matrix_from_array(rows, rep_type=cdd.RepType.INEQUALITY)
    g = cdd.gmp.copy_generators(cdd.gmp.polyhedron_from_matrix(mat))
    if g.lin_set:
        raise RuntimeError("fiber has lineality (should be bounded)")
    out = []
    for r in g.array:
        if r[0] != 1:
            raise RuntimeError("fiber unbounded")
        out.append(full([Fraction(v) for v in r[1:]]))
    return tuple(out)


@primitive("fiber-vertices", 1, "Partial -> List<Point>", "vert(fib({0}))", r"\mathrm{{vert}}(\mathrm{{fib}}({0}))", "G")
def p_fiber_vertices(P):
    return list(_fiber_vertices(P))


@primitive("extend", (1, 2), "Partial [:lexmin] -> Point|#f", "ext_lex({0})", r"\mathrm{{ext}}_{{\mathrm{{lex}}}}({0})")
def p_extend(P, mode=None):
    vs = _fiber_vertices(P)
    if not vs:
        return False
    return min(vs, key=lambda x: x.fractions())


@primitive("pairs-point", 3, "Nat Rat List<(Tuple Rat)> -> Point", "x", "x")
def p_pairs_point(n, default, entries):
    vals = {p: Q(default) for p in pairs(n)}
    for (ij, q) in entries:
        i, j = ij
        vals[(min(i, j), max(i, j))] = Q(q)
    return Point.from_fractions(n, [vals[p] for p in pairs(n)])


@primitive("lit-point", 3, "Nat Nat List<Int> -> Point", "x", "x")
def p_lit_point(n, D, nums):
    return Point.make(n, D, list(nums))
