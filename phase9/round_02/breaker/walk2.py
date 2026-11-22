import random, time, sys, json, glob
from collections import Counter
from lib9b import *
rng = random.Random(int(sys.argv[1])); n = int(sys.argv[2]); iters = int(sys.argv[3]); minpp = int(sys.argv[4])
seeds = []
for f in glob.glob('walk_*.json'):
    for D, r in json.load(open(f)).items():
        pp = odd_pp(int(D))
        if pp and max(pp) >= minpp and r['n'] <= n:
            seeds.append(r)
A, b = core.ineq_matrix(n)
found = {}; C = Counter(); t = time.time()
for it in range(iters):
    r = rng.choice(seeds); x = Point.make(r['n'], r['D'], r['nums'])
    while x.n < n:
        x = lift(x, rng)
    T = core.tight_set(x)
    S = [q for q in T if rng.random() < rng.choice([0.8, 0.9, 0.95])]
    big = A[S].sum(axis=0) * 1000
    obj = [int(big[e]) + rng.randint(-3, 3) for e in range(len(big))]
    y = free_lp(n, rng, obj)
    C[y.D] += 1
    if y.D not in found and check(y)['vertex']:
        found[y.D] = dict(n=n, D=y.D, nums=list(y.nums), parent=f"n={r['n']} D={r['D']}", drop=len(T) - len(S))
print(sorted(C.items())[-12:], time.time() - t, file=sys.stderr)
json.dump(found, open(f'walk2_{n}_{sys.argv[1]}.json', 'w'))
