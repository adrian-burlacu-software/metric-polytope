# Phase 2 verification report

code_version `a09c22c7b551f6de`, git `no-commit+dirty`, seed 20261121

| quantity | n | published | ours | status | note |
|---|---|---|---|---|---|
| vertex orbits (Deza reps -> distinct canonical forms) | 3 | 1 | 1 | PASS |  |
| vertices (orbit-stabilizer sum over Deza reps) | 3 | 4 | 4 | PASS |  |
| all Deza reps pass exact vertex test | 3 | True | True | PASS |  |
| orbit sizes == metric_n.inv | 3 | True | True | PASS |  |
| incidences == metric_n.inv | 3 | True | True | PASS |  |
| our facet list == metric_n.ine (lex coordinate order) | 3 | True | True | PASS |  |
| vertex orbits (Deza reps -> distinct canonical forms) | 4 | 1 | 1 | PASS |  |
| vertices (orbit-stabilizer sum over Deza reps) | 4 | 8 | 8 | PASS |  |
| all Deza reps pass exact vertex test | 4 | True | True | PASS |  |
| orbit sizes == metric_n.inv | 4 | True | True | PASS |  |
| incidences == metric_n.inv | 4 | True | True | PASS |  |
| our facet list == metric_n.ine (lex coordinate order) | 4 | True | True | PASS |  |
| vertex orbits (Deza reps -> distinct canonical forms) | 5 | 2 | 2 | PASS |  |
| vertices (orbit-stabilizer sum over Deza reps) | 5 | 32 | 32 | PASS |  |
| all Deza reps pass exact vertex test | 5 | True | True | PASS |  |
| orbit sizes == metric_n.inv | 5 | True | True | PASS |  |
| incidences == metric_n.inv | 5 | True | True | PASS |  |
| our facet list == metric_n.ine (lex coordinate order) | 5 | True | True | PASS |  |
| vertex orbits (Deza reps -> distinct canonical forms) | 6 | 3 | 3 | PASS |  |
| vertices (orbit-stabilizer sum over Deza reps) | 6 | 554 | 544 | SOURCE-TYPO | page says 554; Deza's own metric_6.inv sizes 32+32+480 = 544; orbit-stabilizer and cdd give 544 -> page typo |
| all Deza reps pass exact vertex test | 6 | True | True | PASS |  |
| orbit sizes == metric_n.inv | 6 | True | True | PASS |  |
| incidences == metric_n.inv | 6 | True | True | PASS |  |
| our facet list == metric_n.ine (lex coordinate order) | 6 | True | True | PASS |  |
| vertex orbits (Deza reps -> distinct canonical forms) | 7 | 13 | 13 | PASS |  |
| vertices (orbit-stabilizer sum over Deza reps) | 7 | 275840 | 275840 | PASS |  |
| all Deza reps pass exact vertex test | 7 | True | True | PASS |  |
| orbit sizes == metric_n.inv | 7 | True | True | PASS |  |
| incidences == metric_n.inv | 7 | True | True | PASS |  |
| our facet list == metric_n.ine (lex coordinate order) | 7 | True | True | PASS |  |
| vertex orbits (Deza reps -> distinct canonical forms) | 8 | 533 | 533 | PASS |  |
| vertices (orbit-stabilizer sum over Deza reps) | 8 | 1550825600 | 1550825600 | PASS |  |
| all Deza reps pass exact vertex test | 8 | True | True | PASS |  |
| orbit sizes == metric_n.inv | 8 | True | True | PASS |  |
| incidences == metric_n.inv | 8 | True | True | PASS |  |
| our facet list == metric_n.ine (lex coordinate order) | 8 | True | True | PASS |  |
| vertices (cdd exact enumeration) | 3 | 4 | 4 | PASS |  |
| vertex orbits (canonicalizing all enumerated vertices) | 3 | 1 | 1 | PASS |  |
| enumerated orbits == Deza orbits; orbit union == vertex set | 3 | True | True | PASS |  |
| facets (all facet-defining) | 3 | 4 | 4 | PASS |  |
| facet orbits | 3 | 1 | 1 | PASS |  |
| extreme rays of metric cone M_n (cdd) | 3 | 3 | 3 | PASS |  |
| vertices (cdd exact enumeration) | 4 | 8 | 8 | PASS |  |
| vertex orbits (canonicalizing all enumerated vertices) | 4 | 1 | 1 | PASS |  |
| enumerated orbits == Deza orbits; orbit union == vertex set | 4 | True | True | PASS |  |
| facets (all facet-defining) | 4 | 16 | 16 | PASS |  |
| facet orbits | 4 | 1 | 1 | PASS |  |
| extreme rays of metric cone M_n (cdd) | 4 | 7 | 7 | PASS |  |
| vertices (cdd exact enumeration) | 5 | 32 | 32 | PASS |  |
| vertex orbits (canonicalizing all enumerated vertices) | 5 | 2 | 2 | PASS |  |
| enumerated orbits == Deza orbits; orbit union == vertex set | 5 | True | True | PASS |  |
| facets (all facet-defining) | 5 | 40 | 40 | PASS |  |
| facet orbits | 5 | 1 | 1 | PASS |  |
| extreme rays of metric cone M_n (cdd) | 5 | 25 | 25 | PASS |  |
| vertices (cdd exact enumeration) | 6 | 554 | 544 | MISMATCH | see orbit-stabilizer row |
| vertex orbits (canonicalizing all enumerated vertices) | 6 | 3 | 3 | PASS |  |
| enumerated orbits == Deza orbits; orbit union == vertex set | 6 | True | True | PASS |  |
| facets (all facet-defining) | 6 | 80 | 80 | PASS |  |
| facet orbits | 6 | 1 | 1 | PASS |  |
| extreme rays of metric cone M_n (cdd) | 6 | 296 | 296 | PASS |  |
| face orbits by codim | 4 | [1, 1, 3] | [1, 1, 3] | PASS |  |
| Deza face reps map 1-1 onto our face orbits | 4 | True | True | PASS |  |
| face orbits by codim | 5 | [1, 2, 6] | [1, 2, 6] | PASS |  |
| Deza face reps map 1-1 onto our face orbits | 5 | True | True | PASS |  |
| face orbits by codim | 6 | [1, 3, 10, 34] | [1, 3, 10, 34] | PASS |  |
| Deza face reps map 1-1 onto our face orbits | 6 | True | True | PASS |  |
| face orbits by codim | 7 | [1, 3, 13, 61] | [1, 3, 13, 61] | PASS |  |
| Deza face reps map 1-1 onto our face orbits | 7 | True | True | PASS |  |
| canonical form: fast == brute force == min_pi switch_canon (n<=6, n=7 reps), invariant (n=8 sample) | 3-8 | True | True | PASS |  |
| clause (+-1) encoding: Deza rule == catalog, group = column ops, cut tight iff NAE | 3-8 | True | True | PASS |  |
