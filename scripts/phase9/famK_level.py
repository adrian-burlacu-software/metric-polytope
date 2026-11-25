"""Is the level-s closure of K_t^(k) total? One level per process (fast, mod p). python famK_level.py k t s1,s2,..."""
import sys, time
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts/phase9')
import multiprocessing as mp
from famK import metric
from locality_fast import locality_fast
from family_extend import dihedral

def job(a):
    k, t, s = a
    t0 = time.time()
    d, w = metric(t, k)
    L, prof = locality_fast(2 * t, d.tolist(), dihedral(t), smax=s, smin=s)
    return k, t, s, prof, round(time.time() - t0)

if __name__ == "__main__":
    k, t = int(sys.argv[1]), int(sys.argv[2]); ss = [int(v) for v in sys.argv[3].split(",")]
    with mp.get_context("spawn").Pool(len(ss)) as pool:
        for k, t, s, prof, sec in pool.imap_unordered(job, [(k, t, s) for s in ss]):
            print(f"k = {k} t = {t} n = {2*t}: classes of cl_{s} = {prof[s]} ({sec} s)", flush=True)
