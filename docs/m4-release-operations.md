# M4 release operations runbook

Owner: Vinh (@macvinh2007-sketch)  
Repository: `emt0147t/caroAI`  
Release workflow: `.github/workflows/ci-cd.yml`  
Last reviewed: 2026-11-02

## 1. Promotion source and baseline

The intended promotion source is `develop`. Do not release the old `main` baseline.

Repository state captured for this M4 handover:
- `main` baseline: `d444119d5eb757e364f904bb9eacddd27e14e507`.
- `develop` baseline: `e45b077fefee9e08136215c366178c2fee4fb81b`.
- GitHub comparison `main...develop`: 352 commits ahead, 0 behind at the time checked.
- `feature/devops` was fast-forwarded to the recorded `develop` baseline before the M4 commits. The M4 PR is based on `develop`, not directly on `main`.

**M1 confirmation is still required.** The SHA above is the observed `develop` baseline, not a claim that M1 has signed it off. Before opening a promotion PR, M1 must confirm the intended source SHA and complete backend acceptance. Recheck `develop` and PR #46 at that time; if either changes, update this record and re-run all required checks against the new head. Do not dispatch a release from a stale `main`.

### PR disposition

- PR #35 is **CLOSED / SUPERSEDED**, not merged. It targeted the stale `main` baseline and proposed process-local/in-memory History. The current `develop` implementation uses SQLAlchemy-backed persistence for `GET /api/history`; do not reopen or merge PR #35.
- PR #46 is the M1 backend acceptance/rollback handover. It is **not** a production release authorization and does not replace the separately reviewed `develop → main` promotion PR.
- PR #47 is the M4 CI/CD and release-workflow deliverable. It must merge to `develop`, not directly to `main`. M1 review/sign-off and M5 QA review are separate gates.

## 2. CI and disposable database acceptance

Normal push/PR validation is non-production. The workflow runs frontend syntax/regression checks, Python flake8/pytest, Docker Compose configuration validation, PostgreSQL acceptance, Compose functional/persistence smoke, secret scanning, Browser E2E, and a non-publishing Docker candidate build.

### PostgreSQL acceptance

The PostgreSQL job uses a disposable `caroai_test` database and configures:
- `pg_isready` health checking.
- `TEST_DATABASE_URL` pointing to the CI PostgreSQL service.
- `CAROAI_TEST_DATABASE_CONFIRMED=disposable-test-database`.
- A JUnit guard that fails if any PostgreSQL acceptance test is skipped.

Never point CI or an automated smoke test at the production `DATABASE_URL`.

### Compose functional and persistence smoke

The `compose-smoke` job uses the repository's disposable Compose stack. It exercises:
1. PvP game creation and one player move.
2. PvAI game creation, human move, and AI move.
3. Game detail responses, board state, and expected `move_count`.
4. History lookup for both created games.
5. Restart of the API container, then re-read of both games and History to verify persistence.
6. Cleanup with `docker compose down --volumes --remove-orphans` even if an earlier step fails.

This is evidence for persistence across an **API container restart in CI only**. It is not evidence of staging or production persistence.

For controlled local reproduction, use disposable local containers and never source production environment values:

```bash
docker compose up --build -d
docker compose ps
docker compose logs --no-color db app
curl --fail http://localhost:8000/health
curl --fail http://localhost:8000/ready
docker compose down --volumes --remove-orphans
```

The application entrypoint applies versioned SQL migrations before Uvicorn starts. `/health` is liveness; `/ready` checks database connectivity using the application's readiness logic. Neither endpoint proves that a particular game record persisted.

## 3. GitHub Environment: production

**OWNER VERIFICATION REQUIRED**

An authorized repository owner/admin must inspect Settings → Environments → `production` and confirm each item below. This workflow/code review alone does not prove the Environment has been configured.

1. An Environment named exactly `production` exists.
2. At least one authorized **Required reviewer** is configured.
3. **Prevent self-review** is enabled.
4. Deployment branch/tag restrictions allow only `main`.
5. The required secrets are stored as Environment-scoped secrets:
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_TOKEN`
   - `RENDER_DEPLOY_HOOK`
   - `RENDER_API_KEY`
   - `RENDER_SERVICE_ID`
6. The Environment variable `CAROAI_PUBLIC_URL` is set to the intended public HTTPS base URL, without a trailing slash.

To verify configuration without exposing values, an owner can inspect the Environment's secret/variable names and update timestamps in GitHub Settings, then run a properly approved release preflight. The workflow checks only whether required values are non-empty and validates the public URL format; it does not print secret values. Do not paste values into PRs, issue comments, docs, CI logs, screenshots, or artifacts.

The dispatch input `release_approved=true` is only a request to run the release job. It is not a substitute for GitHub Environment review. Until the owner confirms these protections, report **PENDING OWNER VERIFICATION** and do not claim the production gate is fully configured.

## 4. Render production configuration

**OWNER VERIFICATION REQUIRED**

An authorized Render owner must verify the production service before release:

- The service uses an image-backed deployment (not a source/build deployment).
- The configured image repository is `docker.io/<namespace>/caroai`.
- If the Docker Hub repository is private, Render has the appropriate registry credentials.
- Render's `DATABASE_URL` is configured in the Render service's secret/environment settings and points to the intended production PostgreSQL database.
- Startup migration behavior is understood and compatible with the image being released. Do not assume a successful build means migrations have run.
- The Render service and GitHub Environment variable `CAROAI_PUBLIC_URL` refer to the same intended public service.
- The public service uses HTTPS.

Do not record a real database URL, password, token, API key, or deploy hook in this document.

### Image and deployment verification

The approved release publishes two SHA-tagged references: the full source SHA and a 12-character short SHA. It also records the image digest returned by the Docker build when available. The Render deploy hook receives the **full-SHA image reference**.

A tag containing a SHA is not automatically immutable. Unless Docker Hub tag-protection/immutability policy has been independently verified, describe these as **SHA-tagged image references**, not immutable tags. Do not use `latest` as release evidence.

The workflow must obtain the Render deployment ID from the deploy-hook response without printing the raw response, poll that deployment through the Render API, and fail unless Render reports status `live` and the exact requested full-SHA image reference. A deploy-hook HTTP success, Docker push, or build success alone is not release evidence.

## 5. Approved release procedure

Do not skip the order below:

1. M1 confirms the baseline/source SHA and completes backend acceptance, including the handover evidence in PR #46.
2. Re-check the latest `develop` SHA and confirm it is the agreed source. Re-run all required checks on the intended commit.
3. Open a separate promotion PR from `develop` to `main`. Include the approved source SHA and evidence; obtain the required review and passing checks.
4. Merge the promotion PR only after approval. Record its merge SHA.
5. Verify `main` points to the approved promotion commit. Do not dispatch from the stale baseline `d444119d5eb757e364f904bb9eacddd27e14e507`.
6. Confirm the owner has completed GitHub Environment and Render configuration verification. If not, stop with **PENDING OWNER VERIFICATION**.
7. In GitHub Actions, select **CaroAI CI**, choose branch `main`, and dispatch with `release_approved=true`.
8. Wait for an authorized Required reviewer to approve the `production` Environment deployment. A dispatch without Environment approval must not publish/deploy.
9. Confirm all prerequisite jobs succeeded and the release job publishes the full- and short-SHA-tagged image references. Record the image digest when returned.
10. Confirm the Render deployment ID, `live` status, and exact full-SHA image reference. A mismatch or timeout is a failed release.
11. Confirm the public URL is valid HTTPS and that read-only GET `/health` and GET `/ready` both return successful responses within the configured retry/timeout policy.
12. Perform only the non-writing production checks described in section 7. Save the workflow URL, run ID, source SHA, image references/digest, Render deployment ID, public URL, timestamps, and sanitized outcomes.

Pull-request and normal push workflows must not publish an image or trigger Render. Production release must never be dispatched just to test the workflow.

## 6. Functional smoke testing by environment

Keep the three environments and their evidence separate.

### CI / disposable Compose

Allowed automated write tests:
- PvP create/move.
- PvAI create/human move/AI move.
- History lookup and game detail.
- Board and `move_count` assertions.
- Persistence after API container restart.
- Cleanup of disposable Compose resources.

This is the automated functional acceptance path used by the PR checks.

### Staging

Staging must use a separate staging service and staging PostgreSQL database, never production credentials/data. Validate:
- Public staging UI and API.
- CSS, JavaScript, and static assets.
- CORS and browser console/network behavior.
- PvP, PvAI, History, and game detail.
- Browser E2E.
- Persistence after a controlled staging redeploy.

Record the staging URL, source/image SHA, deployment ID, test record IDs, before/after timestamps, and sanitized results.

### Production — read-only release verification

The automated production release job is intentionally restricted to:
- Deployment status and exact image-reference verification.
- HTTPS base URL format verification.
- GET `/health`.
- GET `/ready`.

It must not call POST `/api/games`, POST `/moves`, POST `/ai-move`, or any other endpoint that mutates production state. Do not add a public write-smoke to the release workflow.

A manual, non-writing production UI/assets/CORS check may load the home page, CSS/JS/static assets, and use safe GET/OPTIONS requests. Do not create a game or change user data as part of routine release verification. Health/readiness and static asset checks do not prove PvP/PvAI functionality or game persistence on production.

### Separate production write/persistence acceptance

A production game write test is outside the release workflow and may happen only when both M1 and an authorized production owner have explicitly approved a controlled test plan. That plan must define the intended test record, visibility in user History, operator, timing, evidence, and data-retention handling. Do not automatically clean up or delete production records, and do not add a public deletion endpoint merely to hide a test.

Record the public game ID, source/image SHA, timestamps before and after redeploy, Render deployment ID, observed History/detail state, and sanitized evidence. If there is no approved process, mark production persistence **NOT TESTED / PENDING APPROVAL**. Never use CI or staging evidence to claim production acceptance.

## 7. Production read-only verification

After Render confirms the exact requested image is live:

1. Record the Render deployment ID, live status, and image reference.
2. Confirm the public base URL is HTTPS, has a valid hostname, and contains no URL credentials, path, query, fragment, or trailing slash.
3. GET `/health` with a connection timeout and request timeout.
4. GET `/ready` with a connection timeout and request timeout.
5. Retry each endpoint within the workflow's bounded retry window. A non-2xx result or exhausted retry window fails the release job.
6. Save timestamped, sanitized HTTP status outcomes. Do not save response headers, cookies, tokens, deploy hooks, or secrets.

Interpretation:
- `/health` demonstrates that the application responds (liveness).
- `/ready` demonstrates the database readiness check implemented by the application.
- Neither proves that game creation, moves, History, or data persistence works.

The release job must remain read-only with respect to production business data. The public write-smoke previously present in the workflow has been removed; PvP/PvAI/History writes are covered by disposable Compose instead.

## 8. Persistence evidence and scope

Use precise labels:

| Evidence | What it proves | What it does not prove |
|---|---|---|
| PostgreSQL acceptance | API/model/migration acceptance against disposable CI PostgreSQL | Production database behavior |
| Compose persistence after API restart | Test records survive an API container restart with the disposable Compose database | Persistence after staging or production redeploy |
| Staging persistence after redeploy | The recorded staging game survived the staging redeploy tested | Production persistence |
| Production persistence after redeploy | Only an explicitly owner-approved production test can establish this | It is not established by CI, staging, `/health`, or `/ready` |

Do not report production persistence as PASS unless a controlled owner-approved production test was actually completed and its public game ID, timestamps, image SHA, Render deployment ID, and before/after state are recorded.

## 9. Rollback readiness and procedure

Before a release, identify a previously deployed full source SHA and verify that the corresponding full-SHA image reference is still available in Docker Hub. Record its digest when available. Do not assume a previous SHA-tagged reference is immutable unless registry policy has been checked.

For an authorized rollback:

1. Identify the previous known-good full source SHA and image reference.
2. Retrieve the Render deploy hook and Render API key from the approved secret store. Do not paste them into a terminal transcript or print them.
3. Trigger the Render deployment for `docker.io/<namespace>/caroai:<PREVIOUS_FULL_SHA>` using the securely retrieved deploy hook.
4. Capture the returned deployment ID without exposing the raw hook response.
5. Poll the Render API until the deployment is `live`; verify the exact previous full-SHA image reference.
6. Re-run public HTTPS GET `/health` and GET `/ready`.
7. Record the incident/reason, previous SHA, image digest, deployment ID, timestamps, sanitized health/readiness outcomes, and operator.

**Database warning:** rolling back an application image does not automatically roll back database schema changes. For a schema-changing release, require a separately reviewed migration plan, a backup/restore plan, and an explicit backward-compatibility assessment. Never run an old image against a schema it cannot understand.

## 10. Secret hygiene

The workflow has two independent blocking scans:

1. **PR-range scan:** Gitleaks Action, pinned by commit SHA, with comments disabled.
2. **Full-history scan:** checkout with `fetch-depth: 0` and `persist-credentials: false`, then pinned Gitleaks CLI using:
   ```bash
   gitleaks git --redact --verbose --no-banner /repo
   ```

The PR-range scan is not a substitute for a full-history scan. The full-history job must report the actual number of commits scanned and finish with no leaks. Both scans are dependencies of candidate build and production release.

Before promotion/release:
- Review tracked files for accidental `.env`, private key, token, password, or database URL files. Only sanitized placeholders belong in `.env.example`.
- Inspect CI logs/artifacts for accidental sensitive output; do not publish raw secret-bearing reports.
- If a credential is detected, block promotion/release, notify M1 and the repository owner, revoke/rotate it with the provider, and assess history/log cleanup. Removing the credential from the latest file alone is not sufficient.
- Never put production values in Git, PR comments, documentation, screenshots, artifacts, or logs.

The most recent full-history evidence recorded before this revision was 348 commits scanned with no leaks on the previous PR head. **That result does not certify the revised head.** Record the latest full-history run URL, actual scanned commit count, and result after this revision's checks finish.

## 11. Release evidence record

Complete every field only with observed evidence. Use `PENDING`, `NOT RUN`, or `NOT APPLICABLE` where appropriate; do not invent values.

| Evidence | Required record |
|---|---|
| M1 source sign-off | Reviewer/date + approved source SHA |
| Promotion PR | URL + review/checks + merge SHA |
| Required checks | Workflow URLs + conclusion on final SHA |
| M4 PR | PR URL + final head SHA + review status |
| Release workflow | URL + run ID + conclusion |
| Source | Full source SHA |
| Docker image | Repository + full/short SHA tags + digest if available |
| Render deployment | Deployment ID + live status |
| Render image | Exact deployed full-SHA image reference |
| Public URL | HTTPS base URL |
| Health/readiness | Timestamp + sanitized GET status for each |
| CI PvP/PvAI/History | Workflow URL + test result |
| Browser E2E | Workflow URL + artifacts/result |
| Staging UI/CORS | Timestamp + sanitized evidence |
| Staging persistence | Record ID + before/after timestamp + deployment evidence |
| Production persistence | Only an explicitly owner-approved test record; otherwise NOT TESTED |
| Rollback | Previous full-SHA image availability + deployment verification |
| Secret hygiene | PR scan + full-history scan URL, scanned commit count, result |
| Owner verification | GitHub Environment and Render config review status |

## 12. M4 completion gates

### Level 1 — PR #47 Ready for review

Require: no production write-smoke; full PvP/PvAI/History/game-detail/persistence tests in disposable CI or staging; production release restricted to read-only checks; Environment gate fully described; exact `workflow_dispatch` + `main` + `release_approved=true` condition; blocking PR-range and full-history scans; full-SHA Render verification; bounded health/readiness retries; runbook complete; all required checks green on the final head; no secrets in tracked files/logs; accurate PR description/evidence; and PR no longer Draft.

### Level 2 — PR #47 may merge to develop

Additionally require M1 review of source/promotion boundary, M5 QA review as applicable, no unresolved review threads, required checks green on final SHA, base branch still `develop`, and merge only into `develop`. Record the merge SHA.

### Level 3 — M4 production release completed

Separate gate; merging PR #47 does not satisfy it. Require completed M1 backend acceptance, reviewed/merged `develop → main` promotion, `main` at the approved source, owner-verified GitHub Environment and Render/database configuration, approved release dispatch, published SHA-tagged image/digest, Render `live` on the exact image, successful public HTTPS health/readiness, UI/assets/CORS verification, functional acceptance in the appropriate environment, persistence evidence for the environment claimed, rollback image/procedure verification, clean credential hygiene, and a completed evidence record.

If the production owner has not verified the Environment/Render configuration, report **PENDING PRODUCTION OWNER VERIFICATION**. If the production release was not authorized, report **PENDING RELEASE APPROVAL**. Do not mark production release complete based only on green CI.
