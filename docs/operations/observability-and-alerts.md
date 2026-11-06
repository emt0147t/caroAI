# CaroAI observability and initial alert guidance

**Current code target:** Phase C feature branch; the metrics endpoint becomes available only after this code is deployed.  
**Production dashboard:** Render service `srv-dbkd2dflk1mc73fd2ukg`.  
**SLO status:** none of the thresholds below are formally adopted SLOs. They are initial operational warning/critical recommendations that must be tuned against measured production traffic and the Render plan's actual capacity.

## Application metrics

The application exports Prometheus text format at `GET /metrics` only when `CAROAI_METRICS_TOKEN` is configured. The route requires `Authorization: Bearer <token>` and returns 404 when no token is configured; missing or incorrect credentials receive HTTP 401. Store the token as a Render secret or another secret-manager value, never in source control.

| Metric | Labels | Meaning |
|---|---|---|
| `caroai_http_requests_total` | `method, route, status` | HTTP request/error rate by fixed normalized route |
| `caroai_http_request_duration_seconds` | `method, route` | API/UI HTTP duration histogram |
| `caroai_ai_search_duration_seconds` | `difficulty, outcome` | Engine duration split into normal search, tactical shortcut, and timeout fallback |
| `caroai_ai_search_nodes` | `difficulty` | Visited Minimax nodes |
| `caroai_ai_root_candidates` | `difficulty` | Available root candidates before search |
| `caroai_ai_generated_candidates` | `difficulty` | Generated candidates across visited nodes |
| `caroai_ai_average_branching_factor` | `difficulty` | Mean post-cap branching factor per search |
| `caroai_ai_alpha_beta_pruning_rate` | `difficulty` | Share of post-cap candidate edges pruned by alpha-beta cutoffs |
| `caroai_ai_candidate_cap_pruning_rate` | `difficulty` | Share of generated candidates removed by configured candidate caps at internal search nodes |
| `caroai_ai_search_timeouts_total` | `difficulty` | Searches that returned a deterministic legal fallback after budget expiry |
| `caroai_ai_admission_rejections_total` | `difficulty` | IMPOSSIBLE requests rejected by the per-process admission guard |
| `caroai_db_connections_checked_out` | none | Live SQLAlchemy DBAPI connections checked out in this process |
| `caroai_db_connection_hold_seconds` | none | Time a DBAPI connection remains checked out |
| `caroai_db_statement_duration_seconds` | `operation, row_lock` | SQL execution duration, operation grouped into SELECT/INSERT/UPDATE/DELETE/OTHER |
| `caroai_db_transaction_duration_seconds` | none | Root SQLAlchemy transaction duration |

### Cardinality and measurement notes

- Request routes are normalized to a finite route vocabulary. Raw game IDs, QA run IDs, query strings, SQL text, user data, and request IDs are never metric labels.
- AI metrics label only the four fixed difficulties and three fixed outcome groups. A tactical root shortcut is distinguished from depth-limited search; do not mix shortcut latency into a search-only latency comparison.
- Search node and candidate metrics are histograms, not per-game time series. Use the checked-in benchmark CSV/JSON to segment controlled fixtures; production runtime does not know a fixture's name.
- SQL `row_lock=true` identifies statement text containing `FOR UPDATE`; it does not measure the exact time spent waiting for the lock.
- Connection-hold duration measures checkout-to-checkin, not pool checkout wait. This application metric does not directly expose connection-acquisition latency.
- The checked-out gauge is per process. With multiple Uvicorn workers/instances, sum gauges across targets to approximate total connections; the admission guard is also process-local and does not coordinate between workers.
- Render CPU, memory, instance count, HTTP request count, and platform HTTP latency are provider metrics, not exported by `/metrics`. Track them in the Render service Metrics page. Neon is an external database provider, so the Render service's app metrics show SQLAlchemy connection-pool use, not Neon account-wide connection counts.

## Initial alert recommendations

Use the rules in `ops/monitoring/caroai-alerts.yml` as templates for Prometheus/Alertmanager. They are not installed or wired to a paging destination by this repository PR.

| Signal | Warning | Critical | Evaluation window |
|---|---:|---:|---|
| HTTP 5xx ratio | >1% | >5% | 5 minutes |
| Overall API/UI P95 | >2 seconds | >5 seconds | 5 minutes |
| IMPOSSIBLE search P95, excluding tactical shortcuts | >2.5 seconds | >5 seconds | 5 minutes |
| Checked-out DB connections (assuming default 5 + 10 overflow = 15 per process) | >12 | >14 | 5 minutes |
| DB connection-hold P95 | >500 ms | >2 seconds | 5 minutes |
| Root transaction P95 | >500 ms | >2 seconds | 5 minutes |
| Render service CPU | >80% | >95% | 10 / 5 minutes |
| Render service memory | >85% | >95% | 10 / 5 minutes |

The CPU/memory checks are operational dashboard guidance because this project does not configure a Render-to-Prometheus exporter or alert connector. Revisit the assumed SQLAlchemy pool cap if pool settings or instance count change. An IMPOSSIBLE guard rejection is explicit back-pressure, not necessarily an application fault; monitor its rate and correlate it with HTTP 429s.

## Metrics endpoint security

- `CAROAI_METRICS_TOKEN`: optional secret enabling `/metrics`; when unset, the endpoint is disabled (404). When set, requests must supply the exact bearer token. Use a dedicated random scrape token with read-only monitoring scope; do not reuse database, Docker Hub, or Render credentials.
- The scrape token is not logged or exposed as a Prometheus label. If a hosted scraper cannot send an Authorization header, use a private authenticated proxy or a dedicated exporter rather than making `/metrics` public.

## IMPOSSIBLE budget and admission configuration

All settings are optional and preserve current behavior when unset:

- `CAROAI_IMPOSSIBLE_TIME_BUDGET_MS`: no deadline when unset; a non-negative number of milliseconds when set. Root immediate-win and immediate-block checks always run before the deadline applies. A timeout returns a deterministic legal fallback and increments the timeout metric; it does not guarantee strategic quality.
- `CAROAI_IMPOSSIBLE_MAX_CONCURRENCY`: `0` (default) is unlimited; a positive integer limits in-flight IMPOSSIBLE searches per Python process.
- `CAROAI_IMPOSSIBLE_QUEUE_WAIT_MS`: `0` (default) fails fast when capacity is full; a positive integer waits up to that many milliseconds.

The admission guard is process-local. It is appropriate as a small first back-pressure mechanism for the current single-process topology. It is not a distributed limit: for multiple workers or multiple Render instances, use a shared queue/lock or a worker service before claiming a global concurrency cap.

## Operational runbook

1. Compare `caroai_http_requests_total` 5xx/429 rates with request duration by normalized route.
2. For slow PvAI requests, compare AI search duration/nodes/branching with SQL statement, connection-hold, and transaction histograms. Low row-lock query time with high AI time points to search/CPU contention; long connection hold/transaction duration points to transaction-boundary or DB occupancy.
3. Check Render CPU, memory, instance count and platform HTTP P95. Do not run a load test against production to reproduce an alert.
4. If the IMPOSSIBLE guard is active, check admission rejection rate and HTTP 429 volume. Increase capacity only after reviewing measured CPU/memory headroom.
5. If QA acceptance fails, first inspect whether the runner reports a cleanup failure. The runner prints its run capability only when cleanup fails; invoke the same `DELETE /api/qa/runs` with `X-CaroAI-QA-Run-ID` set to that exact capability. Do not delete unrelated games manually.
6. Keep the two-second Phase A/Phase B reference provisional until the team explicitly accepts an SLO and measures a representative production traffic distribution.

## Evidence still required

- Collect a new Phase C controlled AI benchmark (30 measured trials plus warmups per fixture/difficulty) after the instrumented engine is verified; update the raw CSV/JSON/report with a full source SHA.
- Run the new production PvP/PvAI QA acceptance only after this migration and API code are deployed by the approved production workflow.
- Select the Render workspace explicitly before querying Render CPU/memory/HTTP metrics through the connected monitoring integration.
- Confirm an alert manager / notification destination before treating any rule as an active alert.
