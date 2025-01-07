import asyncio
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import text, Result
from app.db.database import engine, get_connection, init_db
from app.src.user.schemes import UserCreate


async def create_user_in_db(conn: AsyncConnection, user: UserCreate) -> dict:
    result = await conn.execute(
        text(
            f"""
        INSERT INTO users (name, age, email) 
        VALUES (:name, :age, :email)
    """
        ),
        {
            "name": user.name,
            "age": user.age,
            "email": user.email,
        },
    )
    await conn.commit()


async def show_users_in_db(conn: AsyncConnection):
    result = await conn.execute(
        text(
            f"""
        SELECT * 
        FROM users;
    """
        )
    )
    result = [
        {
            "id": raw[4],
            "name": raw[0],
            "age": raw[1],
            "email": raw[2],
            "created_at": raw[3],
        }
        for raw in result.fetchall()
    ]
    print(result)
    return result
