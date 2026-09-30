from .game_state import BOARD_SIZE, GameState, GameStatus, Move, Player


class InvalidMoveError(ValueError):
    """Raised when a move violates game rules."""


class GameRules:
    DIRECTIONS = (
        (0, 1),   # horizontal
        (1, 0),   # vertical
        (1, 1),   # diagonal \
        (1, -1),  # diagonal /
    )

    @staticmethod
    def validate_move(state: GameState, row: int, col: int) -> None:
        if state.status != GameStatus.IN_PROGRESS:
            raise InvalidMoveError("Game is already finished")

        if not (0 <= row < BOARD_SIZE):
            raise InvalidMoveError("Row must be between 0 and 14")

        if not (0 <= col < BOARD_SIZE):
            raise InvalidMoveError("Column must be between 0 and 14")

        if state.board[row][col] != "EMPTY":
            raise InvalidMoveError("Cell is already occupied")

    @staticmethod
    def apply_move(state: GameState, row: int, col: int) -> Move:
        GameRules.validate_move(state, row, col)

        player = state.current_player

        state.board[row][col] = player.value
        state.move_count += 1

        move = Move(
            row=row,
            col=col,
            player=player,
            move_number=state.move_count,
        )

        if GameRules.has_won(state, row, col, player):
            state.status = (
                GameStatus.X_WON
                if player == Player.X
                else GameStatus.O_WON
            )
            state.winner = player

        elif state.move_count == BOARD_SIZE * BOARD_SIZE:
            state.status = GameStatus.DRAW

        else:
            state.current_player = (
                Player.O if player == Player.X else Player.X
            )

        return move

    @staticmethod
    def has_won(
        state: GameState,
        row: int,
        col: int,
        player: Player,
    ) -> bool:
        for dr, dc in GameRules.DIRECTIONS:
            count = 1

            count += GameRules._count_direction(
                state, row, col, player, dr, dc
            )

            count += GameRules._count_direction(
                state, row, col, player, -dr, -dc
            )

            if count >= 5:
                return True

        return False

    @staticmethod
    def _count_direction(
        state: GameState,
        row: int,
        col: int,
        player: Player,
        dr: int,
        dc: int,
    ) -> int:
        count = 0
        r = row + dr
        c = col + dc

        while (
            0 <= r < BOARD_SIZE
            and 0 <= c < BOARD_SIZE
            and state.board[r][c] == player.value
        ):
            count += 1
            r += dr
            c += dc

        return count