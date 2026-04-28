from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.events.base import AttemptSubmittedEvent
from app.events.publisher import EventPublisher
from app.models.attempt import AttemptStatus, SolutionAttempt
from app.repositories.attempt_repository import AttemptRepository
from app.repositories.exercise_repository import ExerciseRepository


class AttemptService:
    def __init__(self, session: AsyncSession, publisher: EventPublisher | None = None) -> None:
        self.session = session
        self.repo = AttemptRepository(session)
        self.exercise_repo = ExerciseRepository(session)
        self.publisher = publisher or EventPublisher()

    async def create_or_get_draft(self, user_id: UUID, exercise_id: UUID) -> SolutionAttempt:
        exercise = await self.exercise_repo.get_by_id(exercise_id)
        if exercise is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

        existing = await self.repo.get_existing_draft(user_id=user_id, exercise_id=exercise_id)
        if existing is not None:
            return existing

        attempt = SolutionAttempt(user_id=user_id, exercise_id=exercise_id, board_state={})
        return await self.repo.add(attempt)

    async def get_attempt(self, attempt_id: UUID) -> SolutionAttempt:
        attempt = await self.repo.get_by_id(attempt_id)
        if attempt is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
        return attempt

    async def save_board_state(self, attempt_id: UUID, board_state: dict) -> SolutionAttempt:
        attempt = await self.get_attempt(attempt_id)
        if attempt.status == AttemptStatus.checked:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Checked attempt cannot be modified",
            )
        attempt.board_state = board_state
        await self.session.flush()
        await self.session.refresh(attempt)
        return attempt

    async def submit(self, attempt_id: UUID) -> SolutionAttempt:
        attempt = await self.get_attempt(attempt_id)
        attempt.status = AttemptStatus.submitted
        await self.session.flush()
        await self.session.refresh(attempt)

        event = AttemptSubmittedEvent.create(
            attempt_id=attempt.id,
            exercise_id=attempt.exercise_id,
            user_id=attempt.user_id,
        )
        await self.publisher.publish(topic="attempts", event=event)
        return attempt

    async def add_teacher_comment(self, attempt_id: UUID, comment: str) -> SolutionAttempt:
        attempt = await self.get_attempt(attempt_id)
        attempt.teacher_comment = comment
        attempt.status = AttemptStatus.checked
        await self.session.flush()
        await self.session.refresh(attempt)
        return attempt
