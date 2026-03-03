import logging
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool
from urllib.parse import quote

logger = logging.getLogger(__name__)

def build_pg_connectin(
        db:str,
        user:str,
        password:str,
        host:str,
        port:int,
    ):
    conninfo = f'postgresql://{quote(user, safe= '')}:{quote(password, safe='')}@{host}:{port}/{db}'
    logger.debug(f"Connecting to\n postgresql://{quote(user, safe= '')}:{quote(password, safe='')}@{host}:{port}/{db} ")
    return conninfo

async def get_pg_connection(
        db:str,
        user:str,
        password:str,
        host:str,
        port:int,
    )->AsyncConnection:
    conninfo = build_pg_connectin(db, user, password, host, port)
    conn: AsyncConnection | None = None
    try:
        conn = await AsyncConnection.connect(conninfo)
        logger.debug(f"Connection succeeded")
        return conn
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        if conn:
           await conn.close()
        raise

async def get_pg_pool(
        db:str,
        user:str,
        password:str,
        host:str,
        port:int,
        min_size:int=1,
        max_size:int=3,
        timeout: float|None= 60.0,
    ):
    conninfo = build_pg_connectin(db, user, password, host, port)
    db_pool: AsyncConnectionPool | None = None
    try:
        db_pool = AsyncConnectionPool(
            conninfo=conninfo,
            min_size=min_size,
            max_size=max_size,
            timeout=timeout,
            open = False
        )

        await db_pool.open()

        async with db_pool.connection() as conn:
            logger.debug(f"Connection succeeded")
        return db_pool
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        if db_pool and not db_pool.closed:
            await db_pool.close()
        raise
