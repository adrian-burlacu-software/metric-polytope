#!/usr/bin/env python3
"""Fast locality for metrics with a known symmetry group (exploration tool; scripts/phase9/locality.py is the exact
reference).

Two speed-ups over locality.py:
1. Symmetry. If every permutation in G preserves d, the closure cl_s is G-invariant, so only one s-subset per G-orbit
   is solved and each merge is applied together with all its images.
2. Arithmetic modulo p = 2^31 - 1 (numpy) instead of rationals. The solution space mod p contains the reduction of
   the rational one, so a merge can be missed only if a rank drops mod p, and a false merge needs two different
   rational expressions to agree mod p; both have probability about 1e-9 per test. Values reported from this module
   are therefore "computed mod p"; anything stated as exact must be re-run with locality.py.

locality_fast(n, d, G, smax) -> (L or None, profile) where profile[s] = number of classes of cl_s.
"""
from __future__ import annotations

import itertools

import numpy as np

P_MOD = 2147483647


def forced_equal_mod(M):
    """M: int64 matrix (equations x variables). Groups of variables with identical expressions in the free variables
    of the solution space mod p."""
    M = M % P_MOD
    m, nv = M.shape
    piv, r = [], 0
    for c in range(nv):
        nz = np.flatnonzero(M[r:, c])
        if nz.size == 0:
            continue
        i = r + int(nz[0])
        if i != r:
            M[[r, i]] = M[[i, r]]
        inv = pow(int(M[r, c]), P_MOD - 2, P_MOD)
        M[r] = (M[r] * inv) % P_MOD
        col = M[:, c].copy()
        col[r] = 0
        M = (M - np.outer(col, M[r])) % P_MOD
        piv.append(c)
        r += 1
        if r == m:
            break
    ps = set(piv)
    free = [c for c in range(nv) if c not in ps]
    groups = {}
    for k, c in enumerate(free):
        e = np.zeros(len(free), dtype=np.int64)
        e[k] = 1
        groups.setdefault(e.tobytes(), []).append(c)
    if free:
        sub = (-M[:len(piv)][:, free]) % P_MOD
        for i, c in enumerate(piv):
            groups.setdefault(sub[i].tobytes(), []).append(c)
    else:                                                   # no free variable: only the zero solution (cannot happen
        return []                                           # for a metric, u = 1 is a solution)
    return [g for g in groups.values() if len(g) > 1]


def locality_fast(n, d, G=None, smax=None, smin=4):
    G = G or [list(range(n))]
    P = list(itertools.combinations(range(n), 2))
    idx = {p: i for i, p in enumerate(P)}
    gp = [[idx[(min(g[a], g[b]), max(g[a], g[b]))] for a, b in P] for g in G]      # action on pairs
    par = list(range(len(P)))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    T = [(a, b, m) for a, b in P for m in range(n) if m != a and m != b and d[a][b] == d[a][m] + d[m][b]]
    Tn = [(frozenset((a, b, m)), idx[(a, b)], idx[(min(a, m), max(a, m))], idx[(min(m, b), max(m, b))],
           d[a][b], d[a][m], d[m][b]) for a, b, m in T]
    ncls = len(P)
    profile = {}
    for s in range(smin, (smax or n) + 1):
        seen, subs = set(), []
        for W in itertools.combinations(range(n), s):
            if W in seen:
                continue
            for g in G:
                seen.add(tuple(sorted(g[v] for v in W)))
            Ws = set(W)
            tw = [t[1:] for t in Tn if t[0] <= Ws]
            if tw:
                subs.append(tw)
        last = [None] * len(subs)
        changed = True
        while changed and ncls > 1:
            changed = False
            for k, tw in enumerate(subs):
                sig = tuple(find(t[0]) for t in tw) + tuple(find(t[1]) for t in tw) + tuple(find(t[2]) for t in tw)
                if last[k] == sig:
                    continue
                last[k] = sig
                var, rows, seenr = {}, [], set()
                for pa, pp, pq, da, dp, dq in tw:
                    r = {}
                    for cl, c in ((find(pa), da), (find(pp), -dp), (find(pq), -dq)):
                        r[cl] = r.get(cl, 0) + c
                    r = tuple(sorted((c_, v) for c_, v in r.items() if v))
                    if r and r not in seenr:
                        seenr.add(r)
                        rows.append(r)
                        for c_, _v in r:
                            var.setdefault(c_, len(var))
                if len(var) < 2:
                    continue
                M = np.zeros((len(rows), len(var)), dtype=np.int64)
                for i, r in enumerate(rows):
                    for c_, v in r:
                        M[i, var[c_]] = v
                names = list(var)
                for grp in forced_equal_mod(M):
                    a = names[grp[0]]
                    for j in grp[1:]:
                        b = names[j]
                        for g in gp:
                            ra, rb = find(g[a]), find(g[b])
                            if ra != rb:
                                par[ra] = rb
                                ncls -= 1
                                changed = True
        profile[s] = ncls
        if ncls == 1:
            return s, profile
    return None, profile
