"""Necessary (proved): conjunction of four proved necessary conditions: 2-connected (a cut node makes d a sum of two
metrics, one per side), split-prime (05), geodesic exchange connected (06), exchange quotient connected (07).
"""
NAME = "combined-necessary"
KIND = "necessary"
STATEMENT = (
    'A ray on at least 3 nodes is 2-connected, has no split with positive isolation index, has its '
    'edges connected by geodesic exchanges with enough exchanges, and has a connected exchange '
    'quotient with at least (classes - 1) relations.'
)

INF = 10 ** 9


def _dist(k, edges):
    d = [[INF] * k for _ in range(k)]
    for i in range(k):
        d[i][i] = 0
    for a, b, w in edges:
        if w < d[a][b]:
            d[a][b] = d[b][a] = w
    for m in range(k):
        dm = d[m]
        for i in range(k):
            dim, di = d[i][m], d[i]
            for j in range(k):
                if dim + dm[j] < di[j]:
                    di[j] = dim + dm[j]
    return d


def _pr(a, b):
    return (a, b) if a < b else (b, a)


def _pairs(k):
    return [(a, b) for a in range(k) for b in range(a + 1, k)]


def _connected(k, d):
    return all(d[a][b] < INF for a, b in _pairs(k))


def _tight(k, d):
    """Geodesic triples (a, b, m): m lies strictly between a and b."""
    return [(a, b, m) for a in range(k) for b in range(a + 1, k) for m in range(k)
            if m != a and m != b and d[a][b] == d[a][m] + d[m][b]]


class _UF:
    def __init__(self, items=()):
        self.p = {x: x for x in items}

    def f(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def u(self, x, y):
        self.p[self.f(x)] = self.f(y)


def _class_eqs(T, uf):
    """Distinct class relations S = P + Q, one per geodesic triple."""
    out = set()
    for a, b, m in T:
        p, q = sorted((uf.f(_pr(a, m)), uf.f(_pr(m, b))))
        out.add((uf.f(_pr(a, b)), p, q))
    return sorted(out)


def _propagates(k, T, uf):
    """True if, from the length of one class, every class length follows by repeatedly using a geodesic
    triple (long = short1 + short2) in which exactly one class is still unknown."""
    from fractions import Fraction
    classes = {uf.f(p) for p in _pairs(k)}
    eqs = []
    for S, P, Q in _class_eqs(T, uf):
        co = {}
        for r, c in ((S, 1), (P, -1), (Q, -1)):
            co[r] = co.get(r, 0) + c
        co = {r: c for r, c in co.items() if c}
        if co:
            eqs.append(co)
    for seed in classes:
        val = {seed: Fraction(1)}
        changed = True
        while changed:
            changed = False
            for co in eqs:
                unk = [r for r in co if r not in val]
                if len(unk) == 1:
                    val[unk[0]] = -sum(c * val[r] for r, c in co.items() if r != unk[0]) / co[unk[0]]
                    changed = True
        if len(val) == len(classes):
            return True
    return False


def _exchange_classes(k, T):
    """Classes of node pairs forced to have equal length.
    Two geodesic triples that share a class give a relation  A + B = C + D  between classes; read it as
    A - C = D - B and A - D = C - B.  Differences are kept in a signed union-find; when a difference is forced
    to equal its own negative (an odd closed chain of exchanges), or to equal a difference C - C, the two
    classes are merged.  Repeat until nothing changes."""
    uf = _UF(_pairs(k))
    while True:
        eqs = _class_eqs(T, uf)
        par, sg = {}, {}

        def find(x):
            par.setdefault(x, x)
            sg.setdefault(x, 1)
            path = []
            while par[x] != x:
                path.append(x)
                x = par[x]
            s = 1
            for y in reversed(path):
                s *= sg[y]
                sg[y] = s
                par[y] = x
            return x, (sg[path[0]] if path else 1)

        def node(p, q):
            return ((p, q), 1) if p < q else ((q, p), -1)

        def equate(p, q, r, s):          # x_p - x_q = x_r - x_s ; True if two classes were merged
            if p == q and r == s:
                return False
            if p == q:
                uf.u(r, s)
                return True
            if r == s:
                uf.u(p, q)
                return True
            (n1, s1), (n2, s2) = node(p, q), node(r, s)
            (r1, t1), (r2, t2) = find(n1), find(n2)
            rel = s1 * t1 * s2 * t2
            if r1 == r2:
                if rel == -1:
                    uf.u(p, q)
                    return True
                return False
            par[r1] = r2
            sg[r1] = rel
            return False

        def rel22(A, B, C, D):           # x_A + x_B = x_C + x_D
            return equate(A, C, D, B) or equate(A, D, C, B)

        merged = False
        for i in range(len(eqs)):
            S1, P1, Q1 = eqs[i]
            for j in range(i + 1, len(eqs)):
                S2, P2, Q2 = eqs[j]
                if S1 == S2 and rel22(P1, Q1, P2, Q2):
                    merged = True
                    break
                for x1, y1 in ((P1, Q1), (Q1, P1)):
                    for x2, y2 in ((P2, Q2), (Q2, P2)):
                        if not merged and x1 == x2 and rel22(S1, y2, S2, y1):
                            merged = True
                if merged:
                    break
            if merged:
                break
        if not merged:
            return uf


def _quotient_ok(k, T, uf):
    """After merging pairs into exchange classes: every class occurs in a non-trivial class relation, the
    relations connect all classes, and there are at least (number of classes - 1) distinct relations."""
    classes = {uf.f(p) for p in _pairs(k)}
    if len(classes) == 1:
        return True
    g = _UF(classes)
    seen, n = set(), 0
    for S, P, Q in _class_eqs(T, uf):
        co = {}
        for r, c in ((S, 1), (P, -1), (Q, -1)):
            co[r] = co.get(r, 0) + c
        sup = [r for r, c in co.items() if c]
        if not sup:
            continue
        n += 1
        seen.update(sup)
        for r in sup[1:]:
            g.u(sup[0], r)
    return seen == classes and len({g.f(c) for c in classes}) == 1 and n >= len(classes) - 1


def _split_prime(k, d):
    """No split {A, B} of the node set has positive Bandelt-Dress isolation index."""
    for mask in range(1, 1 << (k - 1)):
        A = [i for i in range(k) if mask >> i & 1]
        B = [i for i in range(k) if not mask >> i & 1]
        if not any(max(d[a][b] + d[a2][b2], d[a][b2] + d[a2][b], d[a][a2] + d[b][b2]) == d[a][a2] + d[b][b2]
                   for a in A for a2 in A if a <= a2 for b in B for b2 in B if b <= b2):
            return False
    return True


def _geodesic_exchange_ok(k, edges, d):
    """Edge level: list all geodesics (as edge sets) of every pair; two geodesics P, Q of the same pair give the
    exchange set P xor Q.  Require: every edge lies in some exchange set; the exchange sets connect all edges;
    and sum over pairs of (number of geodesics - 1) >= number of edges - 1."""
    adj = [[] for _ in range(k)]
    for a, b, w in edges:
        adj[a].append((b, w))
        adj[b].append((a, w))
    E = [_pr(a, b) for a, b, w in edges]
    uf = _UF(E)
    covered, count = set(), 0
    for a in range(k):
        for b in range(a + 1, k):
            geos, stack = [], [(a, ())]
            while stack:
                v, path = stack.pop()
                if v == b:
                    geos.append(frozenset(path))
                    continue
                for u, w in adj[v]:
                    if w + d[u][b] == d[v][b]:
                        stack.append((u, path + (_pr(v, u),)))
            count += len(geos) - 1
            for P in geos[1:]:
                s = list(P ^ geos[0])
                covered.update(s)
                for e in s[1:]:
                    uf.u(s[0], e)
    return len(covered) == len(E) and len({uf.f(e) for e in E}) == 1 and count >= len(E) - 1


def _biconnected(k, edges):
    adj = [set() for _ in range(k)]
    for a, b, w in edges:
        adj[a].add(b)
        adj[b].add(a)
    for rem in [None] + list(range(k)):
        nodes = [v for v in range(k) if v != rem]
        seen, st = {nodes[0]}, [nodes[0]]
        while st:
            v = st.pop()
            for u in adj[v]:
                if u != rem and u not in seen:
                    seen.add(u)
                    st.append(u)
        if len(seen) != len(nodes):
            return False
    return True


def claim(k, edges):
    d = _dist(k, edges)
    if not _connected(k, d):
        return False
    if k < 3:
        return True
    if not _biconnected(k, edges):
        return False
    T = _tight(k, d)
    if not _quotient_ok(k, T, _exchange_classes(k, T)):
        return False
    return _geodesic_exchange_ok(k, edges, d) and _split_prime(k, d)
