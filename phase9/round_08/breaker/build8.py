"""Assemble candidates.json: n = 9 small-D rows locally unreached (batch8a/b, localreach8.py) + n = 10/11 extensions
of confirmed round-7 unreachable vertices that reachable_bu (all accepted moves) returned False for (gen8*.json).
Dedupe: n = 9 by group.canonical key against every earlier n = 9 claim (rounds 1-7); n >= 10 by canon_large key
(gen8 already skipped keys in results/phase9/large_orbits.json)."""
import glob, json, sys
from pathlib import Path
H = Path(__file__).resolve().parent
ROOT = H.parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from metricpoly import group
from metricpoly.core import Point
C = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
Dn = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
N9 = int(sys.argv[1]) if len(sys.argv) > 1 else 24
old = set()
for f in glob.glob(str(ROOT / "phase9/round_0[1-7]/breaker/candidates.json")):
    for c in json.load(open(f)):
        if c["n"] == 9:
            old.add(group.canonical(Point.make(9, c["D"], c["nums"])).key())
res = [r for f in ("batch8a.json", "batch8b.json") if (H / f).exists() for r in json.load(open(H / f))]
un9 = [r for r in res if not r["reached"] and r["key"] not in old]
keys = set()
pick9 = []
for D in (7, 9, 10, 12):           # smallest denominators first, spread over D
    pick9 += [r for r in un9 if r["D"] == D and r["key"] not in keys and not keys.add(r["key"])]
pick9 = [r for r in pick9 if r["D"] == 7][:12] + [r for r in pick9 if r["D"] != 7]
out = []
big = [r for f in sorted(glob.glob(str(H / "gen8*.json"))) for r in json.load(open(f)) if r["bu"] is False]
seenb = set()
big = [r for r in big if r["key"] not in seenb and not seenb.add(r["key"])]
big = sorted(big, key=lambda r: (r["how"] == "twin", r["D"]))
nb = min(len(big), 40 - min(N9, len(pick9)), 18)
n9 = 40 - nb
for r in pick9[:n9]:
    out.append({"n": 9, "D": int(r["D"]), "nums": [int(v) for v in C[r["row"]]], "kind": "unreachable",
                "rule": "all-moves-cover",
                "how": f"Deza n=9 row {r['row']} (not a judge target, not claimed in rounds 1-7); design-A depth_detour=None; "
                       f"local fixpoint on a scratch metricpoly.reach.Engine, skip = current reached.json, accepted moves "
                       f"partial-dup + dup-midshift + radial-lowend forward: not reached"})
for r in big[:nb]:
    out.append({"n": r["n"], "D": r["D"], "nums": r["nums"], "kind": "unreachable", "rule": "all-moves-cover",
                "how": f"{r['how']} extension of a round-7 CONFIRMED unreachable n=9 vertex (D={r['seed_D']}); exact vertex; "
                       f"reach_large.reachable_bu with partial-dup + dup-midshift + radial-lowend: False ({r['secs']} s)"})
json.dump(out, open(H / "candidates.json", "w"), indent=1)
json.dump([{k: o[k] for k in ("n", "D", "nums")} for o in out], open(H / "chk8_norule.json", "w"))
from collections import Counter
print(len(out), sorted(Counter((o["n"], o["D"]) for o in out).items()))
