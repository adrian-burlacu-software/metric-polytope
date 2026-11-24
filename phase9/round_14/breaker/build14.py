"""Assemble candidates.json from batch14a-c.json (certified runs: no timeout, positive controls 48312 and 166852
reached). Only fresh rows (never tested or claimed in rounds 1-13, not judge targets); controls excluded; non-dyadic
D only (round 14: D = 10, 15); cap 40."""
import json
from collections import Counter
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent
ROOT = H.parents[2]
C = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
CONTROLS = {48312, 166852}
res = [r for f in sorted(H.glob("batch14*.json")) for r in json.load(open(f))
       if not r["reached"] and r["row"] not in CONTROLS]
res.sort(key=lambda r: (r["D"], r["row"]))
keys, pick = set(), []
for r in res:
    if r["key"] not in keys:
        keys.add(r["key"]); pick.append(r)
pick = pick[:40]
common = ("local fixpoint on a scratch metricpoly.reach.Engine (no timeout, positive controls 48312 and 166852 reached), "
          "skip = current reached.json, base incl. all 398 state.json extra_base keys, moves partial-dup + dup-midshift + "
          "radial-lowend + dup-thirdshift: not reached")
out = [{"n": 9, "D": int(r["D"]), "nums": [int(v) for v in C[r["row"]]], "kind": "unreachable", "rule": "all-moves-cover",
        "how": f"Deza n=9 row {r['row']}, new (round 7 pool7, not a judge target, untested in rounds 1-13; no single-node "
               f"restriction is an m_8 vertex); " + common}
       for r in pick]
json.dump(out, open(H / "candidates.json", "w"), indent=1)
json.dump([{k: o[k] for k in ("n", "D", "nums")} for o in out], open(H / "chk14_norule.json", "w"))
print(len(res), len(out), sorted(Counter(o["D"] for o in out).items()))
