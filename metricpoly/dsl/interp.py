"""Exact interpreter for the rule DSL.

Top-level forms: define, generative, structural, move. Special forms: let, if, case, and, or, implies, for,
forall, exists, first, min-over, max-over, count, closure, lit, pairs. Everything else is a call resolved in:
local env -> DSL defines -> rules -> moves -> primitive registry.

Symmetry policy for domains of orbit representatives (vertices n for n = 7, 8):
  the body is evaluated on a few representatives and on random group images of them (seeded);
  'G'  : invariant/equivariant under the full group     -> evaluate on representatives only
  'Sn' : only under permutations                         -> expand each representative to its switching class
  else : error (the rule is not well-defined on orbit data)
"""
from __future__ import annotations

import itertools
import time
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from .. import group
from ..core import Point
from . import prims  # noqa: F401  (registers kernel primitives)
from . import closure as _closure  # noqa: F401  (registers interpreter-aware primitives)
from .registry import REGISTRY, Primitive, load_extensions
from .sexpr import Kw, NodeSetLit, Sym, read_all, write
from .values import Graph, Mid, Partial, Tree

SPECIAL = {"let", "if", "case", "and", "or", "implies", "for", "forall", "exists", "first", "min-over",
           "max-over", "count", "closure", "lit", "pairs", "else", "where"}


class DSLError(Exception):
    pass


class Verdict:
    """Boolean with an optional witness (the binding that decided a quantifier)."""
    __slots__ = ("value", "witness")

    def __init__(self, value: bool, witness=None):
        self.value, self.witness = bool(value), witness

    def __bool__(self):
        return self.value

    def __repr__(self):
        return f"Verdict({self.value}, {self.witness})"


@dataclass
class Func:
    name: str
    params: List[str]
    body: Any
    env: "Env"
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Rule:
    kind: str                 # 'generative' | 'structural'
    name: str
    param: str
    body: Any
    meta: Dict[str, Any]
    source: str


@dataclass
class Move:
    name: str
    params: List[str]
    body: Any
    meta: Dict[str, Any]
    source: str

    @property
    def grow(self):
        return self.meta.get("grow", 0)


class Env:
    def __init__(self, parent: Optional["Env"] = None, vars: Optional[dict] = None):
        self.parent = parent
        self.vars = dict(vars or {})

    def lookup(self, name):
        e = self
        while e is not None:
            if name in e.vars:
                return True, e.vars[name]
            e = e.parent
        return False, None

    def child(self, **kv):
        return Env(self, kv)


def _meta(items: list, start: int) -> Tuple[Dict[str, Any], int]:
    meta = {}
    i = start
    while i < len(items) and isinstance(items[i], Kw):
        key = items[i].name
        val = items[i + 1]
        if key == "domain":
            val = tuple(val)
        elif isinstance(val, Sym):
            val = val.name
        meta[key] = val
        i += 2
    return meta, i


class Interpreter:
    def __init__(self, seed: int = 20261121, params: Optional[dict] = None, closure_dir: Optional[Path] = None):
        load_extensions()
        self.globals = Env()
        self.defines: Dict[str, Any] = {}
        self.rules: Dict[str, Rule] = {}
        self.moves: Dict[str, Move] = {}
        self.sources: Dict[str, str] = {}
        self.memo: Dict[Tuple[str, int], Any] = {}
        self.stack: List[Tuple[str, int]] = []
        self.rng = np.random.default_rng(seed)
        self.seed = seed
        self.params = dict(params or {})
        self.modes: Dict[Tuple[str, int], str] = {}      # (move or body id, n) -> 'G' | 'Sn'
        self.closure_dir = closure_dir
        self.log: List[str] = []

    # ------------------------------------------------------------------ loading
    def load_file(self, path) -> List[str]:
        return self.load_source(Path(path).read_text(encoding="utf-8"), origin=str(path))

    def load_source(self, src: str, origin: str = "<string>") -> List[str]:
        names = []
        for form in read_all(src):
            names.append(self._toplevel(form, origin))
        return names

    def _toplevel(self, form, origin):
        if not (isinstance(form, list) and form and isinstance(form[0], Sym)):
            raise DSLError(f"{origin}: top-level form must be (define|generative|structural|move ...)")
        head = form[0].name
        if head == "define":
            sig = form[1]
            meta, i = _meta(form, 2)
            body = form[i]
            if isinstance(sig, list):
                name = sig[0].name
                params = [p.name if isinstance(p, Sym) else p[0].name for p in sig[1:]]
                self._check_new(name)
                self.defines[name] = Func(name, params, body, self.globals, meta)
            else:
                name = sig.name
                self._check_new(name)
                self.defines[name] = ("lazy", body)
            self.sources[name] = write(form)
            self._static_check(body, set(params) if isinstance(sig, list) else set(), name)
            return name
        if head in ("generative", "structural"):
            name, param = form[1].name, form[2][0].name
            meta, i = _meta(form, 3)
            body = form[i]
            self._check_new(name)
            self.rules[name] = Rule(head, name, param, body, meta, write(form))
            self.sources[name] = write(form)
            self._static_check(body, {param}, name)
            return name
        if head == "move":
            name = form[1].name
            params = [p.name for p in form[2]]
            meta, i = _meta(form, 3)
            body = form[i]
            self._check_new(name)
            self.moves[name] = Move(name, params, body, meta, write(form))
            self.sources[name] = write(form)
            self._static_check(body, set(params), name)
            return name
        raise DSLError(f"{origin}: unknown top-level form {head!r}")

    def _check_new(self, name):
        if name in self.defines or name in self.rules or name in self.moves:
            raise DSLError(f"{name!r} defined twice")
        if name in REGISTRY:
            raise DSLError(f"{name!r} shadows a primitive")

    def _static_check(self, expr, bound: set, where: str):
        """Load-time check: every called name exists (or is defined later in the file set), arity of primitives."""
        self._pending = getattr(self, "_pending", [])
        self._pending.append((expr, frozenset(bound), where))

    def finalize(self):
        """Resolve names after all files are loaded; raise on unknown names / primitive arity errors."""
        errors = []
        for expr, bound, where in getattr(self, "_pending", []):
            self._walk_check(expr, set(bound), where, errors)
        self._pending = []
        if errors:
            raise DSLError("static check failed:\n  " + "\n  ".join(errors))

    def _walk_check(self, e, bound, where, errors):
        if isinstance(e, Sym):
            n = e.name
            if not (n in bound or n in self.defines or n in self.rules or n in self.moves or n in REGISTRY):
                errors.append(f"{where}: unknown name {n!r}")
            return
        if not isinstance(e, list) or not e:
            return
        h = e[0]
        if isinstance(h, Sym) and h.name in ("for", "forall", "exists", "first", "min-over", "max-over", "count"):
            b = set(bound)
            for g in e[1]:
                self._walk_check(g[1], b, where, errors)
                b.add(g[0].name)
            for x in e[2:]:
                if isinstance(x, list) and x and isinstance(x[0], Sym) and x[0].name == "where":
                    self._walk_check(x[1], b, where, errors)
                else:
                    self._walk_check(x, b, where, errors)
            return
        if isinstance(h, Sym) and h.name == "let":
            b = set(bound)
            for bd in e[1]:
                self._walk_check(bd[1], b, where, errors)
                if isinstance(bd[0], list):
                    b.update(s.name for s in bd[0])
                else:
                    b.add(bd[0].name)
            self._walk_check(e[2], b, where, errors)
            return
        if isinstance(h, Sym) and h.name in ("lit", "pairs"):
            return
        if isinstance(h, Sym) and h.name == "case":
            self._walk_check(e[1], bound, where, errors)
            for cl in e[2:]:
                self._walk_check(cl[1], bound, where, errors)
            return
        if isinstance(h, Sym) and h.name not in SPECIAL and h.name in REGISTRY and h.name not in bound:
            p = REGISTRY[h.name]
            nargs = len([a for a in e[1:]])
            lo, hi = p.arity
            if nargs < lo or (hi is not None and nargs > hi):
                errors.append(f"{where}: {h.name} takes {p.arity} args, got {nargs}")
        for idx, x in enumerate(e):
            if isinstance(x, Kw):
                continue
            if idx == 0 and isinstance(x, Sym) and x.name in SPECIAL and x.name not in bound:
                continue
            self._walk_check(x, bound, where, errors)

    # ------------------------------------------------------------------ evaluation
    def eval(self, e, env: Env):
        if isinstance(e, bool) or isinstance(e, (int, Fraction, str)):
            return e
        if isinstance(e, Kw):
            return e
        if isinstance(e, NodeSetLit):
            return frozenset(e.items)
        if isinstance(e, Sym):
            return self._lookup(e.name, env)
        if not isinstance(e, list) or not e:
            raise DSLError(f"cannot evaluate {e!r}")
        head = e[0]
        if isinstance(head, Sym):
            h = head.name
            found, _ = env.lookup(h)
            if not found and h in SPECIAL:
                return getattr(self, "_sf_" + h.replace("-", "_"))(e, env)
            fn = self._lookup(h, env)
            args = [self.eval(a, env) for a in e[1:]]
            return self.call(fn, args, h)
        fn = self.eval(head, env)
        return self.call(fn, [self.eval(a, env) for a in e[1:]], write(head))

    def _lookup(self, name, env):
        found, v = env.lookup(name)
        if found:
            return v
        if name in self.defines:
            d = self.defines[name]
            if isinstance(d, tuple) and d[0] == "lazy":
                val = self.eval(d[1], self.globals)
                self.defines[name] = ("value", val)
                return val
            if isinstance(d, tuple) and d[0] == "value":
                return d[1]
            return d
        if name in self.rules:
            return self.rules[name]
        if name in self.moves:
            return self.moves[name]
        if name in REGISTRY:
            return REGISTRY[name]
        raise DSLError(f"unknown name {name!r}")

    def call(self, fn, args, label="?"):
        if isinstance(fn, Primitive):
            lo, hi = fn.arity
            if len(args) < lo or (hi is not None and len(args) > hi):
                raise DSLError(f"{fn.name}: expected {fn.arity} args, got {len(args)}")
            try:
                return fn.fn(self, *args) if fn.needs_interp else fn.fn(*args)
            except DSLError:
                raise
            except Exception as ex:
                raise DSLError(f"{fn.name}{tuple(_short(a) for a in args)}: {type(ex).__name__}: {ex}") from ex
        if isinstance(fn, Func):
            if len(args) != len(fn.params):
                raise DSLError(f"{fn.name}: expected {len(fn.params)} args, got {len(args)}")
            return self.eval(fn.body, Env(fn.env, dict(zip(fn.params, args))))
        if isinstance(fn, Rule):
            if len(args) != 1:
                raise DSLError(f"rule {fn.name} takes one size argument")
            return self.run_rule(fn, int(args[0]))
        if isinstance(fn, Move):
            return self.apply_move(fn, args)
        raise DSLError(f"{label} is not callable")

    # ------------------------------------------------------------------ rules
    def run_rule(self, rule: Rule, n: int):
        for (r, n0) in self.stack:
            if r == rule.name and n >= n0:
                raise DSLError(f"rule {rule.name}: recursive call at size {n} >= {n0} (must decrease)")
        key = (rule.name, n)
        if key in self.memo:
            return self.memo[key]
        self.stack.append(key)
        try:
            val = self.eval(rule.body, self.globals.child(**{rule.param: n}))
        finally:
            self.stack.pop()
        if rule.kind == "structural" and not isinstance(val, Verdict):
            val = Verdict(bool(val))
        self.memo[key] = val
        return val

    # ------------------------------------------------------------------ special forms
    def _sf_let(self, e, env):
        new = env.child()
        for b in e[1]:
            v = self.eval(b[1], new)
            if isinstance(b[0], list):
                if len(b[0]) != len(v):
                    raise DSLError(f"let: cannot destructure {len(v)} values into {len(b[0])} names")
                for s, x in zip(b[0], v):
                    new.vars[s.name] = x
            else:
                new.vars[b[0].name] = v
        return self.eval(e[2], new)

    def _sf_if(self, e, env):
        return self.eval(e[2] if self.eval(e[1], env) else e[3], env)

    def _sf_case(self, e, env):
        v = self.eval(e[1], env)
        for cl in e[2:]:
            if isinstance(cl[0], Sym) and cl[0].name == "else":
                return self.eval(cl[1], env)
            if cl[0] == v:
                return self.eval(cl[1], env)
        raise DSLError(f"case: no clause for {v!r}")

    def _sf_and(self, e, env):
        r = True
        for x in e[1:]:
            r = self.eval(x, env)
            if not r:
                return r
        return r

    def _sf_or(self, e, env):
        r = False
        for x in e[1:]:
            r = self.eval(x, env)
            if r:
                return r
        return r

    def _sf_implies(self, e, env):
        a = self.eval(e[1], env)
        return True if not a else self.eval(e[2], env)

    def _sf_lit(self, e, env):
        n, D = self.eval(e[1], env), self.eval(e[2], env)
        return REGISTRY["lit-point"].fn(n, D, [int(v) for v in e[3]])

    def _sf_pairs(self, e, env):
        n, default = self.eval(e[1], env), self.eval(e[2], env)
        entries = [((int(it[0][0]), int(it[0][1])), self.eval(it[1], env)) for it in e[3:]]
        return REGISTRY["pairs-point"].fn(n, default, entries)

    # generators ----------------------------------------------------------
    def _split_comp(self, e):
        gens = e[1]
        where = None
        body = None
        for x in e[2:]:
            if isinstance(x, list) and x and isinstance(x[0], Sym) and x[0].name == "where":
                where = x[1]
            else:
                body = x
        return gens, where, body

    def _iterate(self, gens, where, env, body=None, kind="for"):
        """Yield child envs for every binding combination passing `where` (nested, left to right).
        Representative domains are expanded per the symmetry policy."""
        def rec(i, cur):
            if i == len(gens):
                if where is None or self.eval(where, cur):
                    yield cur
                return
            var = gens[i][0].name
            dom = self.eval(gens[i][1], cur)
            items = self._domain_items(dom, var, gens, where, body, cur, i, kind)
            for v in items:
                yield from rec(i + 1, cur.child(**{var: v}))
        yield from rec(0, env)

    def _domain_items(self, dom, var, gens, where, body, env, i, kind):
        if isinstance(dom, frozenset):
            return sorted(dom)
        if isinstance(dom, prims.DomainList) and dom.kind == "reps":
            mode = self._reps_mode(dom, var, gens, where, body, env, i, kind)
            if mode == "G":
                return list(dom)
            out = []
            for x in dom:
                out.extend(REGISTRY["switch-class"].fn(x))
            return out
        if isinstance(dom, (list, tuple, range)):
            return list(dom)
        raise DSLError(f"cannot iterate over {type(dom).__name__} (variable {var})")

    def _reps_mode(self, dom, var, gens, where, body, env, i, kind):
        key = (id(body), id(where), var, dom.n, kind)
        if key in self.modes:
            return self.modes[key]
        rest = gens[i + 1:]

        def summary(x):
            sub = env.child(**{var: x})
            vals = []
            for c in self._iterate(rest, where, sub, body, kind):
                vals.append(self._invariant_summary(self.eval(body, c) if body is not None else True))
            return frozenset(vals) if kind == "for" else (any(vals) if kind == "exists" else all(vals))

        reps = list(dom)
        sample = reps[: min(5, len(reps))]
        mode = "G"
        for x in sample:
            base = summary(x)
            if any(summary(y) != base for y in self._probe_images(x, switchings=True)):
                mode = "Sn"
                break
        if mode == "Sn":
            for x in sample:
                base = summary(x)
                if any(summary(y) != base for y in self._probe_images(x, switchings=False)):
                    raise DSLError(f"body over representatives of vertices({dom.n}) is not even "
                                   f"permutation-invariant (variable {var}); rule ill-defined on orbit data")
        self.modes[key] = mode
        self.log.append(f"symmetry mode {mode} for {kind} over vertices({dom.n}) var {var}")
        return mode

    def _probe_images(self, x, switchings: bool):
        """Deterministic probes (swap 0<->1, swap 0<->last, reverse; switch {1}, switch {last}) + 3 seeded random
        group elements. Used to classify a body / move as G-, Sn- or label-dependent."""
        n = x.n
        P = prims.p_perm
        perms_ = [tuple([1, 0] + list(range(2, n))), tuple([n - 1] + list(range(1, n - 1)) + [0]),
                  tuple(range(n - 1, -1, -1))]
        imgs = [P(p, x) for p in perms_]
        for _ in range(3):
            p, s = group.random_element(n, self.rng)
            imgs.append(group.apply(n, p, s if switchings else 0, x))
        if switchings:
            imgs += [prims.p_switch(frozenset({1}), x), prims.p_switch(frozenset({n - 1}), x)]
        return imgs

    @staticmethod
    def _invariant_summary(v):
        if isinstance(v, Point):
            return group.canonical(v).key()
        if isinstance(v, (Verdict, bool)):
            return bool(v)
        if isinstance(v, list):
            return frozenset(Interpreter._invariant_summary(x) for x in v)
        return v

    def _sf_for(self, e, env):
        gens, where, body = self._split_comp(e)
        return [self.eval(body, c) for c in self._iterate(gens, where, env, body, "for")]

    def _binding(self, env, gens):
        return {g[0].name: _short(env.lookup(g[0].name)[1]) for g in gens}

    def _sf_forall(self, e, env):
        gens, where, body = self._split_comp(e)
        for c in self._iterate(gens, where, env, body, "forall"):
            v = self.eval(body, c)
            if not v:
                inner = v.witness if isinstance(v, Verdict) else None
                return Verdict(False, {"binding": self._binding(c, gens), "inner": inner,
                                       "values": {g[0].name: c.lookup(g[0].name)[1] for g in gens}})
        return Verdict(True)

    def _sf_exists(self, e, env):
        gens, where, body = self._split_comp(e)
        for c in self._iterate(gens, where, env, body, "exists"):
            v = self.eval(body, c)
            if v:
                return Verdict(True, {"binding": self._binding(c, gens)})
        return Verdict(False)

    def _sf_first(self, e, env):
        gens, where, body = self._split_comp(e)
        for c in self._iterate(gens, where, env, body, "first"):
            v = self.eval(body, c)
            if v is not False and v is not None and not (isinstance(v, Verdict) and not v):
                return v
        return False

    def _sf_min_over(self, e, env):
        gens, where, body = self._split_comp(e)
        vals = [self.eval(body, c) for c in self._iterate(gens, where, env, body, "for")]
        if not vals:
            raise DSLError("min-over: empty domain")
        return min(vals)

    def _sf_max_over(self, e, env):
        gens, where, body = self._split_comp(e)
        vals = [self.eval(body, c) for c in self._iterate(gens, where, env, body, "for")]
        if not vals:
            raise DSLError("max-over: empty domain")
        return max(vals)

    def _sf_count(self, e, env):
        gens, where, body = self._split_comp(e)
        return sum(1 for c in self._iterate(gens, where, env, body, "for") if self.eval(body, c))

    # ------------------------------------------------------------------ moves
    def apply_move_raw(self, mv: Move, args: List[Point]) -> List[Point]:
        if len(args) != len(mv.params):
            raise DSLError(f"move {mv.name}: expected {len(mv.params)} points")
        out = self.eval(mv.body, self.globals.child(**dict(zip(mv.params, args))))
        if not isinstance(out, list):
            raise DSLError(f"move {mv.name} must return a list")
        return [p for p in out if isinstance(p, Point)]

    def move_mode(self, mv: Move, args: List[Point]) -> str:
        key = (mv.name,) + tuple(a.n for a in args)
        if key in self.modes:
            return self.modes[key]

        def keys(xs):
            # orbit keys of the outputs: bliss-based canonical form (exact, any n; same orbit partition as
            # group.canonical, validated in scripts/phase9/validate_canon_large.py). group.canonical enumerates all
            # n! permutations and takes minutes for the size-10 outputs of a size-9 input.
            from ..canon_large import canonical_key
            return frozenset(canonical_key(p) for p in self.apply_move_raw(mv, xs))

        base = keys(args)

        def variants(sw):
            # vary one argument at a time through the probe images (independent actions on each input)
            for pos, a in enumerate(args):
                for y in self._probe_images(a, switchings=sw):
                    yield args[:pos] + [y] + args[pos + 1:]

        mode = "G"
        if any(keys(v) != base for v in variants(True)):
            mode = "Sn"
            if any(keys(v) != base for v in variants(False)):
                raise DSLError(f"move {mv.name} is not permutation-equivariant on sizes "
                               f"{[a.n for a in args]}; quantify over label choices inside the move")
        self.modes[key] = mode
        self.log.append(f"move {mv.name} sizes {[a.n for a in args]}: mode {mode}")
        return mode

    def apply_move(self, mv: Move, args: List[Point], as_orbits: bool = False) -> List[Point]:
        """Apply a move. With as_orbits=True the inputs are orbit representatives and the result covers the
        images of the whole orbits (switching-class expansion when the move is only Sn-equivariant)."""
        if not as_orbits:
            return self.apply_move_raw(mv, args)
        mode = self.move_mode(mv, args)
        if mode == "G":
            return self.apply_move_raw(mv, args)
        out = []
        classes = [REGISTRY["switch-class"].fn(a) for a in args]
        for combo in itertools.product(*classes):
            out.extend(self.apply_move_raw(mv, list(combo)))
        return out

    def _sf_closure(self, e, env):
        from .closure import run_closure
        seeds = self.eval(e[1], env)
        moves = self.eval(e[2], env)
        opts = {}
        i = 3
        while i < len(e):
            opts[e[i].name] = self.eval(e[i + 1], env)
            i += 2
        return run_closure(self, seeds, moves, **{k.replace("-", "_"): v for k, v in opts.items()})


def _short(v):
    if isinstance(v, Point):
        return f"<{v.n}|{v.D}|{','.join(map(str, v.nums))}>"
    if isinstance(v, frozenset):
        return "{" + " ".join(map(str, sorted(v))) + "}"
    if isinstance(v, (list, tuple)) and len(v) > 8:
        return f"[{len(v)} items]"
    return v
