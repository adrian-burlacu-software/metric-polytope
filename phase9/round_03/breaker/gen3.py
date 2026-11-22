"""Round 03 breaker: within-bound vertices of m_10 / m_11 built from unreached n = 8 / 9 targets.
Constructions: L = lift chain, G = glue of two different targets over an exactly matching sub-configuration,
W = walk (face perturbation) from an L/G vertex. Filter: odd prime powers <= 2n-3. Output pool_<seed>.json.
usage: gen3.py SEED SECONDS"""
import sys, json, random, time, itertools
from collections import defaultdict
from fractions import Fraction
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2] / 'round_02' / 'breaker'))
from lib9b import *  # noqa

seed, secs = int(sys.argv[1]), float(sys.argv[2])
rng = random.Random(seed)
U = json.load(open(ROOT / 'results/phase9/unreached_targets.json'))
T = [Point.make(u['n'], u['D'], u['nums']) for u in U]


def ok(y):
    pp = odd_pp(y.D)
    return y.D > 1 and (not pp or max(pp) <= 2 * y.n - 3)


def inv(M, K):
    return tuple(sorted(tuple(sorted(M[i][j] for j in K if j != i)) for i in K))


def match(Mx, K, My, L):
    """bijection s: K -> L with My[s i][s j] == Mx[i][j]; backtracking."""
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
    """x on nodes 0..a-1, y; K subset of x nodes matched to L (y nodes) by s. Build full matrix, random fiber."""
    Mx, My = tomat(x), tomat(y)
    A_only = [i for i in range(x.n) if i not in K]
    B_only = [j for j in range(y.n) if j not in L]
    order = A_only + list(K)        # new labels: A_only, K, B_only
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


def walk(x):
    Am, _ = core.ineq_matrix(x.n)
    Tt = core.tight_set(x)
    S = [r for r in Tt if rng.random() < rng.choice([0.85, 0.92, 0.96])]
    big = Am[S].sum(axis=0) * 1000
    return free_lp(x.n, rng, [int(big[e]) + rng.randint(-3, 3) for e in range(len(big))])


# index k-subset restrictions of targets (k = 6, 7, 8) by invariant + D
idx = defaultdict(list)
mats = [tomat(t) for t in T]
for ti, t in enumerate(T):
    for k in (6, 7, 8):
        if k >= t.n:
            continue
        for K in itertools.combinations(range(t.n), k):
            idx[(k, inv(mats[ti], K))].append((ti, K))
keys = [k for k, v in idx.items() if len({a for a, _ in v}) >= 2]
print('match buckets', len(keys), file=sys.stderr)

pool, seen = [], set()
t0 = time.time()
cnt = defaultdict(int)


def add(y, how):
    if y is None or not ok(y):
        return False
    h = (y.n, y.D, tuple(sorted(y.nums)))
    if h in seen:
        return False
    if not check(y)['vertex']:
        cnt['nonvertex'] += 1
        return False
    seen.add(h)
    pool.append(dict(n=y.n, D=y.D, nums=list(y.nums), how=how))
    cnt[how.split(':')[0]] += 1
    return True


while time.time() - t0 < secs:
    r = rng.random()
    if r < 0.25:                                          # L: lift chain
        ti = rng.randrange(len(T)); x = T[ti]
        target = rng.choice([10, 10, 11])
        while x.n < target:
            x = lift(x, rng)
        add(x, f'L:lift chain of unreached n={T[ti].n} target D={T[ti].D} to n={target}')
    elif r < 0.8:                                         # G: glue two different targets
        kk = keys[rng.randrange(len(keys))]
        (ta, K), (tb, L) = rng.sample(idx[kk], 2)
        if ta == tb:
            continue
        x, y = T[ta], T[tb]
        n = x.n + y.n - len(K)
        if n > 11 or n < 10:
            continue
        s = match(mats[ta], K, mats[tb], L)
        if s is None:
            continue
        z = glue_pair(x, y, K, L, s)
        add(z, f'G:glue of unreached targets n={x.n} D={x.D} and n={y.n} D={y.D} over |K|={len(K)}')
    elif pool:                                            # W: walk from a pool vertex
        p = rng.choice(pool)
        if p['how'].startswith('W'):
            continue
        y = walk(Point.make(p['n'], p['D'], p['nums']))
        add(y, f'W:face walk from {p["how"][:60]}')
print(dict(cnt), len(pool), file=sys.stderr)
json.dump(pool, open(Path(__file__).resolve().parent / f'pool_{seed}.json', 'w'))
