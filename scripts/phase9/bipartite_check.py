"""Check of the corollary on bipartite graphs (paper, after Theorem 3), on random connected bipartite graphs:

    d_G extreme  <=>  one class of the Lomonosov-Sebo oppositeness relation  <=>  L(d_G) = 4.

Extremality is decided by the exact rank of the tight system (sympy), the oppositeness classes by the distance
characterisation of [LS93, Prop. 4], and L by locality.py with smax = 4.
Output: results/phase9/bipartite_check.json
"""
import itertools
import json
import random
import sys

import sympy

sys.path.insert(0, '.'); sys.path.insert(0, 'scripts/phase9')
from locality import locality


def distances(n, edges):
    INF = 10 ** 6
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for a, b in edges:
        d[a][b] = d[b][a] = 1
    for m in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][m] + d[m][j] < d[i][j]:
                    d[i][j] = d[i][m] + d[m][j]
    return d if max(map(max, d)) < INF else None


def is_extreme(n, d):
    pairs = {p: i for i, p in enumerate(itertools.combinations(range(n), 2))}
    key = lambda a, b: pairs[(a, b) if a < b else (b, a)]
    rows = []
    for a, b in pairs:
        for m in range(n):
            if m != a and m != b and d[a][b] == d[a][m] + d[m][b]:
                r = [0] * len(pairs)
                r[key(a, b)] += 1; r[key(a, m)] -= 1; r[key(m, b)] -= 1
                rows.append(r)
    return bool(rows) and sympy.Matrix(rows).rank() == len(pairs) - 1


def opposite_classes(n, d, edges):
    parent = list(range(len(edges)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, (a, b) in enumerate(edges):
        for j in range(i):
            for c, e in (edges[j], edges[j][::-1]):
                if d[a][c] == d[b][e] and d[a][e] == d[b][c] and d[a][c] != d[a][e]:
                    parent[find(i)] = find(j)
    return len({find(i) for i in range(len(edges))})


def main():
    rng = random.Random(20261126)
    stats = {}
    bad = []
    for n in range(5, 11):
        tried = ext = 0
        target = 120 if n <= 8 else 60
        while tried < target:
            k = rng.randint(2, n - 2)
            p = rng.choice([0.5, 0.65, 0.8, 0.9])
            edges = [(a, b) for a in range(k) for b in range(k, n) if rng.random() < p]
            d = distances(n, edges)
            if d is None:
                continue
            tried += 1
            e = is_extreme(n, d)
            c = opposite_classes(n, d, edges)
            L = locality(n, d, 4)
            ext += e
            if not (e == (c == 1) == (L == 4)):
                bad.append({"n": n, "edges": edges, "extreme": e, "classes": c, "L4": L})
        stats[n] = {"graphs": tried, "extreme": ext}
        print(f"n = {n}: {tried} connected bipartite graphs, {ext} extreme, disagreements so far: {len(bad)}", flush=True)
    json.dump({"stats": stats, "disagreements": bad}, open("results/phase9/bipartite_check.json", "w"), indent=1)
    print("disagreements:", len(bad))


if __name__ == "__main__":
    main()
