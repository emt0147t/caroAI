"""Narrowly scoped endpoints for controlled production acceptance runs."""

from collections.abc import Iterator

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from app.api.dependencies import get_game_service
from app.api.qa_security import (
    MAX_QA_GAMES_PER_RUN,
    QARequestLimiter,
    acquire_qa_operation,
    verify_capability,
)
from app.db.repository import GamePersistenceError, QARunLimitExceededError
from app.schemas.game import GameCreateRequest, GameResponse
from app.services.game_service import GameService


def _require_qa_enabled(request: Request) -> None:
    if request.app.state.qa_config is None:
        raise HTTPException(status_code=404, detail="Not found")


router = APIRouter(
    prefix="/api/qa",
    tags=["production-qa"],
    dependencies=[Depends(_require_qa_enabled)],
)

_request_limiter = QARequestLimiter()


def _authorize_qa_run(
    request: Request,
    run_id: str = Header(
        ...,
        alias="X-CaroAI-QA-Run-ID",
        min_length=32,
        max_length=32,
        pattern="^[0-9a-f]{32}$",
    ),
    capability: str | None = Header(
        None,
        alias="X-CaroAI-QA-Capability",
        max_length=160,
    ),
) -> Iterator[tuple[str, int]]:
    """Authenticate a short-lived capability separately from its run scope."""
    config = request.app.state.qa_config
    if config is None or capability is None or not verify_capability(
        run_id, capability, config.hmac_secret
    ):
        raise HTTPException(
            status_code=401,
            detail="A valid QA capability is required.",
            headers={"WWW-Authenticate": "CaroAI-QA"},
        )

    if not _request_limiter.allow(run_id):
        raise HTTPException(
            status_code=429,
            detail="QA request rate limit exceeded.",
            headers={"Retry-After": "60"},
        )

    expires_at = int(capability.split(".", 2)[1])
    with acquire_qa_operation() as acquired:
        if not acquired:
            raise HTTPException(
                status_code=429,
                detail="QA operation capacity is temporarily full.",
                headers={"Retry-After": "1"},
            )
        yield run_id, expires_at


@router.post("/games", response_model=GameResponse, status_code=201)
def create_qa_game(
    request: GameCreateRequest,
    authorization: tuple[str, int] = Depends(_authorize_qa_run),
    service: GameService = Depends(get_game_service),
):
    """Create a normal authoritative game tagged for exact-run cleanup."""
    run_id, expires_at = authorization
    try:
        game_id, state = service.create_game_with_state(
            request.mode,
            qa_run_id=run_id,
            qa_max_games=MAX_QA_GAMES_PER_RUN,
            qa_expires_at=expires_at,
        )
    except QARunLimitExceededError as exc:
        raise HTTPException(
            status_code=429,
            detail="This QA run has reached its game creation limit.",
            headers={"Retry-After": "600"},
        ) from exc
    except GamePersistenceError as exc:
        raise HTTPException(
            status_code=503, detail="Game storage is temporarily unavailable."
        ) from exc
    return GameResponse(
        id=game_id,
        mode=state.mode,
        status=state.status,
        current_player=state.current_player,
        move_count=state.move_count,
        winner=state.winner,
        board=state.board,
    )


@router.delete("/runs")
def cleanup_qa_run(
    authorization: tuple[str, int] = Depends(_authorize_qa_run),
    service: GameService = Depends(get_game_service),
):
    """Delete only the QA games created with the exact supplied run capability."""
    run_id, _expires_at = authorization
    try:
        deleted_ids = service.delete_qa_run(run_id)
    except GamePersistenceError as exc:
        raise HTTPException(
            status_code=503, detail="Game storage is temporarily unavailable."
        ) from exc
    return {
        "deleted_count": len(deleted_ids),
        "deleted_game_ids": deleted_ids,
    }
