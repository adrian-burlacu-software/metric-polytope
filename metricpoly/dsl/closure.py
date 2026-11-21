"""closure: apply moves until nothing new appears (orbitwise), with provenance and checkpoints.

State per size n: canonical key -> {rep, prov}. prov = {"move": name|"seed", "parents": [keys], "round": r}.
A round applies every unary move to every orbit added in the previous round, and every binary move to every
(new, known) and (known, new) pair. Stops when a round adds nothing (saturated) or max_rounds is hit (truncated).
Inputs are orbit representatives; moves that are only permutation-equivariant are applied to whole switching
classes (Interpreter.apply_move(as_orbits=True)).
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .. import group
from ..core import Point
from ..jobs import ROOT, atomic_write_json, code_version
from . import prims
from .registry import primitive


@dataclass
class Closure:
    name: str
    orbits: Dict[int, Dict[str, dict]] = field(default_factory=dict)
    rounds: int = 0
    saturated: bool = False
    truncated_reason: Optional[str] = None
    params: dict = field(default_factory=dict)
    seconds: float = 0.0

    def keys(self, n):
        return set(self.orbits.get(n, {}))

    def reps(self, n):
        lst = prims.DomainList(v["rep"] for v in self.orbits.get(n, {}).values())
        lst.kind = "reps"
        lst.n = n
        return lst

    def to_json(self):
        return {"name": self.name, "rounds": self.rounds, "saturated": self.saturated,
                "truncated_reason": self.truncated_reason, "params": self.params, "seconds": self.seconds,
                "orbits": {str(n): {k: {"rep": [v["rep"].D, list(v["rep"].nums)], "prov": v["prov"]}
                                    for k, v in d.items()} for n, d in self.orbits.items()}}

    @staticmethod
    def from_json(d):
        c = Closure(d["name"], rounds=d["rounds"], saturated=d["saturated"],
                    truncated_reason=d["truncated_reason"], params=d["params"], seconds=d.get("seconds", 0.0))
        for n, dd in d["orbits"].items():
            c.orbits[int(n)] = {k: {"rep": Point(int(n), v["rep"][0], tuple(v["rep"][1])), "prov": v["prov"]}
                                for k, v in dd.items()}
        return c


def _ckpt_path(name: str) -> Path:
    return ROOT / "checkpoints" / f"closure-{name}" / "state.json"


def run_closure(interp, seeds, moves, max_n=8, max_rounds=50, only_vertices=True, checkpoint=None,
                verbose=True, seed_labels=None):
    t0 = time.time()
    moves = list(moves)
    name = checkpoint or "anon"
    params = {"max_n": int(max_n), "max_rounds": int(max_rounds), "only_vertices": bool(only_vertices),
              "moves": [m.name for m in moves], "seeds": [p.key() for p in seeds],
              "seed_labels": list(seed_labels) if seed_labels is not None else None,
              "interp_params": interp.params, "seed": interp.seed}
    cv = code_version()
    src_hash = {m.name: m.source for m in moves}
    C = Closure(name, params=params)
    frontier: List[tuple] = []
    resumed = False
    if checkpoint:
        path = _ckpt_path(checkpoint)
        if path.exists():
            d = json.loads(path.read_text())
            if d.get("code_version") == cv and d.get("params") == params and d.get("move_sources") == src_hash:
                C = Closure.from_json(d["closure"])
                frontier = [tuple(f) for f in d["frontier"]]
                resumed = True
                if verbose:
                    print(f"[closure {name}] resumed at round {C.rounds}, {sum(len(v) for v in C.orbits.values())} orbits")
                if C.saturated or C.truncated_reason:
                    return C
            else:
                path.rename(path.with_name(f"state.stale-{int(time.time())}.json"))

    def add(p: Point, prov) -> Optional[tuple]:
        if p.n > max_n:
            return None
        if only_vertices and not prims.p_vertex(p):
            return None
        k = group.canonical(p).key()
        d = C.orbits.setdefault(p.n, {})
        if k in d:
            # record every derivation of the same (minimal) depth, not only the first one found
            old = d[k]["prov"]
            if prov["move"] != "seed" and old.get("round") == prov["round"]:
                alt = {"move": prov["move"], "parents": prov["parents"]}
                lst = old.setdefault("alternatives", [])
                if alt not in lst and alt != {"move": old["move"], "parents": old["parents"]}:
                    lst.append(alt)
            return None
        d[k] = {"rep": group.canonical(p), "prov": prov}
        return (p.n, k)

    if not resumed:
        labels = list(seed_labels) if seed_labels is not None else ["seed"] * len(seeds)
        for s, lab in zip(seeds, labels):
            f = add(s, {"move": "seed", "seed_rule": lab, "parents": [], "round": 0})
            if f:
                frontier.append(f)

    interp.params["closure-max-n"] = int(max_n)
    unary = [m for m in moves if len(m.params) == 1]
    binary = [m for m in moves if len(m.params) == 2]
    while frontier:
        if C.rounds >= max_rounds:
            C.truncated_reason = f"max_rounds={max_rounds}"
            break
        C.rounds += 1
        r = C.rounds
        new: List[tuple] = []
        tr = time.time()
        # pass 1: all unary moves on the whole frontier; pass 2: binary moves. Within a round every
        # depth-minimal derivation is recorded (primary = first unary one, then "alternatives").
        for (n, k) in frontier:
            x = C.orbits[n][k]["rep"]
            for mv in unary:
                g = mv.grow
                if isinstance(g, int) and n + g > max_n:
                    continue
                for y in interp.apply_move(mv, [x], as_orbits=True):
                    f = add(y, {"move": mv.name, "parents": [k], "round": r})
                    if f:
                        new.append(f)
        for (n, k) in frontier:
            x = C.orbits[n][k]["rep"]
            for mv in binary:
                known = [(n2, k2) for n2, d in C.orbits.items() for k2 in d]
                for (n2, k2) in known:
                    y2 = C.orbits[n2][k2]["rep"]
                    if max(n, n2) + 1 > max_n:
                        continue
                    for a, b, ka, kb in ((x, y2, k, k2), (y2, x, k2, k)):
                        for y in interp.apply_move(mv, [a, b], as_orbits=True):
                            f = add(y, {"move": mv.name, "parents": [ka, kb], "round": r})
                            if f:
                                new.append(f)
        frontier = new
        C.seconds = time.time() - t0
        if verbose:
            tot = {n: len(d) for n, d in sorted(C.orbits.items())}
            print(f"[closure {name}] round {r}: +{len(new)} orbits ({time.time() - tr:.1f}s)  per n: {tot}",
                  flush=True)
        if checkpoint:
            atomic_write_json(_ckpt_path(checkpoint), {"code_version": cv, "params": params,
                                                       "move_sources": src_hash, "frontier": frontier,
                                                       "closure": C.to_json()})
    if not frontier and not C.truncated_reason:
        C.saturated = True
    C.seconds = time.time() - t0
    if checkpoint:
        atomic_write_json(_ckpt_path(checkpoint), {"code_version": cv, "params": params, "move_sources": src_hash,
                                                   "frontier": frontier, "closure": C.to_json()})
    return C


# ======================================================================= interpreter-aware primitives

@primitive("closure-orbits", 2, "Closure Nat -> List<Point>", "𝒞_{1}", r"\mathcal{{C}}_{{{1}}}")
def p_closure_orbits(C, n):
    return C.reps(n)


@primitive("saturated?", 1, "Closure -> Bool", "sat({0})", r"\mathrm{{sat}}({0})")
def p_saturated(C):
    return C.saturated


def _keyset(L):
    return frozenset(group.canonical(p).key() for p in L)


_KEYS_CACHE: Dict[int, frozenset] = {}


def keys_of(L):
    k = id(L)
    if k not in _KEYS_CACHE:
        _KEYS_CACHE[k] = (_keyset(L), L)          # keep L alive so id stays valid
    return _KEYS_CACHE[k][0]


@primitive("in-orbits?", 2, "Point List<Point> -> Bool", "{0}∈G·{1}", r"{0}\in G\cdot{1}")
def p_in_orbits(x, L):
    return group.canonical(x).key() in keys_of(L)


@primitive("uncovered", 2, "Closure Nat -> List<Point>", "V(m_{1})∖𝒞", r"V(m_{{{1}}})\setminus\mathcal{{C}}")
def p_uncovered(C, n):
    have = C.keys(n)
    out = prims.DomainList(x for x in prims.p_vertices(n) if group.canonical(x).key() not in have)
    out.kind = "reps"
    out.n = n
    return out


@primitive("provenance", 2, "Closure Point -> List", "prov({1})", r"\mathrm{{prov}}({1})")
def p_provenance(C, x):
    k = group.canonical(x).key()
    d = C.orbits.get(x.n, {})
    return d[k]["prov"] if k in d else False


@primitive("apply-move", 2, "Move List<Point> -> List<Point>", "{0}({1})", r"{0}({1})", needs_interp=True)
def p_apply_move(interp, mv, L):
    reps = isinstance(L, prims.DomainList) and L.kind == "reps"
    out = []
    for x in L:
        out.extend(interp.apply_move(mv, [x], as_orbits=reps))
    return out


@primitive("produced-by?", 2, "Point Rule -> Bool", "{0}∈{1}", r"{0}\in{1}", needs_interp=True)
def p_produced_by(interp, x, rule):
    return group.canonical(x).key() in keys_of(interp.run_rule(rule, x.n))


@primitive("param", 2, "Str Any -> Any", "{0}", r"{0}", needs_interp=True)
def p_param(interp, name, default):
    return interp.params.get(str(name), default)
