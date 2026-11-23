"""Assemble candidates.json from batch11a.json + batch11c.json (batch11b timed out, its unreached rows were rerun as batch11c) (localreach11.py): n = 9 Deza rows locally unreached with all 4
accepted moves + extra_base (gen-bipartite-glue n = 8 orbits). Dedupe by group.canonical key against every n = 9
claim of rounds 1-10 and against judge targets / unreached nodes (check_point.py confirms the latter)."""
import glob, json, sys
from collections import Counter
from pathlib import Path
H = Path(__file__).resolve().parent
ROOT = H.parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from metricpoly import group
from metricpoly.core import Point
C = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
Dn = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
old = set()
for f in glob.glob(str(ROOT / "phase9/round_*/breaker/candidates.json")):
    if "round_11" in f:
        continue
    for c in json.load(open(f)):
        if c["n"] == 9:
            old.add(group.canonical(Point.make(9, c["D"], c["nums"])).key())
res = [r for f in ("batch11a.json", "batch11c.json") if (H / f).exists() for r in json.load(open(H / f))]
keys, pick = set(), []
for r in sorted(res, key=lambda r: r["D"]):
    if not r["reached"] and r["key"] not in old and r["key"] not in keys:
        keys.add(r["key"]); pick.append(r)
# keep spread: all small-D first, then D = 13, cap 40
pick = pick[:40]
out = [{"n": 9, "D": int(r["D"]), "nums": [int(v) for v in C[r["row"]]], "kind": "unreachable",
        "rule": "all-moves-cover",
        "how": f"Deza n=9 row {r['row']} (not a judge target, not claimed in rounds 1-10); design-A depth_detour=None; "
               f"local fixpoint on a scratch metricpoly.reach.Engine, skip = current reached.json, base incl. "
               f"extra_base (gen-bipartite-glue), moves partial-dup + dup-midshift + radial-lowend + dup-thirdshift: not reached"}
       for r in pick]
json.dump(out, open(H / "candidates.json", "w"), indent=1)
json.dump([{k: o[k] for k in ("n", "D", "nums")} for o in out], open(H / "chk11_norule.json", "w"))
print(len(out), sorted(Counter(o["D"] for o in out).items()), "dropped as old:", sum(r["key"] in old for r in res))
