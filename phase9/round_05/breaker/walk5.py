"""Round 05 breaker: pre-registered walk-distance experiment.
Design (fixed before running): for each seed s in {1,2,3,4} and each n in {10, 11}: CH chains. A chain starts at a
vertex S0 built ONLY from reached pieces (alternating RL = lift chain of one reached n=7/8/9 rep, RG = glue of two
reached reps over an exactly matching K), required within bound AND reachable() == True. Then L face-walk steps
S1..SL, each = a random vertex of a random DIM-dimensional face of m_n through the previous vertex (DIM = 1: an EDGE
step to an adjacent vertex, pushed along the edge's feasible direction); a step that returns the same point, finds no
edge, or lands OUTSIDE the bound is retried (<= 30, then 'stuck'/'outbound'), so chains walk on within-bound vertices.
Every S_k is classified: outbound (odd prime power of D > 2n-3), dup (orbit seen earlier in this process), known
(registry or earlier-round candidates), or tested with reachable(budget) -> T / F / U(ndecided).
'dist' = number of steps since the last chain vertex confirmed True.
DIM = 0: round-4 style walk (maximize 1000 * random 60-96 % of the tight rows + noise).
usage: walk5.py SEED CH L BUDGET TIMECAP [DIM=1] -> walk5_d<DIM>_<seed>.json"""
import sys, json, random, time, itertools
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'round_02' / 'breaker'))
from lib9b import *  # noqa
import numpy as np
from metricpoly.canon_large import canonical_key
from metricpoly.reach_large import reachable
from metricpoly.deza import load_ext

seed, CH, L, bud, cap = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
DIM = int(sys.argv[6]) if len(sys.argv) > 6 else 1
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
for r in ('round_01', 'round_02', 'round_03', 'round_04'):
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


mats = [tomat(t) for t in T]
idx = defaultdict(list)
for ti, t in enumerate(T):
    for k in (5, 6, 7):
        for K in itertools.combinations(range(t.n), k):
            idx[(k, inv(mats[ti], K))].append((ti, K))
gkeys = {nn: [] for nn in (10, 11)}
for kk, v in idx.items():
    tis = {a for a, _ in v}
    if len(tis) < 2:
        continue
    sizes = {T[a].n for a in tis}
    for nn in (10, 11):
        if any(a + b - kk[0] == nn for a in sizes for b in sizes):
            gkeys[nn].append(kk)

seen = set()


def start(n, kind):
    for _ in range(400):
        if kind == 'RL':
            ti = rng.randrange(len(T)); x = T[ti]
            while x.n < n:
                x = lift(x, rng)
            how = f'RL:lift chain of reached n={T[ti].n} D={T[ti].D}'
        else:
            kk = rng.choice(gkeys[n])
            (ta, K), (tb, L_) = rng.sample(idx[kk], 2)
            x0, y0 = T[ta], T[tb]
            if ta == tb or x0.n + y0.n - len(K) != n:
                continue
            s = match(mats[ta], K, mats[tb], L_)
            if s is None:
                continue
            x = glue_pair(x0, y0, K, L_, s)
            how = f'RG:glue of reached n={x0.n} D={x0.D} and n={y0.n} D={y0.D} |K|={len(K)}'
        if x is None or not ok(x) or not check(x)['vertex']:
            continue
        v, _ = reachable(x, budget=bud)
        if v is True:
            seen.add(canonical_key(x))
            return x, how
    return None, None


chains = []
stop = False
for n in (10, 11):
    for c in range(CH):
        if time.time() - t0 > cap:
            stop = True
            break
        x, how = start(n, 'RL' if c % 2 == 0 else 'RG')
        if x is None:
            continue
        steps = []
        dist = 0
        cur = x
        for k in range(1, L + 1):
            if time.time() - t0 > cap:
                stop = True
                break
            nout = 0
            for tr in range(30):
                y, f = walk(cur, DIM)
                if y is None or (tuple(y.nums) == tuple(cur.nums) and y.D == cur.D):
                    continue
                if not ok(y):
                    nout += 1; continue
                break
            if y is None:
                y = cur
            dist += 1
            rec = dict(step=k, dist=dist, n=n, D=y.D, nums=list(y.nums), f=f, outbound_retries=nout)
            if tuple(y.nums) == tuple(cur.nums) and y.D == cur.D:
                rec['cls'] = 'stuck'
            elif not ok(y):
                rec['cls'] = 'outbound'
            else:
                key = canonical_key(y)
                rec['key'] = key
                if key in seen:
                    rec['cls'] = 'dup'
                elif key in known:
                    rec['cls'] = 'known'; seen.add(key)
                else:
                    seen.add(key)
                    t = time.time()
                    v, nodes = reachable(y, budget=bud)
                    rec['cls'] = {True: 'T', False: 'F', None: 'U'}[v]
                    rec['secs'] = round(time.time() - t, 1)
                    if v is True:
                        dist = 0
            steps.append(rec)
            print(seed, n, c, k, rec['dist'], y.D, rec['cls'], file=sys.stderr, flush=True)
            cur = y
        chains.append(dict(n=n, c=c, start_how=how, start=dict(D=x.D, nums=list(x.nums)), steps=steps))
        json.dump(dict(seed=seed, done=not stop, chains=chains), open(HERE / f'walk5_d{DIM}_{seed}.json', 'w'))
    if stop:
        break
json.dump(dict(seed=seed, done=not stop, chains=chains), open(HERE / f'walk5_d{DIM}_{seed}.json', 'w'))
print('done', seed, round(time.time() - t0), 'stop' if stop else '', file=sys.stderr)
