"""Round 06 breaker: walk5.py (round 5) re-run WITH the accepted move partial-dup in the reachability test.
PRE-REGISTERED DESIGN (fixed before running; nothing below was changed after seeing results):
- Same chain construction as walk5 (S0 = RL lift chain or RG glue of reached reps, within bound, reachable() True;
  DIM = 1 edge steps, L = 4). Two processes: seed 21 at n = 10 and seed 22 at n = 11 (n chosen by env WALK_N),
  CH = 30 chains, time cap 270 s each (whatever completes is reported; done = False flags the cap).
- Test of each new within-bound orbit S_k (two stages, both FIXED budgets):
  stage 1: reach_large.reachable(budget = 15 s), built-in moves only. True -> T (moves only add reachability).
  stage 2 (stage 1 False or undecided): reach_large.reachable_bu(moves = [partial-dup], budget = 45 s) -> T / F / U.
  Recorded: cls (final), td (stage 1), bu (stage 2).
- 'dist' = steps since the last chain vertex with final cls T. Rates = F / (T + F) per (n, dist) and per D; U reported
  separately.
- The start S0 test also uses reachable() (stage 1) only, as in round 5.
usage: walk6.py SEED CH L TIMECAP [DIM=1] -> walk6_d<DIM>_<seed>.json"""
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

seed, CH, L, cap = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
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
for n in [int(v) for v in os.environ.get('WALK_N', '10,11').split(',')]:
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
                    rec['td'] = v
                    if v is not True:
                        v, _st = reachable_bu(y, PD, app, budget=BUD2)
                        rec['bu'] = v
                    rec['cls'] = {True: 'T', False: 'F', None: 'U'}[v]
                    rec['secs'] = round(time.time() - t, 1)
                    if v is True:
                        dist = 0
            steps.append(rec)
            print(seed, n, c, k, rec['dist'], y.D, rec['cls'], file=sys.stderr, flush=True)
            cur = y
        chains.append(dict(n=n, c=c, start_how=how, start=dict(D=x.D, nums=list(x.nums)), steps=steps))
        json.dump(dict(seed=seed, done=not stop, chains=chains), open(HERE / f'walk6_d{DIM}_{seed}.json', 'w'))
    if stop:
        break
json.dump(dict(seed=seed, done=not stop, chains=chains), open(HERE / f'walk6_d{DIM}_{seed}.json', 'w'))
print('done', seed, round(time.time() - t0), 'stop' if stop else '', file=sys.stderr)
