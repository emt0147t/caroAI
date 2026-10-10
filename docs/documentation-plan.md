# CaroAI — Documentation Plan (Sprint 1)

> **Sprint 2 status (2026-10-10):** This planning document is retained for ownership and maintenance guidance. Current project state and verified setup/test commands are documented in the repository README and [`test-plan.md`](test-plan.md). Domain/service and API/health regressions passed in isolated test environments. PostgreSQL, API persistence, and Docker database smoke work remain unverified or dependent on their owners.

> **Trạng thái:** Kế hoạch tài liệu của Member 5 cho Sprint 1. Đây không phải README hoàn chỉnh. Các hướng dẫn chỉ được đưa vào README khi đã xác minh với implementation và Team Guide; những giá trị chưa có contract được ghi là cần member phụ trách xác nhận.

## 1. Mục tiêu

Documentation Plan xác định cấu trúc tài liệu của project và thứ tự/nội dung dự kiến cho README. Mục tiêu là thống nhất hướng dẫn setup môi trường, cấu hình environment, chạy ứng dụng, database, tests và Docker; giúp thành viên mới có thể làm theo hướng dẫn đã được xác minh; đồng thời chuẩn bị tài liệu cho Sprint 2 và demo cuối kỳ.

Tài liệu này phân công nguồn thông tin và dependencies, không thay README bằng một hướng dẫn chưa kiểm chứng, không viết thay tài liệu chuyên môn của M1/M2/M3/M4 và không tạo contract mới.

## 2. Documentation Structure

Đề xuất cấu trúc tài liệu:

```text
README.md

docs/
├── database-design.md
├── test-plan.md
├── documentation-plan.md
├── api-contract.md
├── game-domain.md
├── ai-design.md
├── frontend-design.md
└── devops-design.md
```

| File | Mục đích | Phụ trách / nguồn chính |
|---|---|---|
| `README.md` | Điểm vào chung cho project: tổng quan, setup, chạy, test, Docker, workflow và links tới tài liệu chi tiết | M5 tổng hợp; nội dung kỹ thuật lấy từ các member phụ trách và implementation thực tế |
| `docs/database-design.md` | Thiết kế database Sprint 1 và các quyết định còn chờ xác nhận | M5; đối chiếu database contract với M1 |
| `docs/test-plan.md` | Kế hoạch unit, API, database, integration, health và Docker smoke tests | M5; API/game contract từ M1, AI contract từ M2, môi trường/deploy từ M4 |
| `docs/documentation-plan.md` | Cấu trúc tài liệu, kế hoạch README, dependencies và checklist tài liệu | M5 |
| `docs/api-contract.md` | API request/response, validation, status/error behavior đã thống nhất; trạng thái route cần phân biệt implemented với planned | M1 sở hữu contract; M5 có thể ghi nhận implementation hiện tại và trạng thái test, các contract mới cần M1 xác nhận |
| `docs/game-domain.md` | Game domain, board, move, trạng thái và rule quan sát được trong implementation; quyết định business còn mở cần được đánh dấu | M1 sở hữu domain contract; M5 ghi nhận implementation hiện tại và chuyển quyết định chưa xác nhận cho M1 review |
| `docs/ai-design.md` | Thiết kế AI và cấu hình AI theo contract/implementation | M2 sở hữu; không tự tạo nội dung thay M2 |
| `docs/frontend-design.md` | Thiết kế frontend và cách khởi chạy giao diện | M3 sở hữu; không tự tạo nội dung thay M3 |
| `docs/devops-design.md` | Hướng dẫn build/run/deploy, Docker và CI/CD theo môi trường thực tế | M4 sở hữu; không tự tạo nội dung thay M4 |

Các file của M1/M2/M3/M4 trong danh sách là cấu trúc dự kiến, không khẳng định file đã tồn tại hoặc nội dung đã được chốt.

## 3. README Structure

README sẽ theo thứ tự dưới đây. Nội dung được bổ sung khi có nguồn xác nhận; không điền giá trị suy đoán.

| # | Section README | Mục đích và nội dung cần có | Nguồn cần lấy |
|---:|---|---|---|
| 1 | Project overview | Mô tả CaroAI, mục tiêu và phạm vi project | Sprint 1 specification; M1 và M3 xác nhận mô tả sản phẩm |
| 2 | Features / MVP scope | Liệt kê feature thuộc MVP/Sprint 1 và phân biệt phần đã có/chưa có | Sprint 1 specification; M1/M2/M3 xác nhận implementation |
| 3 | Architecture overview | Mô tả các thành phần và cách chúng tương tác ở mức tổng quan | Team Guide; M1/M2/M3/M4 cung cấp kiến trúc thực tế |
| 4 | Tech stack | Liệt kê công nghệ đã được chọn và package đang dùng | Team Guide, `requirements.txt`, M1/M2/M3/M4 |
| 5 | Repository structure | Giải thích thư mục/file chính, cập nhật theo repository thực tế | Cây thư mục hiện tại; M1/M2/M3/M4 xác nhận ownership |
| 6 | Requirements | Nêu phần mềm, runtime và prerequisite cần thiết | Team Guide và M4; phiên bản cụ thể chỉ ghi sau khi chốt |
| 7 | Environment configuration | Hướng dẫn dùng `.env.example`, tạo `.env`, mô tả biến theo specification; nhắc không commit secrets | `.env.example`, Sprint 1 specification, M1/M2/M4 |
| 8 | Local setup | Clone, virtual environment, cài dependencies, cấu hình env và các bước chuẩn bị | M4 về runtime; M1 về app/database; implementation đã xác minh |
| 9 | Database setup | Mô tả PostgreSQL, SQLAlchemy, chuẩn bị database và migration theo công cụ thực tế; link database design | [`database-design.md`](database-design.md), M1 và M4 |
| 10 | Run application | Lệnh chạy và địa chỉ truy cập ứng dụng theo entry point/port thực tế | M1/M4; không ghi startup command/port khi chưa chốt |
| 11 | Run tests | Cách cài test dependencies, chạy toàn bộ, một file, một nhóm và đọc kết quả | [`test-plan.md`](test-plan.md), cấu hình pytest và test tree thực tế; M5/M1 |
| 12 | Docker | Prerequisite, `docker compose up --build`, kiểm tra containers, health, logs và dừng containers; chỉ ghi service/port đã xác nhận | M4 và Compose configuration thực tế |
| 13 | API documentation | Link FastAPI `/docs` và `docs/api-contract.md`; endpoint overview khi contract được xác nhận | M1; `api-contract.md` |
| 14 | Game modes | Giải thích mode đã có trong specification và behavior chỉ khi M1 xác nhận | Sprint 1 specification; M1 và `game-domain.md` |
| 15 | Development workflow | Branch → commit → push → PR → review → merge vào `develop`; rules theo Team Guide | Team Guide và Git rules của team |
| 16 | Branching / Pull Request rules | Không push trực tiếp `main`/`develop`; yêu cầu review; không merge khi CI fail | Team Guide; M4 xác nhận CI workflow thực tế |
| 17 | Team roles | M1 Backend, M2 AI, M3 Frontend, M4 DevOps, M5 DB / QA / Docs; không thêm thông tin cá nhân | Team Guide |
| 18 | Troubleshooting | Nhóm lỗi PostgreSQL, `DATABASE_URL`, Docker, kết nối DB, tests, port conflict, env thiếu; chỉ thêm hướng dẫn đã kiểm chứng | M1/M4 và issue/implementation thực tế |
| 19 | Documentation links | Liên kết tới database, test plan, API/domain/AI/frontend/DevOps docs khi có | Các tài liệu tương ứng và owner member |
| 20 | Future scope / roadmap | Nội dung được specification/team thống nhất cho Sprint 2 và demo cuối kỳ | Sprint plan/specification và quyết định của team |

README không chứa schema database chi tiết hoặc API request/response chưa được M1 chốt.

## 4. Environment Configuration

README cần hướng dẫn thành viên bắt đầu từ `.env.example` và tạo file `.env` cục bộ theo quy trình đã xác minh. Các biến specification đã nêu cần được giải thích theo mục đích và nguồn xác nhận, không công bố secret hoặc giá trị môi trường thật:

| Biến | Cách tài liệu README xử lý |
|---|---|
| `DATABASE_URL` | Mô tả là cấu hình kết nối database; định dạng/giá trị mẫu phải phù hợp implementation và không chứa credential thật |
| `APP_ENV` | Mô tả theo các môi trường mà team thực sự hỗ trợ; danh sách giá trị chờ xác nhận nếu chưa có contract |
| `MODEL_PATH` | Mô tả theo vị trí model do M2/implementation xác nhận |
| `AI_DEFAULT_DEPTH` | Mô tả theo cấu hình AI do M2 xác nhận; không tự đặt giá trị mặc định |
| `LOG_LEVEL` | Mô tả theo logging configuration do M1/M4 xác nhận; không tự đặt danh sách giá trị nếu chưa có |

README phải nhắc rõ:

- Không commit `.env`.
- Không commit password.
- Không commit API key.
- Không commit secret.
- Chỉ dùng placeholder trong tài liệu; không đưa credential thật vào README hoặc ví dụ.

`DATABASE_URL`, `APP_ENV` và `MODEL_PATH` hiện có trong `.env.example`; `AI_DEFAULT_DEPTH` và `LOG_LEVEL` được specification liệt kê nhưng chưa có trong file mẫu hiện tại. Plan ghi nhận chênh lệch này để team xác nhận/cập nhật sau; tài liệu này không sửa `.env.example`.

## 5. Local Setup Documentation

README cần hướng dẫn quy trình local theo thứ tự:

1. Clone repository theo URL/remote do team cung cấp.
2. Tạo virtual environment nếu chạy Python local; dùng lệnh phù hợp với hệ điều hành sau khi team xác nhận cách hướng dẫn.
3. Cài dependencies từ `requirements.txt` theo môi trường thực tế.
4. Tạo `.env` từ `.env.example`; không đưa secret thật vào tài liệu.
5. Khởi động PostgreSQL bằng Docker Compose theo cấu hình M4 cung cấp.
6. Chuẩn bị database và chạy migration theo implementation/tool được chọn. Không ghi câu lệnh migration cụ thể trước khi team chọn migration tool và command.
7. Chạy FastAPI theo startup command và entry point M1/M4 xác nhận.
8. Mở application theo host/port đã được xác nhận.
9. Mở `/docs` khi FastAPI docs được bật trong môi trường tương ứng.
10. Chạy tests theo pytest configuration và test environment đã xác nhận.

Các lệnh cụ thể chỉ được đưa vào README sau khi kiểm tra chúng chạy được trên repository và khớp hướng dẫn M4/M1.

## 6. Docker Documentation

README cần có phần Docker với:

- Docker và Docker Compose prerequisites theo M4 xác nhận.
- Lệnh build/run `docker compose up --build` theo Compose configuration thực tế.
- Cách kiểm tra containers và trạng thái service.
- Application port chỉ khi contract/configuration đã xác định.
- PostgreSQL service name/port chỉ khi Compose configuration đã xác định.
- Health check theo API contract.
- Cách dừng containers và xem logs, dùng cách xác nhận bởi M4.
- Troubleshooting cơ bản cho startup, DB connection, env và port issues; chỉ nêu bước xử lý đã được xác minh.

Không tự đặt tên service, port, volume, health check path khác với contract hoặc command dọn dữ liệu.

## 7. Testing Documentation

README hướng dẫn hiện hành:

- Cài test dependencies đã được khai báo/chuẩn hóa cho project.
- Chạy toàn bộ pytest suite.
- Chạy một test file.
- Chạy một nhóm test nếu project có cấu trúc/marker phù hợp.
- Hiểu kết quả pass/fail và nơi xem lỗi.

Nội dung phải bám [`test-plan.md`](test-plan.md). Test tree hiện có domain, service, API, health, AI và PostgreSQL suites; pytest configuration riêng chưa có. PostgreSQL suite chỉ chạy khi có disposable DB đã được kiểm tra và bật safety confirmation.

## 8. Database Documentation

README cần liên kết tới [`docs/database-design.md`](database-design.md) và mô tả PostgreSQL/SQLAlchemy là schema foundation. Không được nói gameplay hiện đang lưu bằng PostgreSQL: `GameService` vẫn in-memory và repository chưa triển khai.

Schema implementation, migration command, database reset và test database setup phải lấy từ M1/M4 sau khi chốt; database design hiện tại vẫn là proposal ở những điểm được đánh dấu.

## 9. API Documentation

README liên kết tới FastAPI `/docs` và `docs/api-contract.md`. API contract có một số endpoint dự kiến chưa có implementation; README chỉ khẳng định create/get/move và health hiện có.

Endpoint overview có thể liệt kê các path đã nêu trong Team Guide sau khi M1 xác nhận chúng là contract hiện hành:

- `/health`
- `/api/games`
- `/api/games/{game_id}`
- `/api/games/{game_id}/moves`
- `/api/games/{game_id}/ai-move`
- `/api/games/{game_id}/hint`
- `/api/games/{game_id}/analyze`
- `/api/games/{game_id}/moves` (GET; cùng path với endpoint move POST)
- `/api/history`

README không mô tả method-specific request/response, status code, validation hoặc error behavior khi chưa có trong `api-contract.md`. Danh sách path không khẳng định endpoint đã implement.

## 10. Development Workflow

README mô tả workflow Team Guide:

```text
feature branch
    ↓
commit
    ↓
push
    ↓
Pull Request
    ↓
review
    ↓
merge vào develop
```

README cần nhắc:

- Không push trực tiếp vào `main` hoặc `develop`.
- Không commit secrets.
- PR phải được review.
- Không merge khi CI fail.

Branch protection, review count và CI check cụ thể chỉ được nêu nếu Team Guide/repository settings xác nhận.

## 11. Team Documentation

README cần có Team / Responsibilities với vai trò đã cung cấp:

- **M1:** Backend.
- **M2:** AI.
- **M3:** Frontend.
- **M4:** DevOps.
- **M5:** Database / QA / Docs.

Không thêm tên, email hoặc thông tin cá nhân nếu specification/Team Guide không cung cấp.

## 12. Troubleshooting

README cần có hướng dẫn theo nhóm vấn đề:

- PostgreSQL không chạy.
- `DATABASE_URL` sai hoặc thiếu.
- Docker container không start.
- Application không kết nối database.
- Test fail.
- Port conflict.
- Environment variable thiếu.

Mỗi mục chỉ được nêu dấu hiệu, thông tin cần kiểm tra và cách xử lý đã xác minh với cấu hình project. Không tự đề xuất workaround, reset data hoặc lệnh có thể xóa dữ liệu khi chưa được team xác nhận.

## 13. Documentation Maintenance

- API thay đổi → owner M1 cập nhật `api-contract.md`; M5 cập nhật README links/overview khi cần.
- Database schema thay đổi → M5 cập nhật `database-design.md` cùng M1 xác nhận contract/schema.
- Test strategy thay đổi → M5 cập nhật `test-plan.md`.
- Architecture thay đổi → member sở hữu thành phần cập nhật architecture/design docs; README tổng quan được đồng bộ.
- Deployment thay đổi → M4 cập nhật `devops-design.md`; README Docker/setup được đồng bộ.
- README phải phản ánh cách chạy thực tế của repository, không giữ command/config đã lỗi thời.
- Tài liệu của M1/M2/M3/M4 do member tương ứng sở hữu; M5 không tự viết thay nội dung chuyên môn chưa được cung cấp.

## 14. Documentation Checklist

### Sprint 1

- [x] `database-design.md` — tài liệu thiết kế hiện có; các điểm còn mở được ghi rõ.
- [x] `test-plan.md` — kế hoạch kiểm thử hiện có; các dependency contract được ghi rõ.
- [x] `documentation-plan.md` — kế hoạch này đã được tạo; review cùng team vẫn cần thực hiện.
- [x] README structure — thứ tự/mục nội dung đã được đề xuất trong kế hoạch; review cùng team vẫn cần thực hiện.
- [x] Setup instructions planned.
- [x] Test instructions planned.
- [x] Docker instructions planned.
- [ ] Environment configuration documented trong README theo implementation thực tế.
- [ ] Security rules documented trong README.

### Before Sprint 2

- [ ] M1 API contract available.
- [ ] M1 game-domain documentation available.
- [ ] M2 AI design available.
- [ ] M3 frontend design available.
- [ ] M4 DevOps design available.
- [ ] README updated according to actual implementation.

### Sprint 2 update

- [x] README setup, test commands, current in-memory boundary, and documentation links synchronized with checked-in implementation.
- [x] Database design records implemented constraints, runtime boundary, test scope, and open decisions.
- [x] Test plan records coverage, owners, safety requirements, and actual execution blocker.
- [ ] Run Python regression suite after installing declared requirements and pytest in the project environment.
- [ ] Run guarded PostgreSQL tests after provisioning and verifying a disposable test database.
- [ ] M1/M2/M4 integration work remains with the respective owners; see [`test-plan.md`](test-plan.md).

## 15. Dependencies / Open Questions

README chưa thể hoàn thiện các mục sau cho tới khi member/team tương ứng chốt:

- API request/response, errors, status codes và endpoint availability — M1.
- Actual database migration command/tool và schema initialization flow — M1/M4/team.
- Actual application startup command, entry point, host và port — M1/M4.
- Docker Compose service names, ports, readiness/health configuration — M4.
- CI/CD details, checks và branch protections — M4/team.
- AI configuration, model path semantics và default depth — M2.
- Frontend startup flow, URL/port và cách frontend kết nối backend — M3.
- Test database isolation, pytest configuration và lệnh chọn test — M1/M5/team.
- Giá trị hợp lệ/mô tả chính thức cho `APP_ENV`, `LOG_LEVEL` và các biến môi trường khác — owner component/team.

## 16. Nguyên tắc cuối cùng

- Đây là documentation PLAN, không phải README hoàn chỉnh.
- Không sửa source code trong phạm vi tài liệu này.
- Không tạo API contract hoặc database schema mới.
- Không tạo test code.
- Không thêm authentication.
- Không thêm công nghệ ngoài Team Guide.
- Không ghi secret, API key, password hoặc credential thật.
- Nội dung phải nhất quán với [`database-design.md`](database-design.md) và [`test-plan.md`](test-plan.md), đồng thời phân biệt rõ proposal với quyết định đã xác nhận.

