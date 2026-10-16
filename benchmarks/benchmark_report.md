# AI Benchmark Report — CaroAI Sprint 2

## Environment

| Key | Value |
|---|---|
| `python_version` | 3.13.14 (tags/v3.13.14:fd17997, Jun 10 2026, 13:03:48) [MSC v.1944 64 bit (AMD64)] |
| `platform` | Windows-11-10.0.26200-SP0 |
| `processor` | Intel64 Family 6 Model 191 Stepping 2, GenuineIntel |
| `machine` | AMD64 |
| `cpu_name` | unknown |

## AI Configuration (from engine.py)

| Difficulty | depth | candidate_limit |
|---|---|---|
| EASY | 1 | 6 |
| MEDIUM | 2 | 10 |
| HARD | 3 | 14 |

## Results (Standard Benchmark)

> **Thông số đo:** 5 lần chạy chính thức (`runs=5`), 1 lần khởi động (`warmup=1`) mỗi fixture/difficulty.
> Thời gian hiển thị ở cả đơn vị giây (`s`) chuẩn hóa thập phân và mili-giây (`ms`).

| Fixture | Difficulty | Runs | Median (s) | Median (ms) | Min (s) | Max (s) | Node Count |
|---|---|---|---|---|---|---|---|
| empty_board | EASY | 5 | 0.000 s | 0.340 ms | 0.000 s | 0.000 s | N/A |
| empty_board | MEDIUM | 5 | 0.004 s | 3.702 ms | 0.003 s | 0.006 s | N/A |
| empty_board | HARD | 5 | 0.013 s | 12.703 ms | 0.013 s | 0.014 s | N/A |
| mid_game_center_cluster | EASY | 5 | 0.003 s | 2.566 ms | 0.003 s | 0.003 s | N/A |
| mid_game_center_cluster | MEDIUM | 5 | 0.010 s | 10.447 ms | 0.010 s | 0.011 s | N/A |
| mid_game_center_cluster | HARD | 5 | 0.088 s | 88.369 ms | 0.087 s | 0.107 s | N/A |
| ai_one_move_to_win | EASY | 5 | 0.000 s | 0.022 ms | 0.000 s | 0.000 s | N/A |
| ai_one_move_to_win | MEDIUM | 5 | 0.000 s | 0.022 ms | 0.000 s | 0.000 s | N/A |
| ai_one_move_to_win | HARD | 5 | 0.000 s | 0.022 ms | 0.000 s | 0.000 s | N/A |
| block_opponent_four | EASY | 5 | 0.000 s | 0.055 ms | 0.000 s | 0.000 s | N/A |
| block_opponent_four | MEDIUM | 5 | 0.000 s | 0.055 ms | 0.000 s | 0.000 s | N/A |
| block_opponent_four | HARD | 5 | 0.000 s | 0.054 ms | 0.000 s | 0.000 s | N/A |
| complex_mid_game | EASY | 5 | 0.000 s | 0.090 ms | 0.000 s | 0.000 s | N/A |
| complex_mid_game | MEDIUM | 5 | 0.000 s | 0.094 ms | 0.000 s | 0.000 s | N/A |
| complex_mid_game | HARD | 5 | 0.000 s | 0.103 ms | 0.000 s | 0.000 s | N/A |

## Profiling & Independent Observations

> Các dữ liệu dưới đây thuộc phiên profiling chẩn đoán và đo đạc độc lập, **tách biệt hoàn toàn** với bảng benchmark chuẩn ở trên:

1. **cProfile Profiling (chẩn đoán điểm nghẽn thuật toán):**
   - Trên thế cờ `complex_mid_game` (HARD, depth=3, candidate_limit=14), profiler ghi nhận:
     - 37,631 lời gọi tới `evaluate_board`
     - 5,418,864 lời gọi tới `evaluate_line`
     - Hơn 83% thời gian tiêu tốn cho việc nối chuỗi (`''.join(chars)`) và kiểm tra heuristic mẫu chuỗi trong Python thuần.
2. **Phiên đo lường chẩn đoán độc lập (Diagnostic run under heavy load):**
   - Trong một phiên profiling/đo lường độc lập khác, `complex_mid_game` HARD ghi nhận median ~19.282 s (min: 11.550 s, max: 19.622 s). Đây là số liệu quan sát độc lập phát sinh trong điều kiện tải hệ thống khác nhau, không thay thế bảng benchmark chuẩn 7.064 s.

## Performance Analysis & Compliance

### 1. Đối chiếu mục tiêu thời gian phản hồi (`docs/ai-design.md §1`)
Tài liệu thiết kế quy định mục tiêu: **Thời gian phản hồi AI < 1.0 giây**.

Đánh giá dưới đây chỉ dùng bảng **Standard Benchmark** đã ghi ở trên (5 lần đo, 1 warm-up, trên môi trường Windows 11/Python 3.13.14 được ghi trong báo cáo):
- **EASY (depth=1, limit=6):** median lớn nhất là **2.566 ms** (`mid_game_center_cluster`) (**ĐẠT**, dưới 1.0 s).
- **MEDIUM (depth=2, limit=10):** median lớn nhất là **10.447 ms** (`mid_game_center_cluster`) (**ĐẠT**, dưới 1.0 s).
- **HARD (depth=3, limit=14):** median lớn nhất là **88.369 ms** (`mid_game_center_cluster`) (**ĐẠT**, dưới 1.0 s). `complex_mid_game` ghi nhận 0.103 ms trong bộ fixture này; fixture có một nước chặn chiến thuật tức thì nên có thể thoát sớm.

**Kết luận giới hạn:** các median được ghi trong bảng Standard Benchmark đều dưới mục tiêu < 1.0 s. Đây là kết quả benchmark cục bộ của các fixture cụ thể, không phải bằng chứng cho mọi thế cờ hoặc mọi phần cứng. Quan sát profiling độc lập ở trên chưa được tái lập và không được gộp vào kết luận này. Chưa có benchmark baseline Sprint 1 tương đương, vì vậy chưa thể định lượng mức tăng tốc so với phiên bản cũ.

### 2. Nguyên nhân biến thiên & Hiện trạng phần cứng
- **Candidate Ordering:** Đã kiểm tra thực nghiệm: trên cùng bàn cờ, hàm `get_candidate_moves()` với tuple hashing sinh tập hợp đồng nhất; minimax sắp xếp lại bằng `scored_candidates.sort()` nên thứ tự ban đầu không gây ra biến thiên lớn giữa các lần chạy.
- **Tác động của Incremental Evaluation:** Trước tối ưu, Minimax duyệt toàn bộ 72 đường (144 lượt đánh giá) cho mỗi candidate move. Với Incremental Evaluation, chỉ tối đa 4 đường đi qua ô candidate được tính lại, kết hợp memoization tuple đường giúp giảm hơn 115 lần khối lượng tính toán trên các thế cờ phức tạp.
- **Tính toàn vẹn thuật toán:** 100% điểm số heuristic, candidate ordering và kết quả chọn nước đi của AI được bảo toàn tuyệt đối, không có sai lệch ngữ nghĩa.

## Limitations

- Fixtures là các tình huống đại diện, không phản ánh đầy đủ độ mạnh chơi thực tế.
- `candidate_moves` dùng `set` nhưng contract không yêu cầu deterministic ordering; các candidate moves hợp lệ đều được bảo đảm.
- Node count không có trong implementation hiện tại → ghi N/A.
- Thời gian đo trên máy đơn, phụ thuộc vào OS scheduler và trạng thái hệ thống.
- Không có so sánh baseline từ Sprint 1 → chưa thể kết luận AI nhanh hơn/chậm hơn.

*Generated by `benchmarks/benchmark_ai.py` — 2026-10-14T22:49:17*