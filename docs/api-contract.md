# CaroAI API Contract

Base path:

```text
/api
```

## 1. Health Check

### GET `/health`

Response `200`:

```json
{
  "status": "ok"
}
```

---

## 2. Create Game

### POST `/api/games`

Request:

```json
{
  "mode": "HUMAN_VS_AI"
}
```

Allowed modes:

```text
HUMAN_VS_HUMAN
HUMAN_VS_AI
```

Response `201`:

```json
{
  "id": "game-id",
  "mode": "HUMAN_VS_AI",
  "status": "IN_PROGRESS",
  "current_player": "X",
  "move_count": 0,
  "winner": null,
  "board": []
}
```

The actual board must contain 15 × 15 cells.

---

## 3. Get Game

### GET `/api/games/{game_id}`

Response `200`:

```json
{
  "id": "game-id",
  "mode": "HUMAN_VS_AI",
  "status": "IN_PROGRESS",
  "current_player": "X",
  "move_count": 3,
  "winner": null,
  "board": []
}
```

Response `404`:

```json
{
  "detail": "Game not found"
}
```

---

## 4. Make Human Move

### POST `/api/games/{game_id}/moves`

Request:

```json
{
  "row": 7,
  "col": 8
}
```

The backend determines the player from `current_player`.

Response `200`:

```json
{
  "move": {
    "row": 7,
    "col": 8,
    "player": "X",
    "move_number": 1
  },
  "game": {
    "id": "game-id",
    "status": "IN_PROGRESS",
    "current_player": "O",
    "move_count": 1,
    "winner": null,
    "board": []
  }
}
```

Invalid move response: `400`.

Examples:

```text
Cell already occupied
Invalid coordinates
Game already finished
Not player's turn
```

---

## 5. Request AI Move

### POST `/api/games/{game_id}/ai-move`

Used only for `HUMAN_VS_AI`.

Request:

```json
{
  "difficulty": "medium"
}
```

Allowed difficulty values:

```text
easy
medium
hard
```

Response `200`:

```json
{
  "move": {
    "row": 6,
    "col": 8,
    "player": "O",
    "move_number": 2
  },
  "game": {
    "id": "game-id",
    "status": "IN_PROGRESS",
    "current_player": "X",
    "move_count": 2,
    "winner": null,
    "board": []
  }
}
```

The AI service must return a legal move.

The Backend validates the move before applying it.

---

## 6. AI Hint

### POST `/api/games/{game_id}/hint`

Request:

```json
{
  "difficulty": "medium"
}
```

Response `200`:

```json
{
  "suggested_move": {
    "row": 7,
    "col": 9
  },
  "score": 12.5,
  "model": "minimax"
}
```

Hint does not modify the game state.

---

## 7. Move Analysis

### POST `/api/games/{game_id}/analysis`

Request:

```json
{
  "row": 7,
  "col": 8
}
```

Response `200`:

```json
{
  "score": 8.5,
  "best_move": {
    "row": 7,
    "col": 9
  },
  "comment": "Move is playable but not optimal."
}
```

The exact scoring algorithm is owned by the AI module.

---

## 8. Game History

### GET `/api/history`

Response `200`:

```json
{
  "games": []
}
```

History persistence is backed by PostgreSQL in later implementation.

---

# Error Contract

API errors use FastAPI's standard format:

```json
{
  "detail": "Human-readable error message"
}
```

Common status codes:

```text
200 - Success
201 - Resource created
400 - Invalid game action
404 - Resource not found
422 - Request validation error
500 - Unexpected server error
```

# Backend Architecture

```text
Frontend
   ↓
API Routes
   ↓
Services
   ↓
Domain
   ├── GameState
   └── GameRules
   ↓
AI Service
   ↓
Database Repository
   ↓
PostgreSQL
```

Responsibilities:

### Routes

HTTP layer only.

### Services

Application/business orchestration.

### Domain

Pure game rules and state management.

### AI

Move evaluation and move selection.

### Database

Persistence only.

### Important Rule

No Frontend-specific logic inside Domain.

No database-specific logic inside Domain.

No HTTP/FastAPI logic inside Domain.

No AI algorithm inside API routes.
