import structlog

from app.core.config import get_settings
from app.events.base import DomainEvent

logger = structlog.get_logger(__name__)
settings = get_settings()


class EventPublisher:
    """Абстракция публикации событий.

    Сейчас no-op: для MVP Kafka не нужна.
    Позже сюда можно подключить Kafka без переписывания сервисов.
    """

    async def publish(self, topic: str, event: DomainEvent) -> None:
        logger.info(
            "domain_event_published_noop",
            topic=topic,
            event=event.to_dict(),
            kafka_enabled=settings.kafka_enabled,
        )
