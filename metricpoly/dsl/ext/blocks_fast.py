"""Level-2 extension: fast decomposition test, same semantics as `decompose` in rules/blocks.mpr
(equality tested in tests/test_blocks.py). Orbit-invariant (all middle classes are switching-invariant)."""
from __future__ import annotations

from ... import blocks
from ..registry import primitive

_ENGINE = blocks.Engine()


@primitive("decomposes-fast", 3, "Point Nat Bool -> Bool", "dec_{{{1},{2}}}({0})", r"\mathrm{{dec}}_{{{1},{2}}}({0})",
           equivariance="G", kernel=False,
           doc="full recursive block decomposition with every middle of level <= X exists (bv: blocks are vertices)")
def decomposes_fast(x, X, bv):
    return _ENGINE.can(blocks.matrix(x), x.D, int(X), bool(bv))
