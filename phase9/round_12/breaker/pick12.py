"""Pick fresh n = 9 rows from round 7's pool7.json (design-A depth_detour = None, not judge targets) that no earlier
breaker round tested or claimed. Smallest D first. Writes rows12b.txt."""
import glob, json, re, sys
from pathlib import Path
H = Path(__file__).resolve().parent
ROOT = H.parents[2]
pool = json.load(open(ROOT / "phase9/round_07/breaker/pool7.json"))
used = set()
for f in glob.glob(str(ROOT / "phase9/round_*/breaker/*.json")):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    if isinstance(d, list):
        for r in d:
            if isinstance(r, dict):
                if "row" in r: used.add(int(r["row"]))
                m = re.search(r"row (\d+)", str(r.get("how", "")))
                if m: used.add(int(m.group(1)))
for f in glob.glob(str(ROOT / "phase9/round_*/breaker/rows*.txt")):
    used |= {int(x) for x in open(f).read().split()}
print("used", len(used))
print({D: (len(v), sum(r not in used for r in v)) for D, v in sorted(pool.items(), key=lambda t: int(t[0]))})
N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
pick = []
for D in sorted(pool, key=int):
    fresh = [r for r in pool[D] if r not in used]
    pick += fresh[:max(0, min(len(fresh), N - len(pick)))] if D != "9" else fresh[:min(len(fresh), 25, N - len(pick))]
    if len(pick) >= N: break
open(H / "rows12b.txt", "w").write(" ".join(map(str, pick)))
print(len(pick), pick)
