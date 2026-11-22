"""Round 06 part A: replay of round 5's seeded walks (walk5_d*_*.json, seeds 1,2,3,4,11,12,13,14 unchanged) WITH
partial-dup. Pre-registered: steps with round-5 cls T stay T (partial-dup only adds reachability). Every step with cls
F or U is re-tested with reach_large.reachable_bu(moves=[partial-dup], budget = 45 s), fixed. Output: retest6_<shard>.json.
'dist' is then recomputed per chain from the new classes (tab6.py).
usage: retest6.py SHARD NSHARDS"""
import sys, json, glob, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'scripts' / 'phase9'))
from common import interpreter  # noqa
from metricpoly import core
from metricpoly.core import Point
from metricpoly.reach_large import reachable_bu
I, _ = interpreter([])
PD = [('partial-dup', int(I.moves['partial-dup'].grow))]


def app(name, p):
    try:
        return [o for o in I.apply_move(I.moves[name], [p], as_orbits=True) if core.is_feasible(o)]
    except Exception as e:
        print('apply error', e, file=sys.stderr); return []


shard, nsh = int(sys.argv[1]), int(sys.argv[2])
rows = []
for f in sorted(glob.glob(str(ROOT / 'phase9/round_05/breaker/walk5_d*_*.json'))):
    for ci, ch in enumerate(json.load(open(f))['chains']):
        for s in ch['steps']:
            if s['cls'] in ('F', 'U'):
                rows.append(dict(file=Path(f).name, chain=ci, step=s['step'], n=s['n'], D=s['D'], nums=s['nums'], old=s['cls']))
rows = [r for k, r in enumerate(rows) if k % nsh == shard]
out = []
for r in rows:
    t = time.time()
    v, st = reachable_bu(Point.make(r['n'], r['D'], r['nums']), PD, app, budget=45.0)
    r['bu'] = v; r['secs'] = round(time.time() - t, 1); out.append(r)
    json.dump(out, open(HERE / f'retest6_{shard}.json', 'w'))
    print(r['n'], r['D'], r['old'], v, r['secs'], file=sys.stderr, flush=True)
print('done', file=sys.stderr)
