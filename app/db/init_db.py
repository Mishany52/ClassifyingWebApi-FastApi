import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base
from ..config import settings

logger = logging.getLogger(__name__)
# Создание асинхронного движка
engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)


async def init_db():
    async with engine.begin() as conn:
        
        # Создание всех таблиц на основе моделей
        await conn.run_sync(Base.metadata.create_all)

    # Освобождение ресурсов движка
    await engine.dispose()


# Функция для асинхронной сессии
sessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)
