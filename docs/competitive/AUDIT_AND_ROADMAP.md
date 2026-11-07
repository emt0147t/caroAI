# Competitive Engine audit and delivery plan

Audit date: 2026-11-07 (Asia/Bangkok). Production source baseline:
`b848a0e6a527b7ef3f1efa421971c356543fbc17`. Integration branch `develop`:
`1d46da519fb5ff3dceacab1ec786a20e53c8d378`. PR 66 source:
`74c59d5525f113150fe8db892c4db644abe148d6` (open draft).

## Production and baseline

The main SHA matches the supplied production baseline. Develop is behind main's
QA security and automatic shutdown fixes; new work starts from main. No production
writes, QA activation, configuration changes, merge, or deployment are authorized
by this plan. The user identified Render project `prj-dbkcvvflk1mc73fcrlh0`;
read-only platform inspection confirmed the live image matches this main SHA.
Health/readiness are 200 and QA routes are 404. CPU/RAM samples exist; HTTP latency
metrics are empty, so production latency remains unmeasured.

The baseline uses minimax with alpha-beta, deterministic move ordering, radius-two
candidate generation, cached line scoring, and incremental four-line move evaluation.
EASY/MEDIUM/HARD/IMPOSSIBLE use depth/cap 1/6, 2/10, 3/14, 4/20. Root win/block
scans precede the optional clock. No default deadline is set. Timeout discards all
search progress and returns the empty candidate nearest the center. The evaluator's
fixed 1.2 defensive coefficient and a quiet-move cap do not provide tactical proof.
Only the first opponent immediate win is blocked, even if the position is lost.

## PR 66 technical findings

1. **P2: TT horizon alias.** The key is board + side. At nominal depth zero a
   tactical extension is stored as depth one; remaining extension budget is absent.
   An EXACT extended result can satisfy a genuinely deeper request. Reproduction:
   X at (7,3..6),(8,7); O at (7,2),(4..6,7); O to move, AI=O, ply=3.
   Depth 1 fresh = -500; warm table with depth 0 then depth 1 = 9,579,500.
2. **P2: telemetry.** generated_candidates is never incremented. Ordinary heuristic
   leaves are omitted. Example: 16 expanded candidates, zero generated candidates.
3. **Candidate membership depends on TT move.** Promotion precedes the cap, changing
   the searched subtree and making comparisons with/without TT difficult to interpret.
   A tactical move outside the quiet cap has no preservation guarantee.
4. Fork detection correctly recognizes two distinct immediate winning cells, but
   open/broken-three counts are heuristic patterns, not proofs of a forcing sequence.
   A bounded forced-four proof search is absent.
5. Clock begins after root tactical scans and initial evaluation. Default production
   diversification uses global randomness; no request seed or deterministic-node mode.
   Completed-depth fallback and try/finally undo are improvements worth preserving.
6. Bound classification uses the original alpha/beta window, but correct bound
   arithmetic alone cannot repair incompatible TT search horizons.

## Existing evidence and gaps

Phase A workflow 42237743095: 11 fixtures x 4 levels x 30 trials, legality/latency.
Phase B Windows review: original harness hashes not recovered; qualified historical
results, not fully reproducible. Concurrency 4/8 exceeded the proposed 2s reference.
Phase C source 8ca52e0ed4a5a2ba4546f94978dcb0c1fb06339f: independent AI and API/DB
runs, instrumentation, concurrency 1/2. HARD search P95 523ms; IMPOSSIBLE 2277ms on
that host. These numbers are not a comparison with this environment or production.
Several dense/complex fixtures are root shortcuts, not genuine recursive search.
No >=200-game color-swapped tournament, independent tactical oracle, confidence
interval, difficulty progression evidence, forcing-chain corpus, current candidate
latency/concurrency 1/2/4/8 or production latency measurement exists.

## Proposed architecture

- Independent composed-position corpus with explicit legal answer sets and outcomes;
  D4 rotations/reflections and color swaps; independent domain-rule oracle.
- Isolated bitboard tactical state, exact immediate wins and fork checks, preservation
  of forcing moves before quiet pruning; deterministic tie-breaking.
- Iterative deepening alpha-beta with exact horizon/extension-aware per-search TT;
  candidate selection before TT ordering, full board/player key, bounded memory.
- HARD: narrow radius, direct forcing attacks, one tactical extension and proofs
  of up to three continuous-four attacks. IMPOSSIBLE: wider radius, three extensions
  and proofs of up to five attacks. Differences are search policy, not only milliseconds.
- A clock starting at engine entry, mandatory constant-size win/block scan, safe
  fallback and last completed iteration, separate search/engine timing and counters.
- No claim of perfect or unbeatable play; forcing proof is restricted to its model.

## Milestones and PRs

| Milestone / PR | Scope | Acceptance |
|---|---|---|
| M0 evaluation | corpus, tournament, performance harness, this audit | oracle validates every expected set; paired colors/openings; complete game logs; Wilson and pair-cluster intervals; >=200 games/comparison; identical host/runtime/config metadata |
| M1 core | tactical bitboards, forcing search, TT, timeout and integrity tests | all HARD/IMPOSSIBLE corpus cases; no illegal/mutated states; TT on/off equivalent at fixed node-independent horizon; all bound windows; interrupted search restores state |
| M2 integration | route HARD/IMPOSSIBLE; preserve EASY/MEDIUM/API | defaults documented; strict contracts and environment override; all existing tests; PostgreSQL, browser E2E, lint, secret scan, Docker build |
| M3 evidence | frozen-SHA tournaments and latency matrix | >=200 completed games/initial pair; increase samples if inconclusive; no strength claim without intervals; p50/p95/max, nodes, branching, pruning, TT/timeout/fallback rates; API c=1/2/4/8 |
| M4 release review | review evidence, human play test and capacity decision | all mandatory gates PASS; unresolved gates PARTIAL/BLOCKED; explicit user permission before merge/deploy |

The evaluation budget and production/default budget must be identified separately.
A small-budget screening tournament cannot establish default-budget superiority.
No truncated game is silently counted as a draw; record incomplete/error separately.
Persist seeds, openings, all moves, terminal reason, missed-win/block opportunities,
source SHAs, working-tree hashes, Python/package/CPU metadata and raw timing rows.

This document records the audit and plan. Current measured acceptance, CI runs,
limitations and artifact provenance are in [REVIEW.md](../../reports/competitive/REVIEW.md).
