"""Necessary (proved).  A solution x of the tight system is determined by its values on the edges (a pair's length is
the sum along any geodesic), and the only constraints on the edge values are x(P) = x(Q) for two geodesics P, Q of
the same pair; such a constraint involves exactly the edges of P xor Q.  If an edge is in no exchange set it is
free; if the exchange sets split the edges into two or more blocks, each block can be scaled separately; if there
are fewer than (edges - 1) constraints in a generating set the solution space has dimension >= 2.  In each case d
is not a ray (for graphs with at least 2 edges).  Enumerates geodesics: fine for small k, exponential in the worst
case.
"""
NAME = "geodesic-exchange-connected"
KIND = "necessary"
STATEMENT = (
    'In a ray every edge lies in the symmetric difference of two geodesics joining the same pair of '
    'nodes, these symmetric differences connect all edges into one block, and the sum over node '
    'pairs of (number of geodesics - 1) is at least (number of edges - 1).'
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


def claim(k, edges):
    d = _dist(k, edges)
    if not _connected(k, d):
        return False
    if len(edges) < 2:
        return True
    return _geodesic_exchange_ok(k, edges, d)
