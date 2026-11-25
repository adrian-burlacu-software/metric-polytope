"""Family F_t(a, b, c): A = cycle C_t with edge a; B_i joined to A_i (weight b) and to the two vertices of the
cycle antipodal to A_i (weight c). Scan small weights: extreme ray? locality (fast, mod p)?"""
import sys, itertools, time
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts/phase9')
import multiprocessing as mp
import numpy as np
import family12 as F
from locality_fast import locality_fast


def group(t):
    n = 2 * t
    rot = [(i + 1) % t for i in range(t)] + [t + (i + 1) % t for i in range(t)]
    ref = [(-i) % t for i in range(t)] + [t + (-i) % t for i in range(t)]
    G, fr = {tuple(range(n))}, [tuple(range(n))]
    while fr:
        nx = []
        for h in fr:
            for g in (rot, ref):
                c = tuple(g[h[i]] for i in range(n))
                if c not in G:
                    G.add(c); nx.append(c)
        fr = nx
    return [list(g) for g in G]


def job(args):
    t, a, b, c, offs = args
    n = 2 * t
    E = [(i, (i + 1) % t, a) for i in range(t)] + [(i, t + i, b) for i in range(t)]
    for o in offs:
        E += [((i + o) % t, t + i, c) for i in range(t)] + [((i - o) % t, t + i, c) for i in range(t)]
    E = [(min(x, y), max(x, y), w) for x, y, w in E]
    d = F.metric(n, E)
    if not F.is_ray(d):
        return args, None, None
    L, prof = locality_fast(n, d.tolist(), group(t))
    return args, L, prof


if __name__ == "__main__":
    t = int(sys.argv[1]); R = int(sys.argv[2])
    offs = [(t - 1) // 2] if len(sys.argv) < 4 else [int(v) for v in sys.argv[3].split(",")]
    items = [(t, a, b, c, tuple(offs)) for a in range(1, R + 1) for b in range(1, R + 1) for c in range(1, R + 1)
             if np.gcd.reduce([a, b, c]) == 1]
    t0 = time.time(); best = []
    with mp.get_context("spawn").Pool(14) as pool:
        for args, L, prof in pool.imap_unordered(job, items, chunksize=4):
            if L is not None:
                best.append((L, args[1:4], prof))
    best.sort(key=lambda r: (-r[0], r[1]))
    from collections import Counter
    print("t", t, "offsets", offs, "rays", len(best), "locality", dict(sorted(Counter(b[0] for b in best).items())), f"({time.time()-t0:.0f} s)")
    for L, abc, prof in best[:6]:
        print("  L", L, "(a,b,c) =", abc, "classes per level", prof)
