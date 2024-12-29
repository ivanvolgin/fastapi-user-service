from fastapi import APIRouter
from app.user.schemes import *

router = APIRouter(prefix='/user', tags=['User'])


@router.post('/')
def is_user_adult(user: User):
    return {
        'name': user.name,
        'age': user.age,
        'is_adult': user.age >= 18
    }
