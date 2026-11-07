"""Bounded continuous-four diagnosis; every positive line has a domain certificate.

NO_PROOF means only no win in this restricted forcing model/horizon. It is never
called a game-theoretic safe position. UNKNOWN is separate from a refuted proof.
"""
from dataclasses import dataclass

from app.ai.threats import bit, cells, encode, four_moves, winning_cells
from benchmarks.competitive.corpus import wins


@dataclass(frozen=True)
class Proof:
    status: str
    line: tuple = ()


class Solver:
    def __init__(self, max_nodes=30000):
        self.remaining_nodes = max_nodes
        self.cache = {}

    def solve(self, own, enemy, remaining):
        key = own, enemy, remaining
        if key in self.cache:
            return self.cache[key]
        if self.remaining_nodes <= 0:
            return Proof('UNKNOWN')
        self.remaining_nodes -= 1
        result = self._visit(own, enemy, remaining)
        if result.status != 'UNKNOWN':
            self.cache[key] = result
        return result

    def _visit(self, own, enemy, remaining):
        occupied = own | enemy
        immediate = winning_cells(own, occupied)
        if immediate:
            return Proof('PROVEN', (('win', next(cells(immediate))),))
        if remaining <= 0:
            return Proof('NO_PROOF')
        unknown = False
        for move in cells(four_moves(own, occupied)):
            mark = bit(move)
            attack, occupied_next = own | mark, occupied | mark
            if winning_cells(enemy, occupied_next):
                continue
            threats = winning_cells(attack, occupied_next)
            if threats.bit_count() >= 2:
                return Proof('PROVEN', (('fork', move),))
            reply = next(cells(threats))
            child = self.solve(attack, enemy | bit(reply), remaining - 1)
            if child.status == 'PROVEN':
                return Proof('PROVEN', (('force', move, reply),) + child.line)
            unknown |= child.status == 'UNKNOWN'
        return Proof('UNKNOWN' if unknown else 'NO_PROOF')


def prove(board, player, depth=3, max_nodes=30000):
    stones = encode(board)
    return Solver(max_nodes).solve(stones[player], stones[3 - player], depth)


def verify_certificate(board, player, line):
    """Verify using domain-rule exhaustive win scans, no candidate threat code."""
    board = [row[:] for row in board]
    for index, step in enumerate(line):
        kind, move, *reply = step
        move = tuple(move)
        r, c = move
        assert board[r][c] == 0
        if kind == 'win':
            assert move in wins(board, player) and index == len(line) - 1
            return True
        board[r][c] = player
        assert not wins(board, 3 - player), 'Defender has a counter-win'
        threats = wins(board, player)
        if kind == 'fork':
            assert len(threats) >= 2 and index == len(line) - 1
            return True
        assert kind == 'force' and len(reply) == 1 and threats == {tuple(reply[0])}
        r, c = reply[0]
        assert board[r][c] == 0
        board[r][c] = 3 - player
    raise AssertionError('Incomplete forcing certificate')
