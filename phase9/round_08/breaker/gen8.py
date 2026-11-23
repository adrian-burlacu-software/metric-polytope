"""Round 8 breaker: cheap n = 10 / 11 vertices containing a CONFIRMED unreachable n = 9 vertex (round 7 judge).
Constructions per seed x (n = 9):
  twin  : zero-copy of node i (x_{i,new} = 0, x_{k,new} = x_{ik}); exact vertex of MET_{n+1} (trivial extension);
  pd/dm/rl: outputs of the accepted moves partial-dup, dup-midshift, radial-lowend on x that are exact vertices.
Each new point: exact vertex check, canon_large key (dedupe against results/phase9/large_orbits.json, read-only),
then the judge's n <= 12 search reach_large.reachable_bu with ALL accepted moves (state.json), budget BUD s.
usage: gen8.py OUT.json BUD SEED_START SEED_END [n11]"""
import json, sys, time, random
from pathlib import Path
H = Path(__file__).resolve().parent
ROOT = H.parents[2]
sys.path.insert(0, str(ROOT / "scripts/phase9"))
sys.path.insert(0, str(ROOT))
from common import interpreter  # noqa
from metricpoly import core
from metricpoly.core import Point
from metricpoly.reach_large import reachable_bu, matrix
from metricpoly.canon_large import canonical_key

out_path, BUD, a, b = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
N11 = len(sys.argv) > 5 and sys.argv[5] == "n11"
NOTWIN = len(sys.argv) > 5 and sys.argv[5] == "notwin"
I, _ = interpreter([])
st = json.loads((ROOT / "checkpoints/phase9/state.json").read_text())
moves = [(m, int(g)) for m, g in st["moves"].items() if m in I.moves]
print("moves", moves, file=sys.stderr)
reg = json.loads((ROOT / "results/phase9/large_orbits.json").read_text())


def app(name, p):
    try:
        return [o for o in I.apply_move(I.moves[name], [p], as_orbits=True) if core.is_feasible(o)]
    except Exception:
        return []


def twin(x, i):
    M = matrix(x)
    n = x.n
    col = [int(M[i, k]) if k != i else 0 for k in range(n)]
    nums = []
    for p in range(n + 1):
        for q in range(p + 1, n + 1):
            nums.append(col[p] if q == n else int(M[p, q]))
    return Point.make(n + 1, x.D, nums)


r7 = json.loads((ROOT / "results/phase9/round_07.json").read_text())["candidates"]
seeds = [Point.make(c["point"]["n"], c["point"]["D"], c["point"]["nums"]) for c in r7
         if c.get("status", "").startswith("CONFIRMED")]
seeds = sorted(seeds, key=lambda p: p.D)[a:b]
rng = random.Random(8)
out, seen = [], set(reg)
for si, x in enumerate(seeds):
    cands = [] if NOTWIN else [("twin", twin(x, i)) for i in range(x.n)]
    for m, _ in moves:
        outs = app(m, x)
        rng.shuffle(outs)
        cands += [(m, o) for o in outs[:40]]
    if N11:   # one more step: twin of a twin-or-move output (n = 11)
        cands = [(t + "+twin", twin(o, 0)) for t, o in cands[:3]] + [(t + "+twin", twin(o, o.n - 1)) for t, o in cands[x.n:x.n + 6]]
    ntest = 0
    for how, y in cands:
        if ntest >= (2 if N11 else 2):
            break
        if not core.is_vertex(y)[0]:
            continue
        k = canonical_key(y)
        if k in seen:
            continue
        seen.add(k)
        t = time.time()
        v, s = reachable_bu(y, moves, app, budget=BUD)
        ntest += 1
        r = {"n": y.n, "D": y.D, "nums": list(y.nums), "key": k, "seed_D": x.D, "seed_nums": list(x.nums),
             "how": how, "bu": v, "secs": round(time.time() - t, 1)}
        out.append(r)
        print(si, x.D, y.n, y.D, how, v, r["secs"], file=sys.stderr, flush=True)
        json.dump(out, open(out_path, "w"))
json.dump(out, open(out_path, "w"))
