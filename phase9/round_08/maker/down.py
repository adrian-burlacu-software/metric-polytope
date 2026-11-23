# for m_7 / m_8 vertex orbit reps: odd D, even frame d, graphic?, reached + provenance
import json, sys, itertools
sys.path.insert(0,'scripts/phase9'); sys.path.insert(0,'.')
from metricpoly.dsl.prims import p_vertices
from metricpoly import group
from fractions import Fraction as F
sys.path.insert(0,'phase9/round_08/maker')
from fam1 import is_graph_metric
R=json.load(open('checkpoints/phase9/reached.json'))
n=int(sys.argv[1]); Dset={int(a) for a in sys.argv[2].split(',')}
from collections import Counter
C=Counter()
for p in p_vertices(n):
    if p.D not in Dset: continue
    t={'n':n,'D':p.D,'nums':list(p.nums)}
    from dmet import dmetric
    d,s=dmetric(t)
    key=group.canonical(p).key()
    prov=R.get(key)
    gm = d is not None and is_graph_metric([[F(v) for v in r] for r in d])
    tag=('base' if prov and prov[1]=='base' else (prov[1][0] if prov else 'UNREACHED'))
    C[(p.D, d is not None, gm, tag)]+=1
for k,v in sorted(C.items(), key=str): print(k,v)
