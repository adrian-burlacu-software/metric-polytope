"""Thin Python builder for hand-writing DSL programs. Programs stay data (nested lists of Sym/atoms).

    from metricpoly.dsl.builder import S, define, generative, to_source
    prog = generative("gen-cuts", "n", for_([("S", S.subsets("n"))], S.cut("n", "S")))
    print(to_source(prog))
"""
from __future__ import annotations

from fractions import Fraction

from .sexpr import Kw, NodeSetLit, Sym, write


def _x(v):
    if isinstance(v, str):
        return Sym(v)
    if isinstance(v, (set, frozenset)):
        return NodeSetLit(tuple(sorted(v)))
    if isinstance(v, tuple):
        return [_x(a) for a in v]
    return v


class _S:
    """S.name(args...) -> (name args...) ; trailing underscore stripped, '_' -> '-'."""
    def __getattr__(self, name):
        op = name.rstrip("_").replace("_", "-")

        def make(*args):
            return [Sym(op)] + [_x(a) for a in args]
        return make


S = _S()


def gens(*pairs):
    return [[Sym(v), _x(d)] for v, d in pairs]


def for_(binds, body, where=None):
    out = [Sym("for"), gens(*binds)]
    if where is not None:
        out.append([Sym("where"), _x(where)])
    return out + [_x(body)]


def define(name, params, body, **meta):
    sig = [Sym(name)] + [Sym(p) for p in params] if params is not None else Sym(name)
    return [Sym("define"), sig] + _meta(meta) + [_x(body)]


def generative(name, param, body, **meta):
    return [Sym("generative"), Sym(name), [Sym(param)]] + _meta(meta) + [_x(body)]


def structural(name, param, body, **meta):
    return [Sym("structural"), Sym(name), [Sym(param)]] + _meta(meta) + [_x(body)]


def move(name, params, body, **meta):
    return [Sym("move"), Sym(name), [Sym(p) for p in params]] + _meta(meta) + [_x(body)]


def _meta(meta):
    out = []
    for k, v in meta.items():
        out += [Kw(k.replace("_", "-")), v]
    return out


def to_source(*forms) -> str:
    return "\n".join(write(f) for f in forms)
