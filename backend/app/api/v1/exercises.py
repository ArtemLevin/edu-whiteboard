from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.schemas.exercise import ExerciseCreate, ExerciseRead
from app.services.exercise_service import ExerciseService

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=list[ExerciseRead])
async def list_exercises(session: AsyncSession = Depends(get_session)):
    service = ExerciseService(session)
    return await service.list_exercises()


@router.post("", response_model=ExerciseRead, status_code=status.HTTP_201_CREATED)
async def create_exercise(payload: ExerciseCreate, session: AsyncSession = Depends(get_session)):
    service = ExerciseService(session)
    exercise = await service.create_exercise(payload)
    await session.commit()
    return exercise


@router.get("/{exercise_id}", response_model=ExerciseRead)
async def get_exercise(exercise_id: UUID, session: AsyncSession = Depends(get_session)):
    service = ExerciseService(session)
    return await service.get_exercise(exercise_id)
