"""Attack maker proposals 01 dup-recentre, 02 dup-midshift on random vertices n = 4..7 (exact): feasibility of outputs,
restriction to the first n nodes, vertex counts, and G-equivariance (orbit set of outputs of x vs of g.x, g random)."""
import sys, random, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'scripts' / 'phase9'))
import numpy as np
from common import interpreter
from metricpoly import core, group
from metricpoly.core import Point
from metricpoly.dsl import prims
from metricpoly.deza import load_ext
from metricpoly.canon_large import canonical_key
rng = random.Random(606); nrng = np.random.default_rng(606)
files = [str(HERE.parent / 'maker' / f) for f in ('01_dup_recentre.mpr', '02_dup_midshift.mpr')]
I, names = interpreter(files)
print('moves', names)
pts = []
for n in (4, 5, 6):
    V = list(prims.p_vertices(n)); pts += rng.sample(V, min(6, len(V)))
pts += rng.sample(list(load_ext(7)), 8)
res = {}
for nm in [m for m in names if m in I.moves]:
    bad_feas = bad_res = bad_eq = nv = tot = 0
    for x in pts:
        out = I.apply_move(I.moves[nm], [x])
        n = x.n
        for o in out:
            tot += 1
            if not core.is_feasible(o):
                bad_feas += 1
            sub = Point.make(n, o.D, [o.nums[k] for k, (a, b) in enumerate(core.pairs(n + 1)) if b < n]) if hasattr(core, 'pairs') else None
            if (np.array(sub.nums, dtype=object) * x.D != np.array(x.nums, dtype=object) * sub.D).any():
                bad_res += 1
            if prims.p_vertex(o):
                nv += 1
        if n <= 7:
            p, s = group.random_element(n, nrng)
            gx = group.apply(n, p, s, x)
            k1 = {canonical_key(o) for o in out}
            k2 = {canonical_key(o) for o in I.apply_move(I.moves[nm], [gx])}
            if k1 != k2:
                bad_eq += 1
    res[nm] = dict(inputs=len(pts), outputs=tot, infeasible=bad_feas, restriction_bad=bad_res, vertices=nv, equivariance_fail=bad_eq)
    print(nm, res[nm], flush=True)
json.dump(res, open(HERE / 'attack6.json', 'w'), indent=1)
