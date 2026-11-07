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

Current correctness/lint, PostgreSQL acceptance, Browser E2E, secret scan and Docker
build are PASS on the tested integration head. Frozen-SHA default-policy adjacent-level
tournaments and performance artifacts exist; current results and remaining gates
are in [REVIEW.md](../../reports/competitive/REVIEW.md). A stronger published external
reference engine, human play tests and production candidate latency remain unmeasured.
The tactical-greedy reference is independent in decision policy, not a published
strong-engine benchmark. Broader VCT/multilayer tactical coverage remains future work.
All PRs remain draft. Merge and production deploy require explicit user authorization.

Corpus v2 has 240 color/symmetry variants, including two- and three-attack continuous-
four certificates verified by an independent exhaustive domain-rule oracle, and an
unavoidable open-four loss. HARD's short proof search addresses the newly exposed
three-attack miss; IMPOSSIBLE retains longer proofs and wider/deeper tactical search.
Engine measurements include an excluded warm-up, mandatory-root/optional-search
separation, shortcut-stratified latency and truthful legacy fallback counts. A new
runtime-changing head cancels superseded jobs of the same benchmark group. A
preflight compares the previous head to the new head so report-only changes preserve
active evidence and skip heavy jobs. Workflow infrastructure/matrix changes can be
measured with workflow_dispatch. Incomplete logs never count as accepted tournaments.
