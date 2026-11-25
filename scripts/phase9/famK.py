"""Family K_t^(k): A = cycle C_t (edge a); spokes A_i - B_i (b); cross edges A_i - B_{i+-k} (c); B_i - B_j for
non-consecutive i, j (e), with the weights forced by the three coincidences
    k a = b + c   (A_i, A_{i+k}: along the cycle, or spoke + cross)
    2 c = 2 b + e (A_i, A_{i+2k}: two crosses through B_{i+k}, or spoke + chord + spoke)
    2 e = 2 b + a (B_i, B_{i+1}: two chords, or spoke + edge + spoke)
i.e. (a, b, c, e) = (10, 4k - 1, 6k + 1, 4k + 4). Extreme ray? locality (fast, mod p)?
  python scripts/phase9/famK.py K T1,T2,...  [smax]"""
import sys, time, math
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts/phase9')
import multiprocessing as mp
import numpy as np
import family12 as F
from locality_fast import locality_fast
from family_extend import dihedral


def metric(t, k, w=None):
    a, b, c, e = w or (10, 4 * k - 1, 6 * k + 1, 4 * k + 4)
    E = [(i, (i + 1) % t, a) for i in range(t)] + [(i, t + i, b) for i in range(t)]
    E += [((i + k) % t, t + i, c) for i in range(t)] + [((i - k) % t, t + i, c) for i in range(t)]
    E += [(t + i, t + j, e) for i in range(t) for j in range(i + 1, t) if (j - i) % t not in (1, t - 1)]
    E = [(min(x, y), max(x, y), w_) for x, y, w_ in E]
    return F.metric(2 * t, E), (a, b, c, e)


def job(args):
    t, k, smax = args
    t0 = time.time()
    d, w = metric(t, k)
    genuine = bool(d[0][1] == w[0] and d[0][t] == w[1] and d[k][t] == w[2] and d[t][t + 2] == w[3])
    if not F.is_ray(d):
        return t, k, w, genuine, False, None, None, round(time.time() - t0)
    L, prof = locality_fast(2 * t, d.tolist(), dihedral(t), smax)
    return t, k, w, genuine, True, L, prof, round(time.time() - t0)


if __name__ == "__main__":
    k = int(sys.argv[1]); ts = [int(v) for v in sys.argv[2].split(",")]
    smax = int(sys.argv[3]) if len(sys.argv) > 3 else None
    with mp.get_context("spawn").Pool(min(len(ts), 6)) as pool:
        for t, k, w, gen, ray, L, prof, sec in pool.imap(job, [(t, k, smax) for t in ts]):
            print(f"k = {k} t = {t} n = {2*t} weights {w} edges genuine {gen} ray {ray} L {L} classes per level {prof} ({sec} s)", flush=True)
