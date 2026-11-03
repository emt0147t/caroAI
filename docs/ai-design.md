# CaroAI — AI Engine Technical Design Specification

- **Role / Author:** AI Engineer (Member 2)
- **Target Module:** `app/ai/`
- **Integration Target:** `app/game/`, `app/api/`
- **Target Platform:** Python 3.12, CPU execution inside Docker / Linux container
- **Design Philosophy:** Latency-first, deterministic tactical defense/offense, zero external heavy ML runtime in Sprint 1.

---

## 1. Audit Code & Trạng thái hiện tại
Theo baseline kiến trúc hệ thống:
- Source code tổ chức trong `app/ai/`: `evaluator.py`, `move_generator.py`, `minimax.py`, `engine.py`.
- Stateless, giới hạn độ sâu 1–3 để phản hồi < 1s trên container.

---

## 2. Board Representation & Game State
- Kích thước 15x15.
- `EMPTY = 0`, `PLAYER_X = 1`, `PLAYER_O = 2`.
- Sử dụng backtracking trực tiếp trên mảng 2D để tránh copy state.

---

## 3. Pattern Detection & Bảng trọng số Heuristic
- FIVE: 100,000,000
- OPEN_FOUR: 10,000,000
- FOUR: 500,000
- OPEN_THREE: 100,000
- THREE: 5,000
- OPEN_TWO: 500
- Công thức: Total = AI_Score - 1.2 * Opponent_Score.

---

## 4. Candidate Move Generation & Move Ordering
- Quét bán kính Chebyshev R=1 hoặc R=2 quanh các quân đã có.
- Bàn rỗng đánh (7, 7).
- Kiểm tra ngay Immediate Win và Immediate Block trước khi search sâu.

---

## 5. Minimax with Alpha-Beta Pruning
- Duyệt cây Minimax kết hợp cắt tỉa Alpha-Beta.
- Backtracking apply/undo move.

---

## 6. Cấu hình độ khó
- EASY: Depth 1
- MEDIUM: Depth 2 (MVP baseline)
- HARD: Depth 3

---

## 7. AI Hint & Move Analysis
- Hint: Gợi ý nước đi tốt nhất kèm giải thích.
- Analysis: Phân loại BEST, GOOD, INACCURACY, MISTAKE dựa trên chênh lệch điểm.

---

## 8. IO Contract với Backend FastAPI
- Input: `board: List[List[int]]`, `ai_player: int`, `difficulty: str`
- Output: `{"row": int, "col": int, "score": int, "elapsed_ms": float}`