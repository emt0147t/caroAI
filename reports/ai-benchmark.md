# CaroAI Sprint 3 — AI Benchmark

**Status: NOT RUN on the Sprint 3 benchmark branch yet.** This file is an explicit placeholder, not performance evidence. Do not infer a median, p95, SLO pass, or container result from Sprint 2 measurements.

After syncing the branch and installing project requirements, run from the repository root:

    py -3 -m pytest tests/unit/test_ai_sprint3_benchmark.py -v --tb=short
    py -3 scripts/benchmark_ai_sprint3.py --runs 5 --warmup 1
    py -3 -m pytest tests/ -v --tb=short
    git diff --check

The benchmark command writes:
- reports/ai-benchmark.md — generated summary and environment/SHA.
- reports/ai-benchmark.csv — individual measured calls and warm-ups explicitly marked.
- reports/ai-benchmark.json — raw data, fixture boards, configuration, and summaries.
- reports/ai-demo-boards.json — the three fixed demo cases.

The script includes 11 fixed/deterministic nonterminal fixtures, all three configured difficulties, root candidate count, legality/output-shape checks, board immutability, median, and nearest-rank p95. Per-fixture p95 from five samples equals the maximum and is not a stable production percentile. The aggregate p95 combines the equal-weight fixture workload and must not be described as the actual production request distribution.

The proposed p95 <= 2,000 ms target from Issue #28 remains **PENDING TEAM CONFIRMATION**. Benchmarking on Windows is local evidence only. Run the same command in the Linux/Docker environment provided by M4 and keep that report separate; do not combine environments.

No measured values are populated here because this coding environment cannot execute the repository's Python test suite or benchmark. Replace this placeholder by running the script on the exact SHA being reported. Do not mark Issue #28 complete until results, raw artifacts, and integrated-SHA verification are attached.
