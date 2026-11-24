# Track A, round 16: covers of n = 9 targets (given D) by scaled graph metrics, in any switching frame.
# For each target: all subsets T (|T| >= 3) with x^S|T = (a/D) d_G for some switching S (canonical: S excludes min(T)).
# Then pairs (A, B) with A u B = V and |A n B| = ov. Output summary of cover types.
import json, sys, itertools, time
from collections import Counter, defaultdict
UT = json.load(open('results/phase9/unreached_targets.json'))

def gm_check(N, T, D):
    # N: dict (a,b)->numerator (in frame). return (m, E, degs) or None
    vals = list(N.values()); m = min(vals)
    if m == 0: return None
    if any(v % m for v in vals): return None
    A = {e: v // m for e, v in N.items()}
    adj = {a: [] for a in T}
    for (a, b), v in A.items():
        if v == 1: adj[a].append(b); adj[b].append(a)
    for s in T:
        dist = {s: 0}; fr = [s]
        while fr:
            nf = []
            for u in fr:
                for w in adj[u]:
                    if w not in dist: dist[w] = dist[u] + 1; nf.append(w)
            fr = nf
        for t in T:
            if t > s and dist.get(t) != A[(s, t)]: return None
    E = tuple(sorted(e for e in A if A[e] == 1))
    degs = tuple(sorted(len(adj[a]) for a in T))
    return (m, E, degs)

def goods(X, n, D, kmin=3):
    out = defaultdict(list)
    for k in range(kmin, n):
        for T in itertools.combinations(range(n), k):
            pairs = list(itertools.combinations(T, 2))
            for Sm in range(1 << (k - 1)):
                Ss = {T[i + 1] for i in range(k - 1) if Sm >> i & 1}
                N = {(a, b): (D - X[a][b]) if ((a in Ss) != (b in Ss)) else X[a][b] for a, b in pairs}
                g = gm_check(N, T, D)
                if g: out[T].append((frozenset(Ss), g))
    return out

def load(n, Ds):
    res = []
    for t in UT:
        if t['n'] == n and t['D'] in Ds:
            it = iter(t['nums']); X = [[0] * n for _ in range(n)]
            for i in range(n):
                for j in range(i + 1, n): X[i][j] = X[j][i] = next(it)
            res.append((t['id'], t['D'], X))
    return res

if __name__ == '__main__':
    n = int(sys.argv[1]); Ds = {int(a) for a in sys.argv[2].split(',')}; lim = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
    out = []
    t0 = time.time()
    for tid, D, X in load(n, Ds)[:lim]:
        g = goods(X, n, D)
        rec = {'id': tid, 'D': D, 'goods': [[list(T), [[sorted(S), m, len(E), list(dg), [list(e) for e in E]] for S, (m, E, dg) in L]] for T, L in g.items()]}
        out.append(rec)
        mx = max((len(T) for T in g), default=0)
        print(tid, D, 'nsub', len(g), 'max', mx, Counter(len(T) for T in g), round(time.time() - t0, 1), flush=True)
    json.dump(out, open('phase9/round_16/maker/A_work/goods_n%d_%s.json' % (n, sys.argv[2].replace(',', '_')), 'w'))
