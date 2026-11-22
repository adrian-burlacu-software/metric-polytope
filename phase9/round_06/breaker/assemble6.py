"""Collect F (reachable_bu with partial-dup = False) points from walk6 / gen6, dedupe, prioritize 3 | D, cap 30."""
import json, glob
from pathlib import Path
HERE = Path(__file__).resolve().parent
rows, keys = [], set()
for f in sorted(glob.glob(str(HERE / 'walk6_d*_*.json'))):
    for ch in json.load(open(f))['chains']:
        for s in ch['steps']:
            if s['cls'] == 'F' and s['key'] not in keys:
                keys.add(s['key'])
                rows.append(dict(n=s['n'], D=s['D'], nums=s['nums'], src='walk6',
                                 how=f"walk6 edge walk {s['step']} step(s) from reachable start ({ch['start_how']}); reachable() False, reachable_bu([partial-dup], 45 s) False"))
for f in sorted(glob.glob(str(HERE / 'gen6_*.json')) + glob.glob(str(HERE / 'gen6b_*.json'))):
    for s in json.load(open(f)):
        if s['bu'] is False and s['key'] not in keys:
            keys.add(s['key'])
            rows.append(dict(n=s['n'], D=s['D'], nums=s['nums'], src='gen6',
                             how="gen6 edge walk from earlier unreachable candidates; reachable() False, reachable_bu([partial-dup], 45 s) False"))
rows.sort(key=lambda r: (r['D'] % 3 != 0, r['src'] != 'walk6', r['n'], r['D']))
m3 = [r for r in rows if r['D'] % 3 == 0]
other = [r for r in rows if r['D'] % 3]
# up to 30: all multiples of 3 first, then spread over other (n, D)
sel = m3[:24]
seenND = {}
for r in other:
    if len(sel) >= 30:
        break
    if seenND.get((r['n'], r['D']), 0) < 2:
        seenND[(r['n'], r['D'])] = seenND.get((r['n'], r['D']), 0) + 1; sel.append(r)
print('pool F', len(rows), 'mult3', len(m3), 'selected', len(sel))
json.dump([dict(n=r['n'], D=r['D'], nums=r['nums']) for r in sel], open(HERE / 'chk6_norule.json', 'w'))
json.dump([dict(n=r['n'], D=r['D'], nums=r['nums'], kind='unreachable', rule='all-moves-cover', how=r['how']) for r in sel],
          open(HERE / 'sel6.json', 'w'))
for r in sel:
    print(r['n'], r['D'], r['src'])
