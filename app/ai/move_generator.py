from typing import List, Tuple, Set

BOARD_SIZE = 15
EMPTY = 0


def get_candidate_moves(
    board: List[List[int]],
    radius: int = 1
) -> List[Tuple[int, int]]:
    """
    Sinh danh sÃ¡ch cÃ¡c Ã´ Ä‘i tiá»m nÄƒng dá»±a trÃªn bÃ¡n kÃ­nh lÃ¢n cáº­n cá»§a cÃ¡c quÃ¢n hiá»‡n cÃ³.
    - Náº¿u bÃ n cá» trá»‘ng: tráº£ vá» Ã´ trung tÃ¢m (7, 7).
    - NgÆ°á»£c láº¡i: tráº£ vá» cÃ¡c Ã´ EMPTY náº±m trong pháº¡m vi Chebyshev <= radius so vá»›i cÃ¡c quÃ¢n Ä‘Ã£ Ä‘Ã¡nh.
    """
    occupied_cells: List[Tuple[int, int]] = []

    # BÆ°á»›c 1: Thu tháº­p táº¥t cáº£ cÃ¡c Ã´ Ä‘Ã£ cÃ³ quÃ¢n
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] != EMPTY:
                occupied_cells.append((r, c))

    # Náº¿u bÃ n cá» rá»—ng hoÃ n toÃ n, tráº£ vá» vá»‹ trÃ­ trung tÃ¢m
    if not occupied_cells:
        center = BOARD_SIZE // 2
        return [(center, center)]

    candidate_set: Set[Tuple[int, int]] = set()

    # BÆ°á»›c 2: QuÃ©t xung quanh cÃ¡c Ã´ cÃ³ quÃ¢n theo bÃ¡n kÃ­nh radius
    for r, c in occupied_cells:
        r_min = max(0, r - radius)
        r_max = min(BOARD_SIZE - 1, r + radius)
        c_min = max(0, c - radius)
        c_max = min(BOARD_SIZE - 1, c + radius)

        for nr in range(r_min, r_max + 1):
            for nc in range(c_min, c_max + 1):
                if board[nr][nc] == EMPTY:
                    candidate_set.add((nr, nc))

    return list(candidate_set)
