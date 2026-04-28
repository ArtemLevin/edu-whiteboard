from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Exercise(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "exercises"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str] = mapped_column(String(100), nullable=False, default="math")
    topic: Mapped[str] = mapped_column(String(100), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False, default="medium")
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)

    attempts = relationship("SolutionAttempt", back_populates="exercise")
