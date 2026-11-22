"""Level-2 extension for the Phase 8a ledger rule (docs/denominator_lemma.md, Theorem 4).

den-bound-ok? d n : every odd prime power p^e exactly dividing d satisfies p^e <= 2n - 3
"""
from __future__ import annotations

from ..registry import primitive


def odd_prime_powers(d: int):
    d = int(d)
    while d % 2 == 0:
        d //= 2
    out, p = [], 3
    while p * p <= d:
        if d % p == 0:
            q = 1
            while d % p == 0:
                d //= p
                q *= p
            out.append(q)
        p += 2
    if d > 1:
        out.append(d)
    return out


@primitive("den-bound-ok?", 2, "Nat Nat -> Bool", "denbound({0},{1})", r"\mathrm{{denbound}}({0},{1})", kernel=False)
def p_den_bound_ok(d, n):
    return all(q <= 2 * int(n) - 3 for q in odd_prime_powers(d))
