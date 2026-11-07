"""Offline on-policy Monte Carlo actor/critic from complete self-play games.

Terminal rewards are +1/-1/0 by side. Updates occur only between batches; both
sides use the frozen actor within a batch. This is a small RL baseline, not AlphaZero.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from app.domain.game_rules import GameRules
from app.domain.game_state import GameState, Player
from benchmarks.competitive.metrics import provenance
from benchmarks.competitive.tournament import opening
from benchmarks.learning.model import Model, actor_options, probabilities
from benchmarks.learning.records import board_key, numeric_board


def episode(model, rng, seed, temperature):
    state = GameState()
    prefix = opening(seed)
    for move in prefix:
        GameRules.apply_move(state, *move)
    steps, moves, early_keys = [], [], []
    while state.status.value == 'IN_PROGRESS':
        board = numeric_board(state)
        if state.move_count <= 8:
            early_keys.append(board_key(board, 1))
        player = 1 if state.current_player == Player.X else 2
        options, features, forced, value = actor_options(board, player, model)
        probs = probabilities(model.logits(features), temperature)
        action = int(rng.choice(len(options), p=probs))
        gradient = np.zeros_like(model.policy) if forced else (features[action] - probs @ features) / temperature
        steps.append((player, value, gradient, float(model.predict(value))))
        move = options[action]
        GameRules.apply_move(state, *move)
        moves.append({'ply': state.move_count, 'player': player, 'row': move[0], 'col': move[1]})
    winner = 1 if state.winner == Player.X else 2 if state.winner == Player.O else 0
    return steps, {'seed': seed, 'opening': prefix, 'moves': moves, 'terminal': state.status.value,
                   'winner': winner, 'root_canonical_key': board_key_from_prefix(prefix),
                   'early_position_keys': early_keys}


def board_key_from_prefix(prefix):
    state = GameState()
    for move in prefix:
        GameRules.apply_move(state, *move)
    return board_key(numeric_board(state), 1)


def update(model, episodes, learning_rate):
    policy_grad, value_grad = np.zeros_like(model.policy), np.zeros_like(model.value)
    count, errors = 0, []
    for steps, record in episodes:
        for player, features, gradient, prediction in steps:
            reward = 0 if record['winner'] == 0 else (1 if record['winner'] == player else -1)
            advantage = reward - prediction
            policy_grad += advantage * gradient
            value_grad += advantage * (1 - prediction * prediction) * features
            errors.append(advantage * advantage)
            count += 1
    if not count:
        raise ValueError('No completed training positions')
    model.policy = np.clip(model.policy + learning_rate * policy_grad / count, -10, 10)
    model.value = np.clip(model.value + learning_rate * value_grad / count, -10, 10)
    return float(np.mean(errors))


def train(args):
    if args.games < 1 or args.batch < 1 or not 0 < args.learning_rate <= 1:
        raise ValueError('Positive game/batch counts and a learning rate in (0,1] required')
    args.output.mkdir(parents=True, exist_ok=True)
    model, rng = Model(), np.random.default_rng(args.seed)
    initial_digest = model.digest()
    model.save(args.output / 'initial-model.json')
    reserved = {board_key_from_prefix(opening(args.evaluation_seed + i)) for i in range(args.evaluation_pairs)}
    if args.reserved_openings:
        reserved.update(json.loads(args.reserved_openings.read_text()))
    episodes, batch, errors, seed, excluded = [], [], [], args.opening_seed, 0
    while len(episodes) < args.games:
        prefix = opening(seed)
        # Longer unique starts; no canonical overlap with reserved evaluation roots.
        if len(prefix) < 6 or board_key_from_prefix(prefix) in reserved:
            seed += 1
            continue
        steps, record = episode(model, rng, seed, args.temperature)
        seed += 1
        if reserved.intersection(record['early_position_keys']):
            excluded += 1
            continue
        record['actor_model_sha256'] = model.digest()
        episodes.append(record)
        batch.append((steps, record))
        if len(batch) == args.batch or len(episodes) == args.games:
            errors.append(update(model, batch, args.learning_rate))
            batch = []
        if len(episodes) % 20 == 0:
            print(f'Complete self-play games: {len(episodes)}/{args.games}', flush=True)
    raw = ''.join(json.dumps(row, separators=(',', ':')) + '\n' for row in episodes)
    (args.output / 'selfplay.jsonl').write_text(raw)
    environment = provenance(Path(__file__).resolve().parents[2])
    source = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob('*.py')):
        source.update(path.name.encode())
        source.update(path.read_bytes())
    environment['learning_source_content_sha256'] = source.hexdigest()
    manifest = {'selfplay_sha256': hashlib.sha256(raw.encode()).hexdigest(),
                'training_root_keys': sorted({g['root_canonical_key'] for g in episodes}),
                'reserved_root_keys': sorted(reserved),
                'training_games': len(episodes), 'completed_excluded_games': excluded,
                'evaluation_seed': args.evaluation_seed, 'evaluation_pairs': args.evaluation_pairs}
    manifest_raw = json.dumps(manifest, sort_keys=True, indent=2) + '\n'
    (args.output / 'training-manifest.json').write_text(manifest_raw)
    model.metadata = {'training_games': len(episodes), 'training_seed': args.seed,
                      'protocol': {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
                      'selfplay_sha256': hashlib.sha256(raw.encode()).hexdigest(),
                      'reserved_roots_sha256': hashlib.sha256(json.dumps(sorted(reserved)).encode()).hexdigest(),
                      'initial_model_sha256': initial_digest,
                      'training_manifest_sha256': hashlib.sha256(manifest_raw.encode()).hexdigest(),
                      'environment': environment,
                      'limitations': 'CPU actor/critic with tactical masks; no MCTS/neural network/automatic promotion.'}
    model.save(args.output / 'model.json')
    report = {'games': len(episodes), 'terminal_games': len(episodes), 'batch_value_mse': errors,
              'initial_model_sha256': initial_digest, 'trained_model_sha256': model.digest(),
              'policy_changed': not np.array_equal(model.policy, Model().policy),
              'value_changed': not np.array_equal(model.value, Model().value),
              'canonical_openings': len({g['root_canonical_key'] for g in episodes}),
              'completed_excluded_games': excluded}
    (args.output / 'training-summary.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--games', type=int, default=400)
    parser.add_argument('--batch', type=int, default=20)
    parser.add_argument('--seed', type=int, default=731)
    parser.add_argument('--opening-seed', type=int, default=20280001)
    parser.add_argument('--evaluation-seed', type=int, default=20300101)
    parser.add_argument('--evaluation-pairs', type=int, default=100)
    parser.add_argument('--temperature', type=float, default=.7)
    parser.add_argument('--learning-rate', type=float, default=.1)
    parser.add_argument('--reserved-openings', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    train(parser.parse_args())
