#!/usr/bin/env python3
"""
LP + GPU (no V->H->V): Classify metric polytope inequalities against a V-JSON base.

Key points
- No V->H->V conversion. We optimize directly over (lambda, mu):
    x = V λ + R μ
    λ >= 0, 1^T λ = 1
    μ >= 0
    0 <= Vλ + Rμ <= 1   (implicit metric bounds ON)
- Exact LP solved by your 'cdd' binding (float NumberType), one LP per inequality (objective only changes).
- GPU (CuPy) used for:
    - fast "box" redundancy prefilter: ub_box(a) = sum(max(a_i, 0)) <= b
    - fast vertex witnesses if input vertices already lie in [0,1]^m
    - batched argmax over input vertices for witnesses/debug

Outputs
1) --out-h: Inequalities JSON: redundant / not_redundant with optional lp_opt and box_upper_bound.
2) --out-v: V-JSON witnesses: original generators and, per inequality:
   - tight_generator_indices (input vertices with a·v ≈ b)
   - max_generator_indices (input vertices achieving max a·v)
   - violating_vertex_indices (in-box input vertices with a·v > b)

Requirements
- CUDA Toolkit + compatible GPU
- Python packages:
    pip install pycddlib
    pip install cupy-cuda12x   # or cupy-cuda11x, matching your CUDA
    pip install numpy

Usage
  python metric_vjson_to_redundancy_lp_gpu.py --in base_v.json --out-h out_h.json --out-v out_v.json
  optional: --families nonneg,upper,triangle,perimeter
  optional: --tol 1e-12   # numeric tolerance for GPU comparisons only

Input V-JSON schema
{
  "n": 3,                                  # optional; inferred from dimension if omitted
  "variables": [[1,2],[1,3],[2,3]],        # optional; default lex (1<=i<j<=n)
  "generators": [
    {"type": "vertex", "coords": ["1","1","0"]},
    {"type": "vertex", "coords": ["1","0","1"]},
    {"type": "vertex", "coords": ["0","1","1"]}
    // Optional rays:
    // {"type": "ray", "coords": ["1","-1","0"]}
  ],
  "families": ["nonneg","upper","triangle","perimeter"]   # optional; defaults to all
}

Note
- The provided cdd API is used exactly as in your stub:
  - Build constraints matrix with cdd.matrix_from_array(...)
  - Mark equalities via Matrix.lin_set (1-based)
  - Set Matrix.obj_type = cdd.LPObjType.MAX and Matrix.obj_func = objective
  - Create LP via cdd.linprog_from_matrix(mat) and solve with cdd.linprog_solve(lp)
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

try:
    import cupy as cp
except Exception as e:
    raise SystemExit(
        "CuPy is required. Install a wheel matching your CUDA version, e.g.:\n"
        "  pip install cupy-cuda12x   # for CUDA 12.x\n"
        "  pip install cupy-cuda11x   # for CUDA 11.x\n"
        f"Import error: {e}"
    )

try:
    import cdd  # your library as per provided __init__.pyi
except Exception as e:
    raise SystemExit(
        "Could not import 'cdd'. Please ensure your library is installed/importable.\n"
        f"Import error: {e}"
    )

Index = Tuple[int, int]  # (i,j) with 1<=i<j<=n


# ========= Parsing helpers =========

def to_float(x) -> float:
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        # allow "p/q" strings
        if "/" in x:
            p, q = x.split("/", 1)
            return float(float(p) / float(q))
        return float(x)
    raise TypeError(f"Unsupported numeric literal: {x!r}")


def infer_n_from_m(m: int) -> int:
    # m = n(n-1)/2 => n = (1 + sqrt(1+8m))/2
    import math
    disc = 1 + 8 * m
    r = int(math.isqrt(disc))
    if r * r != disc:
        raise ValueError(f"Cannot infer n from m={m}")
    n2 = 1 + r
    if n2 % 2 != 0:
        raise ValueError("Inferred n is not integer.")
    n = n2 // 2
    if n * (n - 1) // 2 != m:
        raise ValueError("Inferred n is inconsistent.")
    return n


def default_variables(n: int) -> List[Index]:
    out: List[Index] = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            out.append((i, j))
    return out


# ========= Metric catalog =========

@dataclass(frozen=True)
class Inequality:
    b: float
    a: Tuple[float, ...]  # length m
    kind: str
    meta: Dict

def pair_index_map(variables: Sequence[Index]) -> Dict[Index, int]:
    """
    Map each (i, j) pair to its position. Using tuple unpacking preserves the
    fixed-length tuple type so Pylance infers Dict[Index, int] correctly.
    """
    return {(i, j): k for k, (i, j) in enumerate(variables)}


def gen_metric_catalog(n: int, variables: List[Index], families: Sequence[str]) -> List[Inequality]:
    allowed = {"nonneg", "upper", "triangle", "perimeter"}
    for f in families:
        if f not in allowed:
            raise ValueError(f"Unknown family: {f}")
    idx = pair_index_map(variables)
    m = len(variables)
    out: List[Inequality] = []

    # nonneg and upper
    if "nonneg" in families or "upper" in families:
        for (i, j), pos in idx.items():
            if "nonneg" in families:
                a = [0.0] * m
                a[pos] = -1.0  # -x_ij <= 0
                out.append(Inequality(b=0.0, a=tuple(a), kind="nonneg", meta={"edge": [i, j]}))
            if "upper" in families:
                a2 = [0.0] * m
                a2[pos] = 1.0   # x_ij <= 1
                out.append(Inequality(b=1.0, a=tuple(a2), kind="upper", meta={"edge": [i, j]}))

    # triangle and perimeter
    import itertools
    for i, j, k in itertools.combinations(range(1, n + 1), 3):
        def p(u: int, v: int) -> int:
            if u > v:
                u, v = v, u
            return idx[(u, v)]
        if "triangle" in families:
            a = [0.0] * m
            a[p(i, j)] = 1.0
            a[p(i, k)] = -1.0
            a[p(j, k)] = -1.0
            out.append(Inequality(b=0.0, a=tuple(a), kind="triangle",
                                  meta={"triple": [i, j, k], "form": "ij<=ik+jk"}))

            a = [0.0] * m
            a[p(i, k)] = 1.0
            a[p(i, j)] = -1.0
            a[p(j, k)] = -1.0
            out.append(Inequality(b=0.0, a=tuple(a), kind="triangle",
                                  meta={"triple": [i, j, k], "form": "ik<=ij+jk"}))

            a = [0.0] * m
            a[p(j, k)] = 1.0
            a[p(i, j)] = -1.0
            a[p(i, k)] = -1.0
            out.append(Inequality(b=0.0, a=tuple(a), kind="triangle",
                                  meta={"triple": [i, j, k], "form": "jk<=ij+ik"}))
        if "perimeter" in families:
            a = [0.0] * m
            a[p(i, j)] = 1.0
            a[p(i, k)] = 1.0
            a[p(j, k)] = 1.0
            out.append(Inequality(b=2.0, a=tuple(a), kind="perimeter", meta={"triple": [i, j, k]}))

    return out


# ========= GPU helpers =========

def rows_to_np(rows: List[Tuple[float, ...]]) -> np.ndarray:
    if not rows:
        return np.zeros((0, 0), dtype=np.float64)
    m = len(rows[0])
    M = np.empty((len(rows), m), dtype=np.float64)
    for i, r in enumerate(rows):
        M[i, :] = r
    return M


def in_box_mask(vertices: List[Tuple[float, ...]], tol: float) -> np.ndarray:
    V = rows_to_np(vertices)
    if V.size == 0:
        return np.zeros((0,), dtype=bool)
    # Use keepdims=True so np.all returns an ndarray, not a scalar, then ravel to 1-D.
    lower = np.all(V >= -tol, axis=1, keepdims=True)  # shape (nv, 1), dtype=bool
    upper = np.all(V <= 1.0 + tol, axis=1, keepdims=True)  # shape (nv, 1), dtype=bool
    return np.ravel(lower & upper)  # shape (nv,), dtype=bool


# ========= LP over (lambda, mu) with implicit bounds =========

def build_lambda_mu_matrix(V_cols: List[Tuple[float, ...]], R_cols: List[Tuple[float, ...]]) -> cdd.Matrix:
    """
    Build a cdd Matrix representing constraints in z = [λ (nv), μ (nr)]:
      sum λ = 1                              (equality via lin_set)
      -λ_i <= 0, -μ_j <= 0
      For each coord t:  -(V_t)·λ - (R_t)·μ <= 0   and   (V_t)·λ + (R_t)·μ <= 1
    Uses your cdd API: matrix_from_array(..., lin_set, rep_type=INEQUALITY, obj_type set later).
    """
    nv = len(V_cols)
    if nv == 0:
        raise ValueError("At least one vertex is required (nv >= 1).")
    nr = len(R_cols)
    m = len(V_cols[0])

    # Sanity dims
    for v in V_cols:
        if len(v) != m:
            raise ValueError("All vertices must share same dimension.")
    for r in R_cols:
        if len(r) != m:
            raise ValueError("All rays must share same dimension as vertices.")

    dim = nv + nr
    rows: List[List[float]] = []
    lin_rows_1based: List[int] = []

    # Equality: sum λ = 1
    eq = [0.0] * (dim + 1)
    eq[0] = 1.0  # b
    for i in range(nv):
        eq[1 + i] = 1.0
    rows.append(eq)
    lin_rows_1based.append(1)  # first row is equality

    # -λ_i <= 0
    for i in range(nv):
        row = [0.0] * (dim + 1)
        row[0] = 0.0
        row[1 + i] = -1.0
        rows.append(row)

    # -μ_j <= 0
    for j in range(nr):
        row = [0.0] * (dim + 1)
        row[0] = 0.0
        row[1 + nv + j] = -1.0
        rows.append(row)

    # Box: 0 <= Vλ + Rμ <= 1
    for t in range(m):
        # lower: -(V_t)·λ - (R_t)·μ <= 0
        low = [0.0] * (dim + 1)
        low[0] = 0.0
        for i in range(nv):
            low[1 + i] = -V_cols[i][t]
        for j in range(nr):
            low[1 + nv + j] = -R_cols[j][t]
        rows.append(low)

        # upper: (V_t)·λ + (R_t)·μ <= 1
        up = [0.0] * (dim + 1)
        up[0] = 1.0
        for i in range(nv):
            up[1 + i] = V_cols[i][t]
        for j in range(nr):
            up[1 + nv + j] = R_cols[j][t]
        rows.append(up)

    # BASELINE FIX: rows above are [b, a] meaning a.z <= b, but cdd reads [b, a] as b + a.z >= 0.
    # Convert to cdd form [b, -a]; and cdd's lin_set is 0-based (row 0 is the equality).
    rows = [[r[0]] + [-v for v in r[1:]] for r in rows]
    mat = cdd.matrix_from_array(
        array=rows,
        lin_set={r - 1 for r in lin_rows_1based},
        rep_type=cdd.RepType.INEQUALITY,
        obj_type=cdd.LPObjType.NONE,
        obj_func=None,
    )
    return mat


# ========= Classification =========

@dataclass
class RedundancyResult:
    inequality: Inequality
    is_redundant: bool
    reason: Optional[str]  # None if redundant; 'vertex_witness' or 'lp>bound'
    lp_opt: Optional[float]  # exact per your library's NumberType (float)
    box_upper_bound: Optional[float]
    tight_generator_indices: List[int]  # input vertices with a·v ≈ b
    max_generator_indices: List[int]    # input vertices achieving max a·v
    violating_vertex_indices: List[int] # in-box input vertices with a·v > b + tol


def classify_with_gpu_prefilter(
    V_cols: List[Tuple[float, ...]],
    R_cols: List[Tuple[float, ...]],
    catalog: List[Inequality],
    tol: float = 1e-12,
) -> List[RedundancyResult]:
    m = len(V_cols[0]) if V_cols else 0
    k = len(catalog)

    # Build A and b for all candidates on CPU
    A = np.empty((k, m), dtype=np.float64)
    b_vec = np.empty((k,), dtype=np.float64)
    for i, ineq in enumerate(catalog):
        A[i, :] = ineq.a
        b_vec[i] = ineq.b

    # Upload to GPU
    A_gpu = cp.asarray(A)
    b_gpu = cp.asarray(b_vec)

    # Box upper bound: ub_box(a) = sum(max(a_i, 0))
    ub_box_gpu = cp.sum(cp.maximum(A_gpu, 0.0), axis=1)
    redundant_by_box = ub_box_gpu <= (b_gpu - tol)

    # Vertices and in-box mask
    V_np = rows_to_np(V_cols)             # [nv, m]
    nv = V_np.shape[0]
    V_in_box = in_box_mask(V_cols, tol)   # boolean mask length nv

    # Prepare witnesses via GPU dot-products
    max_vertex_lists: List[List[int]] = [[] for _ in range(k)]
    violating_vertex_lists: List[List[int]] = [[] for _ in range(k)]
    tight_vertex_lists: List[List[int]] = [[] for _ in range(k)]
    if nv > 0:
        Vt_gpu = cp.asarray(V_np.T)       # [m, nv]
        Sv = A_gpu @ Vt_gpu               # [k, nv]
        max_vals = cp.max(Sv, axis=1)     # [k]

        Sv_cpu = cp.asnumpy(Sv)
        max_vals_cpu = cp.asnumpy(max_vals)

        for i in range(k):
            mv = max_vals_cpu[i]
            # argmax vertices (1-based)
            max_idxs = [j + 1 for j, val in enumerate(Sv_cpu[i]) if abs(val - mv) <= tol]
            max_vertex_lists[i] = max_idxs
            # violating in-box vertex witnesses
            viol = [j + 1 for j, val in enumerate(Sv_cpu[i]) if V_in_box[j] and (val > b_vec[i] + tol)]
            violating_vertex_lists[i] = viol
            # tight vertices relative to b
            tight = [j + 1 for j, val in enumerate(Sv_cpu[i]) if abs(val - b_vec[i]) <= tol]
            tight_vertex_lists[i] = tight

    # Precompute objective blocks on GPU for speed: lambda part (V^T a) and mu part (R^T a)
    nr = len(R_cols)
    R_np = rows_to_np(R_cols)             # [nr, m]
    Sr_cpu = np.zeros((k, nr), dtype=np.float64)
    if nr > 0:
        Rt_gpu = cp.asarray(R_np.T)       # [m, nr]
        Sr = A_gpu @ Rt_gpu               # [k, nr]
        Sr_cpu = cp.asnumpy(Sr)

    # Build the common constraint matrix once
    base_mat = build_lambda_mu_matrix(V_cols, R_cols)

    results: List[RedundancyResult] = []
    for i, ineq in enumerate(catalog):
        # Prefilter 1: box redundancy
        if bool(cp.asnumpy(redundant_by_box[i])):
            results.append(RedundancyResult(
                inequality=ineq,
                is_redundant=True,
                reason=None,
                lp_opt=None,
                box_upper_bound=float(cp.asnumpy(ub_box_gpu[i])),
                tight_generator_indices=tight_vertex_lists[i],
                max_generator_indices=max_vertex_lists[i],
                violating_vertex_indices=[],
            ))
            continue

        # Prefilter 2: vertex witness (already in [0,1]^m)
        if violating_vertex_lists[i]:
            results.append(RedundancyResult(
                inequality=ineq,
                is_redundant=False,
                reason="vertex_witness",
                lp_opt=None,
                box_upper_bound=float(cp.asnumpy(ub_box_gpu[i])),
                tight_generator_indices=tight_vertex_lists[i],
                max_generator_indices=max_vertex_lists[i],
                violating_vertex_indices=violating_vertex_lists[i],
            ))
            continue

        # Exact LP: set objective and solve
        # Objective vector z = [V^T a, R^T a]
        obj_lambda = []
        if nv > 0:
            # Use the CPU row of Sv if computed; recompute simple dot if not
            obj_lambda = list(np.dot(V_np, np.array(ineq.a, dtype=np.float64)))
        obj_mu = []
        if nr > 0:
            obj_mu = list(Sr_cpu[i])

        obj = [0.0] + obj_lambda + obj_mu  # BASELINE FIX: cdd needs the constant term first (length nv+nr+1)

        # Set objective on base_mat and build LP
        base_mat.obj_type = cdd.LPObjType.MAX
        base_mat.obj_func = obj

        lp = cdd.linprog_from_matrix(base_mat)
        # Use default solver (DUAL_SIMPLEX) or pass explicitly:
        cdd.linprog_solve(lp, solver=cdd.LPSolverType.DUAL_SIMPLEX)

        status = lp.status
        if status == cdd.LPStatusType.OPTIMAL:
            opt = float(lp.obj_value)
            is_red = opt <= ineq.b + tol
            results.append(RedundancyResult(
                inequality=ineq,
                is_redundant=is_red,
                reason=None if is_red else "lp>bound",
                lp_opt=opt,
                box_upper_bound=float(cp.asnumpy(ub_box_gpu[i])),
                tight_generator_indices=tight_vertex_lists[i],
                max_generator_indices=max_vertex_lists[i],
                violating_vertex_indices=[],
            ))
        elif status in (cdd.LPStatusType.UNBOUNDED, cdd.LPStatusType.DUAL_UNBOUNDED):
            # Should rarely occur due to 0<=x<=1 box; treat as not redundant.
            results.append(RedundancyResult(
                inequality=ineq,
                is_redundant=False,
                reason="lp_unbounded",
                lp_opt=None,
                box_upper_bound=float(cp.asnumpy(ub_box_gpu[i])),
                tight_generator_indices=tight_vertex_lists[i],
                max_generator_indices=max_vertex_lists[i],
                violating_vertex_indices=[],
            ))
        elif status in (cdd.LPStatusType.INCONSISTENT, cdd.LPStatusType.STRUC_INCONSISTENT):
            raise RuntimeError("Base constraints infeasible for LP (check generators).")
        else:
            # UNDECIDED or dual inconsistent: report as not redundant with reason
            results.append(RedundancyResult(
                inequality=ineq,
                is_redundant=False,
                reason=str(status.name).lower(),
                lp_opt=None,
                box_upper_bound=float(cp.asnumpy(ub_box_gpu[i])),
                tight_generator_indices=tight_vertex_lists[i],
                max_generator_indices=max_vertex_lists[i],
                violating_vertex_indices=[],
            ))

    return results


# ========= I/O =========

def _normalize_variables(raw: Sequence[Sequence[int]], expected_len: int) -> List[Index]:
    if len(raw) != expected_len:
        raise ValueError(f"'variables' length {len(raw)} does not match dimension m={expected_len}.")
    out: List[Index] = []
    for pair in raw:
        if len(pair) != 2:
            raise ValueError(f"Each 'variables' entry must have length 2, got {pair!r}.")
        i, j = map(int, pair)
        if i > j:
            i, j = j, i
        out.append((i, j))
    return out


def load_v_json(path: str) -> Tuple[int, List[Index], List[Tuple[float, ...]], List[Tuple[float, ...]], List[str]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    generators = data.get("generators")
    if not isinstance(generators, list) or not generators:
        raise ValueError("Input JSON must contain a non-empty 'generators' array.")

    parsed: List[Tuple[str, Tuple[float, ...]]] = []
    for g in generators:
        t = g.get("type")
        coords = g.get("coords")
        if t not in ("vertex", "ray"):
            raise ValueError("Each generator 'type' must be 'vertex' or 'ray'.")
        if not isinstance(coords, list):
            raise ValueError("Each generator must have a 'coords' list.")
        parsed.append((t, tuple(to_float(c) for c in coords)))

    m = len(parsed[0][1])
    if not all(len(p[1]) == m for p in parsed):
        raise ValueError("All generators must share the same dimension (coords length).")

    n = data.get("n")
    if n is None:
        n = infer_n_from_m(m)
    n = int(n)

    # variables
    vars_raw = data.get("variables")
    if vars_raw is None:
        variables: List[Index] = default_variables(n)
    else:
        if not isinstance(vars_raw, list):
            raise ValueError("'variables' must be a list of pairs.")
        variables = _normalize_variables(vars_raw, m)

    # split generators
    vertices: List[Tuple[float, ...]] = [coords for (t, coords) in parsed if t == "vertex"]
    rays: List[Tuple[float, ...]] = [coords for (t, coords) in parsed if t == "ray"]

    # families
    fam_raw = data.get("families")
    if isinstance(fam_raw, list):
        families: List[str] = [str(x) for x in fam_raw]
    else:
        families = ["nonneg", "upper", "triangle", "perimeter"]

    return n, variables, vertices, rays, families


def results_to_inequalities_json(
    n: int,
    variables: List[Index],
    families: List[str],
    results: List[RedundancyResult],
) -> Dict:
    def fmt(x: Optional[float]) -> Optional[str]:
        return None if x is None else f"{x:.12g}"

    out = {
        "n": n,
        "variables": [list(p) for p in variables],
        "families": families,
        "redundant": [],
        "not_redundant": []
    }
    for r in results:
        obj = {
            "kind": r.inequality.kind,
            "meta": r.inequality.meta,
            "b": f"{r.inequality.b:.12g}",
            "a": [f"{x:.12g}" for x in r.inequality.a],
        }
        if r.box_upper_bound is not None:
            obj["box_upper_bound"] = fmt(r.box_upper_bound)
        if r.lp_opt is not None:
            obj["lp_opt"] = fmt(r.lp_opt)

        if r.is_redundant:
            out["redundant"].append(obj)
        else:
            obj["reason"] = r.reason or "unknown"
            out["not_redundant"].append(obj)
    return out


def results_to_v_witness_json(
    n: int,
    variables: List[Index],
    vertices: List[Tuple[float, ...]],
    rays: List[Tuple[float, ...]],
    results: List[RedundancyResult],
    families: List[str],
) -> Dict:
    def fmt_vec(v: Sequence[float]) -> List[str]:
        return [f"{x:.12g}" for x in v]

    out = {
        "n": n,
        "variables": [list(p) for p in variables],
        "generators": (
            [{"type": "vertex", "coords": fmt_vec(v)} for v in vertices] +
            [{"type": "ray", "coords": fmt_vec(r)} for r in rays]
        ),
        "families": families,
        "implicit_bounds": "0<=x<=1",
        "inequality_witnesses": []
    }
    for r in results:
        rec = {
            "kind": r.inequality.kind,
            "meta": r.inequality.meta,
            "status": "redundant" if r.is_redundant else "not_redundant",
        }
        if r.lp_opt is not None:
            rec["lp_opt"] = f"{r.lp_opt:.12g}"
        if r.tight_generator_indices:
            rec["tight_generator_indices"] = r.tight_generator_indices
        if r.max_generator_indices:
            rec["max_generator_indices"] = r.max_generator_indices
        if r.violating_vertex_indices:
            rec["violating_vertex_indices"] = r.violating_vertex_indices
        if r.reason and not r.is_redundant:
            rec["reason"] = r.reason
        out["inequality_witnesses"].append(rec)
    return out


def main():
    ap = argparse.ArgumentParser(
        description="LP+GPU classification of metric inequalities against a V-JSON base "
                    "with implicit bounds 0<=x<=1. No V->H->V conversion."
    )
    ap.add_argument("--in", dest="inp", required=True, help="Path to input V-JSON file")
    ap.add_argument("--out-h", dest="out_h", required=True, help="Path to output inequalities JSON")
    ap.add_argument("--out-v", dest="out_v", required=True, help="Path to output V-JSON witnesses")
    ap.add_argument("--families", dest="families", default="",
                    help="Comma-separated subset of {nonneg,upper,triangle,perimeter}; default=all or input's 'families'")
    ap.add_argument("--tol", type=float, default=1e-12, help="numeric tolerance for GPU comparisons")
    args = ap.parse_args()

    n, variables, V_cols, R_cols, families_in_file = load_v_json(args.inp)
    families = families_in_file
    if args.families.strip():
        families = [f.strip() for f in args.families.split(",") if f.strip()]

    if not V_cols:
        raise SystemExit("Input must provide at least one vertex generator.")

    # Build catalog
    catalog = gen_metric_catalog(n, variables, families)

    # Classify
    results = classify_with_gpu_prefilter(V_cols, R_cols, catalog, tol=args.tol)

    # Write outputs
    out_h = results_to_inequalities_json(n, variables, families, results)
    with open(args.out_h, "w", encoding="utf-8") as f:
        json.dump(out_h, f, indent=2)

    out_v = results_to_v_witness_json(n, variables, V_cols, R_cols, results, families)
    with open(args.out_v, "w", encoding="utf-8") as f:
        json.dump(out_v, f, indent=2)

    red = sum(1 for r in results if r.is_redundant)
    nred = len(results) - red
    print(f"Wrote {args.out_h} and {args.out_v}. Redundant={red}, Not redundant={nred}. "
          f"(GPU tol={args.tol}, exact LP per candidate via cdd.linprog_from_matrix)")
    

if __name__ == "__main__":
    main()