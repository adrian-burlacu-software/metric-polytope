"""Local reachability check with the judge's engine library (metricpoly/reach.py) on a SCRATCH engine:
targets = my candidate rows only; already-reached keys from checkpoints/phase9/reached.json are skipped (crossed off,
read-only); base = results/n9/base_keys.json + graph test; user moves = rules/phase9_accepted.mpr (partial-dup,
dup-midshift, radial-lowend via state.json) applied forward exactly as the judge does. Output: per row, reached or not.
Usage: python localreach7.py OUT.json CACHE_DIR ROW [ROW ...]"""
import json, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts/phase9"))
sys.path.insert(0, str(ROOT))
import numpy as np
import os
MAXSKIP = int(os.environ.get("MAXSKIP", "9"))


def main():
    from common import interpreter
    from judge import load_base, make_is_base
    from phase9_round import Forward, _user_moves, load_state
    from metricpoly.reach import Engine
    from metricpoly.core import Point
    out, cache, rows = sys.argv[1], Path(sys.argv[2]), [int(r) for r in sys.argv[3:]]
    C = np.load(ROOT / "data/deza/orbits9/coords.npy", mmap_mode="r")
    Dn = np.load(ROOT / "data/deza/orbits9/den.npy", mmap_mode="r")
    pts = [Point.make(9, int(Dn[r]), [int(v) for v in C[r]]) for r in rows]
    t0 = time.time()
    reached, st = load_state()
    I, _ = interpreter()
    eng = Engine(cache, workers=int(os.environ.get("WK", "3")))
    eng.add_targets(pts, verbose=True)
    print("info later");print("targets added", round(time.time() - t0, 1), flush=True)
    base = load_base()
    with Forward(eng, [], int(os.environ.get("WK", "3")), [k for k in eng.rep if k not in reached]) as fw:
        after, info = eng.run(make_is_base(base, set(st["extra_base"])), _user_moves(I, st), I, skip={k: v for k, v in reached.items() if k in eng.rep and int(k.split("|")[0]) <= MAXSKIP},
                           verbose=False, forward=fw, deadline=time.time() + 240)
    print("run info", str(info)[:300], flush=True)
    res = []
    for i, (r, p) in enumerate(zip(rows, pts)):
        k = eng.target_key(i)
        res.append({"row": r, "D": p.D, "key": k, "reached": k in after, "how": str(after.get(k))[:200]})
    print(json.dumps([(x["row"], x["D"], x["reached"]) for x in res]), round(time.time() - t0, 1), flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
