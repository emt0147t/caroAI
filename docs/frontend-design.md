# CaroAI Frontend Design

## 1. Sprint 1 scope

The frontend is a presentation and interaction layer. It must not own game rules, winner detection, turn transitions, or AI move selection.

Sprint 1 freezes the interface between Frontend and Backend so implementation can proceed without changing the API contract independently.

## 2. UI structure

### Welcome
- Select game mode:
  - \`HUMAN_VS_HUMAN\`
  - \`HUMAN_VS_AI\`
- Start a new game.
- AI difficulty is a UI concern for the future AI endpoint; the current create-game API accepts \`mode\` only.

### Game
- 15 × 15 board.
- Render \`X\`, \`O\`, and empty cells from the server response.
- Show current player.
- Highlight the latest move.
- Show \`IN_PROGRESS\`, \`X_WON\`, \`O_WON\`, or \`DRAW\`.
- Show loading state while waiting for an API response.
- Show an error state for network/API failures.
- Provide a new-game action.

### Result
Existing win/lose/draw visual pages are presentation prototypes. Final result values must come from backend game state rather than hard-coded values.

## 3. Frontend state model

The browser may keep transient UI state:

| State | Owner | Purpose |
|---|---|---|
| \`gameId\` | Frontend | Identify the current server game |
| \`game\` | Backend response | Current board/status/turn |
| \`loading\` | Frontend | Disable interactions during request |
| \`error\` | Frontend | Display request/API failures |
| \`lastMove\` | Derived from latest move response | Highlight the latest move |

The frontend must not independently calculate:
- valid moves
- winner
- draw
- next player
- AI move
- heuristic score

## 4. Current Backend API mapping

### Create game

\`POST /api/games\`

Request:

\`\`\`json
{
  "mode": "HUMAN_VS_HUMAN"
}
\`\`\`

Response \`201\`:

\`\`\`json
{
  "id": "game-id",
  "mode": "HUMAN_VS_HUMAN",
  "status": "IN_PROGRESS",
  "current_player": "X",
  "move_count": 0,
  "winner": null,
  "board": [["EMPTY"]]
}
\`\`\`

The actual board is 15 × 15.

### Get game

\`GET /api/games/{game_id}\`

Response \`200\`:

Same \`GameResponse\` structure as create game.

### Make move

\`POST /api/games/{game_id}/moves\`

Request:

\`\`\`json
{
  "row": 7,
  "col": 8
}
\`\`\`

Response \`200\`:

\`\`\`json
{
  "move": {
    "row": 7,
    "col": 8,
    "player": "X",
    "move_number": 1
  },
  "game": {
    "id": "game-id",
    "mode": "HUMAN_VS_HUMAN",
    "status": "IN_PROGRESS",
    "current_player": "O",
    "move_count": 1,
    "winner": null,
    "board": [["EMPTY"]]
  }
}
\`\`\`

The backend is authoritative. The frontend re-renders from \`game.board\` and \`game.status\`.

## 5. Error mapping

| HTTP | Frontend behavior |
|---|---|
| 400 | Show invalid-game-action message |
| 404 | Show game-not-found message and offer a new game |
| 422 | Show request-validation message |
| 5xx | Show service-unavailable message |
| Network failure | Show connection-error message |

## 6. Planned AI integration

The current frontend must not implement a fake/random AI.

The planned interface from \`docs/api-contract.md\` is:

\`POST /api/games/{game_id}/ai-move\`

The AI engine implementation is owned by the AI module. When that endpoint is implemented, the frontend will call it and render its returned \`move\` + \`game\` response.

Planned features:
- Easy / Medium / Hard
- AI thinking indicator
- Hint
- Move analysis

These are Sprint 2+ integrations, not local business logic.

## 7. Integration sequence

\`\`\`text
User
  ↓
Frontend event
  ↓
HTTP request
  ↓
FastAPI
  ↓
GameService / AI
  ↓
GameState
  ↓
JSON response
  ↓
Frontend render
\`\`\`

## 8. Acceptance criteria

- [x] 15 × 15 board UI exists.
- [x] X/O rendering exists.
- [x] Player-turn indicator exists.
- [x] PvP and PvAI modes are represented.
- [x] Last-move highlight exists.
- [x] Loading state exists.
- [x] Error state exists.
- [x] Frontend does not calculate win/draw/turn/AI decisions.
- [x] Current Backend request/response mapping is documented.
- [ ] Full backend integration is completed in the next integration phase.
- [ ] AI endpoint integration waits for AI implementation.
