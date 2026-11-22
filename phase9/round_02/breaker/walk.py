import random, time, sys, json
import numpy as np
from collections import Counter
from lib9b import *
rng = random.Random(int(sys.argv[1])); n = int(sys.argv[2]); iters = int(sys.argv[3])
d = np.load(str(ROOT/'data/deza/orbits9/den.npy'), mmap_mode='r'); c = np.load(str(ROOT/'data/deza/orbits9/coords.npy'), mmap_mode='r')
dd = np.asarray(d)
seeds = [int(i) for D in (43, 41, 37, 31, 29, 27, 25, 23) for i in np.flatnonzero(dd == D)[:3]]
A, b = core.ineq_matrix(n)
found = {}; C = Counter(); t = time.time()
for it in range(iters):
    i = rng.choice(seeds); x = Point.make(9, int(dd[i]), c[i].tolist())
    while x.n < n:
        x = lift(x, rng)
    T = core.tight_set(x)
    S = [r for r in T if rng.random() < rng.choice([0.75, 0.85, 0.92, 0.96])]
    big = A[S].sum(axis=0) * 1000
    obj = [int(big[e]) + rng.randint(-3, 3) for e in range(len(big))]
    y = free_lp(n, rng, obj)
    pp = odd_pp(y.D); C[y.D] += 1
    if pp and max(pp) > 2 * n - 3 and not any(p in (43, 41, 37, 31, 29, 27, 25, 23) and y.D % p == 0 and p == x.D for p in pp):
        pass
    if y.D not in found and check(y)['vertex']:
        found[y.D] = dict(n=n, D=y.D, nums=list(y.nums), seed_row=i, seedD=int(dd[i]), drop=len(T) - len(S))
print(sorted(C.items()), time.time() - t, file=sys.stderr)
json.dump(found, open(f'walk_{n}_{sys.argv[1]}.json', 'w'))
