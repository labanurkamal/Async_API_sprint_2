from typing import Optional

import asyncpg

postgres: Optional[asyncpg.Connection] = None


async def get_postgres() -> Optional[asyncpg.Connection]:
    return postgres
