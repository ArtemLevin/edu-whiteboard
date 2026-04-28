from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exercise import Exercise
from app.repositories.base import BaseRepository


class ExerciseRepository(BaseRepository[Exercise]):
    model = Exercise

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list(self, limit: int = 50, offset: int = 0) -> list[Exercise]:
        stmt = select(Exercise).order_by(Exercise.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.scalars(stmt)
        return list(result.all())
