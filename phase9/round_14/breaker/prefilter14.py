"""Prefilter: fresh pool7 rows (not used in earlier breaker rounds, not judge targets) of the given D whose 9
single-node restrictions are all NON-vertices of m_8 (float rank of the tight rows < 28). Such rows cannot be a
one-step 'lift' of an n = 8 vertex, which is how most round 14 batch-a rows were reached.
Usage: prefilter14.py OUT.json D [D ...]"""
import glob, json, re, sys, time
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent
ROOT = H.parents[2]
sys.path.insert(0, str(ROOT))
from metricpoly.core import ineq_matrix, pairs
pool = json.load(open(ROOT / "phase9/round_07/breaker/pool7.json"))
used = set()
for f in glob.glob(str(ROOT / "phase9/round_*/breaker/*.json")):
    if "prefilter" in f: continue
    try: d = json.load(open(f))
    except Exception: continue
    if isinstance(d, list):
        for r in d:
            if isinstance(r, dict):
                if "row" in r: used.add(int(r["row"]))
                m = re.search(r"row (\d+)", str(r.get("how", "")))
                if m: used.add(int(m.group(1)))
for f in glob.glob(str(ROOT / "phase9/round_*/breaker/rows*.txt")):
    used |= {int(x) for x in open(f).read().split()}
tg = set(json.load(open(ROOT / "results/phase9/baseline.json"))["n9_rows"])
C = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
A8, b8 = ineq_matrix(8)
A8 = np.asarray(A8, dtype=float); b8 = np.asarray(b8, dtype=float).ravel()
P9 = pairs(9)
subs = []
for k in range(9):
    subs.append([i for i, (a, b) in enumerate(P9) if a != k and b != k])
out, Ds = sys.argv[1], sys.argv[2:]
t0 = time.time(); res = {}
for D in Ds:
    keep = []
    for r in pool[D]:
        if r in used or r in tg: continue
        x = np.asarray(C[r], dtype=float)
        ok = True
        for s in subs:
            y = x[s]
            sl = b8 * int(D) - A8 @ y
            T = A8[np.abs(sl) < 1e-9]
            if len(T) >= 28 and np.linalg.matrix_rank(T) == 28:
                ok = False; break
        if ok: keep.append(r)
    res[D] = keep
    print(D, len(pool[D]), len(keep), round(time.time() - t0, 1), flush=True)
json.dump(res, open(H / out, "w"))
