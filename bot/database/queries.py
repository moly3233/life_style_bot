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
    start_date = today - datetime.timedelta(days=days )

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

async def get_all_day_descriptions_for(conn: AsyncConnection, tg_id: int, days: int):
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days)

    query = """
        SELECT day_description
        FROM app.every_day_report
        WHERE tg_id = %s AND date BETWEEN %s AND %s
        ORDER BY date ASC
    """
    params = (str(tg_id), start_date, today)

    async with conn.cursor() as cur:
        await cur.execute(query, params)
        rows = await cur.fetchall()
        if not rows:
             raise Exception

        descriptions = [desc[0] for desc in rows]
        print(descriptions)
        return descriptions

async def load_target(conn: AsyncConnection, tg_id: int, target_text:str):
    today = datetime.date.today()

    query = """
        INSERT INTO app.users_targets (tg_id, target_text, created_at, is_active)
        VALUES (%s, %s, %s, True)
    """
    params = (str(tg_id), target_text, today)

    async with conn.cursor() as cur:
        await cur.execute(query, params)
    await conn.commit()

async def get_active_targets_query(conn: AsyncConnection, tg_id: int):
    query = """
        SELECT target_text
        FROM app.users_targets
        WHERE tg_id = %s AND is_active = True
        ORDER BY created_at DESC
    """
    params = (str(tg_id),)
    async with conn.cursor() as cur:
        await cur.execute(query, params)
        rows = await cur.fetchall()
        targets = ['~ '+ row[0] for row in rows]
        if not rows:
            return []
        else:
            return targets

async def set_status_target_query(conn: AsyncConnection, tg_id: int, target_text: str):
    query = """ 
        UPDATE app.users_targets
        SET is_active = False
        WHERE tg_id = %s AND target_text = %s
    """
    params = (str(tg_id), target_text)
    async with conn.cursor() as cur:
        await cur.execute(query, params)
    await conn.commit()

async def load_user_training_query(
        conn: AsyncConnection,
        tg_id: int,
        training_name:str,
        mood_before:int,
        training_log:str,
        mood_after:int,
        feelings_after:str,
        mentor_comment:str
):
    today = datetime.date.today().strftime('%Y-%m-%d')

    query = """
        INSERT INTO app.users_trainings VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (str(tg_id),today, training_name, mood_before, training_log,mood_after, feelings_after, mentor_comment)

    async with conn.cursor() as cur:
        await cur.execute(query, params)
    await conn.commit()


async def get_user_bmi(conn: AsyncConnection, tg_id: int):
    query = """ 
            SELECT measured_at, height_cm, weight_kg, bmi
            FROM app.users_imt_metrics
            WHERE tg_id = %s AND is_active = True
            ORDER BY measured_at desc
            LIMIT 1
        """
    params = (str(tg_id),)
    async with conn.cursor() as cur:
        await cur.execute(query, params)
        row = await cur.fetchone()
        if row is None:
            return False
        else:
            res = {
                'measured_at': row[0],
                'height_cm': row[1],
                'weight_kg': row[2],
                'bmi': row[3]
            }
        return res


async def get_trainings_dates(conn: AsyncConnection, tg_id: int):
    query = """ 
        SELECT date
        FROM app.users_trainings
        WHERE tg_id = %s 
        ORDER BY date DESC
    """
    params = (str(tg_id),)
    async with conn.cursor() as cur:
        await cur.execute(query, params)
        rows = await cur.fetchall()
        res = ['Тренировка за '+ row[0].strftime('%Y-%m-%d') for row in rows]
        if not rows:
            return ['Тренировок нет']
        return res

async def get_training_info_query(conn: AsyncConnection, tg_id:int, training_date:str):
    query = """
        SELECT date, training_name, mood_before, training_log, mood_after, feelings_after, mentor_comment
        FROM app.users_trainings
        WHERE tg_id = %s AND date = %s
    """
    params = (str(tg_id), training_date)
    async with conn.cursor() as cur:
        await cur.execute(query, params)
        row = await cur.fetchone()
        if row is None:
            return None
        res = {
            'date': row[0],
            'training_name': row[1],
            'mood_before': row[2],
            'training_log': row[3],
            'mood_after': row[4],
            'feelings_after': row[5],
            'mentor_comment': row[6]
        }
    return res

async def change_weight_query(conn: AsyncConnection, tg_id: int, weight: int):
    today = datetime.date.today().strftime('%Y-%m-%d')

    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT height_cm 
            FROM app.users_imt_metrics
            WHERE tg_id = %s AND is_active = TRUE
            ORDER BY measured_at DESC
            LIMIT 1
            """,
            (str(tg_id),)
        )
        height_row = await cur.fetchone()

    height_cm = height_row[0] if height_row else None

    async with conn.transaction():

        await conn.execute(
            """
            UPDATE app.users_imt_metrics
            SET is_active = FALSE
            WHERE tg_id = %s AND is_active = TRUE
            """,
            (str(tg_id),)
        )

        await conn.execute(
            """
            INSERT INTO app.users_imt_metrics 
                (tg_id, measured_at, height_cm, weight_kg, is_active)
            VALUES (%s, %s, %s, %s, TRUE)
            """,
            (str(tg_id), today, height_cm, weight,)
        )
    await conn.commit()

async def change_height_query(conn:AsyncConnection, tg_id: int, height: int):
    today = datetime.date.today().strftime('%Y-%m-%d')

    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT weight_kg 
            FROM app.users_imt_metrics
            WHERE tg_id = %s AND is_active = TRUE
            ORDER BY measured_at DESC
            LIMIT 1
            """,
            (str(tg_id),)
        )
        weight_row =await cur.fetchone()
    weight_kg = weight_row[0] if weight_row else None

    async with conn.transaction():
        await conn.execute(
            """ 
            UPDATE app.users_imt_metrics
            SET is_active = FALSE
            WHERE tg_id = %s AND is_active = TRUE
            """,
            (str(tg_id),)
        )
    await conn.commit()

    async with conn.transaction():
        await conn.execute(
            """
            INSERT INTO app.users_imt_metrics VALUES
            (%s, %s,%s,%s)
            """,
            (str(tg_id), today, height, weight_kg,)
        )
    await conn.commit()


async def get_id_admins_query(conn: AsyncConnection):
    async with conn.cursor() as cur:
        await cur.execute(
            """ 
                SELECT tg_id
                FROM app.users_role
                WHERE role = 'admin'
            """
        )
        admin_row = await cur.fetchall()
    admin_ids = [row[0] for row in admin_row]
    return admin_ids

async def get_id_users_query(conn: AsyncConnection):
    async with conn.cursor() as cur:
        await cur.execute(
            """
                SELECT tg_id
                FROM app.users_role
            """
        )
        users_row = await cur.fetchall()
    user_ids = [row[0] for row in users_row]
    return user_ids

async def get_date_weight_query(conn:AsyncConnection, tg_id: int):
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=30)).strftime('%Y-%m-%d')

    query = """
        SELECT subquery.measured_at, subquery.weight
        FROM (
            select tg_id, measured_at, height_cm, coalesce(weight_kg,0) as weight,bmi, is_active
            from app.users_imt_metrics
            ) subquery
        WHERE tg_id = %s AND measured_at between %s AND %s
    """
    params = (str(tg_id), start_date, today.strftime('%Y-%m-%d'))

    async with conn.cursor() as cur:
        await cur.execute(query, params)
        rows = await cur.fetchall()
        if not rows:
            return None
        dates = [row[0].strftime('%Y-%m-%d') for row in rows]
        weights = [float(row[1]) for row in rows if row[1] is not None]
    return dates, weights


async def get_trainings_log_for_month_query(conn: AsyncConnection, tg_id: int):
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=30)).strftime('%Y-%m-%d')

    query = """
    SELECT training_name, training_log, feelings_after
    FROM users_trainings
    WHERE tg_id = %s AND date BETWEEN %s AND %s
    """
    params = (str(tg_id), start_date, today.strftime('%Y-%m-%d'))

    async with conn.cursor() as cur:
        await cur.execute(query, params)
        rows = await cur.fetchall()
        if not rows:
            return None
        names = [row[0] for row in rows]
        trainings_logs = [row[1] for row in rows]
        feelings_after =  [row[2] for row in rows]

    return names, trainings_logs, feelings_after

async def insert_user_to_users_integrations(conn: AsyncConnection, tg_id: int):
    query = """
        INSERT INTO user_integrations (tg_id) VALUES (%s);
    """
    params = (str(tg_id),)
    async with conn.cursor() as cur:
        await cur.execute(query, params)
        await conn.commit()

async def input_notion_token_query(conn:AsyncConnection,tg_id:int, notion_token:str):
    query = """
        UPDATE user_integrations
        SET notion_token = %s
        WHERE tg_id = %s;
    """
    params = ( notion_token, str(tg_id), )

    async with conn.cursor() as cur:
        await cur.execute(query, params)
        await conn.commit()
