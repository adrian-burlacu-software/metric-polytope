# Phase 3: old vs new pipeline

code_version `f6f3f63143e0c00a`, git `a5895e3b5e6c0c59a4ea5eaf0f8f9b2685fb5005`

| n | vertices | orbits | switch classes | old: completions / s | new: completions / s | speedup | old-order+exact s | new-order+legacy s | all checks |
|---|---|---|---|---|---|---|---|---|---|
| 3 | 4 | 1 | 1 | 4 / 0.001 | 1 / 0.0002 | 3x | 0.000 | 0.0003 | PASS |
| 4 | 8 | 1 | 1 | 8 / 0.005 | 1 / 0.0004 | 12x | 0.001 | 0.0005 | PASS |
| 5 | 32 | 2 | 2 | 32 / 0.090 | 2 / 0.0015 | 61x | 0.009 | 0.0019 | FAIL |
| 6 | 544 | 3 | 17 | 544 / 9.960 | 3 / 0.0186 | 534x | 0.291 | 0.0202 | FAIL |

Whole-vertex-set completion (original script's use case):

| n | vertices | legacy float LP: s (LPs) | exact: s (LPs) | same valid set |
|---|---|---|---|---|
| 3 | 4 | 0.000 (4) | 0.0000 (0) | True |
| 4 | 8 | 0.000 (16) | 0.0001 (0) | True |
| 5 | 32 | 0.007 (40) | 0.0003 (0) | True |
| 6 | 544 | 50.963 (80) | 0.0096 (0) | True |

Stage timings (seconds):

- n=3: old {'canonicalise': 0.0004, 'complete': 0.0003}; new {'complete': 0.0, 'positional_dedupe': 0.0001, 'switch_classes': 0.0001}
- n=4: old {'canonicalise': 0.0033, 'complete': 0.0015}; new {'complete': 0.0001, 'positional_dedupe': 0.0001, 'switch_classes': 0.0002}
- n=5: old {'canonicalise': 0.0766, 'complete': 0.013}; new {'complete': 0.0004, 'positional_dedupe': 0.0002, 'switch_classes': 0.0009}
- n=6: old {'canonicalise': 9.4682, 'complete': 0.4922}; new {'complete': 0.0014, 'positional_dedupe': 0.0026, 'switch_classes': 0.0146}
