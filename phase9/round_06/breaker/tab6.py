"""Tables for round 06: part A (round-5 walks replayed with partial-dup) and part B (fresh walk6 seeds 21, 22)."""
import json, glob
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
R5 = HERE.parents[1] / 'round_05' / 'breaker'


def tables(chains_iter, label):
    nd = defaultdict(lambda: [0, 0, 0]); dd = defaultdict(lambda: [0, 0, 0])
    for steps in chains_iter:
        dist = 0
        for s in steps:
            dist += 1
            c = s['cls']
            if c not in 'TFU' or c in ('stuck',):
                continue
            if c == 'T' and s.get('_rec', True):
                pass
            i = 'TFU'.index(c)
            nd[(s['n'], min(dist, 3))][i] += 1
            dd[(s['n'], s['D'])][i] += 1
            if c == 'T':
                dist = 0
    print(f'--- {label}: (n, dist) -> F/(T+F)  [U]')
    for k in sorted(nd):
        t, f, u = nd[k]; print(k, f'{f}/{t+f} = {100*f/max(1,t+f):.1f}%', f'U={u}')
    print(f'--- {label}: (n, D) -> F/(T+F) [U]')
    for k in sorted(dd):
        t, f, u = dd[k]; print(k, f'{f}/{t+f}', f'U={u}')


new = {}
for f in glob.glob(str(HERE / 'retest6_*.json')):
    for r in json.load(open(f)):
        new[(r['file'], r['chain'], r['step'])] = {True: 'T', False: 'F', None: 'U'}[r['bu']]


def partA(old=False):
    for f in sorted(glob.glob(str(R5 / 'walk5_d*_*.json'))):
        for ci, ch in enumerate(json.load(open(f))['chains']):
            st = []
            for s in ch['steps']:
                s = dict(s)
                if not old and s['cls'] in 'FU' and s['cls'] in ('F', 'U'):
                    s['cls'] = new.get((Path(f).name, ci, s['step']), 'MISSING')
                st.append(s)
            yield st


print('retested', len(new), 'missing', sum(1 for ch in partA() for s in ch if s['cls'] == 'MISSING'))
tables(partA(old=True), 'A0 round-5 walks, no moves (round 5 result)')
tables(partA(), 'A round-5 walks replayed with partial-dup')


def partB():
    for f in sorted(glob.glob(str(HERE / 'walk6_d*_*.json'))):
        d = json.load(open(f)); print(Path(f).name, 'done', d['done'], 'chains', len(d['chains']))
        for ch in d['chains']:
            yield ch['steps']


tables(partB(), 'B fresh walks (seeds 21 n=10, 22 n=11), two-stage test with partial-dup')
