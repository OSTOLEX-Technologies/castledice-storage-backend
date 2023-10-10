from fastapi import APIRouter

from domain.user import User
from uow.users_uow import UsersSqlAlchemyUnitOfWork
from services.users_services import get_user, create_user


router = APIRouter()


@router.get("/user/{user_id}")
async def get_user_by_id(user_id: int):
    uow = UsersSqlAlchemyUnitOfWork()
    user = await get_user(user_id, uow)
    return user.model_dump()


@router.post("/user", status_code=201)
async def create_user_(user: User):
    uow = UsersSqlAlchemyUnitOfWork()
    user = await create_user(user, uow)
    return {"status": "created", "user": user.model_dump()}
