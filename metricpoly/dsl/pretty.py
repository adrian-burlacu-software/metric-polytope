"""Render DSL expressions as readable formulas (Unicode or LaTeX) for the write-up."""
from __future__ import annotations

from fractions import Fraction

from .registry import REGISTRY
from .sexpr import Kw, NodeSetLit, Sym, write

SF_UNI = {
    "and": " ∧ ", "or": " ∨ ",
}


def render(e, style: str = "unicode") -> str:
    tex = style == "latex"
    r = lambda x: render(x, style)
    if isinstance(e, bool):
        return ("\\top" if e else "\\bot") if tex else ("⊤" if e else "⊥")
    if isinstance(e, Fraction):
        return f"\\tfrac{{{e.numerator}}}{{{e.denominator}}}" if tex else f"{e.numerator}/{e.denominator}"
    if isinstance(e, (int, str)):
        return str(e)
    if isinstance(e, Kw):
        return e.name
    if isinstance(e, NodeSetLit):
        inner = ",".join(map(str, e.items))
        return f"\\{{{inner}\\}}" if tex else "{" + inner + "}"
    if isinstance(e, Sym):
        return e.name if not tex else ("\\mathit{" + e.name.replace("-", "\\text{-}") + "}" if len(e.name) > 1 else e.name)
    if not isinstance(e, list) or not e:
        return write(e)
    h = e[0].name if isinstance(e[0], Sym) else None
    gens = lambda gs: ", ".join(f"{r(g[0])} ∈ {r(g[1])}" if not tex else f"{r(g[0])}\\in {r(g[1])}" for g in gs)

    def comp(e):
        gs, where, body = e[1], None, None
        for x in e[2:]:
            if isinstance(x, list) and x and isinstance(x[0], Sym) and x[0].name == "where":
                where = x[1]
            else:
                body = x
        return gs, where, body
    if h in ("and", "or"):
        op = (" \\wedge " if h == "and" else " \\vee ") if tex else SF_UNI[h]
        return "(" + op.join(r(x) for x in e[1:]) + ")"
    if h == "implies":
        return f"({r(e[1])} {'\\Rightarrow' if tex else '⇒'} {r(e[2])})"
    if h == "if":
        return f"({r(e[2])} if {r(e[1])} else {r(e[3])})"
    if h == "let":
        binds = "; ".join(f"{r(b[0]) if not isinstance(b[0], list) else '(' + ','.join(map(r, b[0])) + ')'} = {r(b[1])}"
                          for b in e[1])
        return f"{r(e[2])}  where  {binds}"
    if h in ("forall", "exists"):
        gs, where, body = comp(e)
        q = ("\\forall " if h == "forall" else "\\exists ") if tex else ("∀ " if h == "forall" else "∃ ")
        cond = f" [{r(where)}]" if where is not None else ""
        return f"{q}{gens(gs)}{cond}: {r(body)}"
    if h == "for":
        gs, where, body = comp(e)
        cond = f", {r(where)}" if where is not None else ""
        return ("\\{" if tex else "{") + f"{r(body)} : {gens(gs)}{cond}" + ("\\}" if tex else "}")
    if h == "first":
        gs, where, body = comp(e)
        return f"first_{{{gens(gs)}}} {r(body)}"
    if h in ("min-over", "max-over"):
        gs, where, body = comp(e)
        op = h.split("-")[0]
        return (f"\\{op}_{{{gens(gs)}}} {r(body)}" if tex else f"{op}_{{{gens(gs)}}} {r(body)}")
    if h == "count":
        gs, where, body = comp(e)
        return f"#{{{gens(gs)} : {r(body)}}}"
    if h == "case":
        cl = "; ".join(f"{r(c[0])} ↦ {r(c[1])}" for c in e[2:])
        return f"case {r(e[1])} of {cl}"
    if h == "lit":
        return f"(1/{r(e[2])})·({' '.join(map(r, e[3]))})"
    if h == "pairs":
        ex = ", ".join(f"x{c[0][0]}{c[0][1]}={r(c[1])}" for c in e[3:])
        return f"[{r(e[2])} except {ex}]"
    if h == "closure":
        return f"Cl({r(e[1])}; {r(e[2])})"
    if h in REGISTRY:
        p = REGISTRY[h]
        tpl = p.tex if tex else p.uni
        args = [r(a) for a in e[1:] if not isinstance(a, Kw)]
        if tpl and "{" in tpl:
            try:
                return tpl.format(*args) if len(args) >= tpl.count("{") - tpl.count("{{") * 2 else tpl.format(", ".join(args))
            except (IndexError, KeyError):
                return f"{h}({', '.join(args)})"
    name = r(e[0])
    return f"{name}({', '.join(r(a) for a in e[1:])})"


def rule_formula(rule, style="unicode") -> str:
    lhs = f"{rule.name}({rule.param})"
    return f"{lhs} := {render(rule.body, style)}"
