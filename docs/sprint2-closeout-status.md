# CaroAI - Báo cáo tình trạng sau Sprint 2

**Snapshot:** 16/10/2026 (giờ Việt Nam)  
**Repository:** https://github.com/emt0147t/caroAI

## Kết luận điều hành

Sprint 2 đã tích hợp các luồng chính về Backend-AI, frontend PvP/PvAI và strict CI. Tuy nhiên, chưa đủ bằng chứng để tuyên bố sản phẩm đã release-ready. PostgreSQL persistence qua GameService/API chưa được triển khai; public deployment/HTTPS và browser E2E chưa được xác minh hoàn tất.

## Trạng thái PR và Issue

| Hạng mục | Trạng thái tại thời điểm chốt | Ghi chú |
|---|---|---|
| PR #17 - Backend-AI integration | Merged | AI-move endpoint, board mapping và regression coverage đã tích hợp. |
| PR #21 - Strict CI | Merged | Lint/test quality gate, Compose validation và Docker build. |
| PR #22 - Frontend PvP/PvAI | Merged | Frontend gọi API tạo game, đọc state, gửi move và gọi AI. CI không phải browser E2E. |
| PR #18 - M5 QA/Docs | Approved, vẫn open | Head đã sync với develop và CI xanh; chưa merge tại snapshot này. |
| PR #25 - Sprint 3 plan | Open | Kế hoạch đã có PR riêng, chưa merge vào develop. |
| Issue #23 - PostgreSQL persistence | Open | GameService/API persistence, transaction, migration và DB runtime smoke. |
| Issue #24 - Sprint 3 kickoff | Open | Điều phối giai đoạn tiếp theo, gán cho 5 thành viên. |

PR #18 head: 75702c4ebc6cab1bfc8e504cd6f9592211cb58b4.  
Develop base tại lần kiểm tra: 5a2bd17cc71ce02d5894158a3f52fde9684aef2a. Branch comparison: 8 commits ahead, 0 behind.

## Bằng chứng CI

Workflow Run #71 thành công trên head PR #18: https://github.com/emt0147t/caroAI/actions/runs/38912078060

- Flake8: 0 findings.
- Pytest trên Python 3.11.17: 178 passed, 11 skipped, 1 warning.
- Frontend JavaScript syntax/regression checks: passed.
- Docker Compose configuration validation và Docker image build: passed.
- 11 PostgreSQL tests bị skip do CI thông thường không cấu hình disposable PostgreSQL test DB và các biến môi trường opt-in. Không được tính là PostgreSQL integration pass.

Thành đã báo cáo smoke test Docker local cho PvAI, PvP và /health thành công. Đây là kiểm chứng local được báo cáo; không thay thế browser E2E hoặc public deployment evidence.

## Tình trạng theo thành viên

| Thành viên / vai trò | Đã có bằng chứng | Bàn giao / còn lại |
|---|---|---|
| Thành - M1 Backend / Tech Lead | Backend API/domain và Backend-AI integration qua PR #17. | Dẫn dắt Issue #23: repository/session contract, API ID sang DB ID, persist game/moves, terminal state và rollback qua service/API. |
| Kiên - M2 AI Engineer | AI engine Minimax/Alpha-Beta, difficulty modes và backend integration. | Benchmark EASY/MEDIUM/HARD và latency evidence trên môi trường thống nhất; chưa có benchmark release-level được xác minh trong snapshot này. |
| Hiền - M3 Frontend | PR #22 merged, PvP/PvAI đã nối API; source-level regression pass. | Browser smoke trên môi trường deploy; kiểm tra error/loading/retry/recovery/end-game và lưu evidence. |
| Vinh - M4 DevOps | PR #21 merged; strict CI, Compose validation và Docker build pass. | Xác minh DB readiness/migrations, registry publish và deployment HTTPS. |
| Hiếu - M5 DB/QA/Docs | PR #18 đã sync, tài liệu cập nhật, CI xanh và reviewer approve. | PR #18 vẫn open; sau merge phối hợp M1/M4 cho DB/API integration QA và giữ evidence theo đúng SHA. |

## Đã hoàn thành trong Sprint 2

- Backend-AI integration và endpoint AI move.
- Frontend tích hợp backend cho PvP/PvAI và lựa chọn difficulty.
- Strict CI quality gate với lint/tests, frontend checks, Compose validation và Docker build.
- Tài liệu README/API/database/test được cập nhật để mô tả đúng implementation và giới hạn.
- PR #18 đã sync, CI xanh và được reviewer approve; còn chờ thao tác merge.

## Chưa hoàn thành - không được tuyên bố đã xong

1. GameService/API vẫn lưu game state trong bộ nhớ tiến trình; PostgreSQL chưa là nguồn state chính.
2. Chưa có bằng chứng transaction/rollback qua service/API; test rollback hiện có ở mức SQLAlchemy/model session.
3. Chưa có migration tooling/lifecycle được xác minh.
4. Chưa có PostgreSQL API/Compose end-to-end smoke evidence.
5. Chưa xác nhận public deployment/HTTPS bằng URL và workflow evidence.
6. CI frontend checks không phải browser-driven E2E.
7. Hint, analysis và history chưa được xác nhận là endpoint triển khai sẵn sàng.

## Ưu tiên chuyển tiếp sang Sprint 3

### P0 - Chốt Sprint 2
- Merge PR #18 sau khi xác nhận required checks và review vẫn hợp lệ.
- Review/merge PR #25 để đưa kế hoạch Sprint 3 vào develop.
- Cập nhật Issue #24 bằng trạng thái và blocker mới nhất.

### P0 - PostgreSQL persistence
- M1 + M5 chốt repository/session contract và ánh xạ API game ID sang DB ID.
- M1 + M5 nối GameService/API với repository; test ordered moves, terminal status/winner, read-back qua session mới và rollback.
- M4 phối hợp schema/migrations, DB readiness và app connectivity.

### P1 - Release readiness
- M4 hoàn thiện publish image/deploy pipeline, secrets an toàn và image tag theo commit SHA.
- M3 + M2 chạy browser/API smoke PvP/PvAI và benchmark AI.
- Cả nhóm lưu workflow URL, commit SHA, environment, test result passed/failed/skipped/not run và demo runbook.

## Release-ready checklist

- [ ] PR #18 merged và develop xanh sau merge.
- [ ] API/service persist game và moves qua PostgreSQL, đọc lại đúng qua session mới.
- [ ] Transaction rollback và persistence errors được test qua service/API.
- [ ] Migration/startup/DB readiness có lệnh tái lập và evidence.
- [ ] PvP/PvAI chạy browser E2E qua backend thật trên môi trường deploy.
- [ ] HTTPS deployment và operational smoke được chứng minh bằng URL/log/commit.
- [ ] Báo cáo không tính test skipped như test pass và không claim tính năng chưa xác minh.

**Kết luận:** Sprint 2 đạt bước tích hợp quan trọng về AI, frontend và quality gates. PostgreSQL persistence, migrations, DB runtime smoke, browser E2E và public HTTPS deployment vẫn là các nội dung trọng tâm của Sprint 3.
