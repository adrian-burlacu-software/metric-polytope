#!/usr/bin/env python3
"""Evaluate every maker claim on the breaker pools (new rays, pool non-rays) and on the public data.
Usage: attack.py [max_per_pool]  -> attack_report.json with the breaking items per claim."""
import sys, json, glob, importlib.util, time, random, traceback
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))
HERE = Path(__file__).resolve().parent
MAKER = HERE.parent / "maker"
sys.path.insert(0, str(MAKER))
DATA = ROOT / "results/phase9/family12"


def main():
    cap = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    only = sys.argv[2] if len(sys.argv) > 2 else ""
    rng = random.Random(5)
    rays = json.loads((HERE / "new_rays.json").read_text())
    non = json.loads((HERE / "pool_nonrays.json").read_text())
    for k in (8, 9):
        for j in json.loads((DATA / f"nonrays_public_k{k}.json").read_text()):
            non.append({"k": j["k"], "edges": j["edges"], "how": "public non-ray"})
    rng.shuffle(rays); rng.shuffle(non)
    # smaller k first is not wanted: keep a balanced mix
    rays, non = rays[:cap], non[:cap]
    report = {}
    for f in sorted(glob.glob(str(MAKER / "[0-9]*.py"))):
        if only and only not in f: continue
        try:
            spec = importlib.util.spec_from_file_location(Path(f).stem, f)
            mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        except Exception:
            print(f, "LOAD FAILED"); traceback.print_exc(); continue
        kind = mod.KIND
        res = {"file": Path(f).name, "kind": kind, "statement": mod.STATEMENT}
        t0 = time.time()
        for label, pool, bad in (("rays", rays, False), ("nonrays", non, True)):
            tested = 0; hits = []; true = 0; errs = 0
            for j in pool:
                if time.time() - t0 > 100: break
                try:
                    v = bool(mod.claim(j["k"], [tuple(e) for e in j["edges"]]))
                except Exception as ex:
                    errs += 1; v = None
                    if errs == 1: res[f"error_{label}"] = repr(ex)[:200]; res[f"error_item_{label}"] = j
                tested += 1; true += bool(v)
                if v is bad and ((label == "rays" and kind in ("necessary", "iff")) or
                                 (label == "nonrays" and kind in ("sufficient", "iff"))):
                    hits.append(j)
            res[label] = {"tested": tested, "claim_true": true, "errors": errs, "breaks": len(hits)}
            res[f"hits_{label}"] = hits[:200]
        report[mod.NAME] = res
        print(mod.NAME, kind, "| rays", res["rays"], "| nonrays", res["nonrays"], f"| {time.time() - t0:.0f}s", flush=True)
    (HERE / f"attack_report{only}.json").write_text(json.dumps(report))


if __name__ == "__main__":
    main()
