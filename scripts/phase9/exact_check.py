"""Exact (rational) locality of the record rays found with the fast mod-p code.
  K_7^(2) on 14 points; the best dihedral two-orbit ray on 18 points; K_11^(2) on 22 points (optional, slow)."""
import json, sys, time
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts/phase9')
import multiprocessing as mp
from locality import locality
from metricpoly.jobs import atomic_write_json

def job(a):
    name, d = a
    t0 = time.time()
    return name, len(d), locality(len(d), d), round(time.time() - t0)

if __name__ == "__main__":
    from famK import metric
    j = json.load(open('results/phase9/sym_search.json'))
    items = [("K_7^(2), weights (10,7,13,12)", metric(7, 2)[0].tolist())]
    b = j['fixed0_orbits2_t9_mirror0_1_fast']['best'][0]
    items.append((f"dihedral two-orbit ray on 18 points (fast L = {b['L']})", b['d']))
    b = j['fixed1_orbits2_t7_mirror0_1_fast']['best'][0]
    items.append((f"centre + two orbits of 7, 15 points (fast L = {b['L']})", b['d']))
    if len(sys.argv) > 1:
        items.append(("K_11^(2) on 22 points", metric(11, 2)[0].tolist()))
    out = {}
    with mp.get_context('spawn').Pool(len(items)) as pool:
        for name, n, L, sec in pool.imap_unordered(job, items):
            print(f"{name}: n = {n}, exact L = {L} ({sec} s)", flush=True)
            out[name] = {"n": n, "L_exact": L, "seconds": sec, "d": dict(items)[name]}
            atomic_write_json(__import__('pathlib').Path('results/phase9/exact_check.json'), out)
