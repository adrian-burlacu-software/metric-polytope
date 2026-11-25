"""Locality of one local-pattern family (family_hunt.py notation) on cycles of several sizes (fast, mod p).
  python scripts/phase9/cand_family.py "2,4" "8,4" "5,3,5,7,7" 7 T1,T2,... [smax]"""
import sys, time
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts/phase9')
import multiprocessing as mp
import family12 as F
from family_hunt import build, is_metric
from locality_fast import locality_fast


def rotations(t, n):
    return [[(i + s) % t for i in range(t)] + [t + (i + s) % t for i in range(t)] + list(range(2 * t, n)) for s in range(t)]


def job(a):
    fA, fB, g, far, t, smax = a
    t0 = time.time()
    d = build(t, fA, fB, g, far)
    if not is_metric(d):
        return t, "not a metric", None, None, 0
    if not F.is_ray(d):
        return t, "not a ray", None, None, 0
    L, prof = locality_fast(2 * t, d.tolist(), rotations(t, 2 * t), smax)
    return t, "ray", L, prof, round(time.time() - t0)


if __name__ == "__main__":
    fA, fB, g = [tuple(int(v) for v in s.split(",")) for s in sys.argv[1:4]]
    far = int(sys.argv[4]); ts = [int(v) for v in sys.argv[5].split(",")]
    smax = int(sys.argv[6]) if len(sys.argv) > 6 else None
    with mp.get_context("spawn").Pool(min(len(ts), 8)) as pool:
        for t, st, L, prof, sec in pool.imap(job, [(fA, fB, g, far, t, smax) for t in ts]):
            print(f"t = {t} n = {2*t}: {st}" + (f", L = {L}, classes per level {prof} ({sec} s)" if st == "ray" else ""), flush=True)
