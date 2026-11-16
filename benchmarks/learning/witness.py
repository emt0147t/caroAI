"""Certify an observed attack plan against every reply at its quiet setup.

A refutation only defeats this demonstrated plan. It never proves that the
alternative wins the full game or that no other human attack exists.
"""
from app.ai.threats import FULL, bit, cells, encode, winning_cells
from benchmarks.competitive.corpus import wins
from benchmarks.learning.certificates import Solver, verify_certificate


def _line_result(solver, own, enemy, depth):
    result = solver.solve(own, enemy, depth)
    return result.status, {'kind': 'vcf', 'line': result.line}


def _plan(solver, own, enemy, plan, depth):
    if not plan or winning_cells(own, own | enemy):
        return _line_result(solver, own, enemy, depth)
    move, *remaining = plan
    mark, occupied = bit(move), own | enemy
    if occupied & mark:
        return 'NO_PROOF', {}
    attack, occupied = own | mark, occupied | mark
    if winning_cells(enemy, occupied):
        return 'NO_PROOF', {}
    threats = winning_cells(attack, occupied)
    if threats.bit_count() >= 2:
        return 'PROVEN', {'kind': 'vcf', 'line': (('fork', move),)}
    if threats:
        reply = next(cells(threats))
        status, child = _plan(solver, attack, enemy | bit(reply), remaining, depth)
        return status, {'kind': 'forced', 'attack': move, 'reply': reply, 'next': child}
    responses, unknown = [], False
    for reply in cells(FULL ^ occupied):
        status, child = _line_result(solver, attack, enemy | bit(reply), depth)
        if status == 'NO_PROOF':
            return 'NO_PROOF', {}
        unknown |= status == 'UNKNOWN'
        responses.append({'reply': reply, 'next': child})
    if not responses:
        return 'NO_PROOF', {}
    return ('UNKNOWN' if unknown else 'PROVEN'), {'kind': 'all_replies', 'attack': move, 'responses': responses}


def prove_plan(board, player, plan, depth=3, max_nodes=30000):
    stones = encode(board)
    return _plan(Solver(max_nodes), stones[player], stones[3 - player], list(plan), depth)


def verify_plan(board, player, certificate):
    if certificate['kind'] == 'vcf':
        return verify_certificate(board, player, certificate['line'])
    board = [row[:] for row in board]
    r, c = certificate['attack']
    assert board[r][c] == 0
    board[r][c] = player
    assert not wins(board, 3 - player)
    threats = wins(board, player)
    if certificate['kind'] == 'forced':
        reply = tuple(certificate['reply'])
        assert threats == {reply}
        board[reply[0]][reply[1]] = 3 - player
        return verify_plan(board, player, certificate['next'])
    assert certificate['kind'] == 'all_replies' and not threats
    legal = {(r, c) for r in range(15) for c in range(15) if not board[r][c]}
    replies = [tuple(record['reply']) for record in certificate['responses']]
    assert len(replies) == len(set(replies)) and set(replies) == legal
    for record in certificate['responses']:
        child = [row[:] for row in board]
        r, c = record['reply']
        child[r][c] = 3 - player
        verify_plan(child, player, record['next'])
    return True
