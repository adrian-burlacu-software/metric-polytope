"""Assemble candidates.json from the locally-unreached rows of batch7a/batch7b (localreach7.py)."""
import json
from pathlib import Path
import numpy as np
H = Path(__file__).parent
ROOT = H.parents[2]
C = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
Dn = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
pick = [52277, 21817, 52211, 25920, 36846, 97190, 50048, 135494, 312449, 437497, 224960, 487762, 368453,
        108402, 442070, 452408, 528380, 748341, 546659, 638417, 535480, 681666, 632247, 673757, 739547,
        1004715, 975278, 917333, 957425, 746376, 954787, 1047384, 1052162, 1042104, 1055441, 1055759, 1056290,
        1042620, 711032, 1030358]
res = {r["row"]: r for f in ("batch7a.json", "batch7b.json") for r in json.load(open(H / f))}
assert len(set(pick)) == 40 and all(r in res and not res[r]["reached"] for r in pick)
assert len({res[r]["key"] for r in pick}) == 40
out = []
for r in pick:
    D = int(Dn[r])
    bound = "; odd prime > 2n-3 = 15 (Theorem 4 bound violated)" if D in (17, 19) else ""
    out.append({"n": 9, "D": D, "nums": [int(v) for v in C[r]], "kind": "unreachable", "rule": "all-moves-cover",
                "how": f"Deza n=9 row {r} (not a judge target, not a round-1 claim); design-A depth_detour=None; "
                       f"local fixpoint with metricpoly.reach.Engine on a scratch engine, skip = current reached.json, "
                       f"accepted moves partial-dup + dup-midshift forward: not reached{bound}"})
json.dump(out, open(H / "candidates.json", "w"), indent=1)
print(len(out), sorted(o["D"] for o in out))
