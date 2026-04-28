from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.schemas.attempt import AttemptCreate, AttemptRead, BoardStateUpdate, TeacherCommentUpdate
from app.services.attempt_service import AttemptService

router = APIRouter(prefix="/attempts", tags=["attempts"])


@router.post("", response_model=AttemptRead, status_code=status.HTTP_201_CREATED)
async def create_or_get_attempt(payload: AttemptCreate, session: AsyncSession = Depends(get_session)):
    service = AttemptService(session)
    attempt = await service.create_or_get_draft(
        user_id=payload.user_id,
        exercise_id=payload.exercise_id,
    )
    await session.commit()
    return attempt


@router.get("/{attempt_id}", response_model=AttemptRead)
async def get_attempt(attempt_id: UUID, session: AsyncSession = Depends(get_session)):
    service = AttemptService(session)
    return await service.get_attempt(attempt_id)


@router.patch("/{attempt_id}/board", response_model=AttemptRead)
async def save_board_state(
    attempt_id: UUID,
    payload: BoardStateUpdate,
    session: AsyncSession = Depends(get_session),
):
    service = AttemptService(session)
    attempt = await service.save_board_state(attempt_id, payload.board_state)
    await session.commit()
    return attempt


@router.post("/{attempt_id}/submit", response_model=AttemptRead)
async def submit_attempt(attempt_id: UUID, session: AsyncSession = Depends(get_session)):
    service = AttemptService(session)
    attempt = await service.submit(attempt_id)
    await session.commit()
    return attempt


@router.patch("/{attempt_id}/teacher-comment", response_model=AttemptRead)
async def add_teacher_comment(
    attempt_id: UUID,
    payload: TeacherCommentUpdate,
    session: AsyncSession = Depends(get_session),
):
    service = AttemptService(session)
    attempt = await service.add_teacher_comment(attempt_id, payload.teacher_comment)
    await session.commit()
    return attempt
