#!/usr/bin/env python3
"""Rebuild the round-5 report after the report-writing crash (coverage dict had mixed int/str keys).
The judge's state (accepted rule, reached set, registry) was written before the crash. Here:
 - partial-dup gain and coverage are recomputed exactly from the saved before/after reached sets
 - the outcomes of the dropped proposals and retries are taken from the round log
 - the 24 breaker candidates are re-judged against the current state (which includes partial-dup)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "phase9"))

from common import interpreter, load_json  # noqa: E402
from judge import CK, OUT, load_base, summarize, targets  # noqa: E402
import phase9_round as P  # noqa: E402
from metricpoly.jobs import atomic_write_json, atomic_write_text, code_version, git_head  # noqa: E402
from metricpoly.reach import Engine  # noqa: E402


def main():
    eng = Engine(CK / "engine")
    T = targets()
    before, _ = P.load_state(ROOT / "checkpoints" / "phase9.before_round05")
    after, st = P.load_state()
    g = P._gain(eng, T, before, after)
    props = []
    for line in (OUT / "round_05.log").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\[round 5\] (RETRY )?(\S+)(?: \(from round (\d+), 900 s\))?: (.+?)  gain (.*)$", line)
        if not m:
            continue
        rec = {"name": m.group(2), "status": m.group(4), "retry": bool(m.group(1)),
               "retry_of_round": int(m.group(3)) if m.group(3) else None, "source": "round log (report rebuilt)"}
        if rec["name"] == "partial-dup" and rec["status"] == "ACCEPTED":
            rec.update(file="phase9/round_05/maker/01_partial_dup.mpr", kind="move", track="main",
                       targets_gained={n: len(v) for n, v in g.items()}, targets_gained_ids=g,
                       nodes_gained=len(after) - len(before), coverage=P.coverage(eng, T, before, g))
        props.append(rec)
    # re-judge the candidates with the current state; take round-5 entries out of the registry first
    reg_path = OUT / "large_orbits.json"
    reg = load_json(reg_path)
    atomic_write_json(reg_path, {k: v for k, v in reg.items() if not v.startswith("round_05")})
    I, _ = interpreter([])
    cands = P.eval_candidates(ROOT / "phase9/round_05/breaker/candidates.json", eng, T, after, st, load_base(), I)
    rep = {"round": 5, "code_version": code_version(), "git": git_head(), "seconds": None,
           "note": "report rebuilt after a report-writing crash; judge state was written before the crash",
           "budget_per_rule": 300, "round_cap": 3600, "proposals": props, "candidates": cands,
           "smallest_counterexamples": {},
           "unreached_before": {str(k): v for k, v in summarize(eng, T, before).items()},
           "unreached_after": {str(k): v for k, v in summarize(eng, T, after).items()}}
    atomic_write_json(OUT / "round_05.json", rep)
    atomic_write_text(OUT / "round_05.md", P.render(rep) + "\nNote: " + rep["note"] + ".\n")
    print(P.render(rep))


if __name__ == "__main__":
    main()
