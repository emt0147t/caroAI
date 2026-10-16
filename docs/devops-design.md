# DevOps Strategy & Architecture Specification (Sprint 1)

* **Owner:** Vinh
* **Branch:** `feature/devops`
* **Repository:** `emt0147t/caroAI`

---

## 1. Audit Cấu Trúc Dự Án & Hiện Trạng DevOps

### 1.1. Khảo sát Cấu trúc Repository
* `app/`: Mã nguồn Backend API service.
* `ai/`: Thuật toán xử lý AI cho cờ Caro.
* `frontend/`: Giao diện người dùng.
* `database/`: Cấu hình schema và script CSDL.
* `tests/`: Thư mục unit test.

### 1.2. Mục tiêu Sprint 1
Đóng gói ứng dụng bằng Docker Multi-stage, chuẩn hóa `docker-compose.yml` local và xây dựng CI/CD Pipeline trên GitHub Actions.

---

## 2. Containerization Design
Thực thi Multi-stage build tối ưu cache và phân quyền non-root `appuser`.

---

## 3. Local Orchestration (`docker-compose.yml`)
Khởi chạy dịch vụ `app` cùng với PostgreSQL `db` container.

---

## 4. CI Quality Gate — Sprint 2 / Issue #16

### 4.1. Triggers
- Push lên `develop` hoặc bất kỳ nhánh `feature/**` nào sẽ chạy workflow.
- Pull request có nhánh đích là `develop` sẽ chạy workflow.
- Có thể kích hoạt thủ công bằng `workflow_dispatch` khi workflow đã có trên nhánh mặc định của repository.

### 4.2. Dependencies và runtime
- GitHub-hosted runner `ubuntu-latest`, Python 3.11.
- `requirements-dev.txt` kế thừa `requirements.txt` và bổ sung `flake8`, `httpx`; `httpx` phục vụ FastAPI TestClient.
- Pip cache gắn với `requirements-dev.txt` để tự làm mới khi dependencies thay đổi.

### 4.3. Quality gates
- Lint: `python -m flake8 app tests --count --max-complexity=10 --max-line-length=127 --statistics`.
- Tests: `python -m pytest -q tests/`.
- Không dùng `--exit-zero`, `|| true`, hoặc cấu hình bỏ qua lỗi. Lỗi lint/test làm job `test` thất bại.
- Docker build chạy ở job riêng có `needs: test`, nên image chỉ build khi quality gates thành công.

### 4.4. Chạy kiểm tra tại máy local
Tạo file environment cục bộ rồi cài dependency và chạy kiểm tra:

```bash
cp .env.example .env
python -m pip install -r requirements-dev.txt
python -m flake8 app tests --count --max-complexity=10 --max-line-length=127 --statistics
python -m pytest -q tests/
docker compose config --quiet
docker compose build
```

### 4.5. Xử lý khi CI thất bại
Mở GitHub → Actions → chọn workflow run đỏ → mở step bị lỗi để xem log.
- Nếu `flake8` thất bại: sửa lỗi tại file/dòng được nêu; không thêm cơ chế bỏ qua lỗi chỉ để làm CI xanh.
- Nếu `pytest` thất bại: kiểm tra traceback và assertion.
- Job Docker build sẽ bị skip nếu job `test` thất bại.

### 4.6. Phạm vi Docker smoke test
Workflow CI hiện kiểm tra khả năng build image sau khi quality gates thành công. Smoke test end-to-end xác nhận cả AI move và PostgreSQL persistence cần được chạy sau khi Backend–AI integration và DB runtime được tích hợp; chỉ build image hoặc gọi `/health` chưa đủ để kết luận gameplay/persistence đã hoạt động.

### 4.7. Environment và secrets
- `.env.example` chỉ chứa giá trị mẫu cho local development.
- File `.env` và các file environment cục bộ bị bỏ qua bởi Git; ngoại lệ được giữ lại cho `.env.example`.
- Không commit credentials thật hoặc secrets production vào repository.
