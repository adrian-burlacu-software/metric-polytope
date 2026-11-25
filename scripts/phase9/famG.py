"""Family G_t(a, b, c, e): A = cycle C_t (edge a); spokes A_i - B_i (b); cross edges A_i - B_{i+-2} (c);
B_i - B_j for non-consecutive i, j (e). Scan integer weights: extreme ray? locality (fast, mod p)."""
import sys, itertools, time, math
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts/phase9')
import multiprocessing as mp
from collections import Counter
import numpy as np
import family12 as F
from locality_fast import locality_fast
from famF import group

_G = {}


def job(args):
    t, a, b, c, e = args
    n = 2 * t
    E = [(i, (i + 1) % t, a) for i in range(t)] + [(i, t + i, b) for i in range(t)]
    E += [((i + 2) % t, t + i, c) for i in range(t)] + [((i - 2) % t, t + i, c) for i in range(t)]
    E += [(t + i, t + j, e) for i in range(t) for j in range(i + 1, t) if (j - i) % t not in (1, t - 1)]
    E = [(min(x, y), max(x, y), w) for x, y, w in E]
    d = F.metric(n, E)
    # all four kinds of edges must be genuine (not shortcut by other paths), otherwise it is another member
    if d[0][1] != a or d[0][t] != b or d[2][t] != c or d[t][t + 2] != e:
        return args, None, None
    if not F.is_ray(d):
        return args, None, None
    if t not in _G:
        _G[t] = group(t)
    L, prof = locality_fast(n, d.tolist(), _G[t])
    return args, L, prof


if __name__ == "__main__":
    t = int(sys.argv[1]); R = int(sys.argv[2])
    items = [(t, a, b, c, e) for a in range(1, R + 1) for b in range(1, R + 1) for c in range(1, R + 1)
             for e in range(1, R + 1) if math.gcd(math.gcd(a, b), math.gcd(c, e)) == 1]
    t0 = time.time(); best = []
    with mp.get_context("spawn").Pool(int(sys.argv[3]) if len(sys.argv) > 3 else 14) as pool:
        for args, L, prof in pool.imap_unordered(job, items, chunksize=64):
            if L is not None:
                best.append((L, args[1:], prof))
    best.sort(key=lambda r: (-r[0], r[1]))
    print("t", t, "weights up to", R, "rays", len(best), "locality", dict(sorted(Counter(b[0] for b in best).items())), f"({time.time()-t0:.0f} s)", flush=True)
    for L, w, prof in best[:8]:
        print("  L", L, "(a,b,c,e) =", w, "classes per level", prof, flush=True)
