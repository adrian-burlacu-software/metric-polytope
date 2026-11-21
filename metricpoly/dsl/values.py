"""Runtime value types of the DSL (besides core.Point, Fraction, int, bool, list, tuple, frozenset)."""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, FrozenSet, Optional, Tuple

from ..core import Point, dim, pairs, pidx


def Q(v) -> Fraction:
    return v if isinstance(v, Fraction) else Fraction(v)


@dataclass(frozen=True)
class Mid:
    """Rectangular exact matrix (rows x cols), e.g. the middle region T x T̄ of a split."""
    rows: int
    cols: int
    data: Tuple[Tuple[Fraction, ...], ...]

    @staticmethod
    def make(rows_data) -> "Mid":
        data = tuple(tuple(Q(v) for v in r) for r in rows_data)
        r = len(data)
        c = len(data[0]) if r else 0
        if any(len(row) != c for row in data):
            raise ValueError("ragged middle")
        return Mid(r, c, data)

    def __getitem__(self, ij):
        return self.data[ij[0]][ij[1]]

    def values(self):
        return [v for r in self.data for v in r]

    def transpose(self) -> "Mid":
        return Mid(self.cols, self.rows, tuple(zip(*self.data)) if self.rows else ())

    def to_json(self):
        return [[str(v) for v in r] for r in self.data]


@dataclass(frozen=True)
class Partial:
    """Point with holes: known[(i,j)] for i<j; holes are the missing pairs."""
    n: int
    known: Tuple[Tuple[Tuple[int, int], Fraction], ...]

    @staticmethod
    def make(n: int, known: Dict[Tuple[int, int], Fraction]) -> "Partial":
        return Partial(n, tuple(sorted(((min(i, j), max(i, j)), Q(v)) for (i, j), v in known.items())))

    def as_dict(self):
        return dict(self.known)

    def holes(self):
        k = self.as_dict()
        return [p for p in pairs(self.n) if p not in k]


@dataclass(frozen=True)
class Graph:
    n: int
    edges: FrozenSet[Tuple[int, int]]

    @staticmethod
    def make(n: int, edges) -> "Graph":
        es = set()
        for e in edges:
            i, j = int(e[0]), int(e[1])
            if i == j or not (0 <= i < n and 0 <= j < n):
                raise ValueError(f"bad edge {e} for n={n}")
            es.add((min(i, j), max(i, j)))
        return Graph(n, frozenset(es))

    def sorted_edges(self):
        return sorted(self.edges)

    def adj(self):
        a = {i: set() for i in range(self.n)}
        for i, j in self.edges:
            a[i].add(j)
            a[j].add(i)
        return a


@dataclass(frozen=True)
class Tree:
    """Decomposition tree node: label + payload + children (all hashable)."""
    label: str
    payload: Tuple = ()
    children: Tuple["Tree", ...] = ()

    def to_json(self):
        def enc(v):
            if isinstance(v, Point):
                return {"point": v.strs(), "n": v.n}
            if isinstance(v, Mid):
                return {"mid": v.to_json()}
            if isinstance(v, (frozenset, set)):
                return sorted(v)
            if isinstance(v, Fraction):
                return str(v)
            if isinstance(v, tuple):
                return [enc(x) for x in v]
            return v
        return {"label": self.label, "payload": [enc(p) for p in self.payload],
                "children": [c.to_json() for c in self.children]}
