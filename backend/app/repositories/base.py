from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelT = TypeVar("ModelT", bound=DeclarativeBase)


class BaseRepository(Generic[ModelT]):
    """Базовый repository.

    Здесь держим общие операции, чтобы не дублировать код по проекту.
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, item_id: UUID) -> ModelT | None:
        return await self.session.get(self.model, item_id)

    async def add(self, item: ModelT) -> ModelT:
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item
