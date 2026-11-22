"""Filter pool points with reach_large.reachable; usage: filt.py SHARD NSHARDS BUDGET -> filt_<shard>.json"""
import sys, json, time, random
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT))
from collections import defaultdict
from metricpoly.core import Point
from metricpoly.reach_large import reachable
sh, ns, bud = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
pool = []
for f in sorted(Path(__file__).resolve().parent.glob('pool_*.json')):
    pool += json.load(open(f))
g = defaultdict(list)
for p in pool:
    g[(p['n'], p['how'][0], p['D'])].append(p)
sel = []
for k in sorted(g):
    sel += g[k][:(2 if k[1] == 'W' else 1)]
sel = sel[sh::ns]
out = []
t0 = time.time()
for p in sel:
    if time.time() - t0 > 250: break
    t = time.time(); v, nodes = reachable(Point.make(p['n'], p['D'], p['nums']), budget=bud)
    p.update(reach=v, nodes=nodes, secs=round(time.time() - t, 1)); out.append(p)
    print(p['n'], p['how'][0], p['D'], v, p['secs'], file=sys.stderr, flush=True)
json.dump(out, open(Path(__file__).resolve().parent / f'filt_{sh}.json', 'w'))
