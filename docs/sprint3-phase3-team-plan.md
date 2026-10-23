# CaroAI — Giai đoạn 3 / Sprint 3: Team Execution Plan

**Ngày:** 16/10/2026  
**Target tăng tốc đề xuất:** 17–21/10/2026  
**Repository:** https://github.com/emt0147t/caroAI

## Mục tiêu

Đưa CaroAI tới release candidate có bằng chứng end-to-end: **test → build Docker image → publish → deploy HTTPS → smoke test**, đồng thời chứng minh game/moves được persist qua PostgreSQL thực sự. Không coi schema/model tests là bằng chứng persistence qua API.

## Trạng thái và blocker hiện tại

- PR #17 Backend–AI: merged — https://github.com/emt0147t/caroAI/pull/17
- PR #21 strict CI quality gates: merged — https://github.com/emt0147t/caroAI/pull/21
- PR #22 Frontend PvP/PvAI: merged — https://github.com/emt0147t/caroAI/pull/22
- Thành báo cáo local Docker smoke đã pass cho PvAI, PvP và `/health`; vẫn cần browser/API smoke trên deployed environment.
- **P0 persistence:** `GameService` còn lưu state trong bộ nhớ tiến trình. Theo dõi ở Issue #23: https://github.com/emt0147t/caroAI/issues/23
- **P0 QA/docs:** PR #18 còn mở; branch cần sync với `develop`, CI xanh trên head SHA mới và cần re-review trước khi merge: https://github.com/emt0147t/caroAI/pull/18

## Owner và nhiệm vụ

### M1 — Thành | Tech Lead + Backend
- Đồng sở hữu Issue #23 với M5; chốt repository/session contract và API game ID sang DB ID.
- Nối GameService/routes với PostgreSQL; persist game, moves có thứ tự, terminal state/winner.
- Test read-back qua session mới và transaction/rollback qua service/API.
- Điều phối dependency, review PR và giữ `develop` xanh.

**DoD:** persistence qua API/service được chứng minh; move ordering, terminal state và rollback đúng; CI xanh trên SHA tích hợp.

### M2 — Kiên | AI Engineer
- Chạy AI legality/tactical regression; không phá Backend–AI contract.
- Benchmark EASY/MEDIUM/HARD trong Docker; ghi median, p95, môi trường và commit SHA.
- Hỗ trợ debug latency/AI response và chuẩn bị phần demo Minimax/Alpha-Beta.

**DoD:** regression xanh và benchmark tái lập được.

### M3 — Hiền | Frontend
- Browser smoke thật cho PvAI/PvP, difficulty, state update, turn lock, loading/thinking, error/retry/recovery.
- Chạy lại các luồng trên public HTTPS sau khi M4 deploy; lưu checklist/ảnh/log.
- Không tuyên bố history/hint/analysis hoạt động khi chưa xác minh luồng API end-to-end; không thêm luật game/AI riêng tại frontend.

**DoD:** PvAI và PvP chạy qua backend thật trên môi trường deploy; UI xử lý lỗi và state đúng.

### M4 — Vinh | DevOps
- Hoàn thiện pipeline test/lint → Docker build → publish image → deploy; build chỉ chạy sau quality gate.
- Thiết lập Docker Hub/registry, deployment target, PostgreSQL readiness/connectivity và migration lifecycle phối hợp M1/M5.
- Lưu production `DATABASE_URL`, registry token và deploy hook bằng GitHub/platform secrets; không commit credentials.
- Ghi image tag theo commit SHA, workflow run, URL HTTPS, `/health`, log và cách redeploy/rollback.

**DoD:** pipeline pass trên SHA được ghi; image/tag và URL xác định; secret an toàn; lỗi gate làm workflow fail.

### M5 — Hiếu | Database + QA + Docs
- Đồng sở hữu Issue #23 với M1; thêm test persistence qua service/API, move ordering, terminal state, transaction/rollback.
- Sync `feature/m5-sprint2` với `origin/develop`; xử lý feedback PR #18; chỉ request re-review khi CI xanh trên head SHA mới.
- Dựng test matrix unit/API/AI/DB/Compose/browser/live smoke, đánh dấu rõ passed/failed/skipped/not run.
- Cập nhật README, API/database docs, migration/deployment runbook và release evidence. Test bị skip không được ghi là pass.

**DoD:** test evidence gắn với SHA/environment; PR #18 xử lý đúng review gate; tài liệu phản ánh implementation thật.

## Lịch tăng tốc đề xuất

| Ngày | Trọng tâm | Owner | Evidence |
|---|---|---|---|
| 17/10 — D1 | Sync PR #18; chốt persistence contract/migrations; chia task | M1 + M5; M4 hỗ trợ | Contract, Issue/PR cập nhật, blocker có owner |
| 18/10 — D2 | Nối persistence qua API/service; read/write/move order/terminal state/rollback | M1 + M5 | API/DB tests qua session mới |
| 19/10 — D3 | PostgreSQL CI/Compose smoke; publish image; staging/public deploy | M4 + M1/M5 | CI SHA, image tag, deploy URL, `/health` |
| 20/10 — D4 | Browser/API E2E, PvAI/PvP, restart persistence, bug fixes | M3 + M2 + M5 | Smoke checklist, test matrix, lỗi còn lại |
| 21/10 — D5 | Release candidate freeze, docs, demo rehearsal and go/no-go | Cả nhóm; M1 điều phối | RC SHA, HTTPS URL, runbook, demo evidence |

Đây là timebox mục tiêu, không phải lý do bỏ quality gates. Nếu còn P0 ở persistence/deploy, nhóm phải báo blocker minh bạch và chưa phát hành.

## Thứ tự tích hợp

**DB/session contract + migrations → Backend/API persistence → API/DB integration tests → PostgreSQL CI + Docker runtime → registry/deploy pipeline → browser/live regression → docs/release candidate.**

Làm song song phần độc lập: M2 chuẩn bị benchmark, M3 browser checklist, M4 pipeline/secrets scaffold, M5 regression matrix. Chỉ merge phần phụ thuộc sau khi contract được chốt.

## Quy tắc Git và cập nhật tiến độ

1. Mỗi task phải có Issue, owner, acceptance criteria và link evidence.
2. Mỗi PR một mục tiêu rõ ràng, target `develop`, kèm cách test và link Issue.
3. Sync `origin/develop`, xử lý conflict, chạy test phù hợp trước khi push.
4. Chỉ merge khi required checks xanh trên **đúng head SHA** và review feedback đã xử lý.
5. Mỗi thành viên cuối ngày cập nhật: **Done / Next / Blocker / Evidence link / full SHA**.
6. Không dùng `|| true`, `--exit-zero`, không commit secret, không gọi test skipped là passed.

## Release gates

### A. Persistence
- [ ] API/service tạo ván, đánh nước và đọc state sử dụng PostgreSQL.
- [ ] Game + ordered moves + winner/status đọc lại đúng qua session mới.
- [ ] State được giữ theo use case qua app restart/reconnect; rollback không để dữ liệu nửa chừng.
- [ ] Migration/startup/readiness được kiểm thử.

### B. CI/runtime
- [ ] Lint/test xanh trên release candidate SHA.
- [ ] PostgreSQL integration tests chạy trong disposable DB; nếu skipped thì gate chưa đạt.
- [ ] Compose config, DB readiness, app–DB connectivity pass.
- [ ] Pipeline failure được thể hiện đúng là failure.

### C. User flow
- [ ] Public HTTPS và `/health` hoạt động.
- [ ] PvAI thật qua backend và PvP chạy end-to-end.
- [ ] Loading/error/retry/recovery và end-game state đúng.
- [ ] DB read-back được chứng minh sau session mới hoặc restart/redeploy.

### D. Evidence
- [ ] Commit SHA, workflow run, image tag, public URL được lưu.
- [ ] Test matrix phân biệt passed/failed/skipped/not run.
- [ ] README/runbook/demo script cập nhật; không có secrets trong Git.
- [ ] Cả 5 thành viên hiểu kiến trúc và pipeline.

## Out of scope

Không mở rộng online multiplayer, đăng nhập phức tạp, Elo/ranking, reinforcement learning hoặc hint/analysis/history mới trừ khi rubric bắt buộc và lõi release đã qua gate. Ưu tiên hoàn thiện và chứng minh hệ thống đang có.

## Kênh làm việc

- Persistence: https://github.com/emt0147t/caroAI/issues/23
- QA/docs re-review: https://github.com/emt0147t/caroAI/pull/18
- Frontend integration baseline: https://github.com/emt0147t/caroAI/pull/22
