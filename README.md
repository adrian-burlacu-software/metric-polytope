# metric-polytope

Code, data and notes for a computational study of the metric cone MET_n and the metric polytope m_n, and for the
paper

> A. Burlacu, *Extremality in the metric cone has unbounded locality* (draft, 27 November 2026):
> [docs/paper.pdf](docs/paper.pdf), source [docs/paper.tex](docs/paper.tex).

Archived at Zenodo: [doi:10.5281/zenodo.24564343](https://doi.org/10.5281/zenodo.24564343) (resolves to the latest archived release and lists
the earlier ones).

## What the paper proves

- The *locality* L(d) of an extreme ray d of MET_n is the least number s of points such that extremality of d can be
  derived by solving the tight triangle equalities inside sets of s points and propagating the proportionalities
  obtained.
- L = 4, the least possible value, for almost all graphs (Theorem 3).
- L is unbounded: an explicit family C_t of extreme rays on 2t points (t odd, t ≥ 9) has L(C_t) = 2t (Theorem 4).
  The bound L > t/6 has a short proof; the equality is computer-assisted, with exact arithmetic.
- A generator of vertices of m_n with fewer than (1 − δ)n bits of choice per node and bounded overlap between its
  inputs produces a vanishing share of the orbits (Theorem 6).

## Where things are

| path | content |
| --- | --- |
| `docs/paper.tex`, `docs/paper.pdf` | the paper |
| `docs/paper_draft.md` | the same text in Markdown, plus a list of what is still open before submission |
| `docs/phase9_status.md` | working notes, in the order the work was done |
| `scripts/phase9/` | scripts for the paper; the table in the paper's "Reproduction" section says which script produces which result |
| `results/phase9/` | their outputs (JSON) |
| `data/` | input lists, with sources and checksums |
| `metricpoly/`, `tests/` | shared library code and its tests |

## Reproducing the computer-assisted part of Theorem 4

Python 3.12 or later, with the packages in `requirements.txt`.

```text
pip install -r requirements.txt
python scripts/phase9/family_C_proof.py          # parts (a), (b): finite checks V1-V3
python scripts/phase9/family_C_top.py            # part (c), t >= 23: checks W1-W3
python scripts/phase9/family_C_top_check.py      # part (c): second, independent implementation
```

Each script writes a JSON file to `results/phase9/` and prints a summary.

## Data that is not in the repository

The list of vertex orbits of m_9 (Deza and Indik) is not included. It is distributed by its authors at
<https://www.cas.mcmaster.ca/~deza/metric.html>; the checksums of the file used here are in
`data/deza/orbits9/SHA256SUMS.txt`. The computations of the paper that are about this list need it.

## Licence

- Code (everything outside `docs/` and `data/`): MIT, see [LICENSE](LICENSE).
- The paper and the notes in `docs/`: Creative Commons Attribution 4.0 International (CC BY 4.0), see
  [docs/LICENSE-CC-BY-4.0.txt](docs/LICENSE-CC-BY-4.0.txt).
- `data/deza/raw/` and `data/smapo/raw/` are third-party data, redistributed unchanged with their sources and
  checksums (see `data/deza/raw/FETCHED_AT.txt` and `data/smapo/SOURCES.md`). They are not covered by the licences
  above; the rights remain with their authors.

## Status

This is a draft. The proofs have been checked only by the author and by the scripts above; they have not yet been
read by a second person. The work was done with an AI assistant (Claude, through Claude Code); see the
acknowledgements section of the paper.
