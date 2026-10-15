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

## CI Sprint 2

### 1. Luồng kích hoạt (Triggers)
- Kích hoạt tự động khi push lên nhánh develop hoặc khi mở/cập nhật pull_request có nhánh đích (target branch) là develop.
- Hỗ trợ kích hoạt thủ công qua workflow_dispatch.

### 2. Môi trường & Dependencies
- Chạy trên runner ubuntu-latest với Python 3.11.
- Quản lý phụ thuộc dev/testing riêng qua requirements-dev.txt (kế thừa requirements.txt, bổ sung flake8 và httpx).
- Tối ưu thời gian chạy bằng cơ chế Pip Cache theo hash của requirements-dev.txt.

### 3. Kiểm tra chất lượng (Quality Gate)
- Linting (flake8): Kiểm tra mã nguồn trong app và tests với --max-complexity=10 và --max-line-length=127.
- Unit Test (pytest): Thực thi toàn bộ bộ test trong thư mục tests/.
- Pipeline áp dụng cơ chế Strict Quality Gate: Bất kỳ lỗi linting hoặc unit test thất bại đều làm dừng pipeline lập tức (không dùng --exit-zero, continue-on-error hay || true).

### 4. Đóng gói Docker
- Job build kiểm tra build Docker image ứng dụng chỉ được thực thi sau khi job test đã hoàn thành thành công (needs: test).

### 5. Xử lý khi CI thất bại
- Vào tab Actions trên GitHub -> chọn Workflow Run bị lỗi.
- Nhấp vào step có biểu tượng đỏ để xem chi tiết log:
  - Nếu lỗi flake8: Đọc rõ file, dòng và mã lỗi (như E302, F401, E501) để sửa đúng trong code.
  - Nếu lỗi pytest: Kiểm tra đoạn traceback để xác định test case hoặc assertion bị fail.
