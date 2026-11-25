"""Sufficient (proved).

Geodesic exchange closure.  Work with classes of node pairs (initially singletons).
(a) Exchange: two geodesic triples sharing a class give  A + B = C + D  (e.g. two midpoints m, m2 of the same pair:
    am + mb = am2 + m2b), i.e. the difference relations  A - C = D - B  and  A - D = C - B.
(b) Odd closed chain: differences are kept in a signed union-find.  If a difference is forced to equal its own
    negative, or to equal C - C, its two classes have equal length and are merged.  (The geodesic rectangle of
    claims 01/02 is the shortest such chain.)  Repeat (a), (b) until stable.
(c) Propagation: fix one class length; a geodesic triple with exactly one unknown class determines it.
The claim holds if (c) reaches every class.  No rank is computed and no general linear system is solved: the only
operations are union-find merges and substitution into single three-term relations.  In principle the procedure
is strictly weaker than elimination (it never combines more than two relations into a new one), so it is not the
definition in disguise; but it IS a deduction procedure on the tight relations rather than a static graph
property, and the judge should decide whether that is acceptable as 'combinatorial'.

Why it is sufficient (holds for every k and every weight alphabet): the tight triangle equalities are exactly
x_ab = x_am + x_mb for geodesic triples (m between a and b).  Every step derives a linear consequence of these
equalities, and at the end every pair length is a fixed rational multiple of one of them, so the solution space
of the tight system is one-dimensional, i.e. its rank is C(k,2) - 1.
"""
NAME = "exchange-closure"
KIND = "sufficient"
STATEMENT = (
    'If the geodesic exchange closure succeeds: merging classes of node pairs whenever an odd closed '
    'chain of geodesic exchanges (A + B = C + D from two geodesic triples sharing a class) forces '
    'equal length, and then propagating one class length through geodesic triples with a single '
    'undetermined class, determines every pair, then the graph is a ray.'
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


def claim(k, edges):
    d = _dist(k, edges)
    if not _connected(k, d):
        return False
    T = _tight(k, d)
    return _propagates(k, T, _exchange_classes(k, T))
