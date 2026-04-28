from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from uuid import UUID


@dataclass(frozen=True)
class DomainEvent:
    event_name: str
    occurred_at: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class AttemptSubmittedEvent(DomainEvent):
    attempt_id: str
    exercise_id: str
    user_id: str

    @classmethod
    def create(cls, attempt_id: UUID, exercise_id: UUID, user_id: UUID) -> "AttemptSubmittedEvent":
        return cls(
            event_name="attempt.submitted",
            occurred_at=datetime.now(timezone.utc).isoformat(),
            attempt_id=str(attempt_id),
            exercise_id=str(exercise_id),
            user_id=str(user_id),
        )
