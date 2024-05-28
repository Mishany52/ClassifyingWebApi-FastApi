

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.init_db import sessionLocal
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with sessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
