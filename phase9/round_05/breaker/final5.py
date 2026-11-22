"""Re-test points with reach_large.reachable_bu (the judge's n <= 12 search) using user moves loaded from .mpr files.
usage: final5.py IN.json OUT.json BUDGET SHARD NSHARDS [MPR ...]   (IN: list of {n,D,nums,...}; only reach==False rows are used
unless the row has no 'reach' field). Default moves: none beyond the files given."""
import sys, json, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts' / 'phase9'))
from common import interpreter  # noqa
from metricpoly import core
from metricpoly.core import Point
from metricpoly.reach_large import reachable_bu

inp, outp, bud, shard, nsh = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
files = sys.argv[6:]
I, names = interpreter(files)
moves = [(nm, int(I.moves[nm].grow)) for nm in names if nm in I.moves]
print('moves', moves, file=sys.stderr)


def app(name, p):
    try:
        return [o for o in I.apply_move(I.moves[name], [p], as_orbits=True) if core.is_feasible(o)]
    except Exception as e:
        print('apply error', name, e, file=sys.stderr)
        return []


rows = [r for k, r in enumerate(json.load(open(inp))) if k % nsh == shard]
out = []
for r in rows:
    x = Point.make(r['n'], r['D'], r['nums'])
    t = time.time()
    v, st = reachable_bu(x, moves, app, budget=bud)
    r = dict(r, bu=v, bu_secs=round(time.time() - t, 1), bu_moves=[m for m, _ in moves])
    out.append(r)
    json.dump(out, open(outp, 'w')); print(r['n'], r['D'], r['how'][:3] if 'how' in r else '', v, r['bu_secs'], file=sys.stderr, flush=True)
json.dump(out, open(outp, 'w'))
