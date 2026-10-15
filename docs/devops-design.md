# DevOps Strategy & Architecture Specification (Sprint 1)

* **Owner:** Vinh
* **Branch:** `feature/devops`
* **Repository:** `emt0147t/caroAI`

---

## 1. Audit Cấu trúc dự án & hiện trạng DevOps

### 1.1. Khảo sát cấu trúc repository
* `app/`: mã nguồn Backend API service.
* `tests/`: unit và API tests.
* `docker-compose.yml`: local orchestration cho app và PostgreSQL.
* `Dockerfile`: multi-stage build, chạy container bằng user không phải root.

### 1.2. Mục tiêu Sprint 1
Đóng gói ứng dụng bằng Docker multi-stage, chuẩn hóa `docker-compose.yml` local và xây dựng CI/CD Pipeline trên GitHub Actions.

---

## 2. Containerization design

Thực thi multi-stage build tối ưu cache và phân quyền non-root `appuser`.

---

## 3. Local orchestration (`docker-compose.yml`)

Khởi chạy dịch vụ `app` cùng với PostgreSQL `db` container. Các biến cấu hình được truyền qua environment variables; `.env.example` chỉ chứa giá trị mẫu cho local development. Không đưa credentials thật vào repository.

---

## 4. CI quality gate — Sprint 2 / Issue #16

### Triggers
- Push lên `develop` hoặc `feature/devops` sẽ chạy workflow.
- Pull request có nhánh đích là `develop` sẽ chạy workflow.
- Có thể kích hoạt thủ công bằng `workflow_dispatch` khi workflow đã có trên nhánh mặc định của repository.

### Dependencies và runtime
- GitHub-hosted runner `ubuntu-latest`, Python 3.11.
- `requirements-dev.txt` kế thừa `requirements.txt` và bổ sung `flake8`, `httpx`; `httpx` được dùng bởi FastAPI TestClient.
- Pip cache gắn với `requirements-dev.txt` để tự làm mới khi dependencies thay đổi.

### Quality gates
- Lint: `python -m flake8 app tests --count --max-complexity=10 --max-line-length=127 --statistics`.
- Tests: `python -m pytest -q tests/`.
- Không dùng `--exit-zero`, `|| true`, hoặc cấu hình bỏ qua lỗi. Bất kỳ lỗi lint/test nào làm job `test` thất bại.
- Docker build nằm trong job riêng có `needs: test`; image chỉ build khi toàn bộ lint và tests đã pass.

### Chạy kiểm tra tại máy local
```bash
python -m pip install -r requirements-dev.txt
python -m flake8 app tests --count --max-complexity=10 --max-line-length=127 --statistics
python -m pytest -q tests/
docker compose config --quiet
docker compose build
```

### Xử lý khi CI thất bại
Mở GitHub → Actions → chọn workflow run đỏ → mở step bị lỗi để xem log.
- Nếu `flake8` thất bại: sửa lỗi tại file/dòng được nêu; không thêm cơ chế bỏ qua lỗi chỉ để làm CI xanh.
- Nếu `pytest` thất bại: kiểm tra traceback và assertion.
- Job Docker build sẽ bị skip nếu job `test` thất bại.

### Phạm vi Docker smoke test
Workflow CI hiện kiểm tra khả năng build image sau khi quality gates thành công. Smoke test end-to-end xác nhận cả AI move và PostgreSQL persistence cần được chạy sau khi Backend–AI integration và DB runtime được tích hợp; chỉ build image hoặc gọi `/health` chưa đủ để kết luận gameplay/persistence đã hoạt động.
