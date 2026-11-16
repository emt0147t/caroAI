# Offline learning tools

These tools do not enable online learning or change the production engine. See
[the protocol](OFFLINE_PROTOCOL.md) and [measured results](../../reports/learning/REVIEW.md).

## Owner-controlled loss analysis

Provide a complete ordered history locally. Dataset schema is `schema_version: 1`
and a `games` array. Each game needs `game_id`, `result` (`X_WON`, `O_WON`, `DRAW`)
and `moves` entries containing integer `ply`, `player` (1/2), `row`, `col`. Include
`difficulty: null` when unrecorded. Missing metadata is not inferred. A final board
alone is insufficient. No command fetches production secrets or queries production.

Keep real data outside the checkout or under ignored, Docker-excluded `work/private/`:

```bash
python -m benchmarks.learning.analyze \
  --dataset work/private/history.json --output work/private/analysis.json
python -m benchmarks.learning.build_corpus \
  --analysis work/private/analysis.json --output work/private/challenges.json
python -m benchmarks.learning.challenges \
  --model work/train/model.json --private-challenges work/private/challenges.json \
  --output work/private/challenge-results.json
```

The corpus builder rechecks positive certificates against the domain oracle and
rechecks every listed alternative. It rejects empty/uncertain sets. A private
result evaluates refutation of a demonstrated plan, not full-game best play.
Private-output commands reject public source-tree destinations. Do not add these
owner-controlled outputs to public repository files, logs or workflow artifacts.

## Generated self-play and held-out evaluation

```bash
python -m benchmarks.learning.train --games 4000 --seed 731 --output work/train
python -m benchmarks.learning.audit --raw work/train/selfplay.jsonl \
  --training-manifest work/train/training-manifest.json --expected-games 4000 \
  --output work/train/replay.json
python -m benchmarks.learning.evaluate --games 200 --seed 20300101 \
  --model work/train/model.json --training-manifest work/train/training-manifest.json \
  --opponent production --level IMPOSSIBLE --budget-ms 700 \
  --output work/evaluation/production-impossible-700.json
```

The contender's production comparator is hash-checked against c10ee273. For the
untrained ablation, pass `--opponent initial --initial-model work/train/initial-model.json`.
The initial artifact must match the one recorded by training. All evaluation roots
must have been reserved before training; raw complete-game logs accompany summaries.

The same full study can be dispatched on the reviewed branch with
`offline_learning=true` and `release_approved=false` in the CaroAI CI workflow.
Public workflow artifacts contain generated self-play, model artifacts and composed
tests only. Private human validation stays NOT_RUN in public CI. No model is
automatically promoted, merged or deployed, even if the jobs complete successfully.
