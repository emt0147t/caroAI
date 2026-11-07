# Candidate integration (M2/M3)

The public `get_ai_move` contract, difficulty normalization/fallback, numeric budget
override and optional SearchStats are preserved. EASY/MEDIUM remain on baseline
minimax. HARD/IMPOSSIBLE route to the isolated core; no backend persistence, frontend,
QA enablement or Render configuration changes. Additional search-stat fields report
completed depth, proof nodes, TT probes/hits, search time, fallback and stop reason.
Prometheus outcome classification recognizes tactical proofs and forced losses.

Default HARD budget is 250ms, IMPOSSIBLE 700ms. Explicit time_budget_ms takes precedence
over CAROAI_IMPOSSIBLE_TIME_BUDGET_MS, which takes precedence over IMPOSSIBLE default.
These are cooperative engine-entry budgets. Mandatory constant-size win/block scans
finish at zero budget; scheduler pauses and interpreter overhead can exceed the
budget. This is not a hard real-time or API response guarantee. EASY/MEDIUM defaults
remain unchanged. Quiet candidate caps exclude the additional preserved forcing moves.

The new evidence workflow runs only on relevant main-targeting PRs, using disposable
PostgreSQL, never a production URL. It uploads complete raw artifacts per head SHA:
200-game default-policy baseline comparisons for each strong level; an independent
tactical-greedy reference; three adjacent-level screening comparisons at 25ms;
same-process serial default latency; engine-thread contention at c=1/2/4/8; and
real HTTP/PostgreSQL default candidate API load at c=1/2/4/8. Each hosted runner records
its own environment. Cross-runner numbers are not speedup evidence.

Opening v2 uses seeded 2/4/6/8-ply prefixes across five styles and D4 transformations.
Repeated exact openings are grouped before bootstrap. Wilson game-win and opening-
sweep intervals accompany the bootstrap: all-identical scores make bootstrap
intervals degenerate and cannot establish certainty about untested positions.
A 25ms result is screening, not default-policy difficulty progression evidence.
If intervals cannot distinguish levels, increase independent opening samples and
retain PARTIAL rather than claiming monotonic strength. Self-play is only one group.

Initial acceptance status: local correctness/lint PASS; full CI and new raw experiments
PENDING. Default-policy adjacent-level tournaments, a stronger published external
reference engine, human play tests and production candidate latency remain PARTIAL.
The tactical-greedy reference is independent in decision policy, not a published
strong-engine benchmark. Broader VCT/multilayer tactical coverage remains future work.
All PRs remain draft. Merge and production deploy require explicit user authorization.
