"""Small NumPy policy/value heads with non-executable, versioned JSON artifacts."""
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path

import numpy as np

from app.ai.competitive import Position
from app.ai.threats import cells, fork_moves, neighborhood

POLICY_FEATURES = ('bias', 'attack_gain', 'defense_gain', 'own_next_wins', 'enemy_next_wins',
                   'own_neighbors', 'enemy_neighbors', 'centrality')
VALUE_FEATURES = ('bias', 'own_score', 'enemy_score', 'own_wins', 'enemy_wins', 'own_stones', 'enemy_stones')


def compressed(value):
    return float(np.clip(np.sign(value) * np.log1p(abs(value)) / 20, -1, 1))


def value_features(pos, player):
    return np.array([1, compressed(pos.raw[player - 1]), compressed(pos.raw[2 - player]),
                     min(2, pos.wins(player).bit_count()) / 2,
                     min(2, pos.wins(3 - player).bit_count()) / 2,
                     pos.stones[player].bit_count() / 225, pos.stones[3 - player].bit_count() / 225], dtype=float)


def action_features(pos, player, move):
    r, c = move
    neighbors = [pos.board[rr][cc] for rr in range(max(0, r - 1), min(15, r + 2))
                 for cc in range(max(0, c - 1), min(15, c + 2))]
    raw = pos.play(move, player)
    try:
        own_gain = pos.raw[player - 1] - raw[player - 1]
        defense_gain = raw[2 - player] - pos.raw[2 - player]
        features = np.array([1, compressed(own_gain), compressed(defense_gain),
                             min(2, pos.wins(player).bit_count()) / 2,
                             min(2, pos.wins(3 - player).bit_count()) / 2,
                             neighbors.count(player) / 8, neighbors.count(3 - player) / 8,
                             1 - (abs(r - 7) + abs(c - 7)) / 14], dtype=float)
        return features, -value_features(pos, 3 - player)
    finally:
        pos.undo(move, player, raw)


def probabilities(logits, temperature=1.0):
    if not np.isfinite(temperature) or temperature <= 0:
        raise ValueError('Temperature must be positive and finite')
    logits = np.asarray(logits, dtype=float) / temperature
    shifted = np.clip(logits - np.max(logits), -50, 0)
    weights = np.exp(shifted)
    return weights / weights.sum()


@dataclass
class Model:
    policy: np.ndarray = field(default_factory=lambda: np.array([0, 1.0, 1.2, 3, -3, .1, .1, .05]))
    value: np.ndarray = field(default_factory=lambda: np.zeros(len(VALUE_FEATURES)))
    metadata: dict = field(default_factory=dict)

    def logits(self, features):
        return np.asarray(features) @ self.policy

    def predict(self, features):
        return np.tanh(np.asarray(features) @ self.value)

    def document(self):
        return {'schema_version': 1, 'algorithm': 'linear_policy_value_monte_carlo_actor_critic',
                'policy_features': list(POLICY_FEATURES), 'value_features': list(VALUE_FEATURES),
                'policy_weights': self.policy.tolist(), 'value_weights': self.value.tolist(),
                'metadata': self.metadata}

    def digest(self):
        return hashlib.sha256(json.dumps(self.document(), sort_keys=True, allow_nan=False).encode()).hexdigest()

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.document(), indent=2, allow_nan=False) + '\n')

    @classmethod
    def load(cls, path):
        doc = json.loads(Path(path).read_text())
        if (doc.get('schema_version') != 1 or doc.get('policy_features') != list(POLICY_FEATURES)
                or doc.get('value_features') != list(VALUE_FEATURES)):
            raise ValueError('Incompatible model feature/schema version')
        policy, value = np.array(doc['policy_weights'], dtype=float), np.array(doc['value_weights'], dtype=float)
        if (policy.shape != (len(POLICY_FEATURES),) or value.shape != (len(VALUE_FEATURES),)
                or not np.all(np.isfinite(policy)) or not np.all(np.isfinite(value))
                or max(np.max(abs(policy)), np.max(abs(value))) > 20):
            raise ValueError('Invalid model dimensions or unbounded/nonfinite weights')
        return cls(policy, value, doc.get('metadata', {}))


def actor_options(board, player, model):
    """Legal tactical mask plus stochastic quiet policy, used only for training."""
    pos = Position(board)
    own, enemy = pos.wins(player), pos.wins(3 - player)
    forced = own or enemy
    if not forced:
        forced = fork_moves(pos.stones[player], pos.occupied)
    moves = list(cells(forced or neighborhood(pos.occupied, 2)))
    if not moves:
        raise ValueError('No legal moves')
    features = np.array([action_features(pos, player, move)[0] for move in moves])
    return moves, features, bool(forced), value_features(pos, player)
