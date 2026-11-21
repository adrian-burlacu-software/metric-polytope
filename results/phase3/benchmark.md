# Phase 3: old vs new pipeline

code_version `fe77b4f569df1d93`, git `864c398664307e46a9d9ddba0905742e39d3aad4`

| n | vertices | orbits | switch classes | old: completions / s | new: completions / s | speedup | old-order+exact s | new-order+legacy s | all checks |
|---|---|---|---|---|---|---|---|---|---|
| 3 | 4 | 1 | 1 | 4 / 0.001 | 1 / 0.0002 | 3x | 0.000 | 0.0003 | PASS |
| 4 | 8 | 1 | 1 | 8 / 0.005 | 1 / 0.0004 | 14x | 0.001 | 0.0005 | PASS |
| 5 | 32 | 2 | 2 | 32 / 0.091 | 2 / 0.0014 | 67x | 0.008 | 0.0020 | PASS |
| 6 | 544 | 3 | 17 | 544 / 9.800 | 3 / 0.0182 | 540x | 0.259 | 0.0203 | PASS |

Whole-vertex-set completion (original script's use case):

| n | vertices | legacy float LP: s (LPs) | exact: s (LPs) | same valid set |
|---|---|---|---|---|
| 3 | 4 | 0.000 (4) | 0.0000 (0) | True |
| 4 | 8 | 0.000 (16) | 0.0001 (0) | True |
| 5 | 32 | 0.007 (40) | 0.0003 (0) | True |
| 6 | 544 | 50.640 (80) | 0.0095 (0) | True |

Stage timings (seconds):

- n=3: old {'canonicalise': 0.0004, 'complete': 0.0003}; new {'complete': 0.0, 'positional_dedupe': 0.0001, 'switch_classes': 0.0001}
- n=4: old {'canonicalise': 0.0034, 'complete': 0.0015}; new {'complete': 0.0001, 'positional_dedupe': 0.0001, 'switch_classes': 0.0002}
- n=5: old {'canonicalise': 0.077, 'complete': 0.0138}; new {'complete': 0.0003, 'positional_dedupe': 0.0002, 'switch_classes': 0.0009}
- n=6: old {'canonicalise': 9.3075, 'complete': 0.4921}; new {'complete': 0.0011, 'positional_dedupe': 0.0026, 'switch_classes': 0.0144}
