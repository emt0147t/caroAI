# Production QA Acceptance Security

The production QA routes are disabled unless the service starts with explicit, valid opt-in configuration. When disabled or incompletely configured, `/api/qa` returns HTTP 404 and does not call the game service. Ordinary game, health, readiness, and history routes remain available.

## Required configuration

Configure these values in both the application runtime and the protected GitHub `production` Environment:

| Name | Type | Requirement |
|---|---|---|
| `CAROAI_QA_ENABLED` | Runtime environment variable and GitHub Environment variable | Exact value `true` to enable QA routes. Missing, false, or any other value keeps them disabled. |
| `CAROAI_QA_HMAC_SECRET` | Runtime environment secret and GitHub Environment secret | At least 32 UTF-8 bytes of operator-generated random secret material. The value in the application runtime and GitHub Environment must match. Never store the value in the repository or print it in logs. |

The release workflow fails its pre-deployment configuration check unless the GitHub Environment has QA enabled and a sufficiently long HMAC secret. The application must also have the matching values configured before the post-deployment acceptance runner can authenticate. Before triggering the production image deploy, the approved release workflow synchronizes `CAROAI_QA_ENABLED` and `CAROAI_QA_HMAC_SECRET` from the protected GitHub `production` Environment into the Render service-level environment variables. This keeps the runtime and runner on the same values without printing either secret or replacing unrelated service variables.

After the production acceptance attempt, the release workflow runs a fail-closed finalizer whenever the full-SHA image was published. The finalizer updates only the Render service-level `CAROAI_QA_ENABLED` variable to the exact string `false`, triggers a deployment of the same `IMAGE_NAME:GITHUB_SHA` image, and waits until Render reports that exact image as live. It then verifies that `POST /api/qa/games` and `DELETE /api/qa/runs` return HTTP 404 without a capability, while `/health`, `/ready`, the dashboard, and history endpoints remain HTTP 200. The finalizer never prints the HMAC secret and does not replace unrelated environment variables.

The shutdown finalizer uses `always()`: it also attempts to close QA routes when gameplay acceptance fails, so the cleanup result is not hidden by a successful shutdown step. A failed gameplay/cleanup acceptance still leaves the overall release job failed. If the shutdown step itself fails, do not assume QA routes are closed; inspect its failure and verify the live deployment before declaring the release secure.

The protected GitHub Environment's `CAROAI_QA_ENABLED=true` remains the release preflight setting so a later approved release can run acceptance. The Render runtime is deliberately returned to `false` at the end of each release. The next approved workflow run synchronizes the temporary `true` value immediately before the acceptance deployment and the finalizer turns it off again.

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

Keep the HMAC secret restricted to the application runtime and the protected release Environment. Rotate both copies together. The signed capability expires automatically; do not copy it into CI output or tickets.

If the acceptance runner reports a cleanup failure, the shutdown finalizer still disables QA routes after the published image is available. The `/api/qa` routes must therefore be temporarily re-enabled before exact-run recovery: use the Render service configuration to set `CAROAI_QA_ENABLED=true` while keeping the existing HMAC secret unchanged, deploy the currently approved full-SHA image, then run `python scripts/production_qa_acceptance.py --cleanup-run-id <run-id>` with `CAROAI_PUBLIC_URL` and `CAROAI_QA_HMAC_SECRET` supplied from the protected operator environment. Use only the exact run ID printed by the failed acceptance attempt. After recovery, set `CAROAI_QA_ENABLED=false`, redeploy that same full-SHA image, and verify the QA create and cleanup routes return HTTP 404 while ordinary health/readiness/history endpoints remain available. Never print or paste the secret, and never use the run ID by itself as a cleanup credential.
