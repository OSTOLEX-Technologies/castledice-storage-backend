from uow.users_uow import UsersUnitOfWork
from domain.user import User


async def get_user(user_id: int, uow: UsersUnitOfWork) -> User:
    async with uow:
        user = await uow.users.get_user(user_id)
        return user


async def create_user(user: User, uow: UsersUnitOfWork):
    async with uow:
        user = await uow.users.create_user(user)
        await uow.commit()
        return user
