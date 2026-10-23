FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt* .
RUN pip install --no-cache-dir --upgrade pip && if [ -f requirements.txt ]; then pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt; else mkdir -p /app/wheels; fi

FROM python:3.11-slim AS runner
WORKDIR /app
RUN groupadd -g 10001 appuser && useradd -u 10001 -g appuser -s /bin/sh -m appuser
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/wheels /wheels
RUN if [ -d /wheels ] && [ "$(ls -A /wheels)" ]; then pip install --no-cache-dir /wheels/*; fi && rm -rf /wheels
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD curl -f http://localhost:8000/health || exit 1
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
