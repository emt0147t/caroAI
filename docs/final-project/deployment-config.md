# CaroAI Deployment Configuration Guide

## Production Environment Sizing & Policy

The production deployment runs as a Docker web service on Render backed by managed PostgreSQL.

### Runtime Specification

| Configuration Key | Baseline Specification | Target Environment |
|---|---|---|
| Base OS / Image | Python 3.11-slim Multi-stage | Render Linux |
| Process Manager | Uvicorn ASGI Server | Container PID 1 |
| Listening Port | Configurable `${PORT:-8000}` | HTTP/HTTPS Proxy |
| Database Pooling | 10 persistent connections, 5 max overflow | SQLAlchemy Engine |
| Zero-Downtime Grace | 45 seconds readiness validation window | Render Deploy Hook |
