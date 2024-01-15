from repositories.in_db_classes import UserInDB
from uow.users_uow import UsersUnitOfWork
from domain.user import User


async def get_user(user_id: int, uow: UsersUnitOfWork) -> User:
    async with uow:
        return await uow.users.get_user(user_id)


async def create_user(user: User, uow: UsersUnitOfWork) -> UserInDB:
    async with uow:
        user = await uow.users.create_user(user)
        await uow.commit()
        return user


async def update_user_by_auth_id(user_data: User, uow: UsersUnitOfWork) -> User:
    async with uow:
        user = await uow.users.get_user_by_auth_id(user_data.auth_id)
        user.name = user_data.name
        if user_data.wallet:
            if not user.wallet:
                user.wallet = user_data.wallet
            user.wallet.address = user_data.wallet.address
        updated_user = await uow.users.update_user(user_data)
        await uow.commit()
        return updated_user


async def delete_user_by_auth_id(auth_id: int, uow: UsersUnitOfWork) -> bool:
    async with uow:
        await uow.users.delete_user(auth_id)
        await uow.commit()
        return True
