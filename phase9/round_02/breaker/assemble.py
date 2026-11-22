import random, json, glob
import numpy as np
from lib9b import *
rng = random.Random(7)
d = np.asarray(np.load(str(ROOT/'data/deza/orbits9/den.npy'), mmap_mode='r'))
c = np.load(str(ROOT/'data/deza/orbits9/coords.npy'), mmap_mode='r')
out = []
def add(x, how):
    r = check(x); assert r['vertex'], how
    pp = odd_pp(x.D)
    out.append(dict(n=x.n, D=x.D, nums=list(map(int, x.nums)), kind='unreachable', rule='all-moves-cover',
                    how=how, max_odd_prime_power=max(pp) if pp else 1, bound_2n_3=2 * x.n - 3))
def rowpt(i): return Point.make(9, int(d[i]), c[i].tolist())
walk = {}
for f in sorted(glob.glob('walk_*.json')) + sorted(glob.glob('walk2_*.json')):
    for D, r in json.load(open(f)).items():
        key = (r['n'], int(D))
        if key not in walk:
            r['src'] = f; walk[key] = r
def walkhow(r):
    if 'seed_row' in r:
        par = f"lift^{r['n']-9}(Deza n=9 row {r['seed_row']}, D={r['seedD']})"
    else:
        par = f"lift-to-n={r['n']} of a {r['parent']} vertex from walk_*.json"
    return (f"exact LP vertex of m_{r['n']} maximizing 1000*(sum of tight rows of {par} minus {r['drop']} dropped rows) "
            f"+ random integer perturbation in [-3,3] (face walk, file {r['src']})")
def pick(n, Ds):
    for D in Ds:
        if (n, D) in walk:
            r = walk[(n, D)]; add(Point.make(n, D, r['nums']), walkhow(r))
# n = 10 : face-walk vertices
pick(10, [50, 43, 41, 37, 31, 29, 27, 25, 23, 19])
# n = 10 : plain lift of Deza n=9 D=43 / D=41 rows
for D in (43, 41):
    i = int(np.flatnonzero(d == D)[0]); add(lift(rowpt(i), rng), f"fiber vertex of lift(Deza n=9 row {i}, D={D}) (exact LP, random objective)")
# n = 10 : n=8 unreachable targets glued / lifted (no denominator proof)
U8 = [u for u in json.load(open(ROOT/'results/phase9/unreached_targets.json')) if u['n'] == 8]
U8.sort(key=lambda u: -u['D'])
for u in U8[:2]:
    x = Point.make(8, u['D'], u['nums']); a = 8; k = 6
    perm = list(range(a - k, a)) + list(range(a - k))
    y = None
    for _ in range(20):
        y = glue(x, x, k, rng, perm)
        if y is not None and check(y)['vertex']: break
    add(y, f"fiber vertex of glue(unreached n=8 target id {u['id']}, itself) over 6 shared nodes (copy relabelled so its first 6 nodes = last 6 of the first copy)")
u = U8[2]; x = Point.make(8, u['D'], u['nums'])
add(lift(lift(x, rng), rng), f"fiber vertex of lift(fiber vertex of lift(unreached n=8 target id {u['id']}))")
# n = 11, 12 : face-walk vertices
pick(11, [53, 49, 47, 43, 41, 37, 31, 29])
pick(12, [69, 53, 49, 47, 46, 43, 41, 37])
# n = 15 : glue of a high-prime vertex with itself, and lifts
def selfglue(x, k, how):
    perm = list(range(x.n - k, x.n)) + list(range(x.n - k))
    for _ in range(10):
        y = glue(x, x, k, rng, perm)
        if y is not None and check(y)['vertex']:
            add(y, f"fiber vertex of glue({how}, itself) over {k} shared nodes"); return y
    print('glue failed', how)
i43 = int(np.flatnonzero(d == 43)[1])
selfglue(rowpt(i43), 3, f"Deza n=9 row {i43} D=43")
w53 = walk[(11, 53)]; x53 = Point.make(11, 53, w53['nums'])
selfglue(x53, 7, "the n=11 D=53 face-walk vertex in this file")
w47 = walk[(11, 47)]; x = Point.make(11, 47, w47['nums'])
for _ in range(4): x = lift(x, rng)
add(x, "lift^4 (fiber vertices, random objectives) of the n=11 D=47 face-walk vertex in this file")
w49 = walk[(12, 49)]; x = Point.make(12, 49, w49['nums'])
for _ in range(3): x = lift(x, rng)
add(x, "lift^3 (fiber vertices, random objectives) of the n=12 D=49 face-walk vertex in this file")
# n = 20
selfglue(x53, 2, "the n=11 D=53 face-walk vertex in this file")
i41 = int(np.flatnonzero(d == 41)[0])
y15 = None
x = rowpt(i41)
y = selfglue(x, 1, f"Deza n=9 row {i41} D=41")  # n = 17
for _ in range(3): y = lift(y, rng)
add(y, f"lift^3 (fiber vertices) of glue(Deza n=9 row {i41} D=41, itself) over 1 shared node")
w47b = walk[(12, 47)]; x = Point.make(12, 47, w47b['nums'])
for _ in range(8): x = lift(x, rng)
add(x, "lift^8 (fiber vertices, random objectives) of the n=12 D=47 face-walk vertex in this file")
x = rowpt(i43)
for _ in range(11): x = lift(x, rng)
add(x, f"lift^11 (fiber vertices, random objectives) of Deza n=9 row {i43} D=43")
from collections import Counter
print(len(out), Counter(o['n'] for o in out))
for o in out: print(o['n'], o['D'], o['max_odd_prime_power'], o['bound_2n_3'], o['how'][:90])
json.dump(out, open('candidates.json', 'w'), indent=1)
