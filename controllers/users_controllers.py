from fastapi import APIRouter

from domain.user import User
from uow.users_uow import UsersSqlAlchemyUnitOfWork
from services.users_services import get_user, create_user, update_user_by_auth_id


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


@router.put("/authuser")
async def _update_user_by_auth_id(user: User):
    uow = UsersSqlAlchemyUnitOfWork()
    user = await update_user_by_auth_id(user, uow)
    return {"status": "updated", "user": user.model_dump()}
