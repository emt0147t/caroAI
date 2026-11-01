# M4 release runbook

Owner: Vinh (@macvinh2007-sketch)  
Repository: `emt0147t/caroAI`  
Release workflow: `.github/workflows/ci-cd.yml`

## 1. Promotion plan and source control

The promotion source is `develop`; do not release the old `main` baseline.

Repository comparison captured on 2026-11-02:
- `main` baseline: `d444119d5eb757e364f904bb9eacddd27e14e507`.
- `develop` baseline: `e45b077fefee9e08136215c366178c2fee4fb81b`.
- GitHub compare `main...develop`: **352 commits ahead**, 0 behind. The earlier planning note saying 253 commits is stale and must not be used as the current count.
- `feature/devops` was 193 commits behind `develop` and had no unique commits. It was fast-forwarded (non-force) to the `develop` baseline before M4 edits. All M4 commits remain on `feature/devops`.

Promotion PR `develop → main` is intentionally a later gate. Coordinate with M1 and open it only after the M1 acceptance PR/evidence is finalized, all required checks are green, and the exact source SHA is agreed. Do not dispatch a release from the old `main` baseline or merge the promotion PR without review.

### PR #35 triage

PR #35 is closed and unmerged as superseded. It targeted the stale `main` baseline and proposed process-local/in-memory History. Current `develop` already serves `GET /api/history` from the SQLAlchemy-backed repository. Do not reopen or merge #35. PR #46 is the focused M1 backend acceptance/rollback handover; it is not the promotion PR and is not release authorization.

## 2. CI, migration, and database gates

PostgreSQL acceptance uses a disposable `caroai_test` database, `pg_isready`, `TEST_DATABASE_URL`, and `CAROAI_TEST_DATABASE_CONFIRMED=disposable-test-database`. The JUnit gate fails if any PostgreSQL acceptance test is skipped. Compose smoke creates a game, writes a move, restarts the API container, then checks the game and history again.

Run from the repository root against a disposable local database only:

```bash
docker compose up -d db
docker compose run --rm --no-deps --entrypoint python app -m scripts.migrate_database
docker compose up --build -d
docker compose ps
docker compose logs --no-color db app
curl --fail http://localhost:8000/health
curl --fail http://localhost:8000/ready
```

`/health` is liveness only. `/ready` executes `SELECT 1` using `DATABASE_URL` and returns 503 if PostgreSQL cannot be queried. Neither endpoint proves game persistence. The Docker entrypoint runs versioned SQL migrations before Uvicorn; production migration does not use SQLAlchemy metadata `create_all`.

## 3. GitHub Environment: production

Repository owner/admin must verify this in Settings → Environments → `production` (the current GitHub connector does not expose Environment protection-rule administration):

- At least one **Required reviewer** is configured.
- **Prevent self-review** is enabled.
- Deployment branch restriction allows only `main`.
- The following are Environment-scoped secrets, not values committed to files:
  - `DOCKERHUB_USERNAME`
  - `DOCKERHUB_TOKEN`
  - `RENDER_DEPLOY_HOOK`
  - `RENDER_API_KEY`
  - `RENDER_SERVICE_ID`
- Environment variable `CAROAI_PUBLIC_URL` is the public HTTPS base URL, with no trailing slash.

Never paste secret values into issues, pull requests, docs, shell transcripts, or workflow output. The workflow checks that required values are present without printing them. A dispatch input `release_approved=true` only requests a release; it does not replace the independent Environment reviewer approval.

## 4. Render production configuration

Verify in the Render dashboard before release:

- The production service is image-backed and points to `docker.io/<namespace>/caroai`, not a source/build deployment.
- Render has registry credentials if the Docker Hub image is private.
- Production `DATABASE_URL` is configured only in Render environment/secrets and points to the production PostgreSQL database.
- Database connectivity is stable and the service's startup command applies versioned migrations before the app accepts traffic.
- The Render service and `CAROAI_PUBLIC_URL` refer to the intended public service.

The workflow publishes immutable full-SHA and 12-character short-SHA tags, sends the **full-SHA image reference** to the Render deploy hook, and polls that deployment until Render reports `live` with the same full-SHA image reference. A Docker build, registry push, or deploy-hook HTTP response alone is not a successful release.

## 5. Approved release sequence

1. Agree with M1 on the exact `develop` source SHA and finish M1 acceptance/evidence.
2. Open and review the promotion PR `develop → main`; wait for required checks and approval; merge it.
3. Confirm `main` now points to the approved promotion commit. Do not dispatch while `main` is still at `d444119d5eb757e364f904bb9eacddd27e14e507`.
4. Open Actions → CaroAI CI → Run workflow, select `main`, set `release_approved=true`.
5. Approve the pending `production` Environment deployment as an authorized reviewer.
6. Confirm the release job completed and record the workflow URL, source full SHA, image full/short tags, Render deployment ID, Render status, image ref, and public URL.
7. Continue with the browser smoke and persistence-after-redeploy procedures below. Do not mark M4 done until those are evidenced.

Normal push/PR runs execute frontend checks, Python lint/tests, PostgreSQL acceptance with zero skipped tests, Compose persistence smoke, and a non-publishing Docker build. They do not publish or deploy.

## 6. Public smoke test

The release workflow checks public HTTPS `/health` and `/ready`, then exercises public API create/move/history flows for both PvP and PvAI. It prints the created public game IDs for evidence. Complete the following browser checks manually against the public UI as well:

- Open the public HTTPS UI in a clean browser session; verify page, CSS, JavaScript, and assets load without mixed-content or 404 errors.
- Open DevTools → Console and Network. Confirm no CORS, proxy, failed asset, or API-base-URL errors.
- Create a PvP game, make moves for both players, refresh/reopen it, and confirm the game state loads.
- Create a PvAI game, make a human move, wait for the AI response, and confirm the board/current player update.
- Open History, confirm both smoke games appear, open each game, and confirm the saved board/move count.
- Record the exact public URL, browser timestamp, PvP/PvAI public IDs, and sanitized results. Do not include cookies, authorization headers, tokens, or environment values in screenshots/logs.

## 7. Persistence after production redeploy

This is a separate production proof; `/health` and `/ready` are not persistence evidence.

1. Before redeploy, create a PvP or PvAI game on the public UI. Record its public ID and make at least three legal moves. For PvAI, include at least one AI move.
2. Confirm the game appears in History and that opening its public ID shows the expected board and move count.
3. Ask the authorized operator to trigger a Render redeploy/restart of the same approved full-SHA image using the normal runbook path. Do not change the image tag for this persistence check.
4. Wait until Render reports that deployment/restart is live and the exact full-SHA image is still active.
5. Reopen the recorded public game ID and History in a fresh browser session. Confirm the same moves, board, mode, status, and move count remain.
6. Record before/after timestamps, public ID, full image SHA, Render deployment ID/status, and sanitized screenshots/API responses.

Do not delete the test game before the evidence is captured. If the game/history disappears, M4 persistence acceptance fails; investigate the Render `DATABASE_URL`, database identity, migration state, and persistent database storage before any sign-off.

## 8. Rollback readiness

Keep the previously deployed full-SHA image in Docker Hub. To request redeployment of a previous immutable image, load the deploy hook securely from the approved secret store and substitute the previous full SHA:

```bash
export RENDER_DEPLOY_HOOK='(load securely; never commit or print)'
export PREVIOUS_SHA='full-previous-commit-sha'
export IMAGE_NAME='docker.io/<namespace>/caroai'
curl --fail --silent --show-error --get \
  --data-urlencode "imgURL=$IMAGE_NAME:$PREVIOUS_SHA" \
  "$RENDER_DEPLOY_HOOK"
```

Then obtain the resulting Render deployment ID, poll the Render API using the secret API key, confirm status `live` and the exact previous image ref, and re-run public `/health`, `/ready`, PvP/PvAI/history smoke. Never log the deploy hook or API key.

**Database warning:** rolling back the application image does not reverse SQL migrations. Before a schema-changing release, document a separately reviewed backward-compatible migration/restore plan. Do not run an old image against a schema it cannot understand.

## 9. Secret hygiene

- Keep local `.env` outside Git; only sanitized placeholders belong in `.env.example`.
- Check tracked files before every release: `git ls-files` and inspect environment/config files; verify no real `.env`, key, token, password, or database URL is tracked.
- CI includes a blocking `secret-scan` job. It runs the Gitleaks Action over the PR commit range and then runs the pinned Gitleaks v8.30.1 CLI against the fully fetched repository history with `gitleaks git --redact --verbose --no-banner /repo`. Both the candidate image build and production release depend on this job.
- Distinguish the two outputs: the Action's range scan alone is not proof that the complete repository history was scanned. The full-history CLI step must explicitly finish successfully and report no leaks.
- For a local full-history scan from a complete clone, run `docker run --rm --volume "$PWD:/repo" ghcr.io/gitleaks/gitleaks:v8.30.1 git --redact --verbose --no-banner /repo`. Do not write an unredacted report into the repository.
- Inspect workflow logs for accidental values. If a real credential is detected, stop promotion/release, rotate the credential at its provider, then assess Git-history cleanup with repository owners.
- If a real credential was committed, posted, or reused, revoke/rotate it at its provider. Removing it from the latest file is not sufficient because Git history and logs may retain it.
- Never place production values in documentation, CI artifacts, issue comments, or screenshots.

## 10. Release evidence record

Complete this record only with observed values; do not invent or infer deployment evidence.

| Field | Evidence |
|---|---|
| Promotion PR | URL + merged commit SHA |
| Required checks | URLs + final conclusion |
| Release workflow | URL + run ID |
| Source SHA | Full SHA |
| Docker image tags | Full SHA tag + 12-char tag |
| Render deployment | Deployment ID + `live` status + exact image ref |
| Public URL | HTTPS base URL |
| Public health/readiness | Timestamp + sanitized HTTP result |
| PvP/PvAI/history | Public game IDs + results |
| Browser/CORS/assets | Timestamp + sanitized evidence |
| Persistence after redeploy | Same public ID + before/after result |
| Rollback | Previous full-SHA image confirmed available |
| Secret hygiene | Scanner result + tracked-file review |

M4 is complete only when Render is live on the approved full-SHA image, public HTTPS checks pass, PvP/PvAI/history work, the same game remains available after production redeploy, and no credential is present in Git.
