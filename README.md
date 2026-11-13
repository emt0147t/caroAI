# CaroAI — Cờ Caro 15×15 với AI

CaroAI là dự án cuối kỳ xây dựng ứng dụng Cờ Caro (Gomoku) 15×15, kết hợp **FastAPI**, **AI tìm kiếm nước đi**, **PostgreSQL**, **Docker**, **GitHub Actions CI/CD** và triển khai qua **Render**.

Dự án đã chốt phạm vi học phần. Thông tin phát hành bên dưới phản ánh **lần nghiệm thu production ngày 07/11/2026**, không phải cam kết dịch vụ luôn trực tuyến tại thời điểm truy cập.

| Tài nguyên | Liên kết |
|---|---|
| Ứng dụng trực tuyến | [Mở CaroAI](https://caroai-bootstrap-a9e753b33198.onrender.com) |
| Mã nguồn | [emt0147t/caroAI](https://github.com/emt0147t/caroAI) |
| CI/CD và bằng chứng triển khai cuối | [GitHub Actions — run 42389707953](https://github.com/emt0147t/caroAI/actions/runs/42389707953) |
| Docker image | [Docker Hub — emt0147/caroai](https://hub.docker.com/r/emt0147/caroai) |

## 1. Tính năng đã hoàn thành

- **PvP cùng thiết bị:** Hai người chơi luân phiên trên một bàn cờ 15×15.
- **PvAI:** Chơi với AI ở bốn mức `easy`, `medium`, `hard`, `impossible`.
- **AI Engine:** `easy`/`medium` sử dụng Minimax/alpha-beta; `hard`/`impossible` sử dụng bộ tìm kiếm chiến thuật cải tiến với kiểm tra thắng/chặn, tìm kiếm có giới hạn và bảng chuyển vị.
- **Luật chơi phía backend:** Kiểm tra lượt, nước đi hợp lệ, thắng năm quân liên tiếp và hòa khi hết ô.
- **PostgreSQL:** Lưu trận đấu, các nước đi và kết quả; có trang xem lịch sử và mở lại trạng thái bàn cờ.
- **Giao diện web:** HTML/CSS/JavaScript thuần, hỗ trợ màn hình nhỏ và giao diện sáng/tối.
- **Vận hành:** Docker, Docker Compose, endpoint kiểm tra sức khỏe và quy trình kiểm thử/triển khai bằng GitHub Actions.

**Giới hạn phạm vi:** PvP hiện là chơi trên cùng thiết bị, **không** phải phòng chơi online. Trang lịch sử **không** có chức năng phát lại từng nước đi. Chưa có tính năng gợi ý/phân tích thế cờ dành cho người dùng. Mức `impossible` **không** có nghĩa AI bất bại. Mô hình học máy trong [PR #71](https://github.com/emt0147t/caroAI/pull/71) chỉ là thử nghiệm offline, **chưa đưa vào production**.

## 2. Kiến trúc

```text
Trình duyệt ── HTTPS ──► Render (Docker)
                            │
                            └─ FastAPI: frontend + REST API
                                 ├─ Game Service / kiểm tra luật
                                 ├─ Python AI Engine
                                 └─ SQLAlchemy ──► Neon PostgreSQL
```

**Công nghệ chính:** Python 3.11, FastAPI, SQLAlchemy, PostgreSQL, JavaScript thuần, Docker, GitHub Actions và Render.

Mã nguồn chính nằm trong `app/` (API, luật chơi, AI, dịch vụ, truy cập DB), `frontend/Caro_AI/` (giao diện), `database/migrations/` (các migration `000`–`003`), `tests/` (kiểm thử), `.github/workflows/` (CI/CD).

## 3. Chạy thử bằng Docker Compose

**Yêu cầu:** Git, Docker và Docker Compose.

```bash
git clone https://github.com/emt0147t/caroAI.git
cd caroAI
cp .env.example .env
# Đổi POSTGRES_PASSWORD trong .env thành mật khẩu dùng cho máy của bạn.
docker compose up --build -d
docker compose ps
```

Nếu dùng PowerShell, thay `cp .env.example .env` bằng `Copy-Item .env.example .env`.

- Giao diện: http://localhost:8080
- FastAPI / Swagger: http://localhost:8000/docs
- Kiểm tra ứng dụng: http://localhost:8000/health
- Kiểm tra kết nối DB: http://localhost:8000/ready

Dừng môi trường bằng `docker compose down`. **Không** dùng `down -v` nếu muốn giữ dữ liệu trong volume PostgreSQL.

## 4. API chính

| Phương thức | Endpoint | Mục đích |
|---|---|---|
| `GET` | `/health`, `/ready` | Kiểm tra ứng dụng và kết nối DB |
| `POST` | `/api/games` | Tạo trận PvP/PvAI |
| `GET` | `/api/games/{game_id}` | Lấy trạng thái bàn cờ |
| `POST` | `/api/games/{game_id}/moves` | Đánh một nước đi |
| `POST` | `/api/games/{game_id}/ai-move` | Yêu cầu AI đánh |
| `GET` | `/api/history` | Danh sách lịch sử trận đấu |

Tài liệu OpenAPI tự động có tại `/docs`.

## 5. Kiểm thử và CI/CD

Chạy kiểm thử Python tại thư mục gốc (cần Python 3.11):

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q tests/
```

Kiểm thử giao diện:

```bash
node --test tests/frontend-regression.test.cjs
npm ci
# Cần chuẩn bị browser/runtime phù hợp trước khi chạy Playwright.
npm run test:e2e
```

Workflow `.github/workflows/ci-cd.yml` kiểm tra mã nguồn, frontend, PostgreSQL, Docker Compose, bảo mật và build image. Phát hành production được kích hoạt thủ công trên `main`, qua môi trường phê duyệt, rồi kiểm chứng deployment và gameplay.

**Kết quả đã ghi nhận trong [workflow ngày 07/11/2026](https://github.com/emt0147t/caroAI/actions/runs/42389707953):**

- Bộ kiểm thử Python: **829 passed, 14 skipped**; bộ PostgreSQL chuyên biệt: **18 passed**.
- Docker image được xuất bản và Render xác nhận triển khai thành công đúng SHA.
- Endpoint `/health`, `/ready`, `/`, `/history.html`, `/api/history`, `/tokens.css` trả HTTP 200 tại thời điểm nghiệm thu.
- Kiểm thử **PvP thắng trận**, **PvAI ra nước đi**, đọc trạng thái và lịch sử trên production **PASS**; dữ liệu QA được dọn dẹp và endpoint QA bị vô hiệu hóa sau nghiệm thu.

## 6. Bản phát hành production đã kiểm chứng

| Thuộc tính | Giá trị |
|---|---|
| Ngày nghiệm thu | 07/11/2026 |
| Commit ứng dụng | [`c10ee2739b6577ea0004f86e91126dd176132319`](https://github.com/emt0147t/caroAI/commit/c10ee2739b6577ea0004f86e91126dd176132319) |
| Image | `docker.io/emt0147/caroai:c10ee2739b6577ea0004f86e91126dd176132319` |
| Digest đã xuất bản | `sha256:36660bc3c4db73f28b676c3cb3cdaf821f6cba02102e3f4723fa8c888a0e8b75` |
| Render deploy nghiệm thu | `dep-dbnkr6h5efls73bkhsi0` |
| Render deploy sau khi tắt QA | `dep-dbnkrjgu01pc73d1s8sg` |

Đây là **bằng chứng tại thời điểm phát hành**, không phải kết quả giám sát uptime hay tải đồng thời dài hạn. Các kết quả benchmark AI trong `reports/` được đo trong môi trường kiểm soát, không nên suy diễn thành cam kết độ trễ production.

## 7. Tài liệu và bằng chứng

- [Báo cáo nghiệm thu học phần](docs/final-project/FINAL_ACCEPTANCE_REPORT.md) — tài liệu lịch sử, có thể phản ánh snapshot trước bản phát hành cuối.
- [Kiểm toán cộng tác Git](docs/final-project/GIT_COLLABORATION_AUDIT.md) và [bằng chứng xử lý merge conflict](docs/final-project/MERGE_CONFLICT_EVIDENCE.md).
- [Báo cáo benchmark AI](reports/competitive/) và [benchmark API/PostgreSQL](reports/benchmark-phase-c/).
- [Lịch sử workflow GitHub Actions](https://github.com/emt0147t/caroAI/actions).

**Bảo mật:** Không đưa mật khẩu, `DATABASE_URL` thật, token hay khóa triển khai vào repository; dùng biến môi trường và secrets của nền tảng.
