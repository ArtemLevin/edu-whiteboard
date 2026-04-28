from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exercise import Exercise
from app.repositories.exercise_repository import ExerciseRepository
from app.schemas.exercise import ExerciseCreate


class ExerciseService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ExerciseRepository(session)

    async def list_exercises(self) -> list[Exercise]:
        return await self.repo.list()

    async def get_exercise(self, exercise_id: UUID) -> Exercise:
        exercise = await self.repo.get_by_id(exercise_id)
        if exercise is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
        return exercise

    async def create_exercise(self, payload: ExerciseCreate) -> Exercise:
        exercise = Exercise(**payload.model_dump())
        return await self.repo.add(exercise)
