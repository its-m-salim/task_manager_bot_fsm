from connection import *


async def create_user(username, full_name, tg_id):
    try:
        conn = await connection_db()
        await conn.execute("""
        insert into users(username, full_name, telegram_id) values
            ($1, $2, $3)
""", username, full_name, str(tg_id))

    except Exception as error:
        print(f"{type(error)}: {error} scu.py")     
    finally:
        await conn.close()   


async def profile(tg_id):
    try:
        conn = await connection_db()
        user = await conn.fetchrow("""
        select * from users
        where telegram_id = $1
""", str(tg_id))

        return user
    except Exception as error:
        print(f"{type(error)}: {error} sp.py")     
    finally:
        await conn.close()   




async def create_task(title, caption, due_date, tg_id):
    try:
        conn = await connection_db()
        await conn.execute("""
        insert into tasks(title, caption, due_date, owner_id) values
            ($1, $2, $3, $4)
""", title, caption, due_date, str(tg_id))
        return True
    except Exception as error:
        print(f"{type(error)}: {error} sct.py")   
        return False  
    finally:
        await conn.close()   


async def update_task(title, caption, due_date, status, tg_id, id):
    try:
        conn = await connection_db()
        await conn.execute("""
        update tasks
        set title = $1,
        caption = $2,
        due_date = $3,
        status = $4
        where id = $5 and owner_id = $6
""", title, caption, due_date, status, int(id), str(tg_id))
        return True
    except Exception as error:
        print(f"{type(error)}: {error} sut.py")
        return False     
    finally:
        await conn.close()   


async def delete_task(id, tg_id):
    try:
        conn = await connection_db()
        await conn.execute("""
        delete from tasks
        where id = $1 and owner_id = $2
""", int(id), str(tg_id))
        return True
    except Exception as error:
        print(f"{type(error)}: {error} sdt.py")  
        return False   
    finally:
        await conn.close()   






async def get_tasks(tg_id):
    try:
        conn = await connection_db()
        tasks = await conn.fetch("""
        select * from tasks
        where owner_id = $1
        """, str(tg_id))
        return tasks
    except Exception as error:
        print(f"{type(error)}: {error} sgt.py")
    finally:
        await conn.close()



async def get_task_by_id(tg_id, task_id):
    try:
        conn = await connection_db()
        task = await conn.fetchrow("""
        select u.full_name as owner, t.id, t.title, t.caption,
        t.due_date, t.status, t.created_at
        from tasks as t
        join users as u on u.telegram_id = t.owner_id
        where t.owner_id = $1 and t.id = $2
        """, str(tg_id), task_id)
        return task
    except Exception as error:
        print(f"{type(error)}: {error} sgbi.py")
    finally:
        await conn.close()