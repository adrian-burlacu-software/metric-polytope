"""Round-based reachability engine (Phase 9 judge).

Targets are points x (n <= 9). Nodes are the orbits (canonical keys) of all restrictions x|T, |T| >= 3, of all targets.
Each node keeps one representative: (target id, node mask). Reachability is decided over nodes:

  round 0      : node is a base piece (key in the base-key sets, or an extra exact predicate such as the n = 9
                 graph-metric test)
  round r >= 1 : UNARY moves in cost order — lift, radial (Λ^1..Λ^3, up to switching) checked backward from
                 unreached nodes; then user unary moves applied FORWARD to nodes reached in earlier rounds (every
                 intermediate of a target's derivation is a node, so forward application is exact and complete). A node is reached in round r if some predecessor for some move was reached
                 in a round <= r - 1. A reached node is crossed off and never retried with a costlier move.
  glue stage   : only when the unary rounds saturate; only on still-unreached nodes and only on splits A ∪ B = T
                 whose two parts are already reached (uncapped overlap). Then unary rounds resume. Fixpoint.

Predecessor lists are cached per (move, node) on disk, so a new base piece is pure propagation and a new move only
costs its own checks. All move checks are exact (certified rank) and identical to scripts/detour_depth2.py.
"""
from __future__ import annotations

import itertools
import json
import math
import multiprocessing as mp
import os
import pickle
import sys
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from . import group
from .core import Point

ROOT = Path(__file__).resolve().parent.parent


_D2 = {}


def _d2():
    if "m" not in _D2:
        if str(ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(ROOT / "scripts"))
        import detour_depth2 as d2
        _D2["m"] = d2
    return _D2["m"]


def _restrict(x: Point, T) -> Point:
    d2 = _d2()
    return d2.restrict(d2.matrix(x), x.D, list(T))


def _bits(mask):
    return [v for v in range(mask.bit_length()) if (mask >> v) & 1]


# ------------------------------------------------------------------ worker functions (module level for pickling)
def w_subset_keys(x: Point):
    """canonical key of x|T for every T with |T| >= 3 (mask -> key)."""
    d2 = _d2()
    M = d2.matrix(x)
    out = {}
    for size in range(3, x.n + 1):
        for T in itertools.combinations(range(x.n), size):
            out[sum(1 << v for v in T)] = group.canonical(d2.restrict(M, x.D, T)).key()
    return out


def w_lift(y: Point):
    """local nodes v such that y is a vertex of the fiber over y minus v."""
    d2 = _d2()
    if y.n <= 3:
        return []
    return [v for v in range(y.n) if d2.fiber_vertex(y, [(min(v, b), max(v, b)) for b in range(y.n) if b != v])]


def w_radial(y: Point):
    d2 = _d2()
    return [tuple(R) for _, R in d2.radial_preds(y)]


def w_glue(args):
    """args = (y, [(A_local_mask, B_local_mask), ...]) -> list of the valid pairs (y vertex of the gluing fiber)."""
    y, pairs = args
    d2 = _d2()
    ok = []
    for am, bm in pairs:
        K = am & bm
        onlyA = [v for v in range(y.n) if (am >> v) & 1 and not (K >> v) & 1]
        onlyB = [v for v in range(y.n) if (bm >> v) & 1 and not (K >> v) & 1]
        holes = [(min(i, j), max(i, j)) for i in onlyA for j in onlyB]
        if d2.fiber_vertex(y, holes):
            ok.append((am, bm))
    return ok


class Engine:
    def __init__(self, cache_dir: Path, workers: int = 19):
        self.dir = Path(cache_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.workers = workers
        self.targets: List[Point] = []
        self.tkeys: List[Dict[int, str]] = []          # per target: mask -> key
        self.rep: Dict[str, Tuple[int, int]] = {}       # key -> (target id, mask)
        self.preds: Dict[Tuple[str, str], list] = {}    # (move, key) -> list of predecessor keys (or key pairs)
        self.glue_done: Dict[str, set] = {}             # key -> local (A,B) pairs already checked
        self.fwd: Dict[Tuple[str, str], list] = {}      # (user move, input key) -> output keys
        self._load()

    # ------------------------------------------------------------ persistence
    def _load(self):
        p = self.dir / "engine.pkl"
        if p.exists():
            with open(p, "rb") as f:
                st = pickle.load(f)
            self.targets, self.tkeys, self.rep = st["targets"], st["tkeys"], st["rep"]
            self.preds, self.glue_done = st["preds"], st["glue_done"]
            self.fwd = st.get("fwd", {})
            self.inv = st.get("inv", {})

    def save(self):
        p = self.dir / "engine.pkl"
        tmp = p.with_suffix(".tmp")
        with open(tmp, "wb") as f:
            pickle.dump({"targets": self.targets, "tkeys": self.tkeys, "rep": self.rep, "preds": self.preds,
                         "glue_done": self.glue_done, "fwd": self.fwd,
                         "inv": getattr(self, "inv", {})}, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, p)

    # ------------------------------------------------------------ targets
    def add_targets(self, pts: List[Point], verbose=True):
        have = {(p.n, p.D, p.nums) for p in self.targets}
        new = [p for p in pts if (p.n, p.D, p.nums) not in have]
        if not new:
            return
        t0 = time.time()
        with mp.Pool(self.workers) as pool:
            tabs = pool.map(w_subset_keys, new, chunksize=4)
        for p, tab in zip(new, tabs):
            tid = len(self.targets)
            self.targets.append(p)
            self.tkeys.append(tab)
            for mask, k in sorted(tab.items(), key=lambda kv: bin(kv[0]).count("1")):
                self.rep.setdefault(k, (tid, mask))
        if verbose:
            print(f"[engine] +{len(new)} targets, {len(self.rep)} nodes  {time.time() - t0:.0f}s", flush=True)
        self.save()

    def point(self, key) -> Point:
        tid, mask = self.rep[key]
        return _restrict(self.targets[tid], _bits(mask))

    def subkey(self, key, local_mask) -> str:
        tid, mask = self.rep[key]
        T = _bits(mask)
        return self.tkeys[tid][sum(1 << T[i] for i in _bits(local_mask))]

    def invariants(self, keys):
        """orbit_invariant per node key (cached on disk with the engine)."""
        if not hasattr(self, "inv"):
            self.inv = {}
        for k in keys:
            if k not in self.inv:
                self.inv[k] = orbit_invariant(self.point(k))
        return {k: self.inv[k] for k in keys}

    def target_key(self, tid) -> str:
        return self.tkeys[tid][(1 << self.targets[tid].n) - 1]

    # ------------------------------------------------------------ predecessor lists
    def _ensure(self, move, keys, pool, user_moves=None, interp=None, deadline=None):
        todo = [k for k in keys if (move, k) not in self.preds]
        if not todo:
            return True
        if move == "lift":
            res = pool.map(w_lift, [self.point(k) for k in todo], chunksize=16)
            for k, vs in zip(todo, res):
                n = self.point(k).n
                self.preds[(move, k)] = sorted({self.subkey(k, ((1 << n) - 1) & ~(1 << v)) for v in vs})
        elif move == "radial":
            res = pool.map(w_radial, [self.point(k) for k in todo], chunksize=16)
            for k, Rs in zip(todo, res):
                self.preds[(move, k)] = sorted({self.subkey(k, sum(1 << r for r in R)) for R in Rs})
        return True

    # ------------------------------------------------------------ the fixpoint
    def run(self, is_base: Callable[[str], bool], user_moves: Optional[dict] = None, interp=None,
            deadline: Optional[float] = None, verbose=True, skip: Optional[dict] = None, forward=None):
        """Return reached: key -> (round, how). user_moves: name -> (Move, grow), in cost order; they are applied
        FORWARD to reached nodes via forward(name, [keys]) -> {key: [output keys]} (cached per (name, key)).
        skip: optional {key: (round, how)} already-reached nodes (crossed off; never retried)."""
        user_moves = user_moves or {}
        order = ["lift", "radial"]
        # already-reached nodes are available from round 0 (their original round is restored on return)
        reached: Dict[str, tuple] = {k: (0, v[1]) for k, v in (skip or {}).items()}
        for k in self.rep:
            if k not in reached and is_base(k):
                reached[k] = (0, "base")
        r = 0
        timed_out = False
        with mp.Pool(self.workers) as pool:
            while True:
                progress = False
                while True:                                   # unary rounds
                    r += 1
                    new = {}
                    unreached = [k for k in self.rep if k not in reached]
                    for mvname in order:
                        cand = [k for k in unreached if k not in new]
                        if not cand:
                            break
                        ok = self._ensure(mvname, cand, pool, user_moves, interp, deadline)
                        for k in cand:
                            ps = self.preds.get((mvname, k))
                            if ps is None:
                                continue
                            for pk in ps:
                                if pk in reached and reached[pk][0] <= r - 1:
                                    new[k] = (r, (mvname, pk))
                                    break
                        if not ok:
                            timed_out = True
                            break
                    for mvname in user_moves:                     # forward: inputs reached in rounds <= r-1
                        if timed_out:
                            break
                        src = [k for k, v in reached.items() if v[0] <= r - 1 and (mvname, k) not in self.fwd]
                        src.sort(key=lambda k: int(k.split("|")[0]))      # smallest (cheapest, most basic) first
                        step = 2 * self.workers                            # small batches: the budget is enforced
                        for i in range(0, len(src), step):
                            if deadline and time.time() > deadline:
                                timed_out = True
                                break
                            self.fwd.update({(mvname, k): v for k, v in forward(mvname, src[i:i + step]).items()})
                        for k, v in reached.items():
                            if v[0] > r - 1:
                                continue
                            for ok_ in self.fwd.get((mvname, k), ()):
                                if ok_ in self.rep and ok_ not in reached and ok_ not in new:
                                    new[ok_] = (r, (mvname, k))
                    reached.update(new)
                    if verbose:
                        print(f"[engine] round {r}: +{len(new)} (unary)  reached {len(reached)}/{len(self.rep)}", flush=True)
                    if not new or timed_out:
                        break
                    progress = True
                if timed_out or (deadline and time.time() > deadline):
                    timed_out = True
                    break
                # glue stage on whatever is still unreached
                r += 1
                gnew = self._glue_stage(reached, r, pool, deadline)
                reached.update(gnew)
                if verbose:
                    print(f"[engine] round {r}: +{len(gnew)} (glue)  reached {len(reached)}/{len(self.rep)}", flush=True)
                if deadline and time.time() > deadline:
                    timed_out = True
                    break
                if not gnew:
                    break
        self.save()
        for k, v in (skip or {}).items():
            reached[k] = tuple(v)
        return reached, timed_out

    def _glue_stage(self, reached, r, pool, deadline):
        jobs = []
        for k in self.rep:
            if k in reached:
                continue
            y_n = bin(self.rep[k][1]).count("1")
            full = (1 << y_n) - 1
            done = self.glue_done.setdefault(k, set())
            pairs = []
            for am in range(1, full):
                if bin(am).count("1") < 3 or self.subkey(k, am) not in reached:
                    continue
                rest = full & ~am
                K_choices = _bits(am)
                for kk in range(1, len(K_choices)):
                    for K in itertools.combinations(K_choices, kk):
                        bm = rest | sum(1 << v for v in K)
                        if bin(bm).count("1") < 3 or (am, bm) in done:
                            continue
                        if self.subkey(k, bm) in reached:
                            pairs.append((am, bm))
            if pairs:
                jobs.append((k, pairs))
        if not jobs:
            return {}
        res = pool.map(w_glue, [(self.point(k), pairs) for k, pairs in jobs], chunksize=4)
        new = {}
        for (k, pairs), ok in zip(jobs, res):
            self.glue_done[k].update(pairs)
            if ok:
                am, bm = ok[0]
                new[k] = (r, ("glue", self.subkey(k, am), self.subkey(k, bm)))
        return new


# ------------------------------------------------------------------ cheap exact orbit invariant (filter only)
_TRI = {}


def orbit_invariant(x: Point) -> str:
    """Invariant under permutations and switchings: for each triple the sorted 4-tuple of the slacks of its 3 triangle
    and 1 perimeter inequalities (switching permutes these four; permutations permute triples), sorted over triples,
    with n and D. Equal orbits => equal invariant (used only to skip canonical forms; never to decide equality)."""
    import hashlib
    n, D = x.n, x.D
    if n not in _TRI:
        idx = {}
        k = 0
        for i in range(n):
            for j in range(i + 1, n):
                idx[(i, j)] = k
                k += 1
        tr = np.array([(idx[(i, j)], idx[(i, l)], idx[(j, l)]) for i, j, l in itertools.combinations(range(n), 3)])
        _TRI[n] = tr
    tr = _TRI[n]
    v = np.asarray(x.nums, dtype=np.int64)
    a, b, c = v[tr[:, 0]], v[tr[:, 1]], v[tr[:, 2]]
    s = np.stack([b + c - a, a + c - b, a + b - c, 2 * D - a - b - c], axis=1)
    s.sort(axis=1)
    s = s[np.lexsort(s.T[::-1])]
    return f"{n}|{D}|" + hashlib.blake2b(s.tobytes(), digest_size=12).hexdigest()
