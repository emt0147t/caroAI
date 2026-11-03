# CaroAI Sprint 3 — AI Benchmark

- Generated at (UTC): 2026-10-23T07:30:51+00:00
- Full source SHA: 12b951cea3cdfe5bc6768a0197402bfdd28ba4d7
- Command: py -3 scripts/benchmark_ai_sprint3.py --runs 5 --warmup 1 --output-dir "C:\Users\Admin\caroAI-benchmark-fix\reports\benchmark-windows-sprint3-fixed"
- Environment: Python 3.13.14 (tags/v3.13.14:fd17997, Jun 10 2026, 13:03:48) [MSC v.1944 64 bit (AMD64)]
- Platform: Windows-11-10.0.26200-SP0
- Machine: AMD64; CPU: Intel64 Family 6 Model 191 Stepping 2, GenuineIntel
- Container detected: False (not detected)
- Fixtures: 11; difficulties: EASY/MEDIUM/HARD; warm-up: 1; measured trials per fixture/difficulty: 5

## Protocol and interpretation

- Timing uses time.perf_counter_ns() around get_ai_move only. Board copying and root candidate-count collection occur outside the timed interval.
- Raw CSV/JSON include measured trials and warm-up rows marked with is_warmup=true. Summaries exclude warm-ups.
- The p95 uses nearest-rank: sorted sample at rank ceil(0.95 × n). With five trials, per-fixture p95 equals the maximum and is not a high-confidence production percentile.
- The by-difficulty p95 aggregates all fixture trials equally; it describes this workload, not the real-world distribution of player positions.
- Root candidate count is measured before the timed call. Node count is not instrumented and is reported as N/A.
- The proposed p95 ≤ 2,000 ms target is pending team confirmation. A measurement below the proposal does not itself accept the SLO.

## Environment metadata

| Field | Value |
|---|---|
| captured_at_utc | 2026-10-23T07:30:39+00:00 |
| source_sha | 12b951cea3cdfe5bc6768a0197402bfdd28ba4d7 |
| source_sha_method | git-head |
| python_version | 3.13.14 (tags/v3.13.14:fd17997, Jun 10 2026, 13:03:48) [MSC v.1944 64 bit (AMD64)] |
| python_executable | C:\Users\Admin\AppData\Local\Programs\Python\Python313\python.exe |
| argv | ['scripts/benchmark_ai_sprint3.py', '--runs', '5', '--warmup', '1', '--output-dir', 'reports/benchmark-windows-sprint3-fixed'] |
| platform | Windows-11-10.0.26200-SP0 |
| system | Windows |
| machine | AMD64 |
| processor | Intel64 Family 6 Model 191 Stepping 2, GenuineIntel |
| cpu_name | Intel64 Family 6 Model 191 Stepping 2, GenuineIntel |
| is_container | False |
| container_hint | not detected |
| command | py -3 scripts/benchmark_ai_sprint3.py --runs 5 --warmup 1 --output-dir "C:\Users\Admin\caroAI-benchmark-fix\reports\benchmark-windows-sprint3-fixed" |

## Per-difficulty summary

| Difficulty | Samples | Failures | Median (ms) | p95 (ms) | Min (ms) | Max (ms) | Proposed 2s threshold | SLO decision |
|---|---:|---:|---:|---:|---:|---:|---|---|
| EASY | 55 | 0 | 2.114 | 12.190 | 0.025 | 12.358 | BELOW PROPOSAL | PENDING_TEAM_CONFIRMATION |
| MEDIUM | 55 | 0 | 10.749 | 67.146 | 0.025 | 69.495 | BELOW PROPOSAL | PENDING_TEAM_CONFIRMATION |
| HARD | 55 | 0 | 85.432 | 907.047 | 0.025 | 961.171 | BELOW PROPOSAL | PENDING_TEAM_CONFIRMATION |

## Per-fixture / difficulty results

| Fixture | Category | Difficulty | n | Failures | Median (ms) | p95 (ms) | Min (ms) | Max (ms) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| demo_ai_win_now | forced_win | EASY | 5 | 0 | 0.027 | 0.029 | 0.025 | 0.029 |
| demo_ai_win_now | forced_win | MEDIUM | 5 | 0 | 0.025 | 0.032 | 0.025 | 0.032 |
| demo_ai_win_now | forced_win | HARD | 5 | 0 | 0.025 | 0.026 | 0.025 | 0.026 |
| demo_forced_block | forced_block | EASY | 5 | 0 | 0.059 | 0.061 | 0.058 | 0.061 |
| demo_forced_block | forced_block | MEDIUM | 5 | 0 | 0.059 | 0.064 | 0.058 | 0.064 |
| demo_forced_block | forced_block | HARD | 5 | 0 | 0.059 | 0.059 | 0.058 | 0.059 |
| demo_midgame_search | representative_midgame | EASY | 5 | 0 | 2.807 | 4.566 | 2.714 | 4.566 |
| demo_midgame_search | representative_midgame | MEDIUM | 5 | 0 | 10.749 | 11.056 | 10.187 | 11.056 |
| demo_midgame_search | representative_midgame | HARD | 5 | 0 | 85.432 | 91.927 | 84.866 | 91.927 |
| opening_two_stones | opening | EASY | 5 | 0 | 2.114 | 2.195 | 2.084 | 2.195 |
| opening_two_stones | opening | MEDIUM | 5 | 0 | 15.557 | 15.934 | 15.198 | 15.934 |
| opening_two_stones | opening | HARD | 5 | 0 | 141.503 | 144.039 | 141.128 | 144.039 |
| opening_six_stones | opening | EASY | 5 | 0 | 2.557 | 2.668 | 2.536 | 2.668 |
| opening_six_stones | opening | MEDIUM | 5 | 0 | 11.029 | 11.171 | 10.972 | 11.171 |
| opening_six_stones | opening | HARD | 5 | 0 | 103.349 | 105.406 | 100.769 | 105.406 |
| mid_game_spread | midgame | EASY | 5 | 0 | 5.531 | 6.159 | 5.372 | 6.159 |
| mid_game_spread | midgame | MEDIUM | 5 | 0 | 22.956 | 24.747 | 22.203 | 24.747 |
| mid_game_spread | midgame | HARD | 5 | 0 | 907.047 | 961.171 | 846.708 | 961.171 |
| edge_midgame | edge | EASY | 5 | 0 | 12.190 | 12.358 | 11.955 | 12.358 |
| edge_midgame | edge | MEDIUM | 5 | 0 | 67.146 | 69.495 | 65.299 | 69.495 |
| edge_midgame | edge | HARD | 5 | 0 | 232.335 | 374.665 | 228.062 | 374.665 |
| competing_open_threes | tactical_midgame | EASY | 5 | 0 | 0.122 | 0.317 | 0.119 | 0.317 |
| competing_open_threes | tactical_midgame | MEDIUM | 5 | 0 | 0.120 | 0.123 | 0.119 | 0.123 |
| competing_open_threes | tactical_midgame | HARD | 5 | 0 | 0.118 | 0.119 | 0.117 | 0.119 |
| complex_mid_game | forced_block | EASY | 5 | 0 | 0.094 | 0.095 | 0.090 | 0.095 |
| complex_mid_game | forced_block | MEDIUM | 5 | 0 | 0.090 | 0.091 | 0.089 | 0.091 |
| complex_mid_game | forced_block | HARD | 5 | 0 | 0.089 | 0.125 | 0.089 | 0.125 |
| dense_midgame_34_stones | dense_midgame | EASY | 5 | 0 | 8.313 | 8.993 | 7.750 | 8.993 |
| dense_midgame_34_stones | dense_midgame | MEDIUM | 5 | 0 | 37.553 | 38.024 | 37.229 | 38.024 |
| dense_midgame_34_stones | dense_midgame | HARD | 5 | 0 | 180.626 | 182.237 | 180.005 | 182.237 |
| dense_midgame_42_stones | dense_midgame | EASY | 5 | 0 | 0.133 | 0.140 | 0.132 | 0.140 |
| dense_midgame_42_stones | dense_midgame | MEDIUM | 5 | 0 | 0.181 | 0.501 | 0.132 | 0.501 |
| dense_midgame_42_stones | dense_midgame | HARD | 5 | 0 | 0.132 | 0.138 | 0.130 | 0.138 |

## Demo fixtures

The exact coordinates and expected tactical outcomes are checked into reports/ai-demo-boards.json.

- demo_ai_win_now: 15 measured calls; failures=0; expected tactical outcome=PASS.
- demo_forced_block: 15 measured calls; failures=0; expected tactical outcome=PASS.
- demo_midgame_search: 15 measured calls; failures=0; expected tactical outcome=NOT APPLICABLE (generic midgame).

## Artifacts

- reports/benchmark-windows-sprint3-fixed/ai-benchmark.csv — raw per-call measurements (including warm-ups flagged explicitly).
- reports/benchmark-windows-sprint3-fixed/ai-benchmark.json — environment, configuration, raw rows and summaries.
- reports/ai-demo-boards.json — fixed demo-board coordinates and expected tactical outcomes.

## Overall status: PASS (benchmark outputs legal and expected moves)

Measured trial failures: 0. This status only covers the listed fixtures, configurations and captured environment.
