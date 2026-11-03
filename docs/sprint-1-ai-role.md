# CaroAI — Sprint 1 AI Engineer Role & Definition of Done

> **Role:** AI Engineer (M2)  
> **Branch:** `feature/ai-engine`  
> **Sprint:** Sprint 1 — Technical Alignment  
> **Objective:** Freeze the AI architecture, AI↔Backend boundary, and a testable rule-based/Minimax baseline so Sprint 2 can integrate the engine without redefining contracts.

## 1. Sprint 1 Responsibilities

### 1.1 Board Representation & Boundary
- Freeze the internal AI board representation for a 15×15 board.
- Document the mapping between Backend `GameState` and AI internal representation.
- Current Backend values are `EMPTY`, `X`, `O`; an internal mapping such as `0/1/2` is allowed only with an explicit adapter/conversion boundary.
- AI must not become a second source of truth for `GameStatus`, turn ownership, or move legality.

### 1.2 Move Generator
Implement and document candidate move generation:
- Empty board → center `(7,7)`.
- Chebyshev neighborhood search with radius `R=1` and `R=2`.
- Never return occupied or out-of-board cells.
- Define deterministic ordering/tie-breaking where practical.

### 1.3 Heuristic Evaluator
Implement and document baseline pattern evaluation:
- Five
- Open Four
- Blocked Four
- Open Three
- Three
- Open Two

Document the score table and evaluation formula. The evaluator must consider both AI and opponent positions.

### 1.4 Tactical Detection
Before deeper search, define the tactical priority:
1. AI can win immediately → play the winning move.
2. Opponent can win immediately → block.
3. Otherwise → run Minimax.

Win detection must remain consistent with the game-domain rules owned by Backend.

### 1.5 Minimax + Alpha-Beta
Implement:
- Minimax
- Alpha-Beta pruning
- Move ordering
- Candidate limitation
- Apply/undo (backtracking)

Difficulty baseline:
| Difficulty | Depth |
|---|---:|
| EASY | 1 |
| MEDIUM | 2 |
| HARD | 3 |

The implementation must correctly distinguish maximizing and minimizing nodes. Tactical checks must not assume that the current node is always controlled by the AI.

### 1.6 AI Engine Facade
Expose one callable interface for Backend integration, for example:

```text
AI Engine
  └── get_ai_move(board, ai_player, difficulty)
```

Expected output:

```json
{
  "row": 0,
  "col": 0,
  "score": 0,
  "elapsed_ms": 0.0
}
```

Requirements:
- Return a legal move.
- Do not mutate the caller's board.
- Do not contain Frontend logic.
- Do not contain FastAPI route logic.
- Do not make HTTP calls to Backend.
- Backend calls/imports the AI engine as an internal service boundary.

### 1.7 AI ↔ Backend Contract
Document:
- Input schema.
- Output schema.
- Board conversion.
- Invalid difficulty behavior.
- Illegal move handling.
- Ownership of move validation.
- Ownership of game status.

The agreed architectural boundary is:

```text
Frontend
   ↓
FastAPI Routes
   ↓
Game Services / Domain
   ├── GameState
   └── GameRules
   ↓
AI Engine
   ├── Move Generator
   ├── Tactical Detection
   ├── Evaluator
   └── Minimax + Alpha-Beta
   ↓
Database / Persistence
```

### 1.8 Runtime / Benchmark
Measure `elapsed_ms` on representative positions for EASY, MEDIUM and HARD.

Do not claim a fixed latency target such as “<1s” without a recorded benchmark environment and result.

### 1.9 Unit Tests
Minimum coverage:
- Empty-board center opening.
- Radius 1 and radius 2 candidate generation.
- Boundary handling.
- No occupied/illegal candidate.
- Horizontal, vertical and diagonal five detection.
- Immediate win.
- Immediate block.
- Minimax minimizing-node behavior.
- Board immutability after search.
- Invalid difficulty behavior.
- Output schema.
- All three difficulty levels.

Run both AI tests and the repository-wide test suite before declaring the work complete.

---

## 2. Documentation Deliverables

### Required
- `docs/ai-design.md`

The design document must clearly distinguish:
- **Implemented**
- **Designed / Contracted**
- **Planned for Sprint 2+**
- **Out of Scope for Sprint 1**

The following are design items only unless code/tests exist:
- Hint
- Move Analysis
- ML training
- Reinforcement Learning
- Neural-network inference

---

## 3. Definition of Done — AI Engineer

Sprint 1 AI is **Done** only when all applicable conditions below are satisfied:

- [ ] AI architecture is documented.
- [ ] Board representation is documented and mapped to Backend representation.
- [ ] AI↔Backend boundary is explicit.
- [ ] Move Generator works for R=1 and R=2.
- [ ] Evaluator covers the defined baseline patterns.
- [ ] Immediate win/block logic works.
- [ ] Minimax + Alpha-Beta works for EASY/MEDIUM/HARD.
- [ ] Minimizing-node behavior is covered by regression tests.
- [ ] AI never returns an occupied/out-of-board move.
- [ ] AI does not mutate the input board.
- [ ] Invalid difficulty has an explicit contract.
- [ ] Runtime benchmark is recorded instead of assumed.
- [ ] AI unit tests pass.
- [ ] Full repository test suite passes.
- [ ] AI contains no Frontend-specific logic.
- [ ] AI contains no HTTP/FastAPI integration logic.
- [ ] Backend remains the source of truth for game state, legality and game status.
- [ ] PR targets `develop`.
- [ ] PR has at least one teammate review before merge.
- [ ] No unrelated project files are deleted or overwritten while syncing the feature branch.

---

## 4. Sprint 1 Non-Goals

Sprint 1 does not require:
- Model training or fine-tuning.
- Reinforcement Learning.
- LLM integration.
- Production-grade performance optimization.
- Completed Hint API.
- Completed Analysis API.

These may be prepared as interfaces/design notes for later sprints.

---

## 5. Integration Checklist for Sprint 2

Before Backend integration starts:
1. Backend and AI agree on the board conversion mapping.
2. Backend remains responsible for validating/applying the returned move.
3. AI receives a snapshot of the board and returns only a decision.
4. AI difficulty values are validated consistently.
5. Tactical win/block behavior is covered by shared regression cases.
6. Integration tests verify Backend → AI → Backend move flow.
