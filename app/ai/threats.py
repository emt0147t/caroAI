"""Exact >=5 and continuous-four geometry on a padded 15x15 bitboard.

The extra column prevents horizontal/diagonal wraparound. All tactical move masks
are intersected with real empty cells. No global mutable search state or randomness.
"""
from itertools import combinations

STRIDE = 16
FULL = sum(1 << (r * STRIDE + c) for r in range(15) for c in range(15))
DIRECTIONS = (1, 16, 17, 15)
STARTS = {}
for _dr, _dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
    STARTS[_dr * STRIDE + _dc] = sum(
        1 << (r * STRIDE + c) for r in range(15) for c in range(15)
        if 0 <= r + 4 * _dr < 15 and 0 <= c + 4 * _dc < 15
    )
GAPS = tuple((i, j, tuple(k for k in range(5) if k not in (i, j)))
             for i, j in combinations(range(5), 2))


def bit(move):
    return 1 << (move[0] * STRIDE + move[1])


def cells(mask):
    while mask:
        low = mask & -mask
        index = low.bit_length() - 1
        yield index // STRIDE, index % STRIDE
        mask ^= low


def encode(board):
    stones = [0, 0, 0]
    for r, row in enumerate(board):
        for c, value in enumerate(row):
            if value:
                stones[value] |= 1 << (r * STRIDE + c)
    return stones


def winning_cells(own, occupied):
    """Every empty cell making >=5; includes gaps, edges, overlines and crosses."""
    result = 0
    for d in DIRECTIONS:
        four = own & (own >> d) & (own >> (2 * d)) & (own >> (3 * d))
        result |= (four >> d) | (four << (4 * d))
        result |= (own & (own >> (2 * d)) & (own >> (3 * d)) & (own >> (4 * d))) << d
        result |= (own & (own >> d) & (own >> (3 * d)) & (own >> (4 * d))) << (2 * d)
        result |= (own & (own >> d) & (own >> (2 * d)) & (own >> (4 * d))) << (3 * d)
    return result & (FULL ^ occupied)


def four_moves(own, occupied):
    """Moves that create at least one next-turn win from an unblocked triple."""
    empty = FULL ^ occupied
    result = 0
    for d in DIRECTIONS:
        for i, j, filled in GAPS:
            starts = STARTS[d] & (empty >> (i * d)) & (empty >> (j * d))
            for k in filled:
                starts &= own >> (k * d)
            result |= (starts << (i * d)) | (starts << (j * d))
    return result & empty


def fork_moves(own, occupied):
    """Exact moves creating two distinct next-turn winning cells.

    Callers must separately check whether the opponent can win immediately.
    """
    result = 0
    for move in cells(four_moves(own, occupied)):
        mark = bit(move)
        if winning_cells(own | mark, occupied | mark).bit_count() >= 2:
            result |= mark
    return result


def neighborhood(occupied, radius):
    if not occupied:
        return bit((7, 7))
    result = occupied
    for _ in range(radius):
        current = result
        for d in DIRECTIONS:
            result |= (current << d) | (current >> d)
        result &= FULL
    return result & (FULL ^ occupied)
