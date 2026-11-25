"""Locality of G_t(a, b, c, e) for one weight vector and a range of t (fast, mod p)."""
import sys, time
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts/phase9')
import multiprocessing as mp
from famG import job

def run(args):
    t0 = time.time()
    r = job(args)
    return r, round(time.time() - t0)

if __name__ == "__main__":
    w = tuple(int(v) for v in sys.argv[1].split(","))
    ts = [int(v) for v in sys.argv[2].split(",")]
    with mp.get_context("spawn").Pool(len(ts)) as pool:
        for (args, L, prof), sec in pool.imap(run, [(t,) + w for t in ts]):
            print("t", args[0], "n", 2 * args[0], "weights", args[1:], "L", L, "classes per level", prof, f"({sec} s)", flush=True)
