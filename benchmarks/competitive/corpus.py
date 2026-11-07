"""Composed tactical positions; coordinates are zero-based, unrestricted >=5 rules.

Fixtures are specifications, independent of candidate search and its threat detector.
The independent oracle uses the authoritative game-domain win implementation.
"""
from dataclasses import dataclass

from app.domain.game_rules import GameRules
from app.domain.game_state import GameState, Player


@dataclass(frozen=True)
class Case:
    name: str
    category: str
    stones: tuple
    player: int
    expected_moves: frozenset
    outcome: str

    def board(self):
        board = [[0] * 15 for _ in range(15)]
        for r, c, p in self.stones:
            assert board[r][c] == 0
            board[r][c] = p
        return board


def wins(board, player):
    """Brute-force domain-rule oracle; deliberately independent of AI bitboards."""
    state = GameState()
    state.board = [['EMPTY' if p == 0 else 'X' if p == 1 else 'O' for p in row] for row in board]
    who = Player.X if player == 1 else Player.O
    result = set()
    for r in range(15):
        for c in range(15):
            if board[r][c]:
                continue
            state.board[r][c] = who.value
            if GameRules.has_won(state, r, c, who):
                result.add((r, c))
            state.board[r][c] = 'EMPTY'
    return result


def fork_moves(board, player):
    result = set()
    for r in range(15):
        for c in range(15):
            if board[r][c]:
                continue
            board[r][c] = player
            try:
                if len(wins(board, player)) >= 2 and not wins(board, 3 - player):
                    result.add((r, c))
            finally:
                board[r][c] = 0
    return result


def base_cases():
    cases = []

    def add(name, category, own, other, moves, outcome, player=1):
        stones = tuple((r, c, player) for r, c in own) + tuple((r, c, 3 - player) for r, c in other)
        cases.append(Case(name, category, stones, player, frozenset(moves), outcome))

    add('win_open_four', 'immediate_win', [(7, c) for c in range(4, 8)], [],
        [(7, 3), (7, 8)], 'win_now')
    add('win_broken_four', 'broken_four', [(7, c) for c in (4, 5, 7, 8)], [], [(7, 6)], 'win_now')
    add('win_edge', 'edge', [(0, c) for c in range(4)], [], [(0, 4)], 'win_now')
    add('win_diagonal', 'immediate_win', [(r, r) for r in range(4, 8)], [],
        [(3, 3), (8, 8)], 'win_now')
    add('block_unique', 'forced_block', [(7, 3)], [(7, c) for c in range(4, 8)],
        [(7, 8)], 'block_unique')
    add('block_gap', 'broken_four', [], [(7, c) for c in (4, 5, 7, 8)], [(7, 6)], 'block_unique')
    add('block_edge', 'edge', [], [(0, c) for c in range(4)], [(0, 4)], 'block_unique')
    add('win_before_block', 'heuristic_trap', [(3, c) for c in range(4)],
        [(7, c) for c in range(4, 8)], [(3, 4)], 'win_now')
    add('extend_open_three', 'open_four', [(7, c) for c in (5, 6, 7)], [],
        [(7, 4), (7, 8)], 'create_fork')
    add('fill_broken_three', 'broken_three', [(7, c) for c in (5, 6, 8)], [],
        [(7, 7)], 'create_fork')
    cross = [(7, 4), (7, 5), (7, 6), (4, 7), (5, 7), (6, 7)]
    closed = [(7, 3), (3, 7)]
    add('cross_double_four', 'double_threat', cross, closed, [(7, 7)], 'create_fork')
    add('defend_cross_fork', 'layered_defense', closed, cross,
        [(7, 7), (7, 8), (8, 7)], 'avoid_fork')
    return cases


def transform_cell(cell, rotation, reflected):
    r, c = cell
    if reflected:
        c = 14 - c
    for _ in range(rotation):
        r, c = c, 14 - r
    return r, c


def cases(expanded=True):
    for case in base_cases():
        for rotation in range(4 if expanded else 1):
            for reflected in range(2 if expanded else 1):
                for swapped in range(2 if expanded else 1):
                    stones = tuple((*transform_cell((r, c), rotation, reflected), 3 - p if swapped else p)
                                   for r, c, p in case.stones)
                    answers = frozenset(transform_cell(m, rotation, reflected) for m in case.expected_moves)
                    yield Case(f'{case.name}-r{rotation}-f{reflected}-c{swapped}', case.category, stones,
                               3 - case.player if swapped else case.player, answers, case.outcome)
