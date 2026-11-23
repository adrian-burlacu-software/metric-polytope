# Round 10: re-judge only

Round 10 has no maker or breaker work. It re-judges `gen-bipartite-glue` (copied unchanged from
`phase9/round_08/maker/01_bipartite_glue.mpr`) under the per-n generation rule (user decision 2026-11-23): base
families are generated one n at a time within the 900 s allowance, and if the allowance runs out at some n, the
family is judged on the sizes that finished, with that stated in its status. In round 9, generating all of n = 3–9
in a single call exceeded 900 s.
