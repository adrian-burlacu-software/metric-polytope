"""metricpoly: exact tools for the metric polytope m_n and its symmetry group.

Conventions (fixed project-wide):
- Nodes are 0-based internally (0..n-1); I/O and write-ups use 1-based labels.
- Coordinates x_ij (i<j) are ordered lexicographically: (0,1),(0,2),...,(0,n-1),(1,2),...
  This matches Deza's .ine/.ext files (verified mechanically in scripts/phase2_verify.py).
- A point is stored exactly as (D, nums): x_e = nums[e] / D, with gcd(D, nums...) = 1.
- Symmetry group G_n = switchings x S_n (order 2^(n-1) * n!).
  Permutation pi:  (pi.x)_{pi(i) pi(j)} = x_ij  (same permutation on rows and columns).
  Switching by S (S a subset of nodes not containing node 0):  x_e -> 1 - x_e for e in the cut delta(S).
- Canonical form: lexicographically smallest coordinate vector over all of G_n,
  = min over pi of switch_canon(pi.x).
"""
