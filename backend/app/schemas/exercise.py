from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExerciseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    subject: str = Field(default="math", min_length=1, max_length=100)
    topic: str = Field(min_length=1, max_length=100)
    difficulty: str = Field(default="medium", min_length=1, max_length=50)
    answer: str | None = None


class ExerciseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content: str
    subject: str
    topic: str
    difficulty: str
    answer: str | None
    created_at: datetime
    updated_at: datetime
