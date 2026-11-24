# for each odd-D n=9 target (even frame d): which k-node restrictions of d are extreme rays of MET_k (tight-triangle rank = C(k,2)-1)?
import json, sys, itertools
from collections import Counter
import numpy as np
def rank_tight(d, T):
    pairs = list(itertools.combinations(T, 2)); idx = {p: i for i, p in enumerate(pairs)}
    rows = []
    for i, j, k in itertools.combinations(T, 3):
        e = [(i, j), (i, k), (j, k)]
        for t in range(3):
            if d[e[t][0]][e[t][1]] == sum(d[e[s][0]][e[s][1]] for s in range(3) if s != t):
                r = [0] * len(pairs); r[idx[e[t]]] = 1
                for s in range(3):
                    if s != t: r[idx[e[s]]] = -1
                rows.append(r)
    if not rows: return 0, len(pairs)
    return np.linalg.matrix_rank(np.array(rows, dtype=float)), len(pairs)
