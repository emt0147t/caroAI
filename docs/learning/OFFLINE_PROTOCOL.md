# Offline learning experiment 1 — protocol frozen before held-out evaluation

Production comparator: `c10ee2739b6577ea0004f86e91126dd176132319`.
This branch adds research tools; the application never imports the learned model.
No training process, model promotion, deploy or business-data write runs on Render.

## Data and the human losses

Real game histories and their derived positions remain in owner-controlled local
storage. No production game IDs, timestamps, ordered histories or derived private
challenge boards are committed here. Public CI uses synthetic fixtures; the optional
`--private-challenges` CLI accepts a local dataset and must not be auto-uploaded.
The earlier temporary raw-data artifact has been removed. The proposed public
workflow has no new production-secret access or production-data export capability.

Private retrospective diagnosis checks the demonstrated human attack against every
legal defender reply at its quiet setup. Positive continuous-four lines are verified
independently with exhaustive domain-rule winning-cell scans. Counter-wins refute a
certificate. Alternative moves refute that particular plan; they are not claimed to
win/save the whole game. `NO_PROOF` is restricted to the model/horizon; exhaustion
is `UNKNOWN`. No move order is inferred from a final board, and missing game-time
engine/difficulty metadata is never invented.

Private cases are visible development regressions, not blind holdout data, and are
never used for gradient updates. Public CI checks the existing independent
240-variant corpus at both strong levels plus composed certificate fixtures. Real
human regression coverage remains NOT_RUN in public CI; promotion requires a
separate local owner-controlled validation with the same model fingerprint.

## What learns

The initial CPU implementation has a linear policy head (8 action features) and a
linear tanh value head (7 relative-position features). It is a Monte Carlo actor/critic
baseline, not a neural/MCTS AlphaZero implementation. Policy warm-start coefficients
encode attack/defense priors; the value head starts at zero. The ablation uses exactly
that recorded initial artifact. Self-play uses a stochastic actor with exact
win/block/fork masks. Terminal rewards are +1/-1/0 for win/loss/draw.
Policy gradients use the stored on-policy action distribution and value baseline;
value regression uses terminal returns. Both sides' parameters stay frozen within
each batch; updates occur only between batches of complete games.

Protocol: 4,000 training games, RNG seed 731, batch 20, learning rate 0.1,
temperature 0.7, opening seeds starting 20280001. Training starts have 6/8 plies.
Evaluation roots are reserved before generation from seeds 20300101–20300200.
D4-canonical overlaps at training roots and early positions are excluded, checked
again by independent replay. Completed excluded episodes are counted separately.
Training games and all evaluation games must finish under actual backend rules;
no incomplete game becomes a draw.

The experimental candidate uses learned policy/value priors for root ordering and
quiet membership, preserving forcing moves. Deeper alpha-beta/TT and root tactical
proofs reuse the unchanged production core. An apparent selective loss widens root
coverage under the original clock/node budget. Ordinary mate-range search scores
do not stop iterative deepening early; exact root shortcuts remain available.
The initial-model opponent has the same algorithm but untrained heads, separating
algorithm changes from evidence that learning itself helps.

## Evaluation and promotion gates

Four paired-color comparisons each have 200 complete games on the reserved opening
set: trained vs production IMPOSSIBLE at 700ms, trained vs initial-model IMPOSSIBLE
at 700ms, trained vs production HARD at 250ms, and an IMPOSSIBLE 25ms stress screen.
Each pair shares host/process, runtime, openings, budget and rules. Every artifact
records environment/source/model hashes and complete move logs. Canonical-opening
cluster bootstrap is the primary uncertainty measure; Wilson game-win intervals
are descriptive because the color-paired games are correlated. Repeated opening
sets across different opponents are not pooled as independent new openings.

Before recommending a learned-model integration:

- Existing tactical corpus: 480/480; private demonstrated-plan challenges: all available variants, validated locally.
- Zero illegal/mutated states and zero missed immediate-win/unique-block events.
- IMPOSSIBLE 700ms: canonical score bootstrap lower bound >50% versus production.
- Learning attribution: lower bound >50% versus the identical initial-model algorithm.
- HARD 250ms: canonical lower bound >=45% (5-point noninferiority margin).
- Same-fixture serial core p95 <=770ms, the 700ms budget plus 10% cooperative margin;
  default measured serial fallback count must be zero. Thread contention c1/2/4/8
  is reported separately and is not a hard real-time or API guarantee.
- Full CI/PG/browser/secret/Docker gates must pass on the reviewed source.

25ms is diagnostic, not the production preset. An inconclusive interval is recorded
as NOT_ESTABLISHED; none of the experiments can trigger an automatic deploy. A failed
challenge/strength gate produces NOT_PROMOTED even if training and CI execute cleanly.
Do not tune a model repeatedly against the final holdout and then report only the
best run. A future iteration needs a separately versioned experiment/holdout.

Same-fixture performance alternates contender order, excludes warm-up and reports
p50/p95/max, nodes, timeout/fallback rates. Tournament timings use different positions
by side and are not used as same-fixture speedups. No new-model HTTP/production
latency or capacity claim is made by this offline pipeline.
