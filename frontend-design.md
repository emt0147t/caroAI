# CaroAI Frontend Design

## Sprint 1 scope
The frontend is a presentation and interaction layer. Backend is the source of truth for board state, legal moves, turn transitions, winner/draw status and AI decisions.

## UI requirements
- 15 x 15 board.
- X/O rendering.
- Current-player indicator.
- Game status: IN_PROGRESS, X_WON, O_WON, DRAW.
- HUMAN_VS_HUMAN and HUMAN_VS_AI mode selection.
- Loading / AI-thinking state.
- Network/API error state.
- Latest-move highlighting when move metadata is available.
- New-game action.

## API mapping
- POST /api/games
- GET /api/games/{game_id}
- POST /api/games/{game_id}/moves
- Future AI integration: POST /api/games/{game_id}/ai-move
- Future hint/analysis integration follows docs/api-contract.md.

## State ownership
Frontend may keep transient UI state such as gameId, loading and error. It must not independently calculate legal moves, winner, draw, turn transitions, heuristic scores or AI moves.

## Error mapping
400 = invalid game action; 404 = game not found; 422 = request validation; 5xx = service failure; network failure = connection error.

## Sprint 1 acceptance
- [x] 15 x 15 UI
- [x] X/O
- [x] turn indicator
- [x] PvP/PvAI modes
- [x] loading state
- [x] error state
- [x] backend API mapping documented
- [x] no local game-rule implementation
- [x] no fake/random AI
- [ ] Full backend integration is completed during integration work.
- [ ] AI endpoint integration waits for the AI module.
