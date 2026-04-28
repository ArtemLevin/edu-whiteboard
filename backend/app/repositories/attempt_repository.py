from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attempt import AttemptStatus, SolutionAttempt
from app.repositories.base import BaseRepository


class AttemptRepository(BaseRepository[SolutionAttempt]):
    model = SolutionAttempt

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_user(self, user_id: UUID) -> list[SolutionAttempt]:
        stmt = select(SolutionAttempt).where(SolutionAttempt.user_id == user_id)
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def list_submitted(self) -> list[SolutionAttempt]:
        stmt = select(SolutionAttempt).where(SolutionAttempt.status == AttemptStatus.submitted)
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def get_existing_draft(self, user_id: UUID, exercise_id: UUID) -> SolutionAttempt | None:
        stmt = select(SolutionAttempt).where(
            SolutionAttempt.user_id == user_id,
            SolutionAttempt.exercise_id == exercise_id,
            SolutionAttempt.status == AttemptStatus.draft,
        )
        result = await self.session.scalars(stmt)
        return result.first()
