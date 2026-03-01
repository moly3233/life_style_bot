from psycopg import AsyncConnection
from psycopg.rows import dict_row
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

async def get_all_dates_query(conn: AsyncConnection) -> list[str]:
    query = """
        SELECT date
        FROM app.every_day_report
        ORDER BY date DESC;
        """
    async with conn.cursor() as cur:
        await cur.execute(query)
        rows = await cur.fetchall()
        dates = [('Отчет за '+row[0].strftime('%Y-%m-%d')) for row in rows]

    return dates

async def get_report_for_date_query(conn: AsyncConnection, date: str)-> dict:
    query = """
        SELECT *
        FROM app.every_day_report
        WHERE date = %s
    """
    params = (date,)
    async with conn.cursor(row_factory= dict_row) as cur:
        await cur.execute(query, params)
        result = await cur.fetchone()
        if result is None:
            return None
        return result

