# Roadmap: an unconditional proof that Deza's m_9 vertex list is complete

Status legend: ✅ done · 🟡 running · ⏸ waiting for OK · ⬜ not started · ❌ failed / abandoned

Last updated: 2026-11-23

## The goal

Prove that the 1,056,368 orbits (switchings ⋊ S_9) of vertices of m_9 listed by Deza et al. are all of them.
Deza's own page says "probably complete": adjacency was computed for all orbits except 20.

The proof has two tracks:

- **Track A** proves the list complete *assuming* the SMAPO list of CUT_9 facets is complete.
- **Track B** tries to prove that assumption (plan B′: facet-side recursive adjacency decomposition).

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
| A2 | Closure walk: expand every listed orbit with incidence < 80 (1,056,311 rows) and check every neighbour is listed. The 56 orbits with incidence ≥ 80 are deferred to A3; walking them in-process could hang all workers. | ⏸ not started (paused 2026-11-23; Track B first, by decision) | `scripts/phase10/closure_check.py --n 9` (deferral, memory guard: RAM < 8 GB or a worker > 12 GB; stall guard: 20 min). Only a short test was run; its checkpoint was deleted. Full run about 40 h on 18 workers, under 1 GB disk. |
| A3 | Hard orbits: the 56 deferred orbits (incidence ≥ 80, including the cut) plus any A2 flags. Each tangent cone is enumerated with Normaliz (40 GB cap) or the recursive decomposition (`metricpoly/adjdec.py`). The cut orbit is covered by the cap lemma (A1) and needs no expansion. | ⬜ | Table: `results/phase10/hard_orbits_n9.json`, commit 9df8e48. Cone sizes unknown; 10^5–10^9 rays plausible. Capped trials first. |

A3 cannot be skipped.
The cap lemma lets us leave unexpanded only the vertices whose convex hull has a known facet list, and that is the cuts.
Putting a hard orbit into H would need the facets of conv(cuts ∪ that orbit), which nobody has.

**Track A is done when:** A2 reports 0 misses, and every deferred or flagged non-cut orbit is expanded in A3 with 0 misses.
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

## Track B: is the CUT_9 facet list complete?

**Current plan: B′, the facet-side recursive adjacency decomposition.** This is the method Deza and Dutour Sikirić used
to complete CUT_8 in 2015, scaled to n = 9. Adopted 2026-11-23, replacing the "sandwich" plan, whose gate failed (see
the history below).

### The argument

The facets of CUT_9 form a connected graph: two facets are adjacent when they share a ridge (a 34-dimensional face).
Take the 164,506 listed classes. If every listed class is **expanded**, meaning every neighbour of its representative
is again listed, then the list is complete. Symmetry carries this from the representative to the whole class.

**Expanding a facet F.** F's neighbours correspond to its ridges, and its ridges are the facets of the 35-dimensional
polytope F′ = conv(roots of F), where the roots are the cuts on F. So:
1. Enumerate the facets of F′ up to Stab(F).
2. For each ridge, rotate F about it (an exact gift-wrapping step over the 256 cuts) to get the neighbouring facet G.
3. Check that G is valid and is a facet (its tight cuts have affine rank 35).
4. Canonicalise G under switchings ⋊ S_9: switch it to the zero cut by each of its roots, take the S_9 canonical form
   with bliss, and keep the minimum.
5. Look G up in the SMAPO list.

**Cheap classes.** If F has exactly 36 roots, F′ is a simplex: 36 ridges, no enumeration needed. That is 45,233
classes. Classes with up to about 45 roots have small F′, which cdd or Normaliz handle instantly; 161,291 classes have
at most 45 roots.

**Degenerate classes.** These are the classes with many roots: the triangle class has 192, 18 classes have more than 80
and 97 have more than 60. For them, enumerating the facets of F′ is itself a recursive adjacency decomposition under
Stab(F). Inside a sub-decomposition, an unexpanded orbit may be skipped by Theorem 1 of arXiv:1501.05407 (from
Balinski) applied at *that* level: either it has at most (dim − 1) members, or all its members contain a common
vertex. This is exactly how CUT_8 was finished: 33 orbits could not be skipped at the top level, but could be at
deeper levels. At the top level no skip is assumed. Every class gets expanded, directly or recursively.

**The crux is the triangle class.** Its F′ has 192 cuts in dimension 35. There is a conjecture that every facet of
CUT_n is adjacent to a triangle facet; it is checked for n ≤ 8. If it holds, F′'s facets reach essentially every
class, so expanding the triangle is nearly the whole problem one dimension down. On the other hand the group Stab(F)
is large, and the deeper-level skips apply there.

**What does not work.** Leaving the triangle class unexpanded and covering it with the polar cap lemma would require
m_9's vertex list, which is Track A. That is circular, so it is not part of this plan.

### Steps

| Step | What | Status | Evidence / estimate |
|---|---|---|---|
| B0 | Literature: where Deza and Dutour Sikirić stopped for CUT_9, and why. | ✅ | See "B0 findings" below. |
| B′1 | Tools: ridge enumeration for a facet (F′ = conv(roots), exact rank checks, cdd/Normaliz under the memory cap); exact rotation about a ridge; facet canonical form under switchings ⋊ S_9; recursive decomposition under Stab(F) with Theorem 1 skips at deeper levels. | 🟡 partial | Done: `metricpoly/cutfacets.py` (exact roots, cdd ridges, rotation, canonical keys; `expand_sym` = Normaliz ridges + Stab_Sn orbit reduction), `scripts/phase10/cut_facet_walk.py`. Recursive ridge enumeration added (`cutfacets.expand_adm`: dual cone of ridge functionals with the line ±(a0,0) cut out, fed to `adjdec` decomposition under Stab_Sn(a0); least-degenerate LP start; parallel, checkpointed, deadline/halt/RAM stop). Validated: equals direct Normaliz on all 11 CUT_7 classes and CUT_8 class 124; recursion forced to depth 3 equals it on all CUT_6 classes and CUT_7 classes 1, 4, 8. Not yet done: Theorem 1 skips at deeper levels, subproblem cache. |
| B′2 | Validation: reproduce completeness of CUT_6 (3 classes), CUT_7 (11) and CUT_8 (147, as in 2015), with a negative control (drop a class, the walk must find it). Also check the triangle-adjacency conjecture at n ≤ 8. | 🟡 146/147 | CUT_5–7 closed. CUT_8: 146 of 147 classes expanded, 0 unlisted neighbours, every drop detectable, all classes adjacent to a triangle. The triangle class (96 roots) hit the 1 h Normaliz budget (16.6 GB at 57 min). `results/phase10/cut_facet_walk_n8.json`. |
| B′3 | Timing sample at n = 9: about 1,000 classes stratified by roots, giving a cost estimate for the whole walk. | ⬜ | Short; the estimate is reported before the full run. |
| B′4 | Walk all non-degenerate classes (roots ≤ T, with T chosen from B′3): about 164,000 classes. | ⬜ | Expected to be the bulk of the classes and the cheap part. |
| B′5 | Degenerate classes except the triangle (roots > T, about 100 classes): recursive decomposition of each F′ under Stab(F). | ⬜ | Unknown; capped trials first, from the least degenerate up. |
| B′6 | **Triangle class** (192 roots): recursive decomposition of F′ under its stabiliser, with deeper-level skips. | ⬜ | **The riskiest step**, possibly the whole difficulty of the problem. Capped trial first. |
| B′7 | Assemble: every class expanded, 0 unlisted neighbours. Cross-check the triangle-adjacency conjecture at n = 9 for free. | ⬜ | |

**Kill criteria** (stop and report honestly):
- B′2 fails to reproduce CUT_8 completeness, so the tools are wrong.
- B′6 cannot be done within the caps (40 GB per call, disk guard, time budgets agreed beforehand), even with recursion
  and deeper-level skips.

**Track B is done when:** all 164,506 classes are expanded (directly or recursively, with skips only at deeper levels
and only by Theorem 1), 0 unlisted neighbours are found, and B′2 has passed.
**Result:** "the SMAPO CUT_9 facet list is complete", which is new. Together with Track A, Deza's m_9 list is complete
with no assumption.

### B0 findings (read 2026-11-23)

- **arXiv:math/0201011** (Deza and Dutour, 2002; text extracted from the arXiv PDF). Section 1: "For the cones MET8, CUT8 ... the adjacency decomposition method gives a lower bound which is conjectured to be the exact value". Also: "For cones CUT9, MET9, ... the adjacency decomposition method gives only an estimate of the complexity." So CUT_9 was never closed by the method in that paper.
- The same paper states a conjecture: "every facet of CUTn is adjacent to a triangle inequality facet".
- **arXiv:1501.05407** (Deza and Dutour Sikirić, 2015; HTML v6, since the PDF text was unreadable). It completes CUT_8 / CUTP_8 by *recursive* adjacency decomposition. There is no K_9 / CUT_9 row; Table 1 stops at n ≤ 8.
  - Skip criteria (Theorem 1, after Balinski): an unexpanded orbit may be skipped if its members number at most m − 1, or if they all contain a common vertex. The second works because removing the edges of one face leaves the graph connected.
  - For CUT_8: "We had to treat the 33 remaining orbits of facets since we could not apply Theorem 1. However, we could apply the theorem in deeper levels of the recursive adjacency method."
  - The triangle-adjacency conjecture is confirmed for n = 8.
- **Consequences for Track B.**
  1. The experts' route is the *facet-side* recursive adjacency decomposition (our B4, done for every class), with the common-vertex criterion applied *inside* the sub-decompositions of the degenerate facets. Nothing on record shows it was ever run to completion at n = 9.
  2. The sandwich gate (B1) failed for a reason consistent with that: the hard part is the cut rays / degenerate facets themselves.
  3. Revised plan, adopted as B′ above: B4′, the facet-side walk over **all** 164,506 classes. For each degenerate class F, enumerate F's ridges, which are the facets of the 35-dimensional polytope conv(roots of F) (192 cuts for the triangle class), by recursive decomposition under Stab(F), using the common-vertex skip at deeper levels as in 2015.
  4. The conjecture "every facet is adjacent to a triangle facet" is a cheap sanity check on the walk.

### History: the sandwich plan (abandoned 2026-11-23)

The idea: leave the degenerate facet classes H* unexpanded and cover them with the cap lemma on the polar side. That
needs all vertices of R(H*), the polytope cut out by H*, with CUT_9 ⊆ R ⊆ m_9.

| Step | What | Status | Evidence |
|---|---|---|---|
| B1 | Gate E1 (m_8): ray count of R's tangent cone at the zero cut. | ❌ | Direct Normaliz: more than 60 roots (1,008 inequalities) hit the 20 min cap; more than 50 roots (8,344) hit the 40 GB cap. The symmetry walk cannot do even the m_7 cut cone (63 rays from 38,780 inequalities) in 5 min. Enlarging H* moves the degeneracy onto the cut rays. `results/phase10/sandwich_cone_n8.json`, commit e848445. |
| B2–B6 | Gate at m_9, choose H*, walk, enumerate R, dual LPs. | — superseded | |

---

## Side results and history

- m_8: list complete, proved (R1). The cut-ray cross-check, which does not use the CUT_8 facet list, is partial:
  |S| = 4, 3, 2 found 0 rays outside the list; |S| = 1 was not completed because of memory (commit 98acd7e).
- Resource guards: under 15 GB free disk a job stops cleanly; each Normaliz call is capped at 40 GB (`metricpoly/resguard.py`).

## Log

- 2026-11-22: A1 done (fed26f9).
- 2026-11-23: hard-orbit table (9df8e48); sandwich-cone tool validated at n = 6, 7; B1 started.
- 2026-11-23: B1 inconclusive, leaning negative. Neither direct Normaliz nor the symmetry walk can compute R's zero-cut cone at m_8 within the caps, and the walk fails even on the m_7 cut cone. Track B is paused pending a decision; options are in the next session note.
- 2026-11-23: B0 done (literature). Track B switched from the sandwich plan to B′ (facet-side recursive adjacency decomposition, the 2015 CUT_8 method).
- 2026-11-23: B′2 at CUT_8: 146/147 classes expanded (class 145, 80 roots: 2,180,786 ridges, 37,012 orbits, 633 s), 0 unlisted, negative control passes, all adjacent to a triangle. The triangle class (96 roots) timed out at 1 h in direct Normaliz, so it needs recursive ridge enumeration. A2 marked not started (Track B first).
- 2026-11-23: recursive ridge enumeration validated (n = 6, 7, and CUT_8 class 124). Fixes in `adjdec`: excess counts ±row pairs once (a simplicial cone was sent to Normaliz, which crashed with exit 3 after its non-pointed restart); Normaliz failure falls back to cdd. CUT_8 triangle trial: the default LP start ridge has 80 of 96 roots and did not finish in 9 min; with the least degenerate of 16 starts, 28,998 ridge orbits expanded in 504 s (45,920 found, queue 16,921 and levelling off).
