# SMAPO cut polytope facet data

Downloaded 2026-11-22 from https://comopt.ifi.uni-heidelberg.de/software/SMAPO/cut/cut.html
(Christof & Reinelt, SMAPO library). File hashes are in SHA256SUMS.txt.

- swcut_n: one representative per facet class under node permutations plus switching, written as a·x <= 0 through the zero cut, with coordinates AB, AC, ..., in lexicographic pair order.
- swcut_n.stt: per-class statistics with columns NUMBER, ROOTS (tight cuts), FACETS AT VERTEX (facets through one cut), FACETS (class size).
- CUT(8): the page says "conjectured complete". Completeness was proved in Deza & Dutour Sikirić, arXiv:1501.05407. The abstract (checked 2026-11-22) says "the huge lists of facets of the cut polytope CUTP_8 and cut cone CUT_8, given in [CR] is complete".
- CUT(9): 164,506 classes and 12,246,651,158,320 facets. The page calls this "description possibly complete", so it is NOT proven.

Exact re-checks: scripts/phase10/cap_lemma_lp.py. Every class representative is a facet, and the class sizes match the stt files and the stated totals for n = 5..8.
