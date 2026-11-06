# Re-run Phase B under Python 3.11

This runbook uses a uniquely named PostgreSQL container with ephemeral anonymous storage. It does not touch the repository's default Compose project. Run from the repository root on a machine where Docker is available.

## 1. Prepare Python 3.11

```bash
python3.11 -m venv .venv-phaseb-py311
.venv-phaseb-py311/bin/python -m pip install -r requirements-dev.txt
```

Record `python --version`, `pip freeze`, Docker version, CPU/RAM, and the exact PostgreSQL image digest in the run artifacts. The current requirements are unpinned, so record the resolved dependency versions.

## 2. Audit the isolated resources

Confirm the chosen name and ports are unused before creating anything:

```bash
docker ps -a --filter name='^/caroai-phaseb-py311$'
ss -ltn | grep -E ':(55432|18000)\\b'
```

If either the container name or a port is occupied, select a new unique name/port pair and record it in `config.json`.

## 3. Start disposable PostgreSQL

```bash
docker run --rm -d \
  --name caroai-phaseb-py311 \
  -e POSTGRES_DB=caroai_phaseb \
  -e POSTGRES_USER=caroai_bench \
  -e POSTGRES_PASSWORD=phaseb_local_only \
  -p 127.0.0.1:55432:5432 \
  postgres:15-alpine
```

Wait until ready:

```bash
docker exec caroai-phaseb-py311 pg_isready -U caroai_bench -d caroai_phaseb
```

Apply only this disposable DB's migrations:

```bash
PYTHONPATH=. DATABASE_URL='postgresql://caroai_bench:phaseb_local_only@127.0.0.1:55432/caroai_phaseb' \
  .venv-phaseb-py311/bin/python scripts/migrate_database.py
```

## 4. Smoke, then full benchmark

```bash
PYTHONPATH=. DATABASE_URL='postgresql://caroai_bench:phaseb_local_only@127.0.0.1:55432/caroai_phaseb' \
  .venv-phaseb-py311/bin/python scripts/benchmark_api_db_phase_b.py \
  --smoke-only --output-dir reports/benchmark-phase-b-py311-smoke
```

After confirming the smoke output and DB correctness checks, run the full matrix:

```bash
PYTHONPATH=. DATABASE_URL='postgresql://caroai_bench:phaseb_local_only@127.0.0.1:55432/caroai_phaseb' \
  .venv-phaseb-py311/bin/python scripts/benchmark_api_db_phase_b.py \
  --samples 30 --warmup 3 --concurrency 1,2,4,8 \
  --output-dir reports/benchmark-phase-b-py311
```

Do not use a production URL. Keep raw request, server, PostgreSQL observation, correctness, environment, and package-version artifacts.

## 5. Remove only the named disposable container

```bash
docker stop caroai-phaseb-py311
```

Because it was started with `--rm`, Docker removes that container and its anonymous data volume on stop. Verify the exact name is absent. Do not run `docker compose down -v` or remove unrelated volumes.
