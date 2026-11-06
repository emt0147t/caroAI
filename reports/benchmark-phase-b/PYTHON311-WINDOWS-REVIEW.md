# Phase B review correction — Python 3.11 Windows run

Run ID: `phaseb-20261106T140340Z-980e7124`  
Source: `f0f1753090fb217d35471d2685778d0feb85df96`  
Runtime: Python 3.11.9, Windows 10, one API worker, PostgreSQL 15.19. PostgreSQL observation interval: 10 ms.

## Validation

The ZIP's CSV files agree with the JSON summary: 3,723 client request rows, 19,942 server metric rows, 46,299 PostgreSQL observation samples, and 2,401 persisted-game checks. All 2,401 checks were valid. There were no unexpected HTTP errors or invalid successful AI responses. The 1,320 HTTP 400 responses are the expected by-turn rejections in the same-game contention groups.

The run covers 30 measured iterations plus 3 warm-ups per workload group. Same-game groups have 30 successful moves per group, with the remaining requests rejected after the first move commits.

## Corrected IMPOSSIBLE results

| Scenario | Concurrency | Engine P95 (ms) | API P95 (ms) | Row-lock query P95 (ms) | Observed lock wait P95 (ms) |
|---|---:|---:|---:|---:|---:|
| Single request | 1 | 728.4 | 739.9 | 1.3 | 0 |
| Different games | 2 | 1,493.9 | 1,565.7 | 1.6 | 0 |
| Different games | 4 | 2,827.9 | 3,263.6 | 150.8 | 0 |
| Different games | 8 | 5,329.8 | 6,311.7 | 329.7 | 0 |
| Same game | 2 | 1,053.5 | 1,070.6 | 970.4 | ~590 |
| Same game | 4 | 799.1 | 822.7 | 743.3 | ~440 |
| Same game | 8 | 855.3 | 888.9 | 624.2 | ~360 |

Lock-wait estimates are approximate lower bounds from 10 ms polling. A `SELECT ... FOR UPDATE` duration includes database execution and any wait; it is not pure lock wait.

## Correct interpretation

The 2,000 ms engine reference is provisional and has not been accepted as an SLO. Single-request and different-game concurrency 2 engine P95 are below it. Different-game concurrency 4 and 8 are above it. The generated report sentence claiming concurrency 4 was below the reference is incorrect; the table and raw rows show 2,827.9 ms.

For different-game IMPOSSIBLE load, throughput stays around 1.40–1.49 requests/s from concurrency 1 through 8 while API P95 rises from 748.7 ms to 6,311.7 ms. No PostgreSQL lock wait was observed in these groups. The data points to search contention in the one-worker API process; it does not isolate Python GIL effects from CPU scheduling.

Same-game contenders do wait on the row lock held through search. At concurrency 2 the observed lock-wait P95 is about 590 ms; at concurrency 4 and 8 it is about 440 ms and 360 ms. These are sampled estimates. Each batch still commits only one AI move; the other requests receive the expected turn-validation HTTP 400.

Peak active database connections were 8. SQLAlchemy's default allowance is 15 (pool size 5 plus overflow 10), and no connection errors appeared. Pool checkout wait was not directly instrumented, so the run does not establish pool-acquisition latency.

## Limits and next engineering decision

This run used a five-ply opening fixture, Windows 10, Python 3.11.9, 16 logical CPUs, and one API worker. The archive's environment metadata omits CPU model, RAM, Docker version/image digest, and the resolved Python package freeze; those details limit exact reproduction. Read-under-load is only one game-detail/history pair and does not support a stable P95.

A concurrency guard for IMPOSSIBLE is a reasonable follow-up to evaluate: on this host, concurrency 2 stayed under the provisional 2 s engine reference, while 4 did not. Confirm the workload and SLO before adopting a production limit. A transaction refactor can reduce lock and connection occupancy, but it will not remove CPU search contention. Any refactor needs state revalidation under lock before persisting.

No business logic or production configuration was changed by this review.
