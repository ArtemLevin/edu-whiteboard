import enum
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class AttemptStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    checked = "checked"


class SolutionAttempt(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "solution_attempts"

    # В MVP user_id просто UUID. Позже заменим на связь с таблицей users.
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    exercise_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    board_state: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[AttemptStatus] = mapped_column(
        Enum(AttemptStatus, name="attempt_status"),
        nullable=False,
        default=AttemptStatus.draft,
    )
    teacher_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    exercise = relationship("Exercise", back_populates="attempts")
