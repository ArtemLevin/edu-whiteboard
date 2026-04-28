import asyncio

from app.db.session import AsyncSessionLocal
from app.models.exercise import Exercise


async def main() -> None:
    async with AsyncSessionLocal() as session:
        exercises = [
            Exercise(
                title="Квадратное уравнение",
                content="Решите уравнение: 2x² − 5x − 3 = 0.",
                subject="math",
                topic="quadratic_equations",
                difficulty="easy",
                answer="x = 3; x = -1/2",
            ),
            Exercise(
                title="Производная",
                content="Найдите производную функции f(x)=x³−4x²+7.",
                subject="math",
                topic="derivatives",
                difficulty="medium",
                answer="f'(x)=3x²−8x",
            ),
        ]
        session.add_all(exercises)
        await session.commit()
        print("Seed completed")


if __name__ == "__main__":
    asyncio.run(main())
