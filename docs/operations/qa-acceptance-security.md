# Production QA Acceptance Security

The production QA routes are disabled unless the service starts with explicit, valid opt-in configuration. When disabled or incompletely configured, `/api/qa` returns HTTP 404 and does not call the game service. Ordinary game, health, readiness, and history routes remain available.

## Required configuration

Configure these values in both the application runtime and the protected GitHub `production` Environment:

| Name | Type | Requirement |
|---|---|---|
| `CAROAI_QA_ENABLED` | Runtime environment variable and GitHub Environment variable | Exact value `true` to enable QA routes. Missing, false, or any other value keeps them disabled. |
| `CAROAI_QA_HMAC_SECRET` | Runtime environment secret and GitHub Environment secret | At least 32 UTF-8 bytes of operator-generated random secret material. The value in the application runtime and GitHub Environment must match. Never store the value in the repository or print it in logs. |

The release workflow fails its pre-deployment configuration check unless the GitHub Environment has QA enabled and a sufficiently long HMAC secret. The application must also have the matching values configured before the post-deployment acceptance runner can authenticate.

## Request authentication and scope

The runner creates a random 128-bit run ID and a short-lived HMAC-SHA256 capability over the exact run ID and expiry timestamp. It sends these as separate headers:

- `X-CaroAI-QA-Run-ID` scopes creation and cleanup to one QA run.
- `X-CaroAI-QA-Capability` authenticates the caller; the server verifies the signature with constant-time comparison and accepts no more than 600 seconds of remaining lifetime.

A run ID alone is never authorization. Missing, malformed, expired, altered, or wrong-run capabilities receive HTTP 401. Capability values are not returned by the API or printed by the runner. The runner reports only the run ID if cleanup fails.

## Resource limits and data isolation

- A run may create at most two QA games. PostgreSQL enforces this across workers and replicas using an atomic quota row. Cleanup removes tagged game data but retains quota usage until the capability expires, so cleanup cannot reset the limit.
- `qa_run_usage` is introduced by migration `003_qa_run_usage.sql`; normal gameplay records and APIs are unchanged.
- QA control routes allow at most 10 authenticated control requests per minute per run and 30 total per minute per Python process, plus at most two simultaneous QA control operations per Python process. These request and concurrency limits are **process-local** and multiply with worker/replica count; they are not deployment-wide limits.
- Ordinary gameplay is not subject to these QA-specific request/concurrency guards.
- Cleanup selects only games tagged with the exact run ID and removes their dependent analysis and move rows in the same transaction. Untagged games and games from other runs remain intact.

## Operations

Keep the HMAC secret restricted to the application runtime and the protected release Environment. Rotate both copies together. The signed capability expires automatically; do not copy it into CI output or tickets. After a cleanup failure, set `CAROAI_PUBLIC_URL` and `CAROAI_QA_HMAC_SECRET` from the protected operator environment, then run `python scripts/production_qa_acceptance.py --cleanup-run-id <run-id>`. The runner generates a fresh short-lived capability in memory, retries exact-run cleanup, and verifies the returned games are no longer readable or present in history. It does not create new games or print the capability. Never use the run ID by itself as a cleanup credential.
