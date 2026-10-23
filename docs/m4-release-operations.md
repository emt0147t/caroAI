# M4 release runbook

## CI and database

Workflow: .github/workflows/ci-cd.yml. PostgreSQL acceptance uses a disposable caroai_test database, pg_isready health checks, TEST_DATABASE_URL, and CAROAI_TEST_DATABASE_CONFIRMED=disposable-test-database. The JUnit gate fails if a PostgreSQL test is skipped. Docker build depends on frontend tests, Python lint/tests, PostgreSQL acceptance, and Compose persistence smoke.

Run from the repository root:

    docker compose up -d db
    docker compose run --rm --no-deps --entrypoint python app -m scripts.migrate_database
    docker compose up --build -d
    docker compose ps
    docker compose logs --no-color db app
    curl --fail http://localhost:8000/health
    curl --fail http://localhost:8000/ready

/health is liveness only. /ready runs SELECT 1 using DATABASE_URL and returns 503 if the database is unavailable. The Docker entrypoint runs versioned SQL migrations before Uvicorn; production migration does not use SQLAlchemy metadata create_all.

## Production approval gate (owner configuration required)

Create a GitHub Actions Environment named `production` in repository Settings → Environments. Configure at least one **required reviewer**, enable **Prevent self-review**, and restrict deployment branches to `main` (or the repository's approved main-branch policy). This is the independent approval gate; the `release_approved=true` workflow-dispatch input only requests a release and is not reviewer approval. The release job is attached to this environment, so its secrets are unavailable until the environment review is approved.

Store the following secrets at the `production` Environment level, not as repository-wide secrets where possible:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `RENDER_DEPLOY_HOOK`
- `RENDER_API_KEY`
- `RENDER_SERVICE_ID`

Add the Environment variable `CAROAI_PUBLIC_URL` (HTTPS base URL, no trailing slash). Manually dispatch CaroAI CI on `main` and set `release_approved=true` only when requesting a release. Normal push and pull_request runs build the candidate image without publishing or deploying. The separate release job requires frontend, Python/lint, PostgreSQL acceptance with zero skipped tests, Compose persistence, and Docker build to pass before it can request Environment approval and release. It publishes both docker.io/<namespace>/caroai:<full-commit-sha> and docker.io/<namespace>/caroai:<first-12-sha>, then asks Render to deploy the full-SHA image reference. It waits for Render status live with that exact image ref and verifies the public HTTPS /health and /ready endpoints.

Render must be configured as an image-backed service for docker.io/<namespace>/caroai, with a valid registry pull credential if the image is private. Set production DATABASE_URL in Render's environment/secrets only; never commit credentials or .env files. The workflow sends imgURL to the Render deploy hook to override the image tag for that deploy.

## Evidence and rollback

Record the final source SHA and push/PR workflow URLs. Ordinary CI being green proves only that the checks and non-publishing image build passed; it is not evidence of production deployment. For a release, record the separate release workflow URL, full source SHA, both image tags, Render deployment ID/status, public HTTPS URL, and results of /health and /ready. A successful build or hook response alone is not deployment success.

To redeploy a previous immutable image, load the hook from a secret manager and substitute the previous full SHA:

    export RENDER_DEPLOY_HOOK='(load securely; do not commit)'
    export PREVIOUS_SHA='full-previous-commit-sha'
    export IMAGE_NAME='docker.io/<namespace>/caroai'
    curl --fail --silent --show-error --get \
      --data-urlencode "imgURL=$IMAGE_NAME:$PREVIOUS_SHA" \
      "$RENDER_DEPLOY_HOOK"

Then confirm Render reports the expected image ref and live status and verify both public endpoints. Keep prior SHA-tagged images in the registry. Application rollback does not reverse database migrations; schema rollback needs a separately reviewed migration plan.
