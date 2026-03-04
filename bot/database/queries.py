from psycopg import AsyncConnection
from psycopg.rows import dict_row
import datetime
from typing import List, Tuple

async def load_today_to_db(conn: AsyncConnection, tg_id, mood, day_desc, mentor_desc, conclusion):
    today = datetime.date.today()

    query = """
        INSERT INTO app.every_day_report 
        (tg_id,date, mood, day_description, mentor_description, conclusion)
        VALUES (%s ,%s, %s, %s, %s, %s);
    """

    params = (str(tg_id),today, mood, day_desc, mentor_desc, conclusion)
    async with conn.cursor() as cur:
        await cur.execute(query, params)
    await conn.commit()


async def get_all_dates_query(conn: AsyncConnection, tg_id) -> list[str]:
    query = """
        SELECT date
        FROM app.every_day_report
        WHERE tg_id = %s
        ORDER BY date DESC;
        """
    params = (str(tg_id),)
    async with conn.cursor() as cur:
        await cur.execute(query, params)
        rows = await cur.fetchall()
        dates = [('Отчет за '+row[0].strftime('%Y-%m-%d')) for row in rows]
        if len(dates) == 0:
            dates.append('У вас пока нет отчетов')

    return dates

async def get_report_for_date_query(conn: AsyncConnection, date: str,tg_id:int)-> dict:
    query = """
        SELECT *
        FROM app.every_day_report
        WHERE date = %s AND tg_id = %s
    """
    params = (date, str(tg_id))
    async with conn.cursor(row_factory= dict_row) as cur:
        await cur.execute(query, params)
        result = await cur.fetchone()
        if result is None:
            return None
        return result

async def has_report_today(conn: AsyncConnection, tg_id: int) -> bool:
    today = datetime.date.today().strftime('%Y-%m-%d')
    query = """
        SELECT date
        from app.every_day_report
        WHERE date = %s AND tg_id = %s
    """
    params = (today, str(tg_id))
    async with conn.cursor() as cur:
        await cur.execute(query, params)
        row = await cur.fetchone()
    return row is not None

async def get_all_tg_id_query(conn: AsyncConnection) -> list:
    query = """
        SELECT DISTINCT tg_id
        FROM app.every_day_report
    """
    async with conn.cursor() as cur:
        await cur.execute(query)
        rows = await cur.fetchall()
        ids = [int(row[0]) for row in rows]

    return ids


async def get_date_mood_for(
        conn: AsyncConnection,
        tg_id: int,
        days: int = 30
) -> Tuple[List[str], List[int]]:
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days - 1)

    query = """
        SELECT date, mood
        FROM app.every_day_report
        WHERE tg_id = %s 
          AND date BETWEEN %s AND %s
        ORDER BY date ASC  
    """

    params = (str(tg_id), start_date, today)

    async with conn.cursor() as cur:
        await cur.execute(query, params)
        rows = await cur.fetchall()

        if not rows:
            print(f"Нет отчётов для tg_id={tg_id} за последние {days} дней")
            return [], []

        dates = [row[0].strftime('%Y-%m-%d') for row in rows]
        moods = [row[1] for row in rows]

        print("Получены данные:")
        print("dates:", dates)
        print("moods:", moods)

        return dates, moods