import os

from databases import Database
from dotenv import load_dotenv

from models import Downtime, User

load_dotenv()

DATABASE_URL = str(os.getenv("DATABASE_URL"))
database = Database(DATABASE_URL)

async def query_user(username: str):
    query = """
    SELECT
        user_id,
        user_name,
        password_hash
    FROM users
    left join roles on users.user_role_id = roles.role_id
    WHERE user_name = :username
    """
    return await database.fetch_one(
        query, values={"username": username.lower()}
    )

async def query_all_users():
    """Get only user names in a list"""
    query = "select user_name from users;"
    users = await database.fetch_all(query)
    return [x['user_name'] for x in users]


async def query_all_roles():
    """Get only role names in a list"""
    query = "select role_name from roles;"
    roles = await database.fetch_all(query)
    return [x['role_name'] for x in roles]


async def query_roles():
    query = "select role_id, role_name, role_description from roles;"
    roles = await database.fetch_all(query)
    return roles


async def update_existing_user(user: User) -> bool:
    """Update user in database"""
    roles = await query_roles()
    roles = {x['role_name']: x['role_id'] for x in roles}

    query = """
        UPDATE OR ROLLBACK users
        SET 
        user_name = :user_name,
        user_role_id = :user_role_id,
        password_hash = :password_hash
        where user_name == :user_name;
            """
    values = {"user_name": user.user_name,
              "user_role_id": roles[user.role_name],
              "password_hash": user.password_hash}
    result = await database.execute(query, values)
    return bool(result)


async def write_new_user(user: User) -> bool:
    """Write new user to database"""
    roles = await query_roles()
    roles = {x['role_name']: x['role_id'] for x in roles}

    query = """
        INSERT OR ROLLBACK INTO users
        (user_name, user_role_id, password_hash)
        VALUES
        (:user_name, :user_role_id, :password_hash);
            """
    values = {"user_name": user.user_name,
              "user_role_id": roles[user.role_name],
              "password_hash": user.password_hash}
    result = await database.execute(query, values)
    return bool(result)


async def db_delete_user(username: str):
    query = """
        DELETE FROM users
        WHERE user_name = :username;
    """
    values = {"username": username}
    result = await database.execute(query, values)
    return bool(result)


async def read_downtimes():
    query = """select
            downtime_id, downtime_start, downtime_end, user_id, comment
            from downtime;
        """
    all_items = await database.fetch_all(query)
    result = []
    for record in all_items:
        id, start, end, user_id, comment = record
        schedule_item = {
            "id": id,
            "start": start,
            "end": end,
            "user_id": user_id,
            "comment": comment,
        }
        result.append(schedule_item)
    return result


async def create_downtime(downtime: Downtime):

    user = await query_user(downtime.user_name)
    user_id = user.user_id

    statement = """
        INSERT INTO downtime
        (downtime_start, downtime_end, user_id, comment)
        VALUES
        (:start_time, :end_time, :user_id, :comment);
    """

    values = {
        "start_time": downtime.start_time,
        "end_time": downtime.end_time,
        "user_id": user_id,
        "comment": downtime.comment,
    }

    result = await database.execute(statement, values=values)
    return bool(result)


async def delete_downtime(downtime_id: int):
    query = """
        DELETE FROM downtime
        WHERE downtime_id = :downtime_id;
    """
    values = {"downtime_id": downtime_id}
    result = await database.execute(query, values)
    return result