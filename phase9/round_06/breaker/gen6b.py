"""Round 06 candidate generator, variant b: only 3 | D with D >= 12 is tested (NOT part of the pre-registered rate experiment).
Pool = earlier-round breaker candidates (rounds 3-5) at n = 10, 11 within the bound. Edge walk (walk6.walk, DIM = 1)
from a random pool point; each new within-bound orbit with 3 | D (others with prob 0.25) is tested: reachable(15 s),
then reachable_bu([partial-dup], 45 s). F points join the pool and the walk continues from them; on T restart.
usage: gen6.py SEED TIMECAP -> gen6_<seed>.json"""
import os, sys, json, random, time, itertools
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'round_02' / 'breaker'))
from lib9b import *  # noqa
import numpy as np
from metricpoly.canon_large import canonical_key
from metricpoly.reach_large import reachable
from metricpoly.deza import load_ext
from metricpoly.reach_large import reachable_bu
sys.path.insert(0, str(HERE.parents[1].parent / 'scripts' / 'phase9'))
from common import interpreter  # noqa
I, _ = interpreter([])
PD = [('partial-dup', int(I.moves['partial-dup'].grow))]


def app(name, p):
    try:
        return [o for o in I.apply_move(I.moves[name], [p], as_orbits=True) if core.is_feasible(o)]
    except Exception as e:
        print('apply error', name, e, file=sys.stderr)
        return []

seed, cap = int(sys.argv[1]), float(sys.argv[2])
DIM = 1
bud, BUD2 = 15.0, 45.0
DIM = int(sys.argv[5]) if len(sys.argv) > 5 else 1
rng = random.Random(1000 + seed)
t0 = time.time()
B = json.load(open(ROOT / 'results/phase9/baseline.json'))['reached_targets']
ext = {7: load_ext(7), 8: load_ext(8)}
C9 = np.load(ROOT / 'data/deza/orbits9/coords.npy', mmap_mode='r')
D9 = np.load(ROOT / 'data/deza/orbits9/den.npy', mmap_mode='r')
T = []
for k in B:
    n, i = map(int, k.split(':'))
    T.append(ext[n][i - 1] if n in ext else Point.make(9, int(D9[i]), [int(v) for v in C9[i]]))
known = set(json.load(open(ROOT / 'results/phase9/large_orbits.json')))
for r in ('round_01', 'round_02', 'round_03', 'round_04', 'round_05'):
    try:
        for c in json.load(open(HERE.parents[1] / r / 'breaker/candidates.json')):
            if c['n'] >= 10:
                known.add(canonical_key(Point.make(c['n'], c['D'], c['nums'])))
    except Exception as e:
        print('skip', r, e, file=sys.stderr)


def ok(y):
    pp = odd_pp(y.D)
    return y.D > 1 and (not pp or max(pp) <= 2 * y.n - 3)


def inv(M, K):
    return tuple(sorted(tuple(sorted(M[i][j] for j in K if j != i)) for i in K))


def match(Mx, K, My, L_):
    K, L_ = list(K), list(L_)
    out = {}

    def bt(a):
        if a == len(K):
            return True
        i = K[a]
        for l in L_:
            if l in out.values():
                continue
            if all(My[l][out[K[b]]] == Mx[i][K[b]] for b in range(a)):
                out[i] = l
                if bt(a + 1):
                    return True
                del out[i]
        return False
    return dict(out) if bt(0) else None


def glue_pair(x, y, K, L_, s):
    Mx, My = tomat(x), tomat(y)
    A_only = [i for i in range(x.n) if i not in K]
    B_only = [j for j in range(y.n) if j not in L_]
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


def walk(x, d=1):
    """Random vertex of a random d-dimensional face through x: shuffle the tight rows, keep a row when it does not
    push the rank above N - d (rows in the current span are always kept, so S is the full face's tight set);
    maximize 10^6 * sum(rows in S) + small random noise (picks a vertex of that face)."""
    Am, _ = core.ineq_matrix(x.n)
    if d == 0:                                   # round-4 style face walk: random fraction f of the tight rows
        f = rng.choice([0.6, 0.75, 0.85, 0.92, 0.96])
        S = [r for r in core.tight_set(x) if rng.random() < f]
        big = Am[S].sum(axis=0) * 1000
        return free_lp(x.n, rng, [int(big[e]) + rng.randint(-3, 3) for e in range(len(big))]), f
    N = Am.shape[1]
    tr = list(core.tight_set(x)); rng.shuffle(tr)
    Q = np.zeros((0, N)); S = []
    for r in tr:
        v = Am[r].astype(float)
        res = v - Q.T @ (Q @ v) if len(Q) else v
        nr = np.linalg.norm(res)
        if nr < 1e-9:
            S.append(r)
        elif len(Q) < N - d:
            Q = np.vstack([Q, res / nr]); S.append(r)
    big = Am[S].sum(axis=0) * 10 ** 6
    if d == 1:                                   # edge: push along the feasible direction of the edge, if any
        v = np.array([rng.gauss(0, 1) for _ in range(N)])
        v = v - Q.T @ (Q @ v)
        sv = Am[tr].astype(float) @ v
        if np.all(sv <= 1e-9):
            pass
        elif np.all(sv >= -1e-9):
            v = -v
        else:
            return None, d                       # S does not span an edge of m_n at this degenerate vertex
        v = v / np.abs(v).max()
        return free_lp(x.n, rng, [int(big[e]) + int(round(1000 * v[e])) for e in range(N)]), d
    return free_lp(x.n, rng, [int(big[e]) + rng.randint(-3, 3) for e in range(len(big))]), d



pool = []
for r in ('round_03', 'round_04', 'round_05'):
    for c in json.load(open(HERE.parents[1] / r / 'breaker/candidates.json')):
        if c['n'] in (10, 11):
            p = Point.make(c['n'], c['D'], c['nums'])
            if ok(p):
                pool.append(p)
print('pool', len(pool), file=sys.stderr)
seen = set(); out = []
cur = rng.choice(pool)
while time.time() - t0 < cap:
    y = None
    for tr in range(20):
        y, _ = walk(cur, 1)
        if y is not None and ok(y) and not (tuple(y.nums) == tuple(cur.nums) and y.D == cur.D):
            break
        y = None
    if y is None:
        cur = rng.choice(pool); continue
    if y.D < 12 or y.D % 3:
        cur = y; continue
    key = canonical_key(y)
    if key in seen or key in known:
        cur = y; continue
    seen.add(key)
    t = time.time()
    v, _n = reachable(y, budget=15.0)
    td = v
    if v is not True:
        v, _st = reachable_bu(y, PD, app, budget=45.0)
    rec = dict(n=y.n, D=y.D, nums=list(y.nums), key=key, td=td, bu=v, secs=round(time.time() - t, 1))
    out.append(rec)
    json.dump(out, open(HERE / f'gen6b_{seed}.json', 'w'))
    print(y.n, y.D, td, v, rec['secs'], file=sys.stderr, flush=True)
    if v is False:
        pool.append(y); cur = y
    elif v is True:
        cur = rng.choice(pool)
    else:
        cur = y
print('done', len(out), file=sys.stderr)
