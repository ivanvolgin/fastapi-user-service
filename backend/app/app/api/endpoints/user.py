from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncConnection
from app.db.database import get_connection
from app.src.user.schemes import UserCreate
from app.src.user.service import create_user_in_db, show_users_in_db

router = APIRouter()


@router.post("/")
async def create_user(
    conn: Annotated[AsyncConnection, Depends(get_connection)],
    user: UserCreate,
) -> dict:
    await create_user_in_db(conn, user)
    return {"message": "User created", "user": user}


@router.get("/show")
async def show_users(
    conn: Annotated[AsyncConnection, Depends(get_connection)],
):
    return await show_users_in_db(conn)
