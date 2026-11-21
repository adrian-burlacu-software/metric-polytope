# Literature sources (Phase 4a)

Local copies live in `data/literature/raw/` (git-ignored: copyrighted). `SHA256SUMS.txt` pins the exact files read.
Fetched 2026-11-21 with curl. Page renders for scanned PDFs: `data/literature/img/` (PyMuPDF, 110 dpi).
PostScript decoded with `scripts/tools/dvips_text.py` (lossy for math glyphs; formulas cross-checked against the PDFs where possible).

| key | reference | URL | access | file |
|---|---|---|---|---|
| L96 | M. Laurent, *Graphic vertices of the metric polytope*, Discrete Math. 151 (1996) 131–153. (Single author. Earlier: Report 91737-OR, Univ. Bonn, 1991.) | https://www.sciencedirect.com/science/article/pii/0012365X9400091V | **PAYWALLED (HTTP 403). Not read.** No open copy found (searched CWI repository, web). | — |
| LP92 | M. Laurent, S. Poljak, *One-third-integrality in the metric polytope*, CWI Report BS-R9209 (May 1992); journal version Math. Programming 71 (1995) 29–50 ("…in the max-cut problem"). | https://ir.cwi.nl/pub/5451/5451D.pdf | open (scanned, read as images, all 28 pp.) | `cwi_5451_laurent_poljak_one_third_1992.pdf` |
| DI05 | A. Deza, G. Indik, *A counterexample to a conjecture of Laurent and Poljak*, arXiv:math/0512493 (2005). | https://arxiv.org/abs/math/0512493 | open, read in full | `arxiv_math0512493.pdf` |
| DI07 | A. Deza, G. Indik, *A counterexample to the dominating set conjecture*, Optimization Letters 1 (2007) 163–169. | https://www.cas.mcmaster.ca/~deza/ol2007.pdf | open (author copy) | `deza_ol2007.pdf` |
| DFMV03 | A. Deza, K. Fukuda, T. Mizutani, C. Vo, *On the face lattice of the metric polytope*, LNCS 2866 (2003) 118–128. **This is the paper at the Springer link given in the brief; its authors are Deza–Fukuda–Mizutani–Vo, not Deza–Fukuda–Pasechnik–Sato.** | https://link.springer.com/chapter/10.1007/978-3-540-44400-8_12 | Springer **paywalled**; read the author preprint `jcdcg24.ps` from Deza's site | `deza_jcdcg24.ps` |
| DFPS01 | A. Deza, K. Fukuda, D. Pasechnik, M. Sato, *On the skeleton of the metric polytope*, LNCS 2098 (2001) 125–136. | https://www.cas.mcmaster.ca/~deza/jcdcg13.ps (also `lncs2001.pdf`, garbled text layer) | open preprint, read via decoded PS | `deza_jcdcg13.ps`, `deza_lncs2001.pdf` |
| DDF96 | A. Deza, M. Deza, K. Fukuda, *On skeletons, diameters and volumes of metric polyhedra*, LIENS-96-2 (1996); LNCS 1120 (1996) 112–128. | https://www.di.ens.fr/reports/1996/liens-96-2.A4.pdf | open (report version; read pp. 1–17 as images/text) | `liens-96-2.pdf` |
| DZ-web | A. Deza, metric polytope page + data files | https://www.cas.mcmaster.ca/~deza/metric.html | open | `data/deza/raw/` |

Secondary pointers (not read): Avis, *On the extreme rays of the metric cone*, Canad. J. Math. 32 (1980) 126–144;
Laurent–Poljak, *The metric polytope*, IPCO 1992, 247–286; Deza–Laurent, *Geometry of Cuts and Metrics* (1997).
