#!/usr/bin/env python3
"""Structure of the family C_t (scripts/phase9/family_C.py): tight triples by type, the classes of the level-4
closure, and the relations left between them, all up to rotation. Exact (rational) closure.
  python scripts/phase9/family_C_structure.py 13 [a2]
"""
import itertools, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
from family_C import metric  # noqa: E402
from locality import _forced_equal  # noqa: E402


def main():
    t = int(sys.argv[1]); a2 = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    level = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    d = metric(t, a2).tolist()
    n = 2 * t

    def nm(v):
        return ("A%d" % v) if v < t else ("B%d" % (v - t))

    def off(i, j):
        o = (j - i) % t
        return o - t if o > t // 2 else o

    def typ(x, y):
        """Type of a pair up to rotation: (kind, offset), with far offsets shown as F."""
        if x > y:
            x, y = y, x
        if y < t:
            k = abs(off(x, y)); return "AA" + (str(k) if k <= 2 else "F")
        if x >= t:
            k = abs(off(x - t, y - t)); return "BB" + (str(k) if k <= 2 else "F")
        o = off(x, y - t); return "AB" + (("%+d" % o) if abs(o) <= 2 else "F")

    P = list(itertools.combinations(range(n), 2)); idx = {p: i for i, p in enumerate(P)}
    T = [(a, b, m) for a, b in P for m in range(n) if m != a and m != b and d[a][b] == d[a][m] + d[m][b]]
    print(f"t = {t}, n = {n}: {len(T)} tight triples (t(3t - 8) = {t * (3 * t - 8)})")
    ct = Counter()
    for a, b, m in T:
        ct[(typ(a, b), tuple(sorted((typ(a, m), typ(m, b)))))] += 1
    print("tight triples by type: long pair = the two short pairs (count; count / t):")
    for (lo, sh), c in sorted(ct.items()):
        print(f"   {lo} = {sh[0]} + {sh[1]}   x {c}   ({c / t:g} per position)")
    # exact closure at the given level
    par = list(range(len(P)))
    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    subs = []
    for W in itertools.combinations(range(n), level):
        Ws = set(W)
        tw = [(idx[(a, b)], idx[(min(a, m), max(a, m))], idx[(min(m, b), max(m, b))], d[a][b], d[a][m], d[m][b]) for a, b, m in T if a in Ws and b in Ws and m in Ws]
        if tw: subs.append(tw)
    changed = True
    while changed:
        changed = False
        for tw in subs:
            rows, seen, var = [], set(), {}
            for pa, pp, pq, da, dp, dq in tw:
                r = {}
                for cl, c in ((find(pa), da), (find(pp), -dp), (find(pq), -dq)):
                    r[cl] = r.get(cl, 0) + c
                r = {c_: v for c_, v in r.items() if v}
                key = tuple(sorted(r.items()))
                if r and key not in seen:
                    seen.add(key); rows.append(r)
            for r in rows:
                for c_ in r: var.setdefault(c_, len(var))
            if len(var) < 2: continue
            names = list(var)
            for g in _forced_equal([{var[c_]: v for c_, v in r.items()} for r in rows], len(var)):
                for j in g[1:]:
                    ra, rb = find(names[g[0]]), find(names[j])
                    if ra != rb: par[ra] = rb; changed = True
    cls = defaultdict(list)
    for i, p in enumerate(P): cls[find(i)].append(p)
    print(f"\nclasses of cl_{level}: {len(cls)}  ((t^2 + 13t + 2)/2 = {(t * t + 13 * t + 2) // 2})")
    shape = Counter()
    ex = {}
    for c in cls.values():
        key = tuple(sorted(Counter(typ(x, y) for x, y in c).items()))
        shape[key] += 1; ex.setdefault(key, c)
    for key, cnt in sorted(shape.items(), key=lambda kv: -kv[1]):
        e = ex[key]
        print(f"   {cnt} classes of shape {dict(key)}; e.g. " + ", ".join(nm(x) + nm(y) for x, y in e[:6]) + (" ..." if len(e) > 6 else ""))
    rep = {p: find(idx[p]) for p in P}
    # name the classes: by the type and position of a canonical member
    def cname(c):
        mem = sorted(cls[c], key=lambda p: (typ(*p), p))
        x, y = mem[0]
        return f"[{nm(x)}{nm(y)}]"
    rel = Counter(); relex = {}
    for a, b, m in T:
        A_, B_, C_ = rep[(a, b)], rep[(min(a, m), max(a, m))], rep[(min(m, b), max(m, b))]
        if len({A_, B_, C_}) == 1: continue
        key = (typ(a, b), d[a][b], tuple(sorted(((typ(a, m), d[a][m]), (typ(m, b), d[m][b])))), len({A_, B_, C_}))
        rel[key] += 1; relex.setdefault(key, (a, b, m))
    print(f"\nrelations between different classes, by type (count per position):")
    for key, c in sorted(rel.items()):
        a, b, m = relex[key]
        print(f"   {key[1]}*{key[0]} = {key[2][0][1]}*{key[2][0][0]} + {key[2][1][1]}*{key[2][1][0]}   x {c} ({c / t:g}/pos), {key[3]} classes;  e.g. {nm(a)}{nm(b)} via {nm(m)}: {cname(rep[(a,b)])} = {cname(rep[(min(a,m),max(a,m))])} + {cname(rep[(min(m,b),max(m,b))])}")


if __name__ == "__main__":
    main()
