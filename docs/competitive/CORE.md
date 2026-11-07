# Candidate core (M1)

This PR adds an unused candidate API (`choose_move`); it does not switch production
routing. EASY/MEDIUM tournament adapters use the unchanged baseline implementation.
HARD uses radius 1, quiet cap 8, depth cap 4, one tactical extension, no VCF solver.
IMPOSSIBLE uses radius 2, quiet cap 12, depth cap 6, three tactical extensions and
bounded continuous-four proof search (at most five attack/reply pairs). Defaults
250/700ms are engine-entry wall-clock budgets, not a server/API SLO. Essential
constant-size immediate-win/block scans still finish even at zero budget.

Quiet caps never remove forcing four moves or safe responses to an opponent fork.
Candidate membership is selected deterministically before transposition ordering.
TT keys include both full bitboards, side, exact nominal depth and remaining threat
extensions. Bounds are fail-soft upper/lower/exact relative to the original window.
Tables are request-local and bounded; no global random choices or board mutation.
Completed iterations are atomic; interrupted work cannot replace the last complete
answer. The initial fallback is legal and explicitly marked when no iteration finishes.

The proof solver returns a move only for a verified continuous-four line: a defender
counter-win refutes it; one winning cell has a mandatory reply, two distinct cells
prove the local forcing win. Exhaustion is unknown. This is not an exhaustive VCT,
proof-number, Renju or perfect-play solver. Rules match the backend's unrestricted
at-least-five win condition, including overlines and wins blocked at both ends.

Validation before frozen-SHA experiments: 718 passed / 14 skipped; 403 core tests;
CI lint passes. Core tests include 192 positions x 2 levels, randomized independent
win-mask checks, exact fork oracles, TT on/off and narrow-window bound checks, the
PR 66 extension-alias regression, safe interruption of all internal state, immutable
inputs, deterministic complete searches, concurrent request isolation, zero budget,
forced loss and a domain-rule verified continuous-four certificate.

Strength and latency acceptance remain PARTIAL until tournament and performance
artifacts on a frozen commit exist. The small corpus is an initial regression suite,
not proof that its tactics represent the full distribution of human games.

The follow-up preserves root alpha bounds between siblings and restricts horizon
extensions to independently verified forcing moves or mandatory replies, with a
stand-pat evaluation only when no immediate block is required. Root pruning is
checked against full-window enumeration with the same answer and no extra nodes.
