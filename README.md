# CaroAI — Ứng dụng Cờ Caro 15×15 tích hợp AI

> **Đồ án cuối kỳ:** Git · Docker · CI/CD · AI Application Deployment  
> **Repository:** [github.com/emt0147t/caroAI](https://github.com/emt0147t/caroAI)  
> **Ứng dụng:** [CaroAI trên Render](https://caroai-bootstrap-a9e753b33198.onrender.com)  
> **Bản phát hành được nghiệm thu:** `main` tại [`c10ee2739b6577ea0004f86e91126dd176132319`](https://github.com/emt0147t/caroAI/commit/c10ee2739b6577ea0004f86e91126dd176132319), ngày **07/11/2026**.

CaroAI là ứng dụng web Cờ Caro (Gomoku) 15×15 cho phép **hai người chơi trên cùng thiết bị (PvP)** hoặc **một người chơi đấu với AI (PvAI)**. Dự án kết hợp Python/FastAPI, thuật toán tìm kiếm AI, PostgreSQL, Docker và GitHub Actions; bản phát hành đã được triển khai trên Render với địa chỉ HTTPS công khai.

**Lưu ý về trạng thái:** README tổng kết bằng chứng đã ghi nhận khi phát hành ngày 07/11/2026; trạng thái HTTPS tại thời điểm người đọc truy cập có thể thay đổi. Dự án đã có kiểm thử gameplay trên production qua API, nhưng không vì thế mà khẳng định đã kiểm thử mọi tình huống trên trình duyệt production hay bảo đảm uptime tuyệt đối.

## 1. Thông tin và liên kết chính

| Hạng mục | Thông tin |
|---|---|
| Tên dự án | **CaroAI — Gomoku 15×15 AI Gaming Platform** |
| Môn học / đề tài | Final Project — Git · Docker · CI/CD · AI Application Deployment |
| Mã nguồn | [emt0147t/caroAI](https://github.com/emt0147t/caroAI) |
| Demo HTTPS | [https://caroai-bootstrap-a9e753b33198.onrender.com](https://caroai-bootstrap-a9e753b33198.onrender.com) |
| Container registry | [`docker.io/emt0147/caroai`](https://hub.docker.com/r/emt0147/caroai) |
| CI/CD phát hành cuối đã xác minh | [GitHub Actions — run #42389707953](https://github.com/emt0147t/caroAI/actions/runs/42389707953) |
| Nền tảng | Render Web Service + Neon PostgreSQL |
| Backend / frontend | FastAPI + HTML/CSS/JavaScript thuần |
| Nhóm thực hiện | **5 thành viên**, chi tiết ở [Mục 6](#6-thành-viên-và-phân-công-công-việc) |

## 2. Đề bài gốc và toàn bộ yêu cầu của giảng viên

**Nguồn:** [*Final Project — Git · Docker · CI/CD · AI Application Deployment* (`project.docx`)](https://drive.google.com/file/d/1K3AffQyBaxMzH5iZ-o4ZQHVrhBlb6r-P/view). Phần này diễn giải đầy đủ đề bài gốc sang tiếng Việt, đồng thời phân biệt **bắt buộc**, **sản phẩm cần nộp** và **chủ đề gợi ý**.

### 2.1. Mục tiêu

Xây dựng một **ứng dụng AI đơn giản**, đóng gói ứng dụng bằng **Docker**, thiết lập quy trình **CI/CD** và triển khai lên một nền tảng miễn phí có **địa chỉ truy cập công khai**.

### 2.2. Kiến trúc tối thiểu do giảng viên đưa ra

```text
Người dùng → HTTPS → Ứng dụng (Docker container) → AI Model / LLM API → Cơ sở dữ liệu
```

Nền tảng đề xuất: **Render, Koyeb, Hugging Face Spaces hoặc nền tảng tương đương**.

**Cách CaroAI hiện thực:** Trình duyệt kết nối HTTPS đến ứng dụng FastAPI chạy trong Docker trên Render. Backend gọi **AI Engine Python nội bộ** để tính nước đi và dùng PostgreSQL lưu dữ liệu. CaroAI sử dụng **AI tìm kiếm theo thuật toán**, không sử dụng LLM API hoặc mô hình machine learning đã huấn luyện. Vì vậy dự án đáp ứng *chức năng AI* nhưng **không triển khai đúng theo nghĩa đen thành phần “AI Model / LLM API”** nếu giảng viên yêu cầu riêng một mô hình học máy hoặc API mô hình ngoài; điểm diễn giải này cần được giảng viên chấp thuận.

### 2.3. Yêu cầu bắt buộc

1. **Quy trình tổng thể:** `Push → GitHub → Test → Build → Deploy → Live`.
2. **Git:** Ít nhất **30 commit có ý nghĩa**; có **feature branch**, **Pull Request (PR)**; xử lý được **ít nhất một merge conflict**.
3. **Docker:** Có `Dockerfile` hoạt động; build thành công image và **đẩy image lên Docker Hub** hoặc registry tương đương.
4. **CI/CD:** Sử dụng **GitHub Actions** để tự động hóa kiểm thử, build và triển khai ứng dụng.
5. **Database:** Sử dụng **PostgreSQL** để lưu dữ liệu ứng dụng một cách bền vững (persistent).
6. **Triển khai:** Ứng dụng truy cập được bằng **HTTPS công khai**, chạy ổn định trong buổi demo.

### 2.4. Sản phẩm phải nộp

1. URL repository GitHub có **ít nhất 20 commit**.
2. Docker image trên Docker Hub.
3. Một GitHub Actions workflow hoạt động.
4. URL HTTPS công khai của ứng dụng.
5. PostgreSQL hoạt động trên server/cloud.
6. README hướng dẫn **cài đặt, chạy và triển khai** hệ thống.

> **Lưu ý về hai mốc commit:** Tài liệu gốc ghi **≥30 commit có ý nghĩa** ở phần *Mandatory Requirements* và **≥20 commit** ở phần *Required Deliverables*. Nhóm đối chiếu theo **mốc chặt hơn là ≥30 commit có ý nghĩa**; không tự coi hai dòng này là hai tiêu chí chấm điểm độc lập.

### 2.5. Chủ đề được gợi ý, không phải tính năng bắt buộc

Giảng viên đề xuất những hướng như **phân loại ảnh**, **phân tích cảm xúc văn bản** và **phân loại email spam**; nhóm cũng có thể đề xuất ứng dụng AI khác. Nhóm chọn **AI chơi Cờ Caro 15×15**. Các chủ đề gợi ý trên **không đồng nghĩa phải triển khai cả ba**.

### 2.6. Thông tin đánh giá trong tài liệu môn học

Tài liệu [*Topics and grading*](https://docs.google.com/document/d/1ygnvqBtYfJbRU9wFR-xICXqNPmW1p9fV-Q2EA7ptagA/edit) công bố cơ cấu **điểm môn học**: chuyên cần **10%**, bài tập **20%**, kiểm tra giữa kỳ **20%**, kiểm tra cuối kỳ **50%**. Đây **không phải rubric chi tiết riêng** cho đồ án CaroAI; chưa có căn cứ để gán phần trăm điểm riêng cho từng tiêu chí Git, Docker, AI hoặc CI/CD.

## 3. Ma trận đối chiếu yêu cầu và bằng chứng hoàn thành

| Tiêu chí từ đề bài | CaroAI đã thực hiện | Trạng thái và bằng chứng |
|---|---|---|
| Ứng dụng có AI | PvAI với Minimax/Alpha-Beta và tìm kiếm chiến thuật bằng Python | **Hoạt động**; [AI Engine](app/ai/engine.py). Lưu ý khác biệt với ML/LLM ở mục 2.2. |
| Luồng `Push → GitHub → Test → Build → Deploy → Live` | GitHub Actions chạy kiểm thử, build Docker image, phát hành theo SHA, kích hoạt Render và kiểm tra ứng dụng | **Đã kiểm chứng** trong [release run #42389707953](https://github.com/emt0147t/caroAI/actions/runs/42389707953). Bước phát hành production cần duyệt/kích hoạt thủ công, không tự động deploy mọi commit. |
| ≥30 commit có ý nghĩa | Có commit xây tính năng, sửa lỗi, kiểm thử, CI, build, refactor và lịch sử PR | **Đạt theo kiểm toán lịch sử**: tại baseline `938a174` ngày 02/11 ghi nhận **159 commit kỹ thuật** trong phạm vi kiểm toán; [Git Collaboration Audit](docs/final-project/GIT_COLLABORATION_AUDIT.md). Đây là số liệu **theo snapshot**, không phải tổng commit hiện tại. |
| Feature branch và Pull Request | Các nhánh `feature/*`, PR tích hợp backend, AI, frontend, DevOps, database; PR phát hành `main` | **Có bằng chứng**: [danh sách PR](https://github.com/emt0147t/caroAI/pulls?q=is%3Apr) và [Git Collaboration Audit](docs/final-project/GIT_COLLABORATION_AUDIT.md). |
| Xử lý ≥1 merge conflict | Xử lý xung đột ở `docs/final-project/deployment-config.md` khi hợp nhất thay đổi về tài nguyên và mạng | **Đã ghi nhận**: commit [`67bdf86`](https://github.com/emt0147t/caroAI/commit/67bdf86020903a9d30fd5b5fa22f6eb5664c3548), [bằng chứng conflict](docs/final-project/MERGE_CONFLICT_EVIDENCE.md). |
| `Dockerfile` và build image | Dockerfile multi-stage Python 3.11, chạy non-root, healthcheck; Docker Compose cho môi trường local | **Đạt**: [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml), build trong CI phát hành. |
| Push image lên registry | Xuất bản Docker image có tag theo commit SHA | **Đã kiểm chứng**: [`emt0147/caroai`](https://hub.docker.com/r/emt0147/caroai) và [release run](https://github.com/emt0147t/caroAI/actions/runs/42389707953). |
| GitHub Actions Test / Build / Deploy | Lint, pytest, frontend regression, PostgreSQL, Compose smoke, secret scan, Docker build và release được phê duyệt | **Đạt**: [ci-cd.yml](.github/workflows/ci-cd.yml) và [workflow phát hành](https://github.com/emt0147t/caroAI/actions/runs/42389707953). |
| PostgreSQL bền vững | Neon PostgreSQL production, SQLAlchemy repository, 4 migration, lưu trận và nước đi | **Đã kiểm chứng** qua kiểm thử PostgreSQL, Compose restart và nghiệm thu production; xem mục 7, 10 và 12. |
| HTTPS công khai / demo | Render phục vụ frontend và REST API trên một origin | **Đã nghiệm thu ngày 07/11/2026**; [URL ứng dụng](https://caroai-bootstrap-a9e753b33198.onrender.com). Tính sẵn sàng ở thời điểm khác phải kiểm tra lại. |
| README đầy đủ | Giới thiệu, hướng dẫn chạy, API, kiểm thử, triển khai, thành viên, tiêu chí và chứng cứ | **Có trong tài liệu này**. |

**Kết luận đối chiếu:** Các hạng mục Git, Docker, registry, Actions, PostgreSQL và HTTPS đều có bằng chứng. Điểm cần trình bày minh bạch với giảng viên là cách **AI thuật toán** của CaroAI thay thế thành phần “AI Model / LLM API” trong sơ đồ đề xuất, và việc CD được **tự động hóa sau bước phê duyệt**, không tự phát hành mỗi lần push.

## 4. Chức năng của ứng dụng

### 4.1. Trò chơi

- **PvP (Human vs Human):** Hai người chơi trên cùng một thiết bị; luân phiên đặt quân `X` và `O`.
- **PvAI (Human vs AI):** Người chơi đánh với AI, lựa chọn `easy`, `medium`, `hard` hoặc `impossible`.
- **Luật và trạng thái:** Bàn cờ **15×15**, `X` đi trước, nước đi không được đè lên ô đã đánh; thắng khi có **từ 5 quân liên tiếp trở lên** theo hàng, cột hoặc đường chéo; hòa nếu hết 225 ô mà chưa có người thắng.
- **Backend là nguồn quyết định:** Kiểm tra nước đi, lượt chơi và kết quả trên server; frontend không tự quyết định kết quả trận.
- **Lịch sử:** Lưu trận đấu, các nước đi và trạng thái; giao diện có thể xem danh sách trận và mở lại **trạng thái bàn cờ**, không phải trình phát lại tuần tự từng nước.

### 4.2. Giao diện và vận hành

- Frontend HTML/CSS/JavaScript thuần, thiết kế responsive, có hỗ trợ giao diện sáng/tối và trạng thái đang xử lý nước đi AI.
- Giao diện và REST API được FastAPI phục vụ chung một origin trong production.
- Các endpoint `/health` và `/ready` tách biệt tình trạng ứng dụng với khả năng kết nối PostgreSQL.

### 4.3. Giới hạn phạm vi đã hoàn thành

- **Chưa có PvP qua mạng** (không có phòng chơi trực tuyến/WebSocket); PvP chỉ diễn ra trên cùng một thiết bị.
- **Chưa có replay từng nước đi** dành cho người dùng; lịch sử có thể mở lại bàn cờ đã lưu.
- **Chưa xác nhận có API/UI gợi ý nước đi hoặc phân tích thế cờ cho người dùng**; bảng `game_analysis` trong DB không chứng minh tính năng đã hoạt động.
- **Không triển khai mô hình học máy đã huấn luyện** trên production. Nghiên cứu offline tại [PR #71](https://github.com/emt0147t/caroAI/pull/71) ở trạng thái **NOT_PROMOTED**.
- Mức `impossible` là tên cấp độ khó, **không khẳng định AI bất bại**.

## 5. Kiến trúc và công nghệ

### 5.1. Kiến trúc triển khai production

```text
Người dùng (trình duyệt desktop/mobile)
                │
              HTTPS
                ▼
      Render Web Service (Docker)
                │
          Python / Uvicorn
                │
              FastAPI
          ┌─────┼─────────────┐
          │     │             │
   Frontend tĩnh REST API   Health / Ready
          │     │
          │  Game Service ────────► AI Engine Python
          │     │                  (Minimax / chiến thuật)
          │     ▼
          │  SQLAlchemy
          │     │
          └─────┼─────────────────┘
                ▼
         Neon PostgreSQL
     (trận đấu, nước đi, lịch sử)
```

**Điểm quan trọng:** Bản cloud dùng một container ứng dụng cho giao diện + API; AI chạy trong tiến trình backend, không phải một mô hình LLM qua API bên ngoài. Docker Compose local có thể chạy **frontend Nginx, backend FastAPI và database PostgreSQL** thành các service riêng.

### 5.2. Công nghệ

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ / backend | Python 3.11, FastAPI, Uvicorn, Pydantic v2 |
| AI | Minimax, Alpha-Beta Pruning, heuristic, threat search, iterative deepening, transposition table |
| Frontend | HTML5, CSS3, JavaScript thuần |
| Cơ sở dữ liệu | PostgreSQL, SQLAlchemy, Psycopg2, versioned SQL migrations |
| Container | Docker multi-stage, Docker Compose, Nginx (local) |
| CI/CD / kiểm thử | GitHub Actions, pytest, flake8, Playwright, Gitleaks |
| Cloud | Render Web Service + Neon PostgreSQL |

### 5.3. Cấu trúc repository

```text
caroAI/
├── .github/workflows/       # CI/CD, E2E, benchmark
├── app/
│   ├── ai/                  # Bộ máy tìm kiếm và đánh giá nước đi
│   ├── api/                 # REST routes, health, QA có kiểm soát
│   ├── db/                  # Models, transaction, repository
│   ├── domain/              # Luật và trạng thái trò chơi
│   ├── schemas/             # Kiểm tra dữ liệu request/response
│   └── services/            # Điều phối nghiệp vụ và AI
├── frontend/Caro_AI/        # Giao diện web
├── database/migrations/     # Các phiên bản 000 đến 003
├── deploy/                  # Cấu hình Nginx cho local Compose
├── scripts/                 # Migrations, benchmark, production QA
├── tests/                   # Unit, API, DB, frontend, E2E
├── docs/                    # Thiết kế, quyết định, kiểm toán
│   └── final-project/       # Báo cáo học phần và Git conflict
├── reports/                 # Kết quả benchmark, AI evaluation
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## 6. Thành viên và phân công công việc

Nhóm có **5 thành viên**. Bảng dưới kết hợp **phân công ban đầu trong [kế hoạch Sprint 1](https://docs.google.com/document/d/1PMAbGlTOAzK5g2gfuqjJQZS42toiK-dc7dYHP7pqbfc/edit)** với **PR tiêu biểu đã được merge** để minh họa công việc thực tế. Nhiều thay đổi phát sinh qua quá trình phối hợp; đóng góp không chỉ giới hạn trong một vai trò cố định.

| Thành viên | Vai trò phụ trách chính | Công việc và bằng chứng tiêu biểu |
|---|---|---|
| **Nguyễn Xuân Thành** — [@emt0147t](https://github.com/emt0147t) | **Tech Lead / Backend / tích hợp** | Thiết kế kiến trúc và API/luật chơi; tích hợp backend–AI [PR #17](https://github.com/emt0147t/caroAI/pull/17); kiểm thử backend/PostgreSQL [PR #46](https://github.com/emt0147t/caroAI/pull/46); tích hợp phát hành, kiểm soát QA production [PR #63](https://github.com/emt0147t/caroAI/pull/63), [PR #67](https://github.com/emt0147t/caroAI/pull/67); tích hợp AI chiến thuật và bằng chứng đánh giá [PR #68–70](https://github.com/emt0147t/caroAI/pull/70). |
| **Trần Danh Kiên** — [@KenKen106](https://github.com/KenKen106) | **AI Engineer** | Minimax/heuristic/Alpha-Beta và độ khó [PR #12](https://github.com/emt0147t/caroAI/pull/12); tăng độ ổn định AI [PR #19](https://github.com/emt0147t/caroAI/pull/19); benchmark/regression [PR #33](https://github.com/emt0147t/caroAI/pull/33), [PR #36](https://github.com/emt0147t/caroAI/pull/36); bổ sung cấp độ `impossible` [PR #53](https://github.com/emt0147t/caroAI/pull/53). |
| **Ngọc Hiền** — [@NgocHein](https://github.com/NgocHein) | **Frontend Developer** | Giao diện PvP/PvAI và tích hợp API [PR #22](https://github.com/emt0147t/caroAI/pull/22); E2E browser và giao diện lịch sử [PR #34](https://github.com/emt0147t/caroAI/pull/34); responsive UX/accessibility [PR #42](https://github.com/emt0147t/caroAI/pull/42). |
| **Mạc Quang Vinh** — [@macvinh2007-sketch](https://github.com/macvinh2007-sketch) | **DevOps Engineer** | Docker, workflow CI/CD; siết quality gates [PR #21](https://github.com/emt0147t/caroAI/pull/21); PostgreSQL CI, migrations, readiness và phát hành theo SHA [PR #37](https://github.com/emt0147t/caroAI/pull/37); tách smoke test khỏi release production [PR #47](https://github.com/emt0147t/caroAI/pull/47). |
| **Vũ Duy Hiếu** — [@dyhieu-vu](https://github.com/dyhieu-vu) | **Database / QA / Documentation** | Nền tảng database và tài liệu Sprint 1 [PR #7](https://github.com/emt0147t/caroAI/pull/7); regression và database QA [PR #18](https://github.com/emt0147t/caroAI/pull/18); kiểm thử persistence và bàn giao [PR #38](https://github.com/emt0147t/caroAI/pull/38); ma trận QA và tài liệu Phase 4 [PR #39](https://github.com/emt0147t/caroAI/pull/39). |

> **Nguyên tắc ghi nhận:** Đây là những **đầu việc và PR tiêu biểu**, không phải danh sách đầy đủ mọi đóng góp hoặc khẳng định mỗi thành viên tự mình thực hiện toàn bộ phần việc nêu trong ô. Bảng vai trò của tài liệu kiểm toán Git cũ có chỗ khác với phân công Sprint 1; bảng này ưu tiên kế hoạch phân công và PR theo tác giả. Có thể đối chiếu thêm với [lịch sử Git và bảng commit](docs/final-project/GIT_COLLABORATION_AUDIT.md).

### 6.1. Cách nhóm phối hợp bằng Git

- Quy trình dự kiến: `feature/* → Pull Request → develop → Pull Request → main`.
- PR được review bởi thành viên khác, có CI kiểm tra trước khi tích hợp; tài liệu Sprint 1 quy định không push trực tiếp lên `main`/`develop`.
- **Thực tế repository có thời điểm cho phép push trực tiếp lên `develop`** để xử lý tích hợp. Vì vậy không khẳng định mọi commit đều đi qua PR hoặc quy tắc bảo vệ nhánh luôn được thực thi tuyệt đối.
- **Merge conflict thật** đã được xử lý tại [`67bdf86`](https://github.com/emt0147t/caroAI/commit/67bdf86020903a9d30fd5b5fa22f6eb5664c3548) và lưu bằng chứng tại [`MERGE_CONFLICT_EVIDENCE.md`](docs/final-project/MERGE_CONFLICT_EVIDENCE.md).
- **Thống kê lịch sử có phạm vi:** bản kiểm toán tại commit `938a174` ngày 02/11 ghi nhận **388 commit trong phạm vi so sánh**, gồm **339 non-merge**, **49 merge**, trong đó **159 commit thuộc các nhóm thay đổi kỹ thuật**. Không sử dụng số này làm thống kê hiện hành của toàn repo.

## 7. AI Engine, database và API

### 7.1. AI Engine

AI Engine ở [`app/ai/engine.py`](app/ai/engine.py) kiểm tra tính hợp lệ của nước đi trước khi trả về backend. Độ khó hiện tại:

| Cấp độ | Hướng xử lý trên nhánh `main` | Cấu hình chính trong code |
|---|---|---|
| `easy` | Minimax/Alpha-Beta cơ bản | Độ sâu 1; tối đa 6 ứng viên |
| `medium` | Minimax/Alpha-Beta cơ bản | Độ sâu 2; tối đa 10 ứng viên |
| `hard` | Tìm kiếm chiến thuật nâng cao | Độ sâu danh nghĩa 4; tối đa 8 ứng viên tĩnh; ngân sách mặc định 250 ms / 16.000 node |
| `impossible` | Tìm kiếm chiến thuật sâu hơn | Độ sâu danh nghĩa 6; tối đa 12 ứng viên tĩnh; ngân sách mặc định 700 ms / 40.000 node |

Bản `hard`/`impossible` có kiểm tra thắng/chặn, xử lý đe dọa, mở rộng tìm kiếm và transposition table. Ngân sách thời gian là **giới hạn hợp tác bên trong bộ tìm kiếm**, **không phải cam kết độ trễ HTTP hoặc SLO production**. Cấu hình chi tiết: [`app/ai/competitive.py`](app/ai/competitive.py).

**Đánh giá AI:** Có benchmark/tournament tái lập và kiểm tra nước đi hợp lệ tại [`reports/competitive/`](reports/competitive/). Các tỷ lệ thắng là kết quả theo đối thủ, opening và môi trường đo cụ thể; không chứng minh AI luôn thắng. Một số báo cáo trong thư mục này còn ghi trạng thái *candidate chưa deploy* theo thời điểm viết; **thực tế mã tích hợp đã được merge qua [PR #70](https://github.com/emt0147t/caroAI/pull/70) và phát hành tại run #42389707953**. Ngược lại, thử nghiệm **offline learning** ở [PR #71](https://github.com/emt0147t/caroAI/pull/71) **chưa được đưa vào bản phát hành**.

### 7.2. PostgreSQL và migrations

| Thành phần | Chức năng |
|---|---|
| `games` | Thông tin trận đấu, chế độ, kết quả, thời gian, mã public ID |
| `moves` | Các nước đi có thứ tự và ràng buộc tọa độ / lượt |
| `game_analysis` | Cấu trúc lưu phân tích; **không đồng nghĩa UI Hint đã triển khai** |
| `qa_run_usage` | Giới hạn số trận được tạo trong quá trình nghiệm thu QA có kiểm soát |
| `schema_migrations` | Theo dõi các migration đã chạy |

Các file migration trong [`database/migrations/`](database/migrations/):

1. `000_initial_schema.sql`: Các bảng nền tảng.
2. `001_games_public_id.sql`: Bảo đảm public ID duy nhất cho từng trận.
3. `002_games_qa_run_id.sql`: Gắn nhãn những trận nghiệm thu QA để dọn dẹp đúng phạm vi.
4. `003_qa_run_usage.sql`: Theo dõi quota tạo trận của QA run.

Migration được chạy trước khi khởi động API trong Docker production bằng `python -m scripts.migrate_database`. Dữ liệu PostgreSQL được lưu ngoài vòng đời container ứng dụng.

### 7.3. REST API chính

| Method | Endpoint | Chức năng |
|---|---|---|
| `GET` | `/health` | Liveness, không phụ thuộc DB |
| `GET` | `/ready` | Readiness, kiểm tra kết nối PostgreSQL |
| `POST` | `/api/games` | Tạo trận `HUMAN_VS_HUMAN` hoặc `HUMAN_VS_AI` |
| `GET` | `/api/games/{game_id}` | Trạng thái, bàn cờ và kết quả trận |
| `POST` | `/api/games/{game_id}/moves` | Gửi nước đi người chơi, JSON `{"row":7,"col":7}` |
| `POST` | `/api/games/{game_id}/ai-move` | AI đánh, JSON `{"difficulty":"hard"}` |
| `GET` | `/api/history?limit=20&offset=0` | Danh sách lịch sử có phân trang |

Swagger / OpenAPI tự sinh tại **`/docs`**. API nghiệm thu `/api/qa/*` chỉ phục vụ release có kiểm soát và đã bị **vô hiệu hóa sau nghiệm thu** ngày 07/11/2026.

## 8. Cài đặt và chạy local

### 8.1. Cách khuyến nghị: Docker Compose

**Yêu cầu:** Git, Docker Engine/Desktop và Docker Compose v2.

```bash
git clone https://github.com/emt0147t/caroAI.git
cd caroAI
cp .env.example .env
```

Trên **PowerShell**, thay `cp` bằng `Copy-Item .env.example .env`. Sau khi copy, **đổi `POSTGRES_PASSWORD` trong `.env` thành mật khẩu local riêng của bạn**. `.env.example` chỉ có giá trị mẫu, không chứa secret production.

```bash
docker compose up --build -d
docker compose ps
```

| Địa chỉ local | Mục đích |
|---|---|
| `http://localhost:8080` | Giao diện qua Nginx (Docker Compose) |
| `http://localhost:8000` | Giao diện/API trực tiếp từ FastAPI |
| `http://localhost:8000/docs` | Swagger |
| `http://localhost:8000/health` | Kiểm tra ứng dụng |
| `http://localhost:8000/ready` | Kiểm tra PostgreSQL |

Kiểm tra bằng `curl`:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Xem log hoặc dừng môi trường:

```bash
docker compose logs -f app
docker compose down
```

Lệnh `docker compose down` mặc định **giữ volume dữ liệu**. **Không** thêm `-v` nếu không muốn xóa database local.

### 8.2. Chạy backend trực tiếp bằng Python (không dùng Docker cho ứng dụng)

**Yêu cầu:** Python 3.11 và một PostgreSQL đang hoạt động. Có thể chạy PostgreSQL riêng bằng Docker hoặc cài local.

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
```

Thiết lập `DATABASE_URL` ứng với database của bạn (không commit giá trị thật):

```bash
# Linux/macOS, ví dụ local:
export DATABASE_URL='postgresql://caroai_user:YOUR_PASSWORD@localhost:5432/caroai_db'

# Windows PowerShell tương đương:
# $env:DATABASE_URL = 'postgresql://caroai_user:YOUR_PASSWORD@localhost:5432/caroai_db'

python -m scripts.migrate_database
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Sau đó truy cập **http://127.0.0.1:8000/**. Trong cách chạy này, bạn phải tự cấu hình và bảo đảm PostgreSQL đang chạy; không dùng mật khẩu sản xuất trong tài liệu.

## 9. Kiểm thử

### 9.1. Python, API và lint

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q tests/
python -m flake8 app tests scripts --count --max-complexity=10 --max-line-length=127 --statistics
```

### 9.2. PostgreSQL integration acceptance

Kiểm thử này yêu cầu **database thử nghiệm dùng một lần**, có cấu hình `TEST_DATABASE_URL` và guard bảo vệ; không chạy trên database production. Xem chính xác cách cấu hình môi trường trong [workflow CI](.github/workflows/ci-cd.yml) trước khi chạy lại. Các test PostgreSQL chuyên biệt nằm trong `tests/test_database_postgres.py` và `tests/postgres_suite.py`.

### 9.3. Frontend và Playwright

```bash
node --check frontend/Caro_AI/trong_tran/script.js
node --test tests/frontend-regression.test.cjs
npm ci
npx playwright install chromium
npm run test:e2e
```

Đối với visual regression, có thêm `npm run test:visual` và `npm run test:visual:mutation` (cần fixture/baseline và môi trường kiểm thử phù hợp). Quy trình browser E2E đầy đủ được mô tả tại [frontend-e2e.yml](.github/workflows/frontend-e2e.yml).

### 9.4. Kết quả kiểm thử được xác minh trên bản phát hành cuối

Nguồn: [CaroAI CI — workflow run #42389707953](https://github.com/emt0147t/caroAI/actions/runs/42389707953), chạy trên commit `c10ee273...` ngày **07/11/2026**.

| Kiểm thử / nghiệm thu | Kết quả ghi nhận |
|---|---|
| Python pytest trong release CI | **829 passed, 14 skipped, 1 warning** |
| PostgreSQL acceptance chuyên biệt | **18 passed** |
| Build và publish Docker image | **PASS** |
| Render xác nhận đúng image SHA | **PASS** |
| HTTP `/health`, `/ready`, `/`, `/history.html`, `/api/history`, `/tokens.css` | **HTTP 200** khi nghiệm thu |
| Gameplay PvP và PvAI trên production qua QA API | **PASS**: xác nhận thắng PvP, nước đi AI, đọc lại trạng thái và lịch sử |
| Dọn dữ liệu QA có gắn nhãn và tắt QA endpoint sau phát hành | **PASS** |

Số lượng test trên là **snapshot của một workflow cụ thể**, không phải số lượng test cố định của codebase. `14 skipped` trong bộ pytest tổng không được diễn giải là 14 lỗi; suite PostgreSQL riêng đã chạy và pass. Kết quả này **không đồng nghĩa** với nghiệm thu browser production toàn diện hoặc benchmark tải dài hạn.

## 10. CI/CD và hướng dẫn triển khai

### 10.1. Luồng GitHub Actions

```text
Feature / develop push hoặc PR
          │
          ▼
    Frontend checks ── Python tests / lint ── PostgreSQL integration
          │
          ├── Compose smoke + khởi động lại kiểm tra persistence
          ├── Quét secret
          └── Build Docker image ứng viên
                         │
                 Review / phê duyệt
                         │
              Manual release từ main
                         │
                         ▼
                 Push lên Docker Hub
                         │
                 Trigger Render deploy
                         │
            Xác minh SHA, HTTPS, PvP/PvAI
                         │
                Dọn QA và tắt QA route
```

- Mã workflow chính: [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml).
- `push` vào `develop`/`feature/**` và PR vào `develop`/`main` kích hoạt các bước xác minh.
- Release production chạy khi người có quyền gọi **`workflow_dispatch` trên `main` với `release_approved=true`** và đáp ứng phê duyệt của môi trường `production`.
- **Không** mặc định push vào `main` là tự động deploy production. Sau khi duyệt, workflow tự thực hiện publish image, trigger Render và nghiệm thu.

### 10.2. Cấu hình triển khai một bản mới trên Render + Neon

1. **Chuẩn bị PostgreSQL:** Tạo database Neon (hoặc PostgreSQL server tương đương), lấy connection string; không đưa hostname và mật khẩu thật vào README/commit.
2. **Chuẩn bị secrets:** Lưu `DATABASE_URL` và các thông tin registry/Render ở nơi quản lý secrets và environment phù hợp. Trong Render, đặt `APP_ENV=production`, `DATABASE_URL` của PostgreSQL và cấu hình cổng theo môi trường.
3. **Docker image:** Build và phát hành image thông qua release workflow; dùng **tag đủ commit SHA**, không dùng `latest` để khẳng định bản phát hành cụ thể.
4. **Render Web Service:** Trỏ tới image đã phát hành, đặt health check `/ready`, bảo đảm ứng dụng lắng nghe `${PORT:-8000}`. Entrypoint Docker chạy migration trước khi khởi động Uvicorn.
5. **Phê duyệt phát hành:** Trên GitHub Actions chọn workflow **CaroAI CI** → **Run workflow** trên nhánh `main` → đặt `release_approved=true`, hoàn thành bước duyệt production Environment nếu được yêu cầu.
6. **Nghiệm thu:** Kiểm tra kết quả workflow, image SHA, Render deploy `live`, `/health`, `/ready`, giao diện và các lượt chơi PvP/PvAI; xác nhận QA record được dọn và QA endpoint bị tắt.
7. **Rollback khi cần:** Dùng lịch sử deploy của Render để quay về **image trước đó đã xác minh**, sau khi kiểm tra tính tương thích schema/dữ liệu. Không rollback migration một cách tùy tiện.

**Bảo mật:** Không commit `.env`, khóa riêng, token Docker Hub, Render API key, DB password hoặc dữ liệu nhạy cảm. Các endpoint QA production phải bị vô hiệu hóa sau khi hoàn tất nghiệm thu.

### 10.3. Bản image và Render deployment đã nghiệm thu

| Thuộc tính | Giá trị |
|---|---|
| Ngày nghiệm thu | **07/11/2026** |
| Nhánh / commit | `main` / [`c10ee2739b6577ea0004f86e91126dd176132319`](https://github.com/emt0147t/caroAI/commit/c10ee2739b6577ea0004f86e91126dd176132319) |
| Docker image | `docker.io/emt0147/caroai:c10ee2739b6577ea0004f86e91126dd176132319` |
| Image digest đã xuất bản | `sha256:36660bc3c4db73f28b676c3cb3cdaf821f6cba02102e3f4723fa8c888a0e8b75` |
| Render deploy đã nghiệm thu gameplay | `dep-dbnkr6h5efls73bkhsi0` |
| Render deploy sau khi vô hiệu hóa QA | `dep-dbnkrjgu01pc73d1s8sg` |
| Bằng chứng | [GitHub Actions — run #42389707953](https://github.com/emt0147t/caroAI/actions/runs/42389707953) |

```bash
# Tải lại đúng image đã ghi nhận trong bản phát hành
# (không chứa mật khẩu hoặc thông tin môi trường production)
docker pull emt0147/caroai:c10ee2739b6577ea0004f86e91126dd176132319
```

Không dùng các SHA/deploy ID của những báo cáo cũ (ví dụ bản `42ee035...` ngày 06/11) để mô tả **bản phát hành cuối ngày 07/11**. Bản `c10ee273...` đã có nghiệm thu PvP/PvAI production qua API, khác với ghi chú “chưa nghiệm thu” trong một số tài liệu được tạo trước đó.

## 11. Kịch bản demo cho giảng viên

1. **Trình bày repo và Git:** Mở [repository](https://github.com/emt0147t/caroAI), chỉ ra feature branches/PR, commit có ý nghĩa và [merge conflict đã xử lý](docs/final-project/MERGE_CONFLICT_EVIDENCE.md).
2. **Docker:** Giới thiệu [Dockerfile](Dockerfile), [Compose](docker-compose.yml) và [Docker Hub image](https://hub.docker.com/r/emt0147/caroai).
3. **CI/CD:** Mở [workflow thành công](https://github.com/emt0147t/caroAI/actions/runs/42389707953), cho thấy kiểm thử, build, publish và deploy.
4. **HTTPS / sức khỏe:** Mở [CaroAI](https://caroai-bootstrap-a9e753b33198.onrender.com); kiểm tra `/health` và `/ready`.
5. **PvP:** Tạo trận, đánh luân phiên cho đến khi có năm quân liên tiếp; giải thích backend quyết định kết quả.
6. **PvAI:** Chọn mức khó, thực hiện nước đi và quan sát AI phản hồi hợp lệ.
7. **Database / lịch sử:** Mở `/history.html`, xem danh sách và mở lại trạng thái một trận đấu đã lưu; trình bày migration và persistence.
8. **Kết luận:** Đối chiếu từng tiêu chí tại [Mục 3](#3-ma-trận-đối-chiếu-yêu-cầu-và-bằng-chứng-hoàn-thành); nêu rõ các giới hạn trong [Mục 4.3](#43-giới-hạn-phạm-vi-đã-hoàn-thành).

**Phương án dự phòng:** Vì Render/Neon có thể cold-start hoặc mất kết nối, chuẩn bị Docker Compose local và bằng chứng workflow đã phát hành. Kết quả CI trước đó không thay thế yêu cầu ứng dụng hoạt động **trực tiếp trong buổi demo**.

## 12. Hạn chế, hướng phát triển và nguyên tắc báo cáo

### Những điểm chưa tuyên bố hoàn thành

- Online PvP với phòng chơi nhiều thiết bị.
- Trình phát lại toàn bộ chuỗi nước đi theo thời gian.
- Gợi ý nước đi/phân tích vị trí ở UI/API cho người dùng.
- Tích hợp mô hình học máy đã được đánh giá đủ và *promote* lên production.
- Cam kết AI bất bại, độ trễ production cố định hoặc SLA uptime chưa được xác lập.

### Hướng mở rộng sau học phần

- Bổ sung phòng chơi online và cơ chế đồng bộ lượt đánh theo thời gian thực.
- Hoàn thiện lịch sử dạng replay và tính năng Hint/Analysis.
- Mở rộng corpus kiểm thử chiến thuật, benchmark đa môi trường và đánh giá độ mạnh công bằng theo màu quân.
- Tăng quan sát vận hành (monitoring, cảnh báo, kiểm tra rollback/khả năng phục hồi).

**Nguyên tắc tổng kết:** Phân biệt rõ tính năng đã merge/deploy, kết quả kiểm thử ở CI, nghiệm thu thật trên production và thử nghiệm offline. Không xem một PR còn mở hoặc báo cáo cũ là bằng chứng rằng tính năng đã có mặt ở production.

## 13. Tài liệu và bằng chứng tham khảo

### Nguồn giảng viên

- [Đề bài gốc — Final Project (`project.docx`)](https://drive.google.com/file/d/1K3AffQyBaxMzH5iZ-o4ZQHVrhBlb6r-P/view).
- [Chương trình môn học và cơ cấu điểm — Topics and grading](https://docs.google.com/document/d/1ygnvqBtYfJbRU9wFR-xICXqNPmW1p9fV-Q2EA7ptagA/edit).

### Nguồn nội bộ và lịch sử triển khai

- [Kế hoạch phân công Sprint 1](https://docs.google.com/document/d/1PMAbGlTOAzK5g2gfuqjJQZS42toiK-dc7dYHP7pqbfc/edit).
- [Git Collaboration Audit](docs/final-project/GIT_COLLABORATION_AUDIT.md): lịch sử hợp tác 5 thành viên, **snapshot ngày 02/11**.
- [Merge Conflict Evidence](docs/final-project/MERGE_CONFLICT_EVIDENCE.md): conflict thật và merge commit.
- [Final Acceptance Report](docs/final-project/FINAL_ACCEPTANCE_REPORT.md): báo cáo lịch sử, **có những trạng thái release/branch đã cũ**; khi khác với release 07/11, ưu tiên bằng chứng từ workflow cuối.
- [Competitive AI report](reports/competitive/REVIEW.md): benchmark/tournament, có những nhận xét *pre-merge* thuộc thời điểm biên soạn.
- [Phase C API/PostgreSQL benchmark](reports/benchmark-phase-c/PHASE_C_BENCHMARK_REPORT.md): số liệu kiểm thử môi trường có kiểm soát, **không phải SLO production**.
- [PR #70 — tích hợp AI chiến thuật](https://github.com/emt0147t/caroAI/pull/70) và [PR #71 — offline learning chưa triển khai](https://github.com/emt0147t/caroAI/pull/71).
- [Workflow phát hành production cuối được kiểm chứng](https://github.com/emt0147t/caroAI/actions/runs/42389707953).

---

**CaroAI — Nhóm 5 thành viên.** README này mô tả phạm vi đồ án, đóng góp và những bằng chứng có thể đối chiếu; không thay thế biên bản chấm điểm chính thức của giảng viên.
