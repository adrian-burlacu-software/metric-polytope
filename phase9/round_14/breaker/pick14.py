"""Pick fresh n = 9 rows from round 7's pool7.json (not judge targets) that no earlier breaker round tested or
claimed, restricted to the denominators given on the command line (round 14: non-dyadic, D != 6,7,8).
Usage: pick14.py OUT N D [D ...]"""
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
tg = set(json.load(open(ROOT / "results/phase9/baseline.json")).get("n9_rows", []))
out, N, Ds = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
print("used", len(used), {D: sum(r not in used and r not in tg for r in pool[D]) for D in Ds})
pick = []
per = -(-N // len(Ds))
for D in Ds:
    fresh = [r for r in pool[D] if r not in used and r not in tg]
    pick += fresh[:per]
pick = pick[:N]
open(H / out, "w").write(" ".join(map(str, pick)))
print(len(pick), pick)
