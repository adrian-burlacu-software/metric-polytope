"""Necessary (proved, classical).  For a split {A, B} of the nodes the Bandelt-Dress isolation index is
alpha = 1/2 min over a, a2 in A and b, b2 in B (repetitions allowed) of
        max(d_ab + d_a2b2, d_ab2 + d_a2b, d_aa2 + d_bb2) - d_aa2 - d_bb2.
If alpha > 0 then d - alpha * cut(A, B) is still a metric (Bandelt and Dress 1992), so d is a sum of two
non-proportional metrics (d is positive on all pairs, a cut is not) and is not extreme.  Hence a ray has
alpha = 0 for every split.  In particular no node of degree 1.  Cost: 2^(k-1) splits, each O(k^4).
"""
NAME = "split-prime"
KIND = "necessary"
STATEMENT = (
    'A ray has no split {A, B} of its node set with positive isolation index: for every split there '
    'are a, a2 in A and b, b2 in B (repetitions allowed) with d_aa2 + d_bb2 >= max(d_ab + d_a2b2, '
    'd_ab2 + d_a2b).'
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


def _split_prime(k, d):
    """No split {A, B} of the node set has positive Bandelt-Dress isolation index."""
    for mask in range(1, 1 << (k - 1)):
        A = [i for i in range(k) if mask >> i & 1]
        B = [i for i in range(k) if not mask >> i & 1]
        if not any(max(d[a][b] + d[a2][b2], d[a][b2] + d[a2][b], d[a][a2] + d[b][b2]) == d[a][a2] + d[b][b2]
                   for a in A for a2 in A if a <= a2 for b in B for b2 in B if b <= b2):
            return False
    return True


def claim(k, edges):
    d = _dist(k, edges)
    if not _connected(k, d):
        return False
    return _split_prime(k, d)
