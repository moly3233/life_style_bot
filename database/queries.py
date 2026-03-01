from psycopg import AsyncConnection
import datetime

async def load_today_to_db(conn: AsyncConnection, mood, day_desc, mentor_desc, conclusion):
    today = datetime.date.today()

    query = """
        INSERT INTO app.every_day_report 
        (date, mood, day_description, mentor_description, conclusion)
        VALUES (%s, %s, %s, %s, %s);
    """

    params = (today, mood, day_desc, mentor_desc, conclusion)

    async with conn.transaction():
        await conn.execute(query, params)