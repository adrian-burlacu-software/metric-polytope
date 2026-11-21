"""Parsers for Deza's metric-polytope data files (treated as untrusted text; parsed, never executed)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

from .core import Point, dim, n_from_dim
from .patterns import Clause, normalize_clause

RAW = Path(__file__).resolve().parent.parent / "data" / "deza" / "raw"

_row_ext = re.compile(r"^\s*(\d+)\s+(\d+)\s*\|\s*([\d\s]+?)\s*$")


def load_ext(n: int, root: Path = RAW) -> List[Point]:
    """metric_n.ext: lines 'i  denominator | numerators...' (lex coordinate order)."""
    pts: List[Point] = []
    for line in (root / f"metric_{n}.ext").read_text(encoding="ascii", errors="strict").splitlines():
        mt = _row_ext.match(line)
        if not mt:
            continue
        i, D = int(mt.group(1)), int(mt.group(2))
        nums = [int(t) for t in mt.group(3).split()]
        if len(nums) != dim(n):
            raise ValueError(f"metric_{n}.ext row {i}: {len(nums)} coords, expected {dim(n)}")
        if i != len(pts) + 1:
            raise ValueError(f"metric_{n}.ext: rows out of order at {i}")
        pts.append(Point.make(n, D, nums))
    return pts


def load_inv(n: int, root: Path = RAW) -> List[Dict[str, int]]:
    """metric_n.inv: rows 'i Icd Adj |O| Adj_delta'."""
    out = []
    text = (root / f"metric_{n}.inv").read_text(encoding="ascii")
    body = text.split("-------------------- orbitwise invariants")[1]
    for line in body.splitlines():
        t = line.split()
        if len(t) == 5 and all(s.isdigit() for s in t):
            i, icd, adj, osz, adjd = map(int, t)
            if i != len(out) + 1:
                raise ValueError(f"metric_{n}.inv out of order at {i}")
            out.append({"i": i, "icd": icd, "adj": adj, "orbit_size": osz, "adj_cut": adjd})
    return out


def load_ine(n: int, root: Path = RAW) -> List[Tuple[Tuple[int, ...], int]]:
    """metric_n.ine (cdd H-rep): row 'b r_1..r_m' means b + r.x >= 0, i.e. (-r).x <= b."""
    lines = (root / f"metric_{n}.ine").read_text(encoding="ascii").splitlines()
    i0 = next(k for k, l in enumerate(lines) if l.strip() == "begin")
    hdr = lines[i0 + 1].split()
    rows_n, cols = int(hdr[0]), int(hdr[1])
    if cols - 1 != dim(n):
        raise ValueError("ine dimension mismatch")
    out = []
    for l in lines[i0 + 2:i0 + 2 + rows_n]:
        t = [int(v) for v in l.split()]
        out.append((tuple(-v for v in t[1:]), t[0]))
    return out


def load_up_lattice(n: int, k: int, root: Path = RAW) -> List[List[Clause]]:
    """up_dk_mn.txt: blocks 'fk_i' followed by k clause rows of length n."""
    text = (root / f"up_d{k}_m{n}.txt").read_text(encoding="ascii")
    body = text.split("canonical representatives")[1]
    faces: List[List[Clause]] = []
    cur = None
    for line in body.splitlines():
        s = line.strip()
        if re.fullmatch(rf"f{k}_\d+", s):
            if cur is not None:
                faces.append(cur)
            cur = []
            idx = int(s.split("_")[1])
            if idx != len(faces) + 1:
                raise ValueError(f"face block out of order: {s}")
            continue
        t = s.split()
        # Rows omit trailing zeros (e.g. '1 1 1' for n=4): pad on the right to length n.
        if cur is not None and 3 <= len(t) <= n and all(re.fullmatch(r"-?\d+", v) for v in t):
            cur.append(normalize_clause([int(v) for v in t] + [0] * (n - len(t))))
    if cur is not None:
        faces.append(cur)
    for f in faces:
        if len(f) != k:
            raise ValueError(f"face with {len(f)} rows in d{k}_m{n}")
    return faces
