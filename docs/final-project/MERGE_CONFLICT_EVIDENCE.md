# CaroAI — Merge Conflict Resolution Evidence
**University Final Project Requirement**: Genuine merge conflict created, resolved, and documented.  
**Repository**: `emt0147t/caroAI`  
**Common Base Commit**: `0ae4ead` (`docs(deploy): add baseline deployment configuration specification`)  
**Resolution Merge Commit**: `67bdf86` (`chore(merge): resolve deployment configuration conflict unifying resource and networking policies`)  
**Target Feature Branch**: `feature/final-project-delivery`  

---

## 1. Conflict Context and Motivation

In preparing the production deployment configuration for Render Web Services and managed PostgreSQL, two independent operational requirements were developed concurrently on separate feature branches:

1. **Branch A (`feature/deploy-config-resources`)**:
   - Focus: Compute resources and container memory governance.
   - Requirement: Define 512MB RAM allocation with 450MB warning threshold and 0.5 vCPU compute allocation.
   - Commit: `8fe6c02` (`docs(deploy): specify container memory and cpu resource limits`).
2. **Branch B (`feature/deploy-config-networking`)**:
   - Focus: Database resilience and zero-downtime deployment health validation.
   - Requirement: Define PostgreSQL connection pooling (10 connections, 5 overflow) and 45-second zero-downtime readiness rollout grace window.
   - Commit: `30530b7` (`docs(deploy): specify database connection pooling and zero-downtime rollout grace`).

Both branches edited the same configuration table in `docs/final-project/deployment-config.md` directly following the `Listening Port` baseline row.

---

## 2. Competing Changes

### Branch A Diff (`8fe6c02` vs Base `0ae4ead`):
```diff
--- a/docs/final-project/deployment-config.md
+++ b/docs/final-project/deployment-config.md
@@ -10,3 +10,5 @@ The production deployment runs as a Docker web service on Render backed by manag
 | Base OS / Image | Python 3.11-slim Multi-stage | Render Linux |
 | Process Manager | Uvicorn ASGI Server | Container PID 1 |
 | Listening Port | Configurable `${PORT:-8000}` | HTTP/HTTPS Proxy |
+| Memory Allocation | 512MB RAM with 450MB Warning Threshold | Render Standard Plan |
+| CPU Allocation | 0.5 vCPU Guaranteed Compute | Container CPU Shares |
```

### Branch B Diff (`30530b7` vs Base `0ae4ead`):
```diff
--- a/docs/final-project/deployment-config.md
+++ b/docs/final-project/deployment-config.md
@@ -10,3 +10,5 @@ The production deployment runs as a Docker web service on Render backed by manag
 | Base OS / Image | Python 3.11-slim Multi-stage | Render Linux |
 | Process Manager | Uvicorn ASGI Server | Container PID 1 |
 | Listening Port | Configurable `${PORT:-8000}` | HTTP/HTTPS Proxy |
+| Database Pooling | 10 persistent connections, 5 max overflow | SQLAlchemy Engine |
+| Zero-Downtime Grace | 45 seconds readiness validation window | Render Deploy Hook |
```

---

## 3. Merge Execution and Actual Conflict

When merging `feature/deploy-config-networking` into `feature/deploy-config-resources`:

```bash
git checkout feature/deploy-config-resources
git merge feature/deploy-config-networking
```

### Git Output:
```text
Auto-merging docs/final-project/deployment-config.md
CONFLICT (content): Merge conflict in docs/final-project/deployment-config.md
Automatic merge failed; fix conflicts and then commit the result.
```

### Conflict Markers in `docs/final-project/deployment-config.md`:
```text
<<<<<<< HEAD
| Memory Allocation | 512MB RAM with 450MB Warning Threshold | Render Standard Plan |
| CPU Allocation | 0.5 vCPU Guaranteed Compute | Container CPU Shares |
=======
| Database Pooling | 10 persistent connections, 5 max overflow | SQLAlchemy Engine |
| Zero-Downtime Grace | 45 seconds readiness validation window | Render Deploy Hook |
>>>>>>> feature/deploy-config-networking
```

---

## 4. Conflict Resolution Strategy

Neither change was redundant or incorrect; both requirements are critical for reliable production operations:
- Resource quotas prevent container OOM (Out Of Memory) kills on the Render platform.
- Database pooling and rollout grace prevent dropped PostgreSQL connections during container restarts.

The conflict was resolved by integrating **both** sets of specifications in logical operational sequence (Compute Resources followed by Database & Networking):

### Resolved Content:
```markdown
| Memory Allocation | 512MB RAM with 450MB Warning Threshold | Render Standard Plan |
| CPU Allocation | 0.5 vCPU Guaranteed Compute | Container CPU Shares |
| Database Pooling | 10 persistent connections, 5 max overflow | SQLAlchemy Engine |
| Zero-Downtime Grace | 45 seconds readiness validation window | Render Deploy Hook |
```

---

## 5. Verification and Commit Evidence

The resolution was validated with `git diff --check`, staged, and committed:

```bash
git add docs/final-project/deployment-config.md
git commit -m "chore(merge): resolve deployment configuration conflict unifying resource and networking policies"
```

- **Merge Resolution Commit SHA**: `67bdf86`
- **Parents**: `8fe6c02` (Branch A) and `30530b7` (Branch B)
- **Status**: Successfully integrated into `feature/final-project-delivery`.
