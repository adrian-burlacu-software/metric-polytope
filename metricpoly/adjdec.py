"""Recursive adjacency decomposition (Bremner–Dutour Sikirić–Schürmann style) for the extreme rays of a tangent cone,
up to the permutation symmetry that fixes the base point.

Setting: a pointed polyhedral cone C = {d in R^m : A d <= 0} over the pairs of K_n (m = C(n,2)), invariant under
G_F = {sigma in S_n : sigma fixes every vector in F} (F = the points fixed so far: the cut ray, then the ray we
recursed at, ...). The extreme rays of C are the vertices of the polytope P = C ∩ {a·d = -1}, where a = sum of the rows
of A (a·d < 0 on C \\ {0} because C is pointed and A has full rank). Vertices of P are enumerated orbit by orbit under
G_F: start from an exact LP vertex, and for each orbit representative compute its neighbours from the extreme rays of
its own tangent cone, either directly (cdd for small cones, Normaliz for medium ones) or recursively with one more
fixed vector (for very degenerate ones).

Exactness: every vertex is checked exactly (feasible, tight rows of certified rank m); canonical forms are bliss
canonical labellings of the pair-incidence graph coloured by the tuples (F_e..., d_e), so two points have the same key
iff they lie in the same G_F orbit; orbit sizes are |G_F| / |Aut(coloured graph)|.
"""
from __future__ import annotations

import json
import math
import subprocess
import os
import time
from functools import lru_cache
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import cdd
import cdd.gmp
import igraph as ig
import numpy as np

from . import resguard
from .core import pairs

ROOT = Path(__file__).resolve().parents[1]
NMZ = ROOT / "tools" / "normaliz-3.11.1" / "normaliz-3.11.1" / "normaliz.exe"
NMZ_WORK = ROOT / "checkpoints" / "phase10" / "nmz_rec"

# Engine choice by the cone's excess = rows - dimension (how far from simple it is), not by raw row count:
CDD_EXCESS = 8      # excess <= this: cdd in-process (near-simple, fast, no process launch; cannot be timed out)
NMZ_EXCESS = 30     # excess <= this: Normaliz without a time limit
MAX_DEPTH = 3       # beyond: Normaliz with a budget, recursion on timeout (at depth MAX_DEPTH: no budget)

Point = Tuple[int, Tuple[int, ...]]          # (D, nums): the rational point nums / D


# ------------------------------------------------------------------ exact H-polytope {x : A x <= b}
class HPoly:
    def __init__(self, A: np.ndarray, b: Sequence[int]):
        self.A = np.asarray(A, dtype=np.int64)
        self.b = np.asarray(b, dtype=np.int64)
        self.m = self.A.shape[1]

    def slacks(self, D, nums):
        return D * self.b - self.A @ np.asarray(nums, dtype=np.int64)

    def tight(self, D, nums):
        return np.nonzero(self.slacks(D, nums) == 0)[0]

    def is_vertex(self, D, nums) -> bool:
        s = self.slacks(D, nums)
        if (s < 0).any():
            return False
        T = np.nonzero(s == 0)[0]
        if len(T) < self.m:
            return False
        from .dsl.prims import certified_rank_is
        return bool(certified_rank_is(self.A[T], self.m))

    def step(self, D, nums, d) -> Point:
        """From vertex (D, nums) along direction d (integer list) to the first leaving facet."""
        s = self.slacks(D, nums)
        best = None
        for i in np.nonzero(s != 0)[0]:
            ad = sum(int(self.A[i, t]) * int(d[t]) for t in range(self.m) if self.A[i, t] and d[t])
            if ad > 0:
                ti = Fraction(int(s[i]), D * ad)
                if best is None or ti < best:
                    best = ti
        if best is None:
            raise RuntimeError("unbounded edge")
        y = [Fraction(int(v), D) + best * int(d[t]) for t, v in enumerate(nums)]
        Dy = 1
        for f in y:
            Dy = Dy * f.denominator // math.gcd(Dy, f.denominator)
        return int(Dy), tuple(int(f * Dy) for f in y)

    def lp_vertex(self, c: Sequence[int]) -> Point:
        """Exact optimal basic solution of max c·x over the polytope (cdd gmp LP)."""
        rows = [[Fraction(int(bi))] + [Fraction(-int(v)) for v in row] for bi, row in zip(self.b, self.A)]
        rows.append([Fraction(0)] + [Fraction(int(v)) for v in c])
        lp = cdd.gmp.linprog_from_array(rows, cdd.LPObjType.MAX)
        cdd.gmp.linprog_solve(lp)
        if lp.status != cdd.LPStatusType.OPTIMAL:
            raise RuntimeError(f"LP status {lp.status}")
        x = [Fraction(v) for v in lp.primal_solution]
        D = 1
        for f in x:
            D = D * f.denominator // math.gcd(D, f.denominator)
        return int(D), tuple(int(f * D) for f in x)


# ------------------------------------------------------------------ cone rays: cdd / Normaliz
def cone_rays_cdd(AT: np.ndarray) -> List[Tuple[int, ...]]:
    mat = cdd.gmp.matrix_from_array([[Fraction(0)] + [Fraction(-int(v)) for v in row] for row in AT],
                                    rep_type=cdd.RepType.INEQUALITY)
    gens = cdd.gmp.copy_generators(cdd.gmp.polyhedron_from_matrix(mat))
    if gens.lin_set:
        raise RuntimeError("cone not pointed")
    out = []
    for r in gens.array:
        if r[0] != 0:
            continue
        fr = [Fraction(v) for v in r[1:]]
        L = 1
        for f in fr:
            L = L * f.denominator // math.gcd(L, f.denominator)
        iv = [int(f * L) for f in fr]
        g = math.gcd(*iv)
        out.append(tuple(v // g for v in iv))
    return out


def cone_rays_nmz(AT: np.ndarray, tag: str, threads: int = 1) -> List[Tuple[int, ...]]:
    NMZ_WORK.mkdir(parents=True, exist_ok=True)
    inp = NMZ_WORK / f"{tag}.in"
    rows = "\n".join(" ".join(str(-int(v)) for v in r) for r in AT)
    inp.write_text(f"amb_space {AT.shape[1]}\ninequalities {len(AT)}\n{rows}\nExtremeRays\n", encoding="ascii")
    cp = subprocess.run([str(NMZ), "-c", f"-x={threads}", str(inp)], capture_output=True, text=True, cwd=NMZ_WORK)
    if cp.returncode != 0:
        raise RuntimeError(f"normaliz failed: {cp.stderr[-500:]}")
    outf = NMZ_WORK / f"{tag}.out"
    lines = outf.read_text().splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().endswith("extreme rays:"):
            k = int(ln.split()[0])
            rays = [tuple(int(v) for v in lines[i + 1 + t].split()) for t in range(k)]
            inp.unlink(missing_ok=True)
            outf.unlink(missing_ok=True)
            return rays
    raise RuntimeError("no extreme rays section in normaliz output")


# ------------------------------------------------------------------ symmetry: G_F = Stab_{S_n}(F)
def _colored_graph(n: int, cols: List[tuple]):
    pr = pairs(n)
    palette = {c: i + 1 for i, c in enumerate(sorted(set(cols)))}
    edges = []
    for e, (i, j) in enumerate(pr):
        edges += [(i, n + e), (j, n + e)]
    return ig.Graph(n=n + len(pr), edges=edges), [0] * n + [palette[c] for c in cols]


def fix_key(n: int, F: List[Tuple[int, ...]], p: Point) -> str:
    """Canonical key of point p under G_F. Vectors may carry extra coordinates after the C(n,2) pair coordinates
    (e.g. a homogenising coordinate); S_n fixes them, so they enter the key verbatim and do not colour the graph."""
    D, nums = p
    m = len(pairs(n))
    cols = [tuple(f[e] for f in F) + (int(nums[e]),) for e in range(m)]
    g, colors = _colored_graph(n, cols)
    lab = g.canonical_permutation(color=colors)
    order = [v for v in lab if v < n]
    pr = pairs(n)
    idx = {e: t for t, e in enumerate(pr)}
    vals = [cols[idx[(min(order[a], order[b]), max(order[a], order[b]))]] for a, b in pr]
    ext = "" if len(nums) == m else "/" + ",".join(str(int(v)) for v in nums[m:])
    return f"{D}{ext}|" + ";".join(",".join(map(str, c)) for c in vals)


def group_order(n: int, F: List[Tuple[int, ...]]) -> int:
    m = len(pairs(n))
    return _group_order(n, tuple(tuple(f[:m]) for f in F))


@lru_cache(maxsize=4096)
def _group_order(n, F) -> int:
    cols = [tuple(f[e] for f in F) for e in range(len(pairs(n)))]
    g, colors = _colored_graph(n, cols)
    return g.count_automorphisms(color=colors)


def orbit_size(n: int, F: List[Tuple[int, ...]], p: Point) -> int:
    D, nums = p
    cols = [tuple(f[e] for f in F) + (int(nums[e]),) for e in range(len(pairs(n)))]
    g, colors = _colored_graph(n, cols)
    return group_order(n, F) // g.count_automorphisms(color=colors)


# ------------------------------------------------------------------ dynamic engine choice + recursion
#
# solve_cone picks, per cone, the cheapest exact route:
#   excess = rows - cone dim <= CDD_EXCESS        -> cdd in-process (no process launch)
#   excess <= NMZ_EXCESS or depth = MAX_DEPTH    -> Normaliz, no time limit
#   otherwise                          -> Normaliz with a time budget; on timeout, recurse (adjacency decomposition
#                                         of the cone's section under the stabiliser, one more fixed vector)
# decompose (sequential) and decompose_parallel (top level, multiprocessing) both process orbits cheapest first
# (fewest tight rows) and stop by Balinski's theorem once the not-yet-expanded orbits contain fewer vertices in total
# than the dimension of the section (the graph of a d-polytope is d-connected, so removing < d vertices keeps it
# connected; all other vertices have been expanded, hence the found set is complete). See BDS, Theorem 5.1.

NMZ_BUDGET = 120.0  # seconds before a degenerate cone falls back to recursion


class Stats:
    def __init__(self):
        self.calls = {"cdd": 0, "nmz": 0, "nmz_timeout": 0, "nmz_memcap": 0, "rec": 0, "balinski_skips": 0}
        self.max_depth = 0

    def merge(self, other: dict):
        for k, v in other.get("calls", {}).items():
            self.calls[k] = self.calls.get(k, 0) + v
        self.max_depth = max(self.max_depth, other.get("max_depth", 0))

    def as_dict(self):
        return {"calls": dict(self.calls), "max_depth": self.max_depth}


class Ctx:
    def __init__(self, threads=1, stopfile: Path = None, tag="c"):
        self.threads = threads
        self.stopfile = stopfile
        self.tag = tag
        self.stats = Stats()

    def stopped(self):
        return self.stopfile is not None and self.stopfile.exists()


class Stopped(Exception):
    pass


class NmzTimeout(Exception):
    pass


def _nmz_run(AT, tag, threads, budget, ctx):
    NMZ_WORK.mkdir(parents=True, exist_ok=True)
    tag = f"{tag}_p{os.getpid()}"
    inp = NMZ_WORK / f"{tag}.in"
    outf = NMZ_WORK / f"{tag}.out"
    rows = "\n".join(" ".join(str(-int(v)) for v in r) for r in AT)
    # Dual input: C = {AT d <= 0} is the dual of the cone generated by the rows of -AT, so its extreme rays are the
    # support hyperplanes of that cone. This skips Normaliz's serial "minimise the given support hyperplanes" hull,
    # which for inequality input runs over the whole ray set (checked identical on the MET_7 cut cone).
    inp.write_text(f"amb_space {AT.shape[1]}\ncone {len(AT)}\n{rows}\nSupportHyperplanes\n", encoding="ascii")
    pr = subprocess.Popen([str(NMZ), "-c", f"-x={threads}", str(inp)], stdout=subprocess.DEVNULL,
                          stderr=subprocess.PIPE, cwd=NMZ_WORK)
    t0 = time.time()
    k = 0
    try:
        while True:
            try:
                pr.wait(timeout=0.5)
                break
            except subprocess.TimeoutExpired:
                if ctx.stopped():
                    raise Stopped()
                if budget is not None and time.time() - t0 > budget:
                    raise NmzTimeout()
                k += 1
                if k % 10 == 0:                                   # every ~5 s: memory and disk guards
                    if resguard.private_gb(pr.pid) > resguard.NMZ_MEM_GB:
                        ctx.stats.calls["nmz_memcap"] += 1
                        raise NmzTimeout()                        # too big for one call: recurse instead
                    resguard.require_disk()                       # LowDisk stops the whole job
    except BaseException:
        pr.kill()
        pr.wait()
        inp.unlink(missing_ok=True)
        outf.unlink(missing_ok=True)
        raise
    if pr.returncode != 0:
        keep = NMZ_WORK / f"failed_{tag}.in"                          # keep the input for diagnosis (small)
        inp.replace(keep)
        outf.unlink(missing_ok=True)
        raise RuntimeError(f"normaliz failed: exit {pr.returncode} ({hex(pr.returncode & 0xFFFFFFFF)}), "
                           f"{len(AT)} rows x {AT.shape[1]}, input kept at {keep}: {pr.stderr.read()[-500:]}")
    lines = outf.read_text().splitlines()
    inp.unlink(missing_ok=True)
    outf.unlink(missing_ok=True)
    for i, ln in enumerate(lines):
        if ln.strip().endswith("support hyperplanes:") and ln.split()[0].isdigit():
            k = int(ln.split()[0])
            return [tuple(int(v) for v in lines[i + 1 + t].split()) for t in range(k)]
    raise RuntimeError("no support hyperplanes section in normaliz output")


def section(AT: np.ndarray) -> HPoly:
    """P = {d : AT d <= 0, a·d = -1}, a = sum of rows of AT."""
    a = AT.sum(axis=0)
    A = np.vstack([AT, a[None, :], -a[None, :]])
    b = np.concatenate([np.zeros(len(AT), dtype=np.int64), [-1, 1]])
    return HPoly(A, b)


def _primitive(nums) -> Tuple[int, ...]:
    g = math.gcd(*[int(v) for v in nums])
    return tuple(int(v) // g for v in nums)


def _rays_to_orbits(n, AT, F, rays):
    out = {}
    a = AT.sum(axis=0)
    for r in rays:
        s = -int(np.dot(a, np.asarray(r, dtype=object)))
        g = math.gcd(s, *r)
        p = (s // g, tuple(int(v) // g for v in r))
        k = fix_key(n, F, p)
        if k not in out:
            out[k] = (p, orbit_size(n, F, p))
    return out


def _n_lines(AT) -> int:
    """Number of rows r of AT whose negative -r is also a row (counted once per pair)."""
    S = {tuple(int(v) for v in r) for r in AT}
    return sum(1 for r in S if tuple(-v for v in r) in S and r > tuple(-v for v in r))


def solve_cone(n, AT, F, cone_dim, depth, ctx: Ctx, force_recurse=False):
    """Orbit representatives under G_F of the extreme rays of {AT d <= 0} (a pointed cone of dimension cone_dim),
    as {key: ((D, nums) on the section a·d = -1, orbit size)}."""
    if ctx.stopped():
        raise Stopped()
    ctx.stats.max_depth = max(ctx.stats.max_depth, depth)
    rows = len(AT)
    if not force_recurse:
        excess = rows - 2 * _n_lines(AT) - cone_dim       # each ±row pair (a line of the dual) cuts one dimension
        if excess <= CDD_EXCESS:
            ctx.stats.calls["cdd"] += 1
            return _rays_to_orbits(n, AT, F, cone_rays_cdd(AT))
        budget = None if (excess <= NMZ_EXCESS or depth >= MAX_DEPTH) else NMZ_BUDGET
        try:
            rays = _nmz_run(AT, f"{ctx.tag}_{depth}_{rows}", ctx.threads, budget, ctx)
            ctx.stats.calls["nmz"] += 1
            return _rays_to_orbits(n, AT, F, rays)
        except NmzTimeout:
            ctx.stats.calls["nmz_timeout"] += 1
        except RuntimeError:
            # Normaliz 3.11.1 can exit with code 3 after "Cone not pointed. Restarting computation" (seen on a
            # simplicial cone given with 4 ±row pairs). cdd is exact; use it instead.
            ctx.stats.calls["nmz_fail_cdd"] = ctx.stats.calls.get("nmz_fail_cdd", 0) + 1
            return _rays_to_orbits(n, AT, F, cone_rays_cdd(AT))
    ctx.stats.calls["rec"] += 1
    return decompose(n, AT, F, cone_dim, depth, ctx)


def expand(n, P: HPoly, F, p: Point, cone_dim, depth, ctx: Ctx):
    """Neighbours (exact vertices of P) of vertex p, one per G_{F+p}-orbit of edges."""
    T = P.tight(*p)
    sub = solve_cone(n, P.A[T], F + [_primitive(p[1])], cone_dim - 1, depth + 1, ctx)
    out = []
    for (_, dnums), _sz in sub.values():
        q = P.step(p[0], p[1], dnums)
        if not P.is_vertex(*q):
            raise RuntimeError("neighbour step did not land on a vertex")
        out.append(q)
    return out


def _start(P, tries: int = 1):
    """An exact LP vertex; with tries > 1, the least degenerate (fewest tight rows) of that many random LP vertices,
    so that the first expansions are cheap and the queue fills before the degenerate orbits are reached."""
    rng = np.random.default_rng(12345)
    best = None
    for _ in range(tries):
        q = P.lp_vertex(rng.integers(-1000, 1000, size=P.m).tolist())
        if best is None or len(P.tight(*q)) < len(P.tight(*best)):
            best = q
    if not P.is_vertex(*best):
        raise RuntimeError("LP start is not a vertex")
    return best


def decompose(n, AT, F, cone_dim, depth, ctx: Ctx):
    """Sequential adjacency decomposition of the section of {AT d <= 0} under G_F, cheapest orbits first,
    with the Balinski stop. cone_dim = dimension of the cone; the section has dimension cone_dim - 1."""
    import heapq
    P = section(AT)
    d_sec = cone_dim - 1
    start = _start(P)
    found, size, heap = {}, {}, []

    def add(q):
        k = fix_key(n, F, q)
        if k not in found:
            found[k] = q
            size[k] = orbit_size(n, F, q)
            heapq.heappush(heap, (len(P.tight(*q)), k))
            return size[k]
        return 0

    remaining = add(start)
    expanded = 0
    while heap:
        if expanded and remaining < d_sec:              # Balinski needs a non-empty expanded set
            ctx.stats.calls["balinski_skips"] += len(heap)
            break
        expanded += 1
        _, k = heapq.heappop(heap)
        remaining -= size[k]
        for q in expand(n, P, F, found[k], cone_dim, depth, ctx):
            remaining += add(q)
    return {k: (p, size[k]) for k, p in found.items()}


# ------------------------------------------------------------------ parallel top level
_W = {}


def _winit(A, b, n, F, cone_dim, stopfile):
    _W.update(P=HPoly(A, b), n=n, F=F, cone_dim=cone_dim, stopfile=stopfile)


def _wtask(key, p, threads, tag):
    ctx = Ctx(threads=threads, stopfile=_W["stopfile"], tag=tag)
    t0 = time.time()
    try:
        nb = expand(_W["n"], _W["P"], _W["F"], p, _W["cone_dim"], 0, ctx)
    except Stopped:
        return key, None, None, 0.0
    return key, [[q[0], list(q[1])] for q in nb], ctx.stats.as_dict(), time.time() - t0


def decompose_parallel(n, AT, F, cone_dim, workers, ckpt: Path, log=print, deadline=None, mem_floor_gb=6.0,
                       star=None):
    """Top-level adjacency decomposition with a process pool. Checkpoint: one JSONL line per expanded orbit
    {key, p, nbrs, stats, secs}; resumes from it. Returns ({key: (p, size)}, Stats, info).
    Raises Stopped (after stopping the workers; resumable from the checkpoint) when time.time() passes `deadline`,
    when the file ckpt.with_suffix('.halt') exists, or when available RAM drops below mem_floor_gb.

    star: optional predicate on a vertex p of the section, true iff p lies on one fixed face Φ of the section (the same
    face for all p; e.g. the facet dual to a G_F-fixed vertex of the primal). Vertices with star(p) false are expanded
    first, and the walk stops once every unexpanded found vertex lies on Φ (Theorem 1 of Deza–Dutour Sikirić 2015,
    second criterion). Proof: the vertices of a polytope off a face Φ induce a connected subgraph (monotone paths for
    the functional supporting Φ), every vertex on Φ has a neighbour off Φ, so every unfound vertex is joined to an
    expanded vertex off Φ by a path avoiding the unexpanded found vertices; the first unfound vertex on it would be a
    neighbour of an expanded vertex, hence found."""
    import heapq
    import multiprocessing as mp
    P = section(AT)
    d_sec = cone_dim - 1
    stopfile = ckpt.with_suffix(".stop")
    stopfile.unlink(missing_ok=True)
    stats = Stats()
    found, size, rows, done = {}, {}, {}, set()

    def add(q):
        k = fix_key(n, F, q)
        if k not in found:
            found[k] = q
            size[k] = orbit_size(n, F, q)
            rows[k] = len(P.tight(*q))
        return k

    add(_start(P, tries=16))
    if ckpt.exists():
        for ln in ckpt.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(ln)
            except json.JSONDecodeError:
                continue                       # partial last line from an interruption
            p = (r["p"][0], tuple(r["p"][1]))
            add(p)
            for D, nums in r["nbrs"]:
                add((D, tuple(nums)))
            done.add(r["key"])
            stats.merge(r["stats"])
    log(f"resume: {len(done)} expanded, {len(found)} found")
    onst = (lambda k: bool(star(found[k]))) if star else (lambda k: False)
    heap = [(onst(k), rows[k], k) for k in found if k not in done]
    heapq.heapify(heap)
    inflight = {}
    t0 = time.time()
    ctxp = mp.get_context("spawn")
    pool = ctxp.Pool(workers, initializer=_winit, initargs=(P.A, P.b, n, F, cone_dim, stopfile))
    skipped = []
    try:
        with open(ckpt, "a", encoding="utf-8") as fh:
            while True:
                remaining = sum(size[k] for k in found if k not in done)
                if done and remaining < d_sec:             # Balinski needs a non-empty expanded set
                    skipped = [k for k in found if k not in done]
                    stats.calls["balinski_skips"] += len(skipped)
                    break
                if star and done and not inflight and all(onst(k) for k in found if k not in done):
                    skipped = [k for k in found if k not in done]
                    stats.calls["star_skips"] = stats.calls.get("star_skips", 0) + len(skipped)
                    log(f"star criterion: {len(skipped)} unexpanded orbits all on the fixed face; done")
                    break
                while heap and len(inflight) < workers:
                    if star and done and onst(heap[0][2]):
                        break                                  # only face orbits left in the queue: never start them
                    _, _, k = heapq.heappop(heap)
                    thr = max(1, workers // (len(inflight) + 1 + len(heap))) if len(heap) < workers else 1
                    inflight[k] = pool.apply_async(_wtask, (k, found[k], thr, f"w{len(done)}_{len(inflight)}"))
                if not inflight:
                    break
                time.sleep(0.2)
                if deadline is not None and time.time() > deadline:
                    log("deadline reached: stopping (resumable)")
                    raise Stopped()
                if ckpt.with_suffix(".halt").exists():
                    log("halt file found: stopping (resumable)")
                    raise Stopped()
                import psutil
                if psutil.virtual_memory().available < mem_floor_gb * 2 ** 30:
                    log(f"available RAM below {mem_floor_gb} GB: stopping (resumable)")
                    raise Stopped()
                for k in [k for k, ar in inflight.items() if ar.ready()]:
                    key, nbrs, st, secs = inflight.pop(k).get()
                    if nbrs is None:
                        continue
                    new = 0
                    for D, nums in nbrs:
                        q = (D, tuple(nums))
                        before = len(found)
                        kq = add(q)
                        if len(found) > before:
                            heapq.heappush(heap, (onst(kq), rows[kq], kq))
                            new += 1
                    done.add(key)
                    stats.merge(st)
                    fh.write(json.dumps({"key": key, "p": [found[key][0], list(found[key][1])], "rows": rows[key],
                                         "nbrs": nbrs, "stats": st, "secs": round(secs, 2)}) + "\n")
                    fh.flush()
                    log(f"expanded {len(done)} (rows {rows[key]}, {secs:.1f} s, +{new} new): found {len(found)}, "
                        f"queue {len(heap)}, in flight {len(inflight)}, {time.time() - t0:.0f} s, {stats.calls}")
    finally:
        stopfile.touch()
        time.sleep(1.5)                        # let workers kill their Normaliz children
        pool.terminate()
        pool.join()
        stopfile.unlink(missing_ok=True)
    info = {"expanded": len(done), "balinski_skipped_orbits": len(skipped), "skip_rule": (
                "star" if stats.calls.get("star_skips") else "balinski" if skipped else None),
            "balinski_skipped_vertices": sum(size[k] for k in skipped), "section_dim": d_sec}
    return {k: (p, size[k]) for k, p in found.items()}, stats, info
