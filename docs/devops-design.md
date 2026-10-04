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
