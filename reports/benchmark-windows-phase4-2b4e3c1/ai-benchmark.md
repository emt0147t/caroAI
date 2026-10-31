# CaroAI Sprint 3 — AI Benchmark

- Generated at (UTC): 2026-10-31T14:23:27+00:00
- Full source SHA: 2b4e3c167d7ca0a2a5b530b7a251ced6dd37d526
- Command: py -3 scripts/benchmark_ai_sprint3.py --runs 5 --warmup 1 --output-dir "C:\Users\Admin\caroAI-benchmark-fix\reports\benchmark-windows-phase4-2b4e3c1"
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
| captured_at_utc | 2026-10-31T14:23:16+00:00 |
| source_sha | 2b4e3c167d7ca0a2a5b530b7a251ced6dd37d526 |
| source_sha_method | git-head |
| python_version | 3.13.14 (tags/v3.13.14:fd17997, Jun 10 2026, 13:03:48) [MSC v.1944 64 bit (AMD64)] |
| python_executable | C:\Users\Admin\AppData\Local\Programs\Python\Python313\python.exe |
| argv | ['scripts/benchmark_ai_sprint3.py', '--runs', '5', '--warmup', '1', '--output-dir', 'reports/benchmark-windows-phase4-2b4e3c1'] |
| platform | Windows-11-10.0.26200-SP0 |
| system | Windows |
| machine | AMD64 |
| processor | Intel64 Family 6 Model 191 Stepping 2, GenuineIntel |
| cpu_name | Intel64 Family 6 Model 191 Stepping 2, GenuineIntel |
| is_container | False |
| container_hint | not detected |
| command | py -3 scripts/benchmark_ai_sprint3.py --runs 5 --warmup 1 --output-dir "C:\Users\Admin\caroAI-benchmark-fix\reports\benchmark-windows-phase4-2b4e3c1" |

## Per-difficulty summary

| Difficulty | Samples | Failures | Median (ms) | p95 (ms) | Min (ms) | Max (ms) | Proposed 2s threshold | SLO decision |
|---|---:|---:|---:|---:|---:|---:|---|---|
| EASY | 55 | 0 | 2.108 | 14.342 | 0.032 | 15.765 | BELOW PROPOSAL | PENDING_TEAM_CONFIRMATION |
| MEDIUM | 55 | 0 | 11.600 | 61.543 | 0.026 | 72.020 | BELOW PROPOSAL | PENDING_TEAM_CONFIRMATION |
| HARD | 55 | 0 | 99.576 | 973.855 | 0.025 | 1017.771 | BELOW PROPOSAL | PENDING_TEAM_CONFIRMATION |

## Per-fixture / difficulty results

| Fixture | Category | Difficulty | n | Failures | Median (ms) | p95 (ms) | Min (ms) | Max (ms) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| demo_ai_win_now | forced_win | EASY | 5 | 0 | 0.035 | 0.039 | 0.032 | 0.039 |
| demo_ai_win_now | forced_win | MEDIUM | 5 | 0 | 0.026 | 0.029 | 0.026 | 0.029 |
| demo_ai_win_now | forced_win | HARD | 5 | 0 | 0.026 | 0.027 | 0.025 | 0.027 |
| demo_forced_block | forced_block | EASY | 5 | 0 | 0.082 | 0.122 | 0.070 | 0.122 |
| demo_forced_block | forced_block | MEDIUM | 5 | 0 | 0.062 | 0.066 | 0.059 | 0.066 |
| demo_forced_block | forced_block | HARD | 5 | 0 | 0.061 | 0.105 | 0.059 | 0.105 |
| demo_midgame_search | representative_midgame | EASY | 5 | 0 | 2.685 | 4.741 | 2.636 | 4.741 |
| demo_midgame_search | representative_midgame | MEDIUM | 5 | 0 | 11.600 | 14.666 | 10.765 | 14.666 |
| demo_midgame_search | representative_midgame | HARD | 5 | 0 | 99.576 | 108.010 | 95.977 | 108.010 |
| opening_two_stones | opening | EASY | 5 | 0 | 2.108 | 2.576 | 2.072 | 2.576 |
| opening_two_stones | opening | MEDIUM | 5 | 0 | 19.344 | 25.328 | 17.694 | 25.328 |
| opening_two_stones | opening | HARD | 5 | 0 | 160.748 | 165.452 | 152.916 | 165.452 |
| opening_six_stones | opening | EASY | 5 | 0 | 2.831 | 4.176 | 2.579 | 4.176 |
| opening_six_stones | opening | MEDIUM | 5 | 0 | 14.822 | 17.169 | 12.232 | 17.169 |
| opening_six_stones | opening | HARD | 5 | 0 | 127.213 | 278.977 | 117.152 | 278.977 |
| mid_game_spread | midgame | EASY | 5 | 0 | 14.342 | 15.765 | 13.156 | 15.765 |
| mid_game_spread | midgame | MEDIUM | 5 | 0 | 61.543 | 72.020 | 53.128 | 72.020 |
| mid_game_spread | midgame | HARD | 5 | 0 | 973.855 | 1017.771 | 356.343 | 1017.771 |
| edge_midgame | edge | EASY | 5 | 0 | 6.374 | 7.458 | 4.167 | 7.458 |
| edge_midgame | edge | MEDIUM | 5 | 0 | 26.908 | 30.657 | 24.328 | 30.657 |
| edge_midgame | edge | HARD | 5 | 0 | 258.218 | 271.382 | 255.114 | 271.382 |
| competing_open_threes | tactical_midgame | EASY | 5 | 0 | 0.114 | 0.131 | 0.114 | 0.131 |
| competing_open_threes | tactical_midgame | MEDIUM | 5 | 0 | 0.115 | 0.118 | 0.114 | 0.118 |
| competing_open_threes | tactical_midgame | HARD | 5 | 0 | 0.118 | 0.126 | 0.116 | 0.126 |
| complex_mid_game | forced_block | EASY | 5 | 0 | 0.090 | 0.101 | 0.089 | 0.101 |
| complex_mid_game | forced_block | MEDIUM | 5 | 0 | 0.092 | 0.103 | 0.090 | 0.103 |
| complex_mid_game | forced_block | HARD | 5 | 0 | 0.092 | 0.160 | 0.090 | 0.160 |
| dense_midgame_34_stones | dense_midgame | EASY | 5 | 0 | 8.143 | 12.628 | 7.822 | 12.628 |
| dense_midgame_34_stones | dense_midgame | MEDIUM | 5 | 0 | 41.882 | 44.777 | 40.466 | 44.777 |
| dense_midgame_34_stones | dense_midgame | HARD | 5 | 0 | 211.315 | 224.979 | 198.820 | 224.979 |
| dense_midgame_42_stones | dense_midgame | EASY | 5 | 0 | 0.131 | 0.141 | 0.130 | 0.141 |
| dense_midgame_42_stones | dense_midgame | MEDIUM | 5 | 0 | 0.140 | 0.217 | 0.131 | 0.217 |
| dense_midgame_42_stones | dense_midgame | HARD | 5 | 0 | 0.131 | 0.133 | 0.128 | 0.133 |

## Demo fixtures

The exact coordinates and expected tactical outcomes are checked into reports/ai-demo-boards.json.

- demo_ai_win_now: 15 measured calls; failures=0; expected tactical outcome=PASS.
- demo_forced_block: 15 measured calls; failures=0; expected tactical outcome=PASS.
- demo_midgame_search: 15 measured calls; failures=0; expected tactical outcome=NOT APPLICABLE (generic midgame).

## Artifacts

- reports/benchmark-windows-phase4-2b4e3c1/ai-benchmark.csv — raw per-call measurements (including warm-ups flagged explicitly).
- reports/benchmark-windows-phase4-2b4e3c1/ai-benchmark.json — environment, configuration, raw rows and summaries.
- reports/ai-demo-boards.json — fixed demo-board coordinates and expected tactical outcomes.

## Overall status: PASS (benchmark outputs legal and expected moves)

Measured trial failures: 0. This status only covers the listed fixtures, configurations and captured environment.
