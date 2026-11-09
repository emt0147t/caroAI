# CaroAI — Sprint 3: Phân công chi tiết theo thành viên

**Snapshot tình trạng:** 16/10/2026 (giờ Việt Nam)  
**Timebox tăng tốc đề xuất:** 17–21/10/2026  
**Repo:** https://github.com/emt0147t/caroAI  
**Đầu mối điều phối:** Issue #24  
**Persistence workstream:** Issue #23

## 1. Trạng thái baseline đã kiểm chứng

- PR #17 Backend–AI integration: merged.
- PR #18 M5 regression/QA/docs: **merged 16/10/2026**, merge commit `2dd55cda274d7112e6d3244a4b457768178e98f8`.
- PR #21 strict CI quality gates: merged.
- PR #22 Frontend PvP/PvAI integration: merged.
- PR #25 bản kế hoạch Sprint 3 cũ và PR #26 closeout report vẫn đang mở nhưng branch của mỗi PR hiện 9 commit behind `develop`; tài liệu phân công chi tiết này được đưa lên branch mới từ baseline hiện tại để tránh dựa trên branch cũ.
- Issue #23 vẫn mở. `app/db/repository.py` còn là placeholder; `GameService` vẫn dùng `self._games` in-memory. Bảng `games` có khóa chính BIGINT identity, trong khi game ID API hiện sinh UUID string — cần thống nhất mapping trước khi code persistence.
- CI đã xanh cho các workflow hiện có, nhưng PostgreSQL tests trong CI thường bị skip; CI source-level frontend checks chưa phải browser-driven E2E.
- Chưa có bằng chứng đầy đủ rằng app đã publish image lên registry, deploy public HTTPS, và dùng PostgreSQL để persistence qua API sau session/process restart.
- Theo Project Specification, **Game History là MVP**. AI Hint/Move Analysis là phần nâng cao sau MVP và không được lấy thời gian của persistence/deployment.

## 2. Mục tiêu chung và thứ tự ưu tiên

Mục tiêu Sprint 3 là gom ba nhóm việc vào cùng một timebox có thứ tự rõ ràng:

1. **Hoàn tất persistence thật:** repository/session → GameService/API → PostgreSQL → read-back/transaction tests.
2. **Hoàn tất user-facing MVP:** PvP/PvAI browser E2E + Game History cơ bản.
3. **Đóng vòng release:** CI với disposable PostgreSQL → Docker/Compose smoke → registry publish → deployment HTTPS → live smoke → demo evidence.

Không thêm online multiplayer, tài khoản phức tạp, ML evaluator, Hint/Analysis mới hoặc ranking trong sprint này trừ khi MVP, persistence và deployment đã vượt qua gate.

## 3. Phân công một dòng

| Thành viên | GitHub account | Owner chính | Kết quả phải giao |
|---|---|---|---|
| M1 — Thành | `emt0147t` | Backend + Tech Lead | GameService/API dùng PostgreSQL thật, API contract/ID mapping rõ, basic history API, integrated develop green |
| M2 — Kiên | `KenKen106` | AI engine + performance | Tactical/legal regression, benchmark median/p95 theo difficulty, báo cáo và tối ưu có bằng chứng |
| M3 — Hiền | `NgocHein` | Frontend + browser E2E | Browser tests PvP/PvAI, state/error/recovery, Game History UI, public HTTPS smoke |
| M4 — Vinh | `macvinh2007-sketch` | DevOps + runtime | PostgreSQL CI service, migrations/readiness phối hợp, Docker publish/deploy pipeline, HTTPS evidence |
| M5 — Hiếu | `dyhieu-vu` | DB + QA + Docs | API/DB integration tests qua service, transaction rollback evidence, test matrix/runbook/final audit |

## 4. M1 — Thành (`emt0147t`): Backend, persistence và điều phối tích hợp

### M1-A — Chốt contract persistence, trước khi triển khai
- Phối hợp M5 và M4 chốt/ghi trong Issue #23: transaction boundary; quy tắc mode/difficulty/status/winner; move ordering; game ID API ↔ khóa database; migration approach; và hành vi khi database lỗi.
- Giải quyết chênh lệch hiện có giữa UUID string do `GameService` tạo và khóa `Game.id` BIGINT identity. Khuyến nghị giữ ID API hiện tại bằng cột `public_id` UUID unique và giữ BIGINT làm khóa nội bộ, nhưng cần M1/M5 chốt bằng ADR trước khi đổi schema. Không tự ý phá contract frontend.
- Giữ `GameRules` là nơi quyết định legality/turn/win/draw. Database phải lưu các nước đi và trạng thái có thể tái tạo/đọc lại; AI chỉ nhận snapshot.

**Đầu ra:** contract/ADR trong Issue #23 hoặc `docs/database-design.md`; quyết định ID mapping, transaction, status/winner và migration được M1+M5 xác nhận.

### M1-B — Xây repository/session thật
- Thay placeholder trong `app/db/repository.py` bằng phương thức tối thiểu để tạo/đọc game, thêm move, lấy moves theo `move_number ASC`, cập nhật terminal status/winner/ended_at và lấy danh sách history.
- Định nghĩa rõ ai sở hữu transaction: repository hay service; mỗi thao tác ghi phải commit toàn bộ hoặc rollback toàn bộ. Không để state trong `self._games` trở thành nguồn sự thật thứ hai.
- Tái tạo GameState nhất quán từ dữ liệu đã lưu hoặc dùng một cơ chế persisted state đã thống nhất; kiểm chứng qua session mới.
- Dùng dependency/session rõ ràng để API tests có thể inject disposable DB.

**Đầu ra:** repository implementation + unit/integration tests; GameService không còn phụ thuộc vào process-local dictionary cho trạng thái chính.

### M1-C — Nối route/service với PostgreSQL
- Nối `POST /api/games`, `GET /api/games/{game_id}`, `POST /api/games/{game_id}/moves`, `POST /api/games/{game_id}/ai-move` với repository/session.
- Mỗi move hợp lệ phải lưu đúng player, row/col, move_number và cập nhật status/result/ended_at khi game kết thúc.
- AI move phải dùng state đọc từ Backend/DB; chỉ apply nước qua GameRules rồi persist trong transaction. Không cho AI sửa trực tiếp GameState authoritative.
- Đảm bảo invalid move, occupied cell, game not found, wrong mode/turn và DB exception trả lỗi theo API contract; không trả thành công giả khi database write thất bại.
- Phối hợp M4 thêm readiness DB-aware riêng nếu cần. `GET /health` hiện là application liveness, không được âm thầm đổi ý nghĩa thành DB readiness.

**Đầu ra:** endpoint hiện có vẫn hoạt động với contract được ghi rõ; API CRUD/move/AI move đọc-ghi từ DB thật.

### M1-D — Game History MVP sau khi persistence ổn định
- Chốt contract tối thiểu cho `GET /api/history` hoặc endpoint danh sách game tương đương: id, mode, status, winner/result, started/ended, move_count, thứ tự danh sách.
- Nối endpoint vào repository. Nếu replay cần danh sách moves, thống nhất cách API trả moves; không giả định endpoint chưa tồn tại là đã được triển khai.
- Chỉ mở rộng phần này khi M1-B/M1-C và DB tests không còn blocker P0.

**Đầu ra:** basic history API đọc dữ liệu persisted; M3 có contract để làm UI.

### DoD của M1
- Không còn `self._games` là nguồn authoritative.
- Tạo game, đánh nước, AI move và đọc lại qua session mới trả cùng trạng thái; thứ tự moves đúng.
- Terminal status/winner/ended_at đúng; lỗi giữa transaction không để dữ liệu một phần.
- Unit/API/DB tests xanh; PR nhỏ, có review và CI xanh trên đúng head SHA.

## 5. M2 — Kiên (`KenKen106`): AI hardening và performance

### M2-A — Regression chiến thuật và legality
- Rà soát test thắng ngay, chặn đối thủ thắng ngay, occupied/out-of-board/malformed output, AI sai turn/mode/difficulty, board snapshot isolation và no-legal-move edge cases.
- Đảm bảo mọi độ khó `easy`, `medium`, `hard` trả nước hợp lệ hoặc lỗi có kiểm soát; Backend vẫn là nơi áp luật.
- Nếu phát hiện lỗi trong M1/M3 integration, cung cấp board fixture + expected behavior tái lập được; không sửa Backend/API contract mà không phối hợp M1.

**Đầu ra:** AI regression suite và bộ board fixture có giải thích.

### M2-B — Benchmark tái lập
- Tạo script, ví dụ `scripts/benchmark_ai.py`, chạy trên CPU/container gần production; tối thiểu 10 board đại diện × 3 difficulty × 5 trial sau warm-up nếu runtime cho phép.
- Bộ board phải gồm opening/ít quân, mid-game, tình huống winning move, forced block và vị trí đông quân. Lưu raw measurements, không chỉ ghi “AI nhanh”.
- Ghi median, p95, số candidate, depth/config, elapsed time, Python version, CPU/container, commit SHA và lệnh chạy.
- Mục tiêu p95 ≤ 2 giây là **SLO đề xuất để nhóm xác nhận ở D1**, không phải kết quả đã đo. Nếu chưa đạt, nêu vị trí gây chậm và một thay đổi tối ưu có đối chứng trước/sau.
- Không đưa ML evaluator, thay đổi heuristic lớn hoặc refactor không cần thiết vào trước khi benchmark xác định bottleneck.

**Đầu ra:** `reports/ai-benchmark.md` + raw CSV/JSON + benchmark command + SHA.

### M2-C — Tối ưu có bằng chứng và hỗ trợ release
- Tối ưu candidate pruning/order/depth chỉ khi benchmark chứng minh cần; chạy lại tactical/legal regression sau mỗi thay đổi.
- Review phần AI interaction của M1 và E2E case của M3; hỗ trợ debug AI latency trên container/public environment.
- Chuẩn bị 3 board demo: AI thắng nếu có cơ hội, AI chặn nước thắng, và một ván chơi bình thường ở MEDIUM/HARD.

### DoD của M2
- Regression AI xanh trên integrated SHA.
- Báo cáo median/p95 tái lập được theo cả ba difficulty; mọi tối ưu có so sánh trước/sau.
- Không có move AI bất hợp lệ trong suite; không claim benchmark nếu chưa chạy.

## 6. M3 — Hiền (`NgocHein`): Browser E2E, UI recovery và History MVP

### M3-A — Browser-driven E2E thật
- Bổ sung Playwright (hoặc browser harness tương đương có thể chạy tái lập trong CI) thay vì chỉ kiểm tra source bằng regex/node tests.
- Test tạo ván PvP: gọi API thật, X/O luân phiên, render state từ response Backend.
- Test tạo ván PvAI: chọn difficulty, human move → AI move qua Backend → render authoritative board; frontend không tự chọn nước AI hoặc tính winner.
- Test loading/busy state, disable double submission, HTTP 400/404/422, network error, retry chỉ retry AI khi thích hợp, không replay human move; recovery bằng `GET /api/games/{game_id}`.
- Test end-game/win/draw UI và không cho đánh tiếp sau game over. Test responsive layout trên viewport desktop và mobile.

**Đầu ra:** browser test script + command + CI evidence hoặc smoke evidence có URL/SHA; không gọi source-level regression là E2E.

### M3-B — Game History MVP
- Sau khi M1 chốt history API, tạo màn/list history với mode, ngày, trạng thái/kết quả, số nước.
- Chọn một ván để xem moves/replay nếu endpoint đã cung cấp. Nếu replay chưa đủ thời gian, vẫn phải deliver history list cơ bản và ghi rõ replay chưa hoàn thành.
- Không tạo history giả trong localStorage; lịch sử phải phản ánh các bản ghi persisted từ backend/DB.
- Thêm loading/empty/error/retry UI cho history.

**Đầu ra:** history UI nối API thật; có E2E kiểm chứng ván mới xuất hiện sau khi chơi và vẫn hiển thị sau refresh/session mới.

### M3-C — Public deployment smoke
- Khi M4 cấp HTTPS URL, chạy browser test trên deployed instance: bắt đầu cả PvP và PvAI, một nước AI, error/network handling, refresh/load game và history.
- Lưu URL (không kèm secret), browser/version, ngày giờ, commit/release ID, kết quả, screenshots/log liên quan.
- Báo ngay lỗi API base URL, proxy, CORS hoặc cache. Không sửa proxy/backend config riêng mà không phối hợp M4/M1.

### DoD của M3
- Browser-driven PvP và PvAI pass với API thật; state đúng do Backend trả về.
- History cơ bản đọc từ DB qua API, không phải mock.
- Public URL smoke có bằng chứng theo release SHA; test thất bại được ghi minh bạch.

## 7. M4 — Vinh (`macvinh2007-sketch`): PostgreSQL CI, migrations/runtime, publish/deploy

### M4-A — PostgreSQL disposable service trong CI
- Mở rộng GitHub Actions theo mô hình: PR → lint/Python tests/frontend tests; integration job có PostgreSQL service riêng với health check `pg_isready`.
- Cung cấp `TEST_DATABASE_URL` và `CAROAI_TEST_DATABASE_CONFIRMED=disposable-test-database` chỉ trỏ vào database của job CI. Tên DB phải rõ `test`; không dùng database shared/production.
- Chạy cả model/session và GameService/API persistence tests. Job này không được báo xanh khi DB tests bị skip; kiểm tra output để bảo đảm test thực sự chạy.
- Docker build phải phụ thuộc các gate cần thiết; bỏ mọi kiểu bypass như `|| true`, `--exit-zero`.

**Đầu ra:** workflow run link + commit SHA; PostgreSQL integration job có kết quả passed/failed rõ, không giả định pass khi skipped.

### M4-B — Schema migration và readiness
- Phối hợp M1/M5 chốt migration tool/lifecycle (ưu tiên migration có version như Alembic; không dùng `create_all` làm migration production ngầm).
- Đảm bảo Compose DB có healthcheck và app không phục vụ gameplay trước khi DB/migration sẵn sàng.
- Phối hợp M1 định nghĩa/readiness endpoint riêng nếu cần; giữ `/health` là application liveness nếu đang dùng như vậy.
- Verify app container kết nối đúng hostname/service, port nội bộ, database và secret; tránh phụ thuộc local host port hoặc thứ tự start đơn thuần.
- Test DB unavailable, migration fail và credentials sai phải làm deploy/gate thất bại rõ ràng.

**Đầu ra:** lệnh migration tái lập; Docker Compose DB readiness/connectivity logs; không claim database-ready chỉ dựa trên `/health`.

### M4-C — Publish image + production deployment
- Xác minh tên workflow hiện hành rồi hoàn thiện pipeline: PR/develop chạy test; phát hành từ `main` sau khi release candidate được duyệt thì test → build → tag theo full/short commit SHA → push registry/Docker Hub → trigger deploy Render.
- Cấu hình registry token và deploy hook trong GitHub Secrets/platform secrets; production `DATABASE_URL` lưu ở nền tảng deploy, không commit file `.env`/credentials.
- Ghi image name/tag, source SHA, workflow URL, deployment URL và cách rollback/redeploy.
- Không dùng `latest` làm bằng chứng truy vết duy nhất; SHA tag là bắt buộc. Chỉ report deploy success khi deployment platform xác nhận và URL thực sự trả đáp án.

**Đầu ra:** image tag truy vết được + deployment HTTPS public URL + workflow run + secret checklist.

### M4-D — Release smoke cùng M1/M3/M5
- Chạy `docker compose up --build`, test DB readiness/migrations, create/move/get và đọc lại dữ liệu từ session mới.
- Sau deploy, xác minh public URL, app liveness, DB readiness, app–DB connectivity. Không coi một `/health 200` đơn lẻ là chứng minh persistence.
- Cấp cho M3/M5 thông tin môi trường và commit/image SHA để browser smoke/test report chính xác.

### DoD của M4
- PostgreSQL integration CI chạy thật; job không xanh khi suite database bị skip.
- Publish/deploy workflow thành công trên SHA được ghi.
- HTTPS app hoạt động; secrets được quản lý an toàn; migration/readiness có lệnh và evidence.

## 8. M5 — Hiếu (`dyhieu-vu`): Integration QA, regression, Docs và Final Audit

### M5-A — Chuyển từ model tests sang API/service persistence tests
- Phối hợp M1 định nghĩa fixture/contract trước khi code thay đổi lớn.
- Mở rộng tests theo luồng thật: create game qua service/API → commit → tạo session/service mới → get game → verify board/status/moves; move order tăng 1..N; test winner/draw/ended_at.
- Test AI move cũng được persist đúng như human move, và API/Service đọc lại cùng state.
- Dùng disposable PostgreSQL/schema isolation; test không được vô tình chạy trên DB dùng chung. Kiểm tra cleanup, kể cả khi test fail.
- Kiểm tra transaction rollback qua service/API khi insert move hoặc update state bị lỗi; không chỉ test rollback trực tiếp bằng SQLAlchemy Session.
- Phối hợp M4 để những test này chạy trong PostgreSQL CI job. Nếu job không cấp DB mà tests bị skip, report là blocker.

**Đầu ra:** API/DB integration suite và report theo full SHA + environment; có test tạo/read-back, ordering, terminal state và rollback.

### M5-B — Regression test matrix và release evidence
- Lập matrix các lớp: unit rules, AI, API, DB model/session, GameService/API persistence, frontend source-level, browser E2E, Compose, registry/deploy/live smoke.
- Mỗi case có status **PASSED / FAILED / SKIPPED / NOT RUN**, link workflow/log, full SHA, môi trường và owner. Historical result để riêng, không gán vào head mới.
- Triaging P0/P1 theo release impact; mỗi lỗi có issue, người chịu trách nhiệm, cách tái hiện và acceptance criteria.
- Review PR của M1/M2/M3/M4 theo ranh giới module; bắt lỗi contract mismatch trước merge.

### M5-C — Docs/runbook
- Cập nhật README: install/run, test, Compose, biến môi trường, migration, tạo test DB an toàn, endpoint thực sự có, giới hạn `/health`, và cách debug.
- Cập nhật `docs/api-contract.md`, `docs/database-design.md`, `docs/test-plan.md`, release checklist và demo runbook theo implementation sau cùng.
- Ghi rõ hint/analysis/replay nếu còn chưa triển khai đầy đủ; không để ví dụ thiết kế cũ làm người đọc nghĩ endpoint đã chạy.
- Hướng dẫn reset dữ liệu test và không bao giờ đưa production credentials vào docs/commit.

### M5-D — Final rubric audit
- Kiểm tra project guide: repository/branch/PR history, meaningful commits (yêu cầu tối thiểu ≥30; mục tiêu nội bộ 40–50 nếu commit history tổng thể chưa đạt), review từ thành viên khác, evidence cho merge-conflict resolution, Docker build, registry image, GitHub Actions, PostgreSQL persistence sau restart/redeploy, public HTTPS, PvAI/PvP, README, không secret.
- Không tạo commit rỗng hoặc chia nhỏ giả tạo chỉ để tăng số lượng commit. Đưa bằng chứng thật vào báo cáo cuối.
- Tập hợp links/ảnh/log cần trình chiếu; mọi số liệu phải gắn với đúng SHA và environment.

### DoD của M5
- Required integration tests chạy thật, không skip giả làm pass.
- Test matrix/report/runbook phản ánh đúng implementation và môi trường cuối.
- Release checklist được đánh dấu theo evidence chứ không theo kỳ vọng.

## 9. Issue tracking và trách nhiệm phụ thuộc

- **Issue #23**: persistence implementation — M1 primary, M5 QA co-owner, M4 support migration/runtime.
- **Issue #24**: overall Sprint 3 coordination — cả 5 thành viên.
- Tạo/duy trì issue riêng: M2 AI benchmark/regression; M3 browser E2E + history UI; M4 PG CI/registry/deploy; M5 integration QA/docs/release audit.
- Mọi task cần: owner chính, collaborator nếu cần, acceptance criteria, test command/evidence, full commit SHA. Không giao một task cho “cả nhóm” mà không chỉ định ai chịu trách nhiệm cuối.

## 10. Chạy song song thế nào để giảm thời gian

### Track A — critical path
1. M1 + M5 chốt contract/ID mapping (D1).
2. M1 triển khai repository/service persistence; M5 viết test contract-driven song song (D1–D3).
3. M4 chuẩn bị PG CI + migration/runtime, tích hợp sau khi contract/schema được chốt.
4. M5 + M4 chạy persistence tests trong disposable PG CI; M1 fix.
5. M4 publish/deploy sau khi persistence gates xanh; M3 chạy browser/live E2E.
6. M5 tổng hợp evidence; cả nhóm go/no-go.

### Track B — chạy song song từ ngày đầu
- M2 không chờ persistence: chạy AI regression và benchmark trên develop/head được ghi, gửi fixture nếu phát hiện lỗi.
- M3 không chờ deploy: viết E2E harness/flow tests và UI history scaffold theo contract tạm đã chốt với M1; sau đó chuyển vào Compose/public URL.
- M4 chuẩn bị secrets/workflow/registry scaffold song song, nhưng không bật production deploy trước release gate.
- M5 tạo test matrix, API/DB fixtures và docs skeleton song song, rồi chạy trên implementation của M1.

## 11. Timebox mục tiêu (không phải cam kết bỏ gate)

| Ngày | M1 | M2 | M3 | M4 | M5 |
|---|---|---|---|---|---|
| **17/10 — D1** | Chốt ID/transaction/API contract | Chốt fixture và benchmark protocol | Chốt E2E cases, thêm browser harness | Chốt CI PG service/migration/deploy design | Viết test matrix và persistence assertions |
| **18/10 — D2** | Repo CRUD + service wiring | AI tactical/legal tests | PvP/PvAI E2E trên Compose local | PG CI + migration scaffold | API/DB tests dùng contract |
| **19/10 — D3** | Persist move/terminal state, fix integration | Benchmark 3 difficulty, tối ưu có đối chứng | Network/error/recovery + history UI scaffold | CI PG job xanh, DB/Compose smoke | Rollback/session-readback tests |
| **20/10 — D4** | History API + bug fixes sau persistence | Final benchmark và AI demo fixtures | Browser E2E/history trên deployed RC | Publish image + Render deploy + readiness | Full matrix, docs/runbook và triage |
| **21/10 — D5** | Code freeze, fix P0/P1 | Evidence + demo script | Public HTTPS smoke + UX audit | Release workflow + redeploy/rollback evidence | Final rubric audit + go/no-go |

Nếu persistence hoặc deployment vẫn còn blocker P0 vào D5 thì không tuyên bố release-ready; báo tình trạng thật và giữ gate mở.

## 12. Giao ước tích hợp, PR và báo cáo

1. Mỗi người làm branch theo một outcome, mở PR nhỏ vào `develop`; không gom nhiều module không liên quan vào một PR.
2. Trước khi push: sync `origin/develop`, giải quyết conflict, chạy test thích hợp; sau push phải xác minh CI trên đúng head SHA.
3. M1 review contract/architecture; M2 review AI logic/performance; M3 review UX/browser tests; M4 review workflow/runtime/secrets; M5 review tests/evidence/docs. Mỗi PR cần ít nhất một reviewer khác author.
4. Không merge khi required CI đỏ. PostgreSQL suite bị skip không đủ gate. Không dùng `|| true`, `--exit-zero`, credential trong code hoặc output “success” giả.
5. Cuối ngày mỗi người cập nhật trên Issue #24: **Done / Next / Blocker / Evidence URL / full SHA / ai cần hỗ trợ**.
6. Blocker cần phối hợp phải báo ngay, nêu bước tái hiện và owner. Ưu tiên giảm thời gian chờ bằng test contract-driven, stub không được dùng làm bằng chứng release cuối.

## 13. Release gates (go/no-go)

### Gate A — Core + Persistence
- [ ] API create/get/move/AI move dùng PostgreSQL thật.
- [ ] API/game ID mapping có quyết định được ghi.
- [ ] Ordered moves, terminal status/winner/ended_at đọc đúng qua session mới.
- [ ] Transaction rollback qua GameService/API, không chỉ ORM unit test.
- [ ] Migration và startup/readiness tái lập được.

### Gate B — Functional + E2E
- [ ] PvP và PvAI pass trong browser với API thật.
- [ ] Error/loading/retry/recovery/end-game state pass.
- [ ] Game History list hiển thị dữ liệu persisted sau refresh/reopen.
- [ ] AI regression xanh và benchmark được ghi theo SHA.

### Gate C — Delivery
- [ ] CI lint/unit/API/frontend/PG integration xanh; DB job không skip.
- [ ] Docker/Compose smoke pass.
- [ ] Image published có tag theo SHA.
- [ ] Production deployment HTTPS thật và kiểm tra được URL/commit đang chạy.
- [ ] Secrets chỉ nằm trong secret store, không trong Git.

### Gate D — Handover/demo
- [ ] Test matrix phân biệt passed/failed/skipped/not run.
- [ ] README, API/database docs, migration/deployment runbook cập nhật.
- [ ] Final rubric audit có bằng chứng; demo walkthrough tái lập.
- [ ] Cả 5 thành viên trình bày được vai trò, architecture, CI/CD và giới hạn còn lại.

## 14. Ngoài phạm vi ưu tiên

- Online multiplayer realtime, auth phức tạp, chat, Elo/ranking, Kubernetes, mobile app native, reinforcement learning.
- AI Hint/Move Analysis nâng cao chỉ bắt đầu sau khi persistence, history MVP, E2E và deployment đã đạt Gate A–C hoặc khi rubric yêu cầu trực tiếp.

**Nguyên tắc cuối:** tốc độ đến từ làm song song những việc không phụ thuộc nhau, chốt hợp đồng sớm và review PR nhỏ. Không đánh đổi persistence thật, CI trung thực hoặc release evidence để kịp một ngày mục tiêu.
