"""
Task B3 — Minimax và alpha-beta regression tests.

Kiểm tra:
- Evaluation utility giữa MAX và MIN.
- Terminal win/loss/draw.
- Alpha-beta không thay đổi giá trị tối ưu so với tìm kiếm đầy đủ.
- Node-counting (nếu implementation có).
"""

from app.ai.minimax import minimax, find_best_move, INF
from app.ai.evaluator import evaluate_board, SCORE_FIVE, get_board_raw_scores

BOARD_SIZE = 15
EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2


def empty_board():
    return [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]


# ── B3.1  Evaluation utility ─────────────────────────────────────────────────

def test_terminal_win_returns_score_five():
    """
    Khi AI đã có 4 quân và 1 ô trống tạo chuỗi 5,
    minimax ở depth=1 phải trả về score >= SCORE_FIVE.
    """
    b = empty_board()
    for c in range(3, 7):
        b[7][c] = PLAYER_X       # 4 quân X nằm ngang
    _, score = find_best_move(b, ai_player=PLAYER_X, depth=1)
    assert score >= SCORE_FIVE, f"Expected terminal win score >= {SCORE_FIVE}, got {score}"


def test_blocking_opponent_returns_negative_score():
    """
    Khi đối thủ có nước thắng ngay và AI phải chặn,
    score trả về nên nhỏ hơn 0 (AI bị bất lợi).
    """
    b = empty_board()
    for c in range(3, 7):
        b[7][c] = PLAYER_O       # O sắp thắng
    b[0][0] = PLAYER_X
    _, score = find_best_move(b, ai_player=PLAYER_X, depth=2)
    assert score < SCORE_FIVE, "Score quá cao khi AI đang chặn, không phải thắng"


def test_evaluate_board_zero_on_empty():
    """Board trống: evaluate_board phải trả về 0 (cân bằng)."""
    b = empty_board()
    score = evaluate_board(b, ai_player=PLAYER_X, human_player=PLAYER_O)
    assert score == 0


def test_evaluate_board_positive_for_ai_advantage():
    """Khi AI có chuỗi dài hơn, evaluate_board phải dương."""
    b = empty_board()
    # AI có chuỗi 4 quân
    for c in range(5, 9):
        b[7][c] = PLAYER_X
    score = evaluate_board(b, ai_player=PLAYER_X, human_player=PLAYER_O)
    assert score > 0, f"Expected positive score for AI advantage, got {score}"


def test_evaluate_board_negative_for_human_advantage():
    """Khi đối thủ có chuỗi dài hơn, evaluate_board phải âm."""
    b = empty_board()
    for c in range(5, 9):
        b[7][c] = PLAYER_O
    score = evaluate_board(b, ai_player=PLAYER_X, human_player=PLAYER_O)
    assert score < 0, f"Expected negative score for human advantage, got {score}"


# ── B3.2  Alpha-beta không thay đổi nước tối ưu so với full minimax ──────────

def _minimax_no_pruning(board, depth, is_maximizing, ai_player, human_player, candidate_limit=8):
    """
    Phiên bản minimax KHÔNG cắt tỉa alpha-beta (alpha=-INF, beta=INF cố định).
    Dùng để so sánh với phiên bản có pruning.
    """
    return minimax(
        board, depth, alpha=-INF, beta=INF,
        is_maximizing=is_maximizing,
        ai_player=ai_player,
        human_player=human_player,
        candidate_limit=candidate_limit,
    )


def test_alpha_beta_same_score_as_full_search_depth1():
    """
    Trên fixture nhỏ depth=1:
    minimax với alpha-beta và không alpha-beta phải trả về cùng score tối ưu.
    """
    b = empty_board()
    b[7][7] = PLAYER_O           # 1 quân, giúp có candidate
    b[7][8] = PLAYER_X

    _, score_ab = minimax(
        b, depth=1, alpha=-INF, beta=INF,
        is_maximizing=True,
        ai_player=PLAYER_X, human_player=PLAYER_O,
        candidate_limit=8
    )
    _, score_full = _minimax_no_pruning(b, depth=1, is_maximizing=True,
                                        ai_player=PLAYER_X, human_player=PLAYER_O)
    assert score_ab == score_full, (
        f"Alpha-beta score {score_ab} != full search score {score_full}"
    )


def test_alpha_beta_same_score_as_full_search_depth2():
    """Depth=2: alpha-beta và full search phải cho score tối ưu như nhau."""
    b = empty_board()
    b[7][7] = PLAYER_O
    b[7][8] = PLAYER_X
    b[6][7] = PLAYER_X

    _, score_ab = minimax(
        b, depth=2, alpha=-INF, beta=INF,
        is_maximizing=True,
        ai_player=PLAYER_X, human_player=PLAYER_O,
        candidate_limit=6
    )
    _, score_full = _minimax_no_pruning(b, depth=2, is_maximizing=True,
                                        ai_player=PLAYER_X, human_player=PLAYER_O,
                                        candidate_limit=6)
    assert score_ab == score_full, (
        f"Alpha-beta depth=2 score {score_ab} != full search score {score_full}"
    )


# ── B3.3  find_best_move trả về move hợp lệ ──────────────────────────────────

def test_find_best_move_returns_tuple():
    """find_best_move phải trả về (tuple, int)."""
    b = empty_board()
    b[7][7] = PLAYER_O
    result = find_best_move(b, ai_player=PLAYER_X, depth=1)
    assert isinstance(result, tuple) and len(result) == 2
    move, score = result
    assert isinstance(move, tuple) and len(move) == 2
    assert isinstance(score, int)


def test_find_best_move_in_bounds():
    """find_best_move phải trả về tọa độ nằm trong [0, BOARD_SIZE)."""
    b = empty_board()
    b[7][7] = PLAYER_O
    move, _ = find_best_move(b, ai_player=PLAYER_X, depth=2)
    r, c = move
    assert 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def test_find_best_move_on_empty_cell():
    """find_best_move phải trả về ô đang trống."""
    b = empty_board()
    b[7][7] = PLAYER_O
    move, _ = find_best_move(b, ai_player=PLAYER_X, depth=2)
    r, c = move
    assert b[r][c] == EMPTY, f"Move {move} lands on occupied cell {b[r][c]}"


# ── B3.4  Depth Cutoff & Horizon Tactical Extension ──────────────────────────

def test_minimax_horizon_detects_immediate_win_at_depth_zero():
    """
    Regression test: Bảo vệ tactical check trước depth cutoff trong minimax().
    Khi AI có 4 quân thành hàng và có ô tạo chuỗi 5 ngay lập tức, minimax ở depth=0
    phải phát hiện nước thắng qua tactical extension và trả về score >= SCORE_FIVE.
    Nếu di chuyển depth cutoff lên trước tactical check, minimax sẽ chỉ trả về
    heuristic evaluation của thế cờ hiện tại (SCORE_OPEN_FOUR = 10_000_000 < SCORE_FIVE)
    và move=None, làm lọt lưới nước thắng tại search horizon.
    """
    b = empty_board()
    for c in range(3, 7):
        b[7][c] = PLAYER_X       # 4 quân X liên tiếp: (7,3), (7,4), (7,5), (7,6)

    move, score = minimax(
        b,
        depth=0,
        alpha=-INF,
        beta=INF,
        is_maximizing=True,
        ai_player=PLAYER_X,
        human_player=PLAYER_O,
        candidate_limit=12,
    )
    assert move in [(7, 2), (7, 7)], f"Expected winning move at (7, 2) or (7, 7), got {move}"
    assert score >= SCORE_FIVE, f"Expected terminal win score >= {SCORE_FIVE} at depth 0, got {score}"


def test_minimax_horizon_detects_immediate_loss_at_depth_zero():
    """
    Regression test: Bảo vệ tactical check chặn thua trước depth cutoff trong minimax().
    Khi đối thủ có 4 quân thành hàng và is_maximizing=False, minimax ở depth=0
    phải phát hiện nguy cơ thua ngay lập tức và trả về score <= -SCORE_FIVE cùng move chặn.
    Nếu di chuyển depth cutoff lên trước tactical check, minimax sẽ trả về heuristic
    (-1.2 * SCORE_OPEN_FOUR = -12_000_000 > -SCORE_FIVE) và move=None,
    không nhận diện được terminal loss tại search horizon.
    """
    b = empty_board()
    for c in range(3, 7):
        b[7][c] = PLAYER_O       # Đối thủ có 4 quân liên tiếp
    b[0][0] = PLAYER_X           # AI đã có ít nhất 1 quân trên bàn

    move, score = minimax(
        b,
        depth=0,
        alpha=-INF,
        beta=INF,
        is_maximizing=False,
        ai_player=PLAYER_X,
        human_player=PLAYER_O,
        candidate_limit=12,
    )
    assert move in [(7, 2), (7, 7)], f"Expected threat move at (7, 2) or (7, 7), got {move}"
    assert score <= -SCORE_FIVE, f"Expected terminal loss score <= {-SCORE_FIVE} at depth 0, got {score}"


# ── B3.5  Correctness & Incremental Evaluation Regression Tests ──────────────

def test_minimax_min_node_does_not_claim_ai_win_when_human_can_block():
    """
    Regression test: Bảo vệ ngữ nghĩa lượt đi tại MIN node (is_maximizing=False).
    Khi AI có 4 quân liên tiếp bị chặn 1 đầu và 1 ô mở (7, 7), nhưng hiện đang là
    lượt của đối thủ (is_maximizing=False), minimax KHÔNG ĐƯỢC trả về ((7, 7), SCORE_FIVE).
    Đối thủ phải được quyền đi trong lượt của mình và sẽ chặn tại (7, 7),
    do đó score trả về phải < SCORE_FIVE (thực tế là điểm sau khi đã chặn, không phải AI thắng).
    """
    b = empty_board()
    b[7][2] = PLAYER_O       # Chặn đầu trái
    for c in range(3, 7):
        b[7][c] = PLAYER_X   # AI có (7, 3), (7, 4), (7, 5), (7, 6)
    # (7, 7) là ô duy nhất AI có thể thắng nếu đến lượt AI

    move, score = minimax(
        b,
        depth=1,
        alpha=-INF,
        beta=INF,
        is_maximizing=False,  # Lượt của Human!
        ai_player=PLAYER_X,
        human_player=PLAYER_O,
        candidate_limit=12,
    )
    # Human đi trong lượt của mình, sẽ chặn tại (7, 7)
    assert move == (7, 7), f"Expected Human to block at (7, 7), got {move}"
    assert score < SCORE_FIVE, f"Expected score < {SCORE_FIVE} at MIN node, got {score}"


def test_win_and_block_detection_not_suppressed_by_opponent_heuristic_pieces():
    """
    Regression test: Bảo vệ ngưỡng thắng/chặn khỏi bị suy giảm bởi heuristic đối thủ (1.2 * opponent).
    1. Khi AI tạo chuỗi 5 nhưng đối thủ có quân trên bàn cờ (ví dụ open three hu_total > 0),
       minimax ở depth=0 vẫn phải nhận diện đúng chiến thắng và trả về SCORE_FIVE thay vì bị
       trừ 1.2 * hu_total khiến score < SCORE_FIVE.
    2. Tương tự, khi đối thủ tạo chuỗi 5 và AI có quân trên bàn cờ, minimax nhận diện
       terminal loss và trả về -SCORE_FIVE.
    """
    # Case 1: AI thắng khi đối thủ có open three
    b_ai = empty_board()
    for c in range(3, 7):
        b_ai[7][c] = PLAYER_X   # 4 quân AI
    for c in range(3, 6):
        b_ai[3][c] = PLAYER_O   # Đối thủ có 3 quân mở (hu_total = 100,000)

    move_ai, score_ai = minimax(
        b_ai,
        depth=0,
        alpha=-INF,
        beta=INF,
        is_maximizing=True,
        ai_player=PLAYER_X,
        human_player=PLAYER_O,
        candidate_limit=12,
    )
    assert move_ai in [(7, 2), (7, 7)], f"Expected winning move at (7, 2) or (7, 7), got {move_ai}"
    assert score_ai == SCORE_FIVE, f"Expected exact {SCORE_FIVE}, got {score_ai}"

    # Case 2: Human thắng khi AI có open three
    b_hu = empty_board()
    for c in range(3, 7):
        b_hu[7][c] = PLAYER_O   # 4 quân Human
    for c in range(3, 6):
        b_hu[3][c] = PLAYER_X   # AI có 3 quân mở (ai_total = 100,000)

    move_hu, score_hu = minimax(
        b_hu,
        depth=0,
        alpha=-INF,
        beta=INF,
        is_maximizing=False,
        ai_player=PLAYER_X,
        human_player=PLAYER_O,
        candidate_limit=12,
    )
    assert move_hu in [(7, 2), (7, 7)], f"Expected block/threat move at (7, 2) or (7, 7), got {move_hu}"
    assert score_hu == -SCORE_FIVE, f"Expected exact {-SCORE_FIVE}, got {score_hu}"


def test_incremental_delta_matches_evaluate_board_across_random_boards():
    """
    Regression test: Xác minh tính tương đương toán học giữa cập nhật vi phân 4 đường
    (Incremental 4-line delta) và đánh giá toàn bàn cờ (evaluate_board).
    Với 50 ván cờ ngẫu nhiên (10 đến 30 quân cờ mỗi ván) và các nước đi ứng viên:
    evaluate_board(b + move) phải bằng chính xác giá trị tính bằng vi phân
    ai_total = base_ai - old_ai + new_ai
    hu_total = base_hu - old_hu + new_hu
    score = int(ai_total - 1.2 * hu_total).
    """
    import random
    from app.ai.evaluator import get_board_raw_scores, get_cell_lines_scores
    from app.ai.move_generator import get_candidate_moves

    rng = random.Random(42)  # Cố định seed để tái lập 100%

    for _ in range(50):
        b = empty_board()
        num_stones = rng.randint(10, 30)
        placed = set()
        for i in range(num_stones):
            r, c = rng.randint(0, BOARD_SIZE - 1), rng.randint(0, BOARD_SIZE - 1)
            if (r, c) not in placed:
                b[r][c] = PLAYER_X if (i % 2 == 0) else PLAYER_O
                placed.add((r, c))

        base_ai, base_hu = get_board_raw_scores(b)
        candidates = get_candidate_moves(b, radius=2)

        for r, c in candidates[:10]:
            old_ai, old_hu = get_cell_lines_scores(b, r, c)

            for player in (PLAYER_X, PLAYER_O):
                b[r][c] = player
                expected_eval = evaluate_board(b, ai_player=PLAYER_X, human_player=PLAYER_O)
                new_ai, new_hu = get_cell_lines_scores(b, r, c)
                b[r][c] = EMPTY

                ai_total = base_ai - old_ai + new_ai
                hu_total = base_hu - old_hu + new_hu
                incremental_eval = int(ai_total - 1.2 * hu_total)

                assert incremental_eval == expected_eval, (
                    f"Mismatch at ({r}, {c}) for player {player}: "
                    f"incremental={incremental_eval} != expected={expected_eval}"
                )


def test_cumulative_open_fours_do_not_trigger_false_positive_terminal_win():  # noqa: C901
    """
    Regression test: Kiểm chứng giả thuyết điểm dồn tích các pattern EPPPPE.
    Khi bàn cờ chứa nhiều chuỗi 4 quân mở (10 chuỗi EPPPPE độc lập trên 10 hàng riêng biệt)
    khiến tổng heuristic raw score toàn bàn cờ (base_ai) đạt hoặc vượt SCORE_FIVE (100,000,000):
    1. Xác nhận fixture KHÔNG có bất kỳ chuỗi 5 quân liên tiếp nào theo mọi hướng
       (ngang, dọc, chéo chính, chéo phụ).
    2. Điểm thô cục bộ (new_ai) của các nước đi không tạo 5 quân không được vượt SCORE_FIVE.
    3. minimax() KHÔNG ĐƯỢC trả về (None, SCORE_FIVE) (false positive coi ván đấu đã kết thúc sẵn),
       mà phải tìm và trả về một nước đi hợp lệ tạo chuỗi 5 thực tế.
    """
    b = empty_board()
    # 10 chuỗi 4 quân mở (EPPPPE = .XXXX.) độc lập trên 10 hàng riêng biệt:
    # 8 hàng chẵn (0, 2, 4, 6, 8, 10, 12, 14) đặt tại các cột 1..4
    for r in [0, 2, 4, 6, 8, 10, 12, 14]:
        for c in range(1, 5):
            b[r][c] = PLAYER_X

    # 2 hàng lẻ (1, 3) đặt tại các cột 8..11
    for r in [1, 3]:
        for c in range(8, 12):
            b[r][c] = PLAYER_X

    # BƯỚC 1: Xác minh hình học của fixture — tối đa chỉ 4 quân liên tiếp trên mọi hướng
    def _get_max_consecutive(board, player):
        max_len = 0
        for r in range(BOARD_SIZE):
            cur = 0
            for c in range(BOARD_SIZE):
                cur = cur + 1 if board[r][c] == player else 0
                max_len = max(max_len, cur)
        for c in range(BOARD_SIZE):
            cur = 0
            for r in range(BOARD_SIZE):
                cur = cur + 1 if board[r][c] == player else 0
                max_len = max(max_len, cur)
        for k in range(-BOARD_SIZE + 1, BOARD_SIZE):
            cur = 0
            for r in range(BOARD_SIZE):
                c = r - k
                if 0 <= c < BOARD_SIZE:
                    cur = cur + 1 if board[r][c] == player else 0
                    max_len = max(max_len, cur)
        for k in range(BOARD_SIZE * 2 - 1):
            cur = 0
            for r in range(BOARD_SIZE):
                c = k - r
                if 0 <= c < BOARD_SIZE:
                    cur = cur + 1 if board[r][c] == player else 0
                    max_len = max(max_len, cur)
        return max_len

    assert _get_max_consecutive(b, PLAYER_X) == 4, "Fixture chỉ được có tối đa 4 quân liên tiếp"
    assert _get_max_consecutive(b, PLAYER_O) == 0

    # BƯỚC 2: Xác nhận tổng raw score toàn bàn cờ >= SCORE_FIVE dù chưa có chuỗi 5
    base_p1, base_p2 = get_board_raw_scores(b)
    assert base_p1 >= SCORE_FIVE, f"Expected cumulative raw score >= {SCORE_FIVE}, got {base_p1}"

    # BƯỚC 3: minimax không được coi bàn cờ là đã kết thúc sẵn (move=None)
    # mà phải duyệt và trả về nước đi thực tế hoàn tất chuỗi 5
    move, score = minimax(
        b,
        depth=1,
        alpha=-INF,
        beta=INF,
        is_maximizing=True,
        ai_player=PLAYER_X,
        human_player=PLAYER_O,
        candidate_limit=12,
    )
    assert move is not None, "minimax không được trả về None khi chưa có ai có chuỗi 5 trên bàn cờ"
    assert score == SCORE_FIVE

    # Kiểm tra nước đi trả về thực sự tạo thành chuỗi >= 5
    b[move[0]][move[1]] = PLAYER_X
    assert _get_max_consecutive(b, PLAYER_X) >= 5, f"Nước đi {move} phải tạo chuỗi >= 5 thực tế"
    b[move[0]][move[1]] = EMPTY


def test_cumulative_open_fours_opponent_does_not_cause_false_terminal_loss():
    """
    Regression test: Khi đối thủ có tổng điểm cộng dồn >= SCORE_FIVE nhưng chưa có chuỗi 5,
    minimax tại lượt của AI (is_maximizing=True) không được coi là đã thua sẵn (None, -SCORE_FIVE),
    mà phải tiếp tục tìm nước đi chiến thuật hợp lệ (move is not None).
    """
    b = empty_board()
    for r in [0, 2, 4, 6, 8, 10, 12, 14]:
        for c in range(1, 5):
            b[r][c] = PLAYER_O
    for r in [1, 3]:
        for c in range(8, 12):
            b[r][c] = PLAYER_O

    base_p1, base_p2 = get_board_raw_scores(b)
    assert base_p2 >= SCORE_FIVE, f"Expected opponent raw score >= {SCORE_FIVE}, got {base_p2}"

    move, score = minimax(
        b,
        depth=1,
        alpha=-INF,
        beta=INF,
        is_maximizing=True,
        ai_player=PLAYER_X,
        human_player=PLAYER_O,
        candidate_limit=12,
    )
    assert move is not None, "AI không được trả về None đầu hàng khi đối thủ chưa thực sự có chuỗi 5"
