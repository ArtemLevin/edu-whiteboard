from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.attempt import AttemptStatus


class AttemptCreate(BaseModel):
    user_id: UUID
    exercise_id: UUID


class BoardStateUpdate(BaseModel):
    # tldraw/excalidraw state — произвольный JSON, но обязательно объект.
    board_state: dict[str, Any] = Field(default_factory=dict)


class AttemptStatusUpdate(BaseModel):
    status: AttemptStatus


class TeacherCommentUpdate(BaseModel):
    teacher_comment: str = Field(min_length=1, max_length=5000)


class AttemptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    exercise_id: UUID
    board_state: dict[str, Any]
    status: AttemptStatus
    teacher_comment: str | None
    created_at: datetime
    updated_at: datetime
