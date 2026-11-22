"""Round 04 breaker: vertices of m_10 / m_11 built ONLY from REACHED pieces (reached n = 7 / 8 / 9 Deza reps of
results/phase9/baseline.json reached_targets), then filtered by reach_large.reachable.
Constructions:
  RG = glue two different reached reps over an exactly matching sub-configuration K (fiber LP vertex);
  RL = lift chain of one reached rep;
  RW = face walk from an RG/RL vertex (maximize 1000 * random 85-99 % of its tight rows + noise, over all of m_n);
  RM = "mix": LP over m_n with objective = sum of random halves of the tight rows of TWO RG/RL vertices.
Every produced vertex (within the bound: odd prime powers of D <= 2n-3) is deduplicated by canon_large and tested
with reachable(budget) unless its orbit is in the registry / round-3 candidates.
usage: gen4.py SEED SECONDS BUDGET -> gen4_<seed>.json (all tested points with reach result)"""
import sys, json, random, time, itertools
from collections import defaultdict, Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'round_02' / 'breaker'))
from lib9b import *  # noqa
import numpy as np
from metricpoly.canon_large import canonical_key
from metricpoly.reach_large import reachable
from metricpoly.deza import load_ext

seed, secs, bud = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
rng = random.Random(seed)
B = json.load(open(ROOT / 'results/phase9/baseline.json'))['reached_targets']
ext = {7: load_ext(7), 8: load_ext(8)}
C9 = np.load(ROOT / 'data/deza/orbits9/coords.npy', mmap_mode='r')
D9 = np.load(ROOT / 'data/deza/orbits9/den.npy', mmap_mode='r')
T = []
for k in B:
    n, i = map(int, k.split(':'))
    if n in ext:
        T.append(ext[n][i - 1])
    else:
        T.append(Point.make(9, int(D9[i]), [int(v) for v in C9[i]]))
known = set(json.load(open(ROOT / 'results/phase9/large_orbits.json')))
for c in json.load(open(HERE.parents[1] / 'round_03/breaker/candidates.json')):
    known.add(canonical_key(Point.make(c['n'], c['D'], c['nums'])))


def ok(y):
    pp = odd_pp(y.D)
    return y.D > 1 and (not pp or max(pp) <= 2 * y.n - 3)


def inv(M, K):
    return tuple(sorted(tuple(sorted(M[i][j] for j in K if j != i)) for i in K))


def match(Mx, K, My, L):
    K, L = list(K), list(L)
    out = {}

    def bt(a):
        if a == len(K):
            return True
        i = K[a]
        for l in L:
            if l in out.values():
                continue
            if all(My[l][out[K[b]]] == Mx[i][K[b]] for b in range(a)):
                out[i] = l
                if bt(a + 1):
                    return True
                del out[i]
        return False
    return dict(out) if bt(0) else None


def glue_pair(x, y, K, L, s):
    Mx, My = tomat(x), tomat(y)
    A_only = [i for i in range(x.n) if i not in K]
    B_only = [j for j in range(y.n) if j not in L]
    order = A_only + list(K)
    n = x.n + len(B_only)
    lab_y = {s[k]: len(A_only) + t for t, k in enumerate(K)}
    for t, j in enumerate(B_only):
        lab_y[j] = x.n + t
    N = [[None] * n for _ in range(n)]
    for a, i in enumerate(order):
        for b, j in enumerate(order):
            N[a][b] = Mx[i][j]
    for i in range(y.n):
        for j in range(y.n):
            N[lab_y[i]][lab_y[j]] = My[i][j]
    holes = [(a, b) for a in range(len(A_only)) for b in range(x.n, n)]
    R = fiber_lp(N, holes, rng)
    return None if R is None else frommat(R)


def tight_obj(x, frac):
    Am, _ = core.ineq_matrix(x.n)
    S = [r for r in core.tight_set(x) if rng.random() < frac]
    return Am[S].sum(axis=0) * 1000


def walk(x):
    big = tight_obj(x, rng.choice([0.6, 0.75, 0.85, 0.92, 0.96]))
    return free_lp(x.n, rng, [int(big[e]) + rng.randint(-3, 3) for e in range(len(big))])


def mix(x, y):
    o = tight_obj(x, 0.5) + tight_obj(y, 0.5)
    return free_lp(x.n, rng, [int(o[e]) + rng.randint(-3, 3) for e in range(len(o))])


idx = defaultdict(list)
mats = [tomat(t) for t in T]
for ti, t in enumerate(T):
    for k in (5, 6, 7):
        for K in itertools.combinations(range(t.n), k):
            idx[(k, inv(mats[ti], K))].append((ti, K))
keys = [k for k, v in idx.items() if len({a for a, _ in v}) >= 2]
print('reached seeds', len(T), 'match buckets', len(keys), file=sys.stderr)

base = defaultdict(list)          # n -> RG/RL vertices (any D, used as walk starts)
out, seen = [], set()
cnt = Counter()
t0 = time.time()


def add(y, how):
    if y is None:
        return
    if not check(y)['vertex']:
        cnt['nonvertex'] += 1
        return
    if how[:2] in ('RG', 'RL'):
        base[y.n].append((y, how))
    elif how[:2] == 'RW' and how.count('walk') < 6:
        base[y.n].append((y, how))
    if not ok(y):
        cnt['outbound'] += 1
        return
    key = canonical_key(y)
    if key in seen:
        cnt['dup'] += 1
        return
    seen.add(key)
    if key in known:
        cnt['known'] += 1
        return
    t = time.time()
    v, nodes = reachable(y, budget=bud)
    rec = dict(n=y.n, D=y.D, nums=list(y.nums), how=how, key=key, reach=v, nodes=nodes,
               secs=round(time.time() - t, 1))
    out.append(rec)
    cnt[(how[:2], v)] += 1
    print(y.n, how[:2], y.D, v, rec['secs'], file=sys.stderr, flush=True)


while time.time() - t0 < secs:
    r = rng.random()
    if r < 0.05 or not base[10]:
        ti = rng.randrange(len(T)); x = T[ti]
        target = rng.choice([10, 10, 11])
        while x.n < target:
            x = lift(x, rng)
        add(x, f'RL:lift chain of reached n={T[ti].n} D={T[ti].D} to n={target}')
    elif r < 0.2:
        kk = keys[rng.randrange(len(keys))]
        (ta, K), (tb, L) = rng.sample(idx[kk], 2)
        x, y = T[ta], T[tb]
        n = x.n + y.n - len(K)
        if ta == tb or n not in (10, 11):
            continue
        s = match(mats[ta], K, mats[tb], L)
        if s is None:
            continue
        add(glue_pair(x, y, K, L, s), f'RG:glue of reached n={x.n} D={x.D} and n={y.n} D={y.D} over |K|={len(K)}')
    elif r < 0.9:
        n = rng.choice([nn for nn in (10, 11) if base[nn]])
        x, h = rng.choice(base[n])
        add(walk(x), ('RW:face walk from ' + h)[:200] if h.startswith('RW') else f'RW:face walk from {h[:70]}')
    else:
        n = rng.choice([nn for nn in (10, 11) if len(base[nn]) >= 2])  if len(base[11]) >= 2 else 10
        if len(base[n]) < 2:
            continue
        (x, h1), (y, h2) = rng.sample(base[n], 2)
        add(mix(x, y), f'RM:mix of [{h1[:45]}] and [{h2[:45]}]')
print(dict(cnt), len(out), file=sys.stderr)
json.dump(out, open(HERE / f'gen4_{seed}.json', 'w'))
