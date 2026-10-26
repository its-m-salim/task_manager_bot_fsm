import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()
p_db = os.getenv("PASSWORD_DB")

async def connection_db():
    try:
        conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="salim",
        database="fsm_task_mn",
        password= p_db
        )
        return conn
    except Exception as error:
        print(f"{type(error)}: {error} conn.py")




async def create_tables():
    try:
        conn = await connection_db()
        await conn.execute("""
        create table if not exists users(
        id serial primary key,
        username varchar(200),
        full_name varchar(200),
        telegram_id varchar(200) unique,
        created_at timestamp default now(),
        is_active bool default true
    );
        create table if not exists tasks(
        id serial primary key,
        title varchar(100),
        caption text,
        due_date varchar(50),
        owner_id varchar(200) references users(telegram_id),
        created_at timestamp default now(),
        status bool default false,
        is_active bool default true)
""")
        print("Таблицы успешно созданы")
    except Exception as error:
        print(f"{type(error)}: {error} con.py")
    finally:
        await conn.close()