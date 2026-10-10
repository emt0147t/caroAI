# CaroAI — Database Design (Sprint 1)

> **Sprint 2 implementation status (2026-10-10):** This design has a SQLAlchemy model foundation, not an integrated persistence layer. `GameService` remains in-memory, `app/db/repository.py` is a placeholder, and no migration tool/schema lifecycle is configured. PostgreSQL model checks are present in the test suite but require an explicitly confirmed disposable test database; their run status is tracked in [`test-plan.md`](test-plan.md).

## 1. Purpose

This document freezes the Database / QA / Docs technical boundary for Sprint 1. PostgreSQL is the target database and SQLAlchemy is the ORM. Sprint 1 is a design and alignment phase; it does not require production PostgreSQL deployment or database-backed GameService.

## 2. Scope

Required Sprint 1 database scope:

- users
- games
- moves
- game_analysis
- relationships
- constraints and indexing considerations
- Database ↔ Backend contract dependencies

Current repository status:

- SQLAlchemy foundation exists for games, moves and game_analysis.
- GameService still uses in-memory storage.
- No users model is frozen because the application/user contract is not defined.
- Migration tooling is not frozen yet.

## 3. Table design

### 3.1 games

| Column | Type | Null | Default | Meaning |
|---|---|---:|---|---|
| id | BIGINT identity | No | generated | Primary key |
| mode | enum/check | No | — | HUMAN_VS_AI or HUMAN_VS_HUMAN |
| difficulty | enum/check | Yes | — | EASY, MEDIUM, HARD; nullability depends on mode contract |
| status | enum/check | No | IN_PROGRESS | IN_PROGRESS, X_WON, O_WON, DRAW |
| result | enum/check | Yes | — | X_WON, O_WON or DRAW; semantics must match status |
| started_at | timestamptz | No | current timestamp | Game start time |
| ended_at | timestamptz | Yes | — | Set when game ends |

### 3.2 moves

| Column | Type | Null | Default | Meaning |
|---|---|---:|---|---|
| id | BIGINT identity | No | generated | Primary key |
| game_id | BIGINT | No | — | FK → games.id |
| player | CHAR(1) | No | — | X or O |
| row | SMALLINT | No | — | 0..14 |
| col | SMALLINT | No | — | 0..14 |
| move_number | INTEGER | No | — | Positive, unique within game |
| created_at | timestamptz | No | current timestamp | Move time |

Required design constraints:
- player must be X or O.
- row and col must be 0..14.
- move_number must be positive.
- UNIQUE(game_id, move_number).

Candidate constraint requiring Backend confirmation:
- UNIQUE(game_id, row, col), because future undo/replay behavior may affect this decision.

### 3.3 game_analysis

| Column | Type | Null | Default | Meaning |
|---|---|---:|---|---|
| id | BIGINT identity | No | generated | Primary key |
| game_id | BIGINT | No | — | FK → games.id |
| move_id | BIGINT | Yes | — | Optional FK → moves.id |
| score | DOUBLE PRECISION | Yes | — | AI analysis score |
| best_move_row | SMALLINT | Yes | — | 0..14 when present |
| best_move_col | SMALLINT | Yes | — | 0..14 when present |
| classification | TEXT | Yes | — | AI-owned classification |
| explanation | TEXT | Yes | — | Human-readable explanation |

Required design constraints:
- best_move_row is null or 0..14.
- best_move_col is null or 0..14.
- move_id remains nullable.
- No uniqueness rule is imposed on move_id until analysis cardinality is decided.

### 3.4 users

The Sprint 1 assignment requires a users table, but the repository does not define a user/API/authentication contract.

Therefore the design freezes the entity requirement without inventing unconfirmed application fields:

- users is a reserved persistent entity.
- primary-key type and user columns remain TBD.
- authentication fields are not introduced.
- no user_id is added to games until the ownership model for Human vs Human and Human vs AI is defined.
- no user-to-game relationship is frozen before Backend/API confirms the contract.

This is intentional contract protection, not an omitted requirement.

## 4. Relationships

Confirmed:

GAMES 1 ─ N MOVES
GAMES 1 ─ N GAME_ANALYSIS
MOVES 0..1 ─ N GAME_ANALYSIS

Meaning:
- every move belongs to one game;
- every analysis belongs to one game;
- an analysis may optionally reference a move;
- multiple analyses per move are currently allowed by design.

Users relationship is pending the application user contract.

## 5. ERD

~~~text
USERS
  |
  | relationship: TBD after user contract
  |
GAMES 1 -------- N MOVES
   |
   +----------- N GAME_ANALYSIS
                    ^
                    |
              optional move_id
                    |
                    +---- MOVES
~~~

The USERS relationship is deliberately not invented. The other three entities and their relationships are frozen for Sprint 1 design.

## 6. Constraints and indexes

Design constraints:
- board coordinates are 0..14 inclusive;
- player values are X/O;
- move_number is positive;
- move_number is unique within a game;
- mode uses the two project game modes;
- status uses the four project game statuses;
- best-move coordinates use 0..14 when present.

Indexing proposal:
- UNIQUE(game_id, move_number) covers ordered move lookup by game.
- index game_analysis.game_id for game analysis lookup.
- consider index game_analysis.move_id if move-level lookup is needed.
- avoid duplicate indexes where a unique constraint already supplies one.

Pending team decisions:
1. PostgreSQL ENUM vs CHECK enforcement.
2. difficulty nullability and relation to mode.
3. status/result semantics and ended_at rules.
4. unique-cell behavior with future undo/replay.
5. delete/cascade policy.
6. simple FK vs composite game_id/move_id relationship.
7. analysis cardinality.
8. classification value set and score semantics.
9. complete users contract.
10. API ID ↔ database ID mapping.

## 7. Backend alignment

Before Sprint 2 database integration, Backend and Database must agree on this mapping:

GameResponse.id ↔ games.id
GameState.mode ↔ games.mode
GameState.status ↔ games.status
Move(row, col, player, move_number) ↔ moves
AI analysis output ↔ game_analysis

Current backend exposes GameResponse.id as a string while the proposed persistent identifier is BIGINT. This is an explicit integration decision and must be confirmed before runtime persistence is wired.

Database must not independently rename API fields, alter game enums, or change GameState semantics.

## 8. Runtime boundary

Sprint 1 does not require:
- production PostgreSQL;
- database credentials;
- migrations;
- database-backed GameService;
- authentication;
- history persistence implementation.

Those belong to implementation/integration work after contract freeze.

## 9. Sprint 1 DoD

- [x] PostgreSQL and SQLAlchemy selected.
- [x] games design defined.
- [x] moves design defined.
- [x] game_analysis design defined.
- [x] users requirement explicitly represented.
- [x] relationships documented.
- [x] ERD included.
- [x] constraints documented.
- [x] index strategy documented.
- [x] Database ↔ Backend dependencies documented.
- [x] runtime implementation boundary documented.
- [ ] Backend/team must confirm the listed open decisions before Sprint 2 integration.

## 10. Implemented model details and runtime boundary

The current SQLAlchemy metadata implements `games`, `moves`, and `game_analysis`:

- `games.id`, `moves.id`, and `game_analysis.id` are PostgreSQL `BIGINT IDENTITY` primary keys.
- `moves.game_id` and `game_analysis.game_id` are non-null foreign keys to `games.id`; `game_analysis.move_id` is nullable and references `moves.id`.
- `moves` enforces player `X`/`O`, row/column `0..14`, positive `move_number`, and unique `(game_id, move_number)`.
- `game_analysis` enforces each optional best-move coordinate to be null or `0..14`.
- Timestamp columns use timezone-aware `DateTime` and server `now()` defaults where defined.
- ORM relationships connect games with moves and analyses. The move relationship does not declare ordering; callers must order moves explicitly. No delete cascade is declared.
- The schema intentionally does not enforce the proposed game mode/status enums, status/result consistency, ended-at rules, unique occupied cells, analysis/game composite association, or the users entity because those contracts remain open.

`app/db/database.py` reads `DATABASE_URL` only when `get_engine()` is called. It does not load `.env`, initialize tables, or run migrations. `GameService` and the current API do not call the database helper or repository. A successful direct-model test therefore proves schema behavior only, not game API persistence.

PostgreSQL tests use `TEST_DATABASE_URL`, a generated schema per test, and cleanup scoped to that schema. They are gated by `CAROAI_TEST_DATABASE_CONFIRMED=disposable-test-database` as an explicit operator confirmation, a database name containing a `test` token, and rejection of names containing `prod`/`live`. The name check is a guardrail, not proof of database purpose. The confirmation must only be set after checking the target database; schema creation/drop requires PostgreSQL privileges for those operations.

## 11. Sprint 2 verification scope

The model-level tests exercise fresh-session reads, move order via explicit query ordering, foreign keys, unique move numbers, CHECK constraints, nullable analysis move references, and transaction rollback. They do not assert ORM relationship ordering, cascade semantics, or API persistence. Open decisions in Section 6 remain pending M1/team confirmation.
