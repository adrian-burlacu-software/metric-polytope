# Round 8 judge note (2026-11-23)

- **gen-bipartite-glue "rejected: generation failed" is an operator error, not a verdict.** While the judge was
  running, I killed two `try_rule.py` processes, thinking they were the maker's leftovers. They were the judge's own
  generation subprocess for this rule, so the rule was never evaluated. Measured afterwards: generation takes about
  1 s at n = 3–7, about 264 s at n = 8 (maker's measurement), and more than 240 s at n = 9. The judge allows half the
  budget (150 s) for n = 3–9 in total, so under the current policy the rule would most likely have been dropped for time.
- **"radial-lowend: rejected: does not load" is a judge bookkeeping bug, now fixed.** The judge re-retried a rule that
  was already accepted on its round 7 retry. `phase9_round.py` now skips previous-round rules that were already
  retried in that round. Checked on rounds 7–9: the old rule also re-scheduled dup-recentre, which had already had its
  900 s retry in round 6 without gain. No retries are owed.
