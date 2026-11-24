"""Assemble candidates.json from batch12c.json and batch12d.json (certified runs: no timeout, positive controls reached).
New rows (not tested in rounds 1-11) first, then round 11's 40 claims re-confirmed with the round 11 house families;
smallest D first, cap 40. batch12a (no controls) and batch12b (timed out) are not used for claims."""
import glob, json, re, sys
from collections import Counter
from pathlib import Path
H = Path(__file__).resolve().parent
ROOT = H.parents[2]
import numpy as np
C = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
r11 = {int(re.search(r"row (\d+)", c["how"]).group(1)) for c in json.load(open(ROOT / "phase9/round_11/breaker/candidates.json"))}
res = [r for f in ("batch12c.json", "batch12d.json") for r in json.load(open(H / f)) if not r["reached"]]
new = sorted([r for r in res if r["row"] not in r11], key=lambda r: r["D"])
old = sorted([r for r in res if r["row"] in r11], key=lambda r: r["D"])
keys, pick = set(), []
for r in new + old:
    if r["key"] not in keys:
        keys.add(r["key"]); pick.append(r)
pick = pick[:40]
common = ("local fixpoint on a scratch metricpoly.reach.Engine (no timeout, positive controls reached), skip = current "
          "reached.json, base incl. all 327 state.json extra_base keys (gen-bipartite-glue, gen-house-c4-d11, "
          "gen-house-p4-d11), moves partial-dup + dup-midshift + radial-lowend + dup-thirdshift: not reached")
out = [{"n": 9, "D": int(r["D"]), "nums": [int(v) for v in C[r["row"]]], "kind": "unreachable", "rule": "all-moves-cover",
        "how": (f"Deza n=9 row {r['row']}, " + ("round 11 claim re-confirmed; " if r["row"] in r11 else
                "new (round 7 pool7, not a judge target, untested in rounds 1-11); ") + common)} for r in pick]
json.dump(out, open(H / "candidates.json", "w"), indent=1)
json.dump([{k: o[k] for k in ("n", "D", "nums")} for o in out], open(H / "chk12_norule.json", "w"))
print(len(out), "new", sum(r["row"] not in r11 for r in pick), sorted(Counter(o["D"] for o in out).items()))
