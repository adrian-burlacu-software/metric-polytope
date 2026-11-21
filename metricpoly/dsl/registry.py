"""Name registry for primitives. The grammar is closed: every call `(OP args...)` resolves here
(or to a DSL-defined function / rule / move). New primitives register from metricpoly/dsl/ext/ without touching
the parser or the kernel table.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Tuple


@dataclass
class Primitive:
    name: str
    fn: Callable
    arity: Tuple[int, Optional[int]]          # (min, max) ; max None = variadic
    sig: str                                   # human-readable type signature
    uni: Optional[str] = None                  # Unicode formula template, {0},{1},... = rendered args
    tex: Optional[str] = None                  # LaTeX template
    equivariance: str = "n/a"                  # 'G' | 'Sn' | 'label' | 'n/a' (not point-valued)
    kernel: bool = True
    doc: str = ""
    needs_interp: bool = False                 # fn(interp, *args)


REGISTRY: Dict[str, Primitive] = {}


def primitive(name, arity, sig, uni=None, tex=None, equivariance="n/a", kernel=True, doc="", needs_interp=False):
    if isinstance(arity, int):
        arity = (arity, arity)

    def deco(fn):
        if name in REGISTRY:
            raise ValueError(f"primitive {name!r} already registered")
        REGISTRY[name] = Primitive(name, fn, arity, sig, uni, tex, equivariance, kernel, doc, needs_interp)
        return fn
    return deco


def kernel_table() -> Dict[str, str]:
    """name -> signature for kernel primitives (hashed by the core-freeze test)."""
    return {k: f"{p.arity}|{p.sig}|{p.equivariance}" for k, p in sorted(REGISTRY.items()) if p.kernel}


def load_extensions():
    """Import every module in metricpoly/dsl/ext (level-2 growth)."""
    import importlib
    import pkgutil
    from . import ext
    for m in pkgutil.iter_modules(ext.__path__):
        importlib.import_module(f"{ext.__name__}.{m.name}")
