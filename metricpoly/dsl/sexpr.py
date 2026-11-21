"""S-expression reader / writer for the rule DSL (programs are data).

Atoms: integers, rationals (2/3, -1/6), #t / #f, strings "...", keywords :name, node-set literals {0 1 2},
symbols. Comments start with ';'. `write(read(s))` round-trips up to whitespace and comments.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, List


@dataclass(frozen=True)
class Sym:
    name: str

    def __repr__(self):
        return self.name


@dataclass(frozen=True)
class Kw:
    name: str

    def __repr__(self):
        return ":" + self.name


@dataclass(frozen=True)
class NodeSetLit:
    items: tuple

    def __repr__(self):
        return "{" + " ".join(map(str, self.items)) + "}"


class ParseError(ValueError):
    pass


_TOKEN = re.compile(r"""
    (?P<ws>\s+) | (?P<comment>;[^\n]*) | (?P<lp>\() | (?P<rp>\)) | (?P<lb>\{) | (?P<rb>\}) |
    (?P<str>"(?:[^"\\]|\\.)*") | (?P<atom>[^\s(){}";]+)
""", re.VERBOSE)
_INT = re.compile(r"^[+-]?\d+$")
_RAT = re.compile(r"^[+-]?\d+/\d+$")


def _atom(tok: str, line: int):
    if _INT.match(tok):
        return int(tok)
    if _RAT.match(tok):
        f = Fraction(tok)
        return f if f.denominator != 1 else int(f)
    if tok == "#t":
        return True
    if tok == "#f":
        return False
    if tok.startswith(":") and len(tok) > 1:
        return Kw(tok[1:])
    return Sym(tok)


def read_all(src: str) -> List[Any]:
    """Parse a whole file into a list of top-level forms."""
    stack: List[list] = [[]]
    braces: List[list] = []
    line = 1
    pos = 0
    while pos < len(src):
        m = _TOKEN.match(src, pos)
        if not m:
            raise ParseError(f"line {line}: cannot tokenize near {src[pos:pos+20]!r}")
        kind, text = m.lastgroup, m.group()
        line += text.count("\n")
        pos = m.end()
        if kind in ("ws", "comment"):
            continue
        if kind == "lp":
            stack.append([])
        elif kind == "rp":
            if len(stack) == 1:
                raise ParseError(f"line {line}: unexpected ')'")
            lst = stack.pop()
            stack[-1].append(lst)
        elif kind == "lb":
            braces.append([])
            stack.append(braces[-1])
        elif kind == "rb":
            if not braces or stack[-1] is not braces[-1]:
                raise ParseError(f"line {line}: unexpected '}}'")
            items = stack.pop()
            braces.pop()
            if not all(isinstance(v, int) and not isinstance(v, bool) for v in items):
                # non-literal node sets are written with (nodes ...) instead
                raise ParseError(f"line {line}: node-set literal must contain integers only")
            stack[-1].append(NodeSetLit(tuple(sorted(set(items)))))
        elif kind == "str":
            stack[-1].append(re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t"}.get(m.group(1), m.group(1)),
                                    text[1:-1]))
        else:
            stack[-1].append(_atom(text, line))
    if len(stack) != 1:
        raise ParseError("unbalanced parentheses at end of input")
    return stack[0]


def read(src: str) -> Any:
    forms = read_all(src)
    if len(forms) != 1:
        raise ParseError(f"expected exactly one form, got {len(forms)}")
    return forms[0]


def write(x: Any) -> str:
    if isinstance(x, list):
        return "(" + " ".join(write(v) for v in x) + ")"
    if isinstance(x, bool):
        return "#t" if x else "#f"
    if isinstance(x, Fraction):
        return f"{x.numerator}/{x.denominator}" if x.denominator != 1 else str(x.numerator)
    if isinstance(x, str):
        return '"' + x.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return repr(x)
