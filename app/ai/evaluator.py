from typing import List, Tuple
from functools import lru_cache

BOARD_SIZE = 15
EMPTY = 0

# Trọng số Heuristic
SCORE_FIVE = 100_000_000
SCORE_OPEN_FOUR = 10_000_000
SCORE_BLOCKED_FOUR = 500_000
SCORE_OPEN_THREE = 100_000
SCORE_BLOCKED_THREE = 5_000
SCORE_OPEN_TWO = 500
SCORE_BLOCKED_TWO = 50

# Bảng tra ký tự nhanh tránh cấp phát chuỗi thủ công
_MAP_P1 = ('E', 'P', 'O')
_MAP_P2 = ('E', 'O', 'P')

# Tọa độ các đường thẳng (cột, đường chéo chính, đường chéo phụ) có độ dài >= 5
# Được tính toán tĩnh một lần để loại bỏ tính toán lặp và cấp phát comprehension động
_COLUMN_COORDS: Tuple[Tuple[Tuple[int, int], ...], ...] = tuple(
    tuple((r, c) for r in range(BOARD_SIZE)) for c in range(BOARD_SIZE)
)

_DIAGONAL_MAIN_COORDS: Tuple[Tuple[Tuple[int, int], ...], ...] = tuple(
    tuple((r, r - k) for r in range(BOARD_SIZE) if 0 <= r - k < BOARD_SIZE)
    for k in range(-BOARD_SIZE + 1, BOARD_SIZE)
    if sum(1 for r in range(BOARD_SIZE) if 0 <= r - k < BOARD_SIZE) >= 5
)

_DIAGONAL_ANTI_COORDS: Tuple[Tuple[Tuple[int, int], ...], ...] = tuple(
    tuple((r, k - r) for r in range(BOARD_SIZE) if 0 <= k - r < BOARD_SIZE)
    for k in range(BOARD_SIZE * 2 - 1)
    if sum(1 for r in range(BOARD_SIZE) if 0 <= k - r < BOARD_SIZE) >= 5
)

_ALL_NON_ROW_COORDS = _COLUMN_COORDS + _DIAGONAL_MAIN_COORDS + _DIAGONAL_ANTI_COORDS

# Bảng tra tĩnh các đường trong _ALL_NON_ROW_COORDS đi qua ô (r, c)
_CELL_NON_ROW_LINES: Tuple[Tuple[Tuple[Tuple[int, int], ...], ...], ...] = tuple(
    tuple(
        tuple(coords for coords in _ALL_NON_ROW_COORDS if (r, c) in coords)
        for c in range(BOARD_SIZE)
    )
    for r in range(BOARD_SIZE)
)


def _eval_line_pattern(line: Tuple[int, ...] | List[int], player: int, p_count: int) -> int:  # noqa: C901
    """
    Đánh giá pattern trên chuỗi đã biết có p_count >= 2 quân của player.
    """
    m = _MAP_P1 if player == 1 else _MAP_P2 if player == 2 else None
    if m is not None:
        s = "".join([m[c] for c in line])
    else:
        chars = []
        for cell in line:
            if cell == player:
                chars.append('P')
            elif cell == EMPTY:
                chars.append('E')
            else:
                chars.append('O')
        s = "".join(chars)

    # 1. Chuỗi 5 quân
    if p_count >= 5 and "PPPPP" in s:
        return SCORE_FIVE

    score = 0
    # 2. 4 quân
    if p_count >= 4:
        if "EPPPPE" in s:
            score += SCORE_OPEN_FOUR
        if "OPPPPE" in s or "EPPPPO" in s:
            score += SCORE_BLOCKED_FOUR
        if "PPPEP" in s or "PEPPP" in s or "PPEPP" in s:
            score += SCORE_BLOCKED_FOUR

    # 3. 3 quân
    if p_count >= 3:
        if "EPPPE" in s or "EPEPPE" in s or "EPPEPE" in s:
            score += SCORE_OPEN_THREE
        if "OPPPE" in s or "EPPPO" in s:
            score += SCORE_BLOCKED_THREE

    # 4. 2 quân
    if "EEPPEE" in s or "EEPEPE" in s:
        score += SCORE_OPEN_TWO
    elif "OPPE" in s or "EPPO" in s:
        score += SCORE_BLOCKED_TWO

    return score


@lru_cache(maxsize=65536)
def _eval_tuple_both(line: Tuple[int, ...]) -> Tuple[int, int]:
    """
    Đánh giá đồng thời điểm số cho cả Player 1 và Player 2 trên một dòng dạng tuple.
    Sử dụng LRU cache để tái sử dụng kết quả cho các dòng lặp lại.
    """
    p1_cnt = line.count(1)
    p2_cnt = line.count(2)
    s1 = _eval_line_pattern(line, 1, p1_cnt) if p1_cnt >= 2 else 0
    s2 = _eval_line_pattern(line, 2, p2_cnt) if p2_cnt >= 2 else 0
    return (s1, s2)


def get_board_raw_scores(board: List[List[int]]) -> Tuple[int, int]:
    """
    Tính tổng điểm thô (p1_score, p2_score) của toàn bộ 72 đường trên bàn cờ.
    """
    p1_total = 0
    p2_total = 0
    for r in range(BOARD_SIZE):
        s1, s2 = _eval_tuple_both(tuple(board[r]))
        p1_total += s1
        p2_total += s2
    for coords in _ALL_NON_ROW_COORDS:
        s1, s2 = _eval_tuple_both(tuple(board[r][c] for r, c in coords))
        p1_total += s1
        p2_total += s2
    return (p1_total, p2_total)


def get_cell_lines_scores(board: List[List[int]], r: int, c: int) -> Tuple[int, int]:
    """
    Tính tổng điểm thô (p1_score, p2_score) của tối đa 4 đường đi qua ô (r, c):
    1 hàng ngang r và tối đa 3 đường (1 cột, tối đa 2 đường chéo) trong _CELL_NON_ROW_LINES.
    """
    p1_sum, p2_sum = _eval_tuple_both(tuple(board[r]))
    for coords in _CELL_NON_ROW_LINES[r][c]:
        s1, s2 = _eval_tuple_both(tuple(board[nr][nc] for nr, nc in coords))
        p1_sum += s1
        p2_sum += s2
    return (p1_sum, p2_sum)


def evaluate_line(line: List[int], player: int) -> int:
    """
    Đánh giá điểm của một dãy ô (chuỗi 1D) theo các pattern cờ Caro.
    """
    if len(line) < 5:
        return 0

    p_count = line.count(player)
    if p_count < 2:
        return 0

    return _eval_line_pattern(line, player, p_count)


def evaluate_board(board: List[List[int]], ai_player: int, human_player: int) -> int:
    """
    Quét toàn bộ bàn cờ theo 4 hướng và tính tổng điểm heuristic.
    """
    if {ai_player, human_player} == {1, 2}:
        p1_score, p2_score = get_board_raw_scores(board)
        ai_score = p1_score if ai_player == 1 else p2_score
        human_score = p2_score if ai_player == 1 else p1_score
        return int(ai_score - 1.2 * human_score)

    ai_score = 0
    human_score = 0

    # 1. Hàng ngang
    for r in range(BOARD_SIZE):
        line = board[r]
        ai_cnt = line.count(ai_player)
        hu_cnt = line.count(human_player)
        if ai_cnt >= 2:
            ai_score += _eval_line_pattern(line, ai_player, ai_cnt)
        if hu_cnt >= 2:
            human_score += _eval_line_pattern(line, human_player, hu_cnt)

    # 2. Hàng dọc & 3, 4. Đường chéo (sử dụng tọa độ tĩnh đã tính trước)
    for coords in _ALL_NON_ROW_COORDS:
        line = [board[r][c] for r, c in coords]
        ai_cnt = line.count(ai_player)
        hu_cnt = line.count(human_player)
        if ai_cnt >= 2:
            ai_score += _eval_line_pattern(line, ai_player, ai_cnt)
        if hu_cnt >= 2:
            human_score += _eval_line_pattern(line, human_player, hu_cnt)

    return int(ai_score - 1.2 * human_score)


def check_win_at(board: List[List[int]], r: int, c: int, player: int) -> bool:
    """
    Kiểm tra xem quân cờ của player tại ô (r, c) có tạo thành chuỗi >= 5 quân
    liên tiếp theo một trong 4 hướng (ngang, dọc, 2 đường chéo) hay không.
    Xác định 100% bằng hình học thực tế, không dựa vào tổng điểm heuristic.
    """
    for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
        count = 1
        nr, nc = r + dr, c + dc
        while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == player:
            count += 1
            nr += dr
            nc += dc
        nr, nc = r - dr, c - dc
        while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == player:
            count += 1
            nr -= dr
            nc -= dc
        if count >= 5:
            return True
    return False


def has_five_in_a_row(board: List[List[int]], player: int) -> bool:
    """
    Kiểm tra xem player đã có sẵn ít nhất một chuỗi >= 5 quân liên tiếp trên bàn cờ hay chưa.
    Chỉ kiểm tra từ các quân cờ hiện có, không phụ thuộc vào heuristic score.
    """
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == player:
                for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                    pr, pc = r - dr, c - dc
                    if 0 <= pr < BOARD_SIZE and 0 <= pc < BOARD_SIZE and board[pr][pc] == player:
                        continue
                    count = 1
                    nr, nc = r + dr, c + dc
                    while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == player:
                        count += 1
                        if count >= 5:
                            return True
                        nr += dr
                        nc += dc
    return False
