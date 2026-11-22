import json, sys, time, random
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
from metricpoly.dsl.prims import _fiber_vertices, p_lift_partial
from metricpoly.core import Point
R = list(json.load(open('checkpoints/phase9/reached.json')))
rng = random.Random(4)
for n in (6, 7, 8):
    ks = rng.sample([k for k in R if k.startswith(f'{n}|')], 5)
    for k in ks:
        _, D, nums = k.split('|'); p = Point.make(n, int(D), [int(v) for v in nums.split(',')])
        t = time.time(); V = _fiber_vertices(p_lift_partial(p)); print(n, len(V), round(time.time() - t, 2), flush=True)
