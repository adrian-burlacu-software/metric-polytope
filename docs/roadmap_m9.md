# Roadmap: an unconditional proof that Deza's m_9 vertex list is complete

Status legend: ✅ done · 🟡 running · ⏸ waiting for OK · ⬜ not started · ❌ failed / abandoned

Last updated: 2026-11-23

## The goal

Prove that the 1,056,368 orbits (switchings ⋊ S_9) of vertices of m_9 listed by Deza et al. are all of them.
Deza's own page says "probably complete": adjacency was computed for all orbits except 20.

The proof has two tracks:

- **Track A** proves the list complete *assuming* the SMAPO list of CUT_9 facets is complete.
- **Track B** tries to prove that assumption.

CUT_9 facet completeness is open in the literature: SMAPO calls the list "possibly complete".
Track A alone already goes beyond what has been published.
Track A and Track B together give the unconditional result.
Track B on its own would also settle the CUT_9 facet question.

The m_8 version of Track A is done and recorded as R1 in `results/ledger/results.json`.
There, CUT_8 facet completeness is a theorem (arXiv:1501.05407).

---

## Track A: m_9 list complete, assuming the CUT_9 facet list is complete

The argument is the cap lemma (see `scripts/phase10/cap_lemma_lp.py`, docstring).

- K = the listed vertices.
- H = the 256 cuts.
- If every listed non-cut vertex has all its neighbours listed, and every facet class of CUT_9 has its LP optimum
  listed or an empty cap, then every vertex of m_9 is listed.
- This needs CUT_9 = conv(H) to have exactly the SMAPO facets.

| Step | What | Status | Evidence / estimate |
|---|---|---|---|
| A1 | One exact LP per CUT_9 facet class (164,506 classes, sizes sum to 12,246,651,158,320). Every optimum is an exact vertex and is in the list. | ✅ | `results/phase10/cap_lemma_n9.json`, commit fed26f9. 0 unlisted optima, 2,477 distinct optimum orbits, all dual certificates exact. |
| A2 | Closure walk: expand every listed non-cut orbit (1,056,367 rows) and check every neighbour is listed. | ⏸ | `scripts/phase10/closure_check.py --n 9`. About 40 h on 19 workers, under 1 GB disk (per-batch detail is pruned; stops at under 15 GB free). |
| A3 | Hard orbits: the ones A2 flags (no result within 600 s). Expected to be about the 20 most degenerate (table below). Each tangent cone is enumerated with Normaliz (40 GB cap) or the recursive decomposition (`metricpoly/adjdec.py`). | ⬜ | Table done: `results/phase10/hard_orbits_n9.json`, commit 9df8e48. Cone sizes unknown; somewhere in 10^5–10^9 rays is plausible. Capped trials first. |

A3 cannot be skipped.
The cap lemma lets us leave unexpanded only the vertices whose convex hull has a known facet list, and that is the cuts.
Putting a hard orbit into H would need the facets of conv(cuts ∪ that orbit), which nobody has.

**Track A is done when:** A2 reports 0 misses, and every orbit A2 flags is expanded in A3 with 0 misses.
**Result:** "Deza's m_9 list is complete if the SMAPO CUT_9 facet list is complete."

### The most degenerate listed orbits (candidates for Deza's 20)

| Row | D | Incidence | Excess (incidence − 36) | Stabiliser | Orbit size |
|---|---|---|---|---|---|
| 0 (cut) | 1 | 252 | 216 | 362,880 | 256 |
| 1 | 3 | 144 | 108 | 2,880 | 32,256 |
| 2 | 3 | 129 | 93 | 288 | 322,560 |
| 9 | 3 | 124 | 88 | 432 | 215,040 |
| 3 | 3 | 122 | 86 | 2,880 | 32,256 |
| 10 | 3 | 118 | 82 | 96 | 967,680 |
| 189 | 3 | 112 | 76 | 384 | 241,920 |
| 11 | 3 | 111 | 75 | 288 | 322,560 |
| 190 | 3 | 105 | 69 | 288 | 322,560 |
| 15 | 3 | 104 | 68 | 4,320 | 21,504 |
| 191 | 3 | 98 | 62 | 960 | 96,768 |
| 16, 17 | 4 | 97 | 61 | 48, 96 | 1,935,360 and 967,680 |
| 18 | 4 | 93 | 57 | 24 | 3,870,720 |
| 19, 226 | 5, 3 | 91 | 55 | 12, 10,080 | 7,741,440 and 9,216 |
| 240, 244 | 4 | 90 | 54 | 64, 32 | 1,451,520 and 2,903,040 |
| 14, 192, 193 | 3, 4, 4 | 89 | 53 | | |

Calibration from m_8:
- The most degenerate non-cut orbit (incidence 88) has 94,847 cone rays.
- The cut (incidence 168) has 119,269,588 rays (MET_8).

---

## Track B: is the CUT_9 facet list complete? (the "sandwich" attack)

### The idea

Walk the facets of CUT_9 the same way Track A walks the vertices of m_9: rotate each facet about each ridge to find its
neighbouring facet and check the neighbour is listed.

- Most classes are cheap. 45,233 of the 164,506 are simplices (exactly 36 roots), and 161,291 have at most 45 roots.
- A few classes are very degenerate. The triangle class has 192 roots and 18 classes have more than 80. These are the
  facet-side counterpart of the hard vertex orbits.

To avoid expanding the degenerate classes H*, use the cap lemma on the polar polytope:

- Let R = R(H*) be the polytope cut out by the inequalities in H*. Since H* includes the triangle class,
  CUT_9 ⊆ R ⊆ m_9.
- For each vertex v of R, solve one LP: find the CUT_9 facet most violated by v. Polar about z = (½, …, ½), a facet
  a·x ≤ b becomes y = a / (b − a·z), and "v violates the facet" becomes y·(v − z) > 1.
- If every such optimum is a listed facet, and every listed facet outside H* has all its neighbours listed, then the
  facet list is complete.
- Coverage: a facet f of CUT_9 not in H* must be violated by some vertex of R. Otherwise f would be valid on R and
  tight on a 35-dimensional face, so f would be a facet of R. Every facet of R is in H*, so f would be in H*.

**Why this is not circular.** With H* = the triangles alone, R = m_9 and we are back to needing Track A, so the
argument goes round in a circle. With a larger H*, R is a different polytope that sits between CUT_9 and m_9 and is
smaller than m_9. The bet is that its hardest vertex, the zero cut, has a tangent cone much nearer the cut cone (255
rays) than MET_9, which is too big to enumerate.

### Steps

| Step | What | Status | Evidence / estimate |
|---|---|---|---|
| B0 | Literature: exactly where Deza and Dutour Sikirić stopped for CUT_9, which classes are unfinished, and why. Read the open copies (arXiv:math/0201110, arXiv:1501.05407, the SMAPO pages). If a source is paywalled, say so. | ⬜ | Under 1 h of reading. Could kill the plan or sharpen H*. |
| B1 | **Gate E1 (m_8):** the tangent cone of R at the zero cut, ray count for growing H*. Does it fall steeply from MET_8 (119,269,588) towards the cut cone (127)? | ❌ inconclusive, leaning negative | Direct Normaliz: more than 60 roots (1,008 inequalities) hit the 20 min cap; more than 50 roots (8,344) hit the 40 GB cap in 3 min. The symmetry walk (adjdec) cannot do even the m_7 cut cone (63 rays from 38,780 inequalities) in 5 min, because the cut rays of these cones are extremely degenerate. Finding: enlarging H* moves the degeneracy from the zero cut onto the cut rays of R's cone. As H* grows the cone tends to the cut cone, whose rays are as hard as MET's. `results/phase10/sandwich_cone_n8.json`. |
| B2 | **Gate E2 (m_9):** the same cone at m_9. More than 120 roots gives 2,898 inequalities; more than 80 roots gives 1.43 million, which needs symmetry reduction (adjdec with group S_9). | ⬜ | Depends on B1. Each run capped at 20–30 min and 40 GB. |
| B3 | Choose H*, trading the number of degenerate facet classes left unexpanded against the size of R's zero-cut cone. | ⬜ | Depends on B1, B2. |
| B4 | Facet-side closure walk over every class not in H*: ridges of each facet (the facets of the 35-dimensional polytope spanned by its roots), rotation about each ridge over the 256 cuts, canonical form under switchings ⋊ S_9, membership in the SMAPO list. Validate on CUT_6, CUT_7, CUT_8 (known complete). | ⬜ | To build. Cost unknown until timed on a sample; near-simplicial classes should be cheap. |
| B5 | Enumerate **all** vertex orbits of R(H*): an adjacency-decomposition walk from a start vertex, with the zero cut's cone (from B2) as the hardest piece. No list exists to check against, so this is a genuine enumeration. | ⬜ | Unknown. **The riskiest step.** R may have more vertices than m_9, or hard vertices of its own. |
| B6 | Dual cap LPs: one exact LP per vertex orbit of R over the polar of CUT_9 (256 constraints). Each optimum must be a listed facet class or the cap must be empty, with exact dual certificates. | ⬜ | Cheap per LP; the count depends on B5. |
| B7 | End-to-end validation at n = 7 and n = 8, where the facet lists are known complete. Include a negative control: drop a class and confirm the test fails. | ⬜ | Before trusting B4–B6 at n = 9. |

**Kill criteria** (stop Track B and report honestly if any of these happen):
- B0 shows a known obstruction that applies to this scheme.
- B1 and B2 show the zero-cut cone of R does not shrink usefully for any H* we can afford: it blows past the 40 GB
  cap, or stays near MET size.
- B5 finds R has unmanageably many vertex orbits, or hard vertices of its own that are as bad as m_9's.

**Track B is done when:** B4 reports 0 misses on all classes outside H*, B5's enumeration of R is complete, B6 finds
every optimum listed, and B7 passes.
**Result:** "the SMAPO CUT_9 facet list (164,506 classes) is complete." Together with Track A this proves Deza's m_9
list is complete with no assumption.

---

## Side results and history

- m_8: list complete, proved (R1). The cut-ray cross-check, which does not use the CUT_8 facet list, is partial:
  |S| = 4, 3, 2 found 0 rays outside the list; |S| = 1 was not completed because of memory (commit 98acd7e).
- Resource guards: under 15 GB free disk a job stops cleanly; each Normaliz call is capped at 40 GB (`metricpoly/resguard.py`).

## Log

- 2026-11-22: A1 done (fed26f9).
- 2026-11-23: hard-orbit table (9df8e48); sandwich-cone tool validated at n = 6, 7; B1 started.
- 2026-11-23: B1 inconclusive, leaning negative. Neither direct Normaliz nor the symmetry walk can compute R's zero-cut cone at m_8 within the caps, and the walk fails even on the m_7 cut cone. Track B is paused pending a decision; options are in the next session note.
