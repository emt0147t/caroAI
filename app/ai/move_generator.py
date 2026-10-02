from typing import List, Tuple, Set

BOARD_SIZE = 15
EMPTY = 0

def get_candidate_moves(
    board: List[List[int]], 
    radius: int = 1
) -> List[Tuple[int, int]]:
    """
    Sinh danh sách các ô đi tiềm năng dựa trên bán kính lân cận của các quân hiện có.
    - Nếu bàn cờ trống: trả về ô trung tâm (7, 7).
    - Ngược lại: trả về các ô EMPTY nằm trong phạm vi Chebyshev <= radius so với các quân đã đánh.
    """
    occupied_cells: List[Tuple[int, int]] = []
    
    # Bước 1: Thu thập tất cả các ô đã có quân
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] != EMPTY:
                occupied_cells.append((r, c))
                
    # Nếu bàn cờ rỗng hoàn toàn, trả về vị trí trung tâm
    if not occupied_cells:
        center = BOARD_SIZE // 2
        return [(center, center)]
        
    candidate_set: Set[Tuple[int, int]] = set()
    
    # Bước 2: Quét xung quanh các ô có quân theo bán kính radius
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