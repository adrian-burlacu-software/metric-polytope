"""Round 7 breaker: candidate pool of n = 9 Deza reps that are NOT judge targets and NOT claimed in round 1.
Stats: per D, how many design-A 'depth_detour = None' targets are still unreached now (retention)."""
import gzip, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
b = json.loads((ROOT / "results/phase9/baseline.json").read_text())
targets = set(b["n9_rows"])
U = json.loads((ROOT / "results/phase9/unreached_nodes.json").read_text())
unr_t = set(U["target_keys"])
r1 = json.loads((ROOT / "phase9/round_01/breaker/candidates.json").read_text())
r1rows = {int(m.group(1)) for c in r1 for m in [re.search(r"row (\d+)", c["how"])] if m}
recs = [json.loads(l) for l in gzip.open(ROOT / "results/n9/orbits_A.jsonl.gz", "rt")]
print("records", len(recs), "r1 rows", len(r1rows))
def oddp(D):
    p, out, d = 3, [], D
    while d % 2 == 0: d //= 2
    while d > 1:
        if d % p == 0:
            out.append(p)
            while d % p == 0: d //= p
        p += 2
    return out
ret = defaultdict(lambda: [0, 0])
pool = defaultdict(list)
for r in recs:
    if r["depth_detour"] is not None:
        continue
    if r["row"] in targets:
        ret[r["D"]][0] += 1
        ret[r["D"]][1] += r["key"] in unr_t
    elif r["row"] not in r1rows:
        pool[r["D"]].append(r["row"])
print("D  targets(None) still_unreached  pool")
for D in sorted(set(ret) | set(pool)):
    print(D, ret[D], len(pool[D]), oddp(D))
json.dump({str(D): v for D, v in pool.items()}, open(Path(__file__).with_name("pool7.json"), "w"))
