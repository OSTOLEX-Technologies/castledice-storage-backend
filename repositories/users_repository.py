import abc

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from db import User as SQLAlchemyUser, Wallet as SQLAlchemyWallet
from domain.user import User
from repositories.exceptions import DoesNotExistException, UserDoesNotExist
from repositories.in_db_classes import UserInDB


class UsersRepository(abc.ABC):
    @abc.abstractmethod
    async def get_user(self, user_id: int) -> UserInDB:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_user_by_auth_id(self, auth_id: int) -> UserInDB:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_user(self, user: User) -> UserInDB:
        raise NotImplementedError

    @abc.abstractmethod
    async def update_user(self, user: User) -> UserInDB:
        raise NotImplementedError


class SQLAlchemyUsersRepository(UsersRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_user_with_filter(self, sqlalchemy_user_filter) -> SQLAlchemyUser:
        user = (await self.session.scalars(select(SQLAlchemyUser)
        .filter(sqlalchemy_user_filter)
        .options(
            joinedload(SQLAlchemyUser.wallet),
            joinedload(SQLAlchemyUser.games),
            joinedload(SQLAlchemyUser.games_won)
        ))).first()
        return user

    async def get_user(self, user_id: int) -> UserInDB:
        user = await self._get_user_with_filter(SQLAlchemyUser.id == user_id)
        if not user:
            raise UserDoesNotExist(user_id)
        return user.to_domain()

    async def get_user_by_auth_id(self, auth_id: int) -> UserInDB:
        user = await self._get_user_with_filter(SQLAlchemyUser.auth_id == auth_id)
        if not user:
            raise UserDoesNotExist(auth_id)
        return user.to_domain()

    async def create_user(self, user: User) -> UserInDB:
        orm_user = SQLAlchemyUser(
            name=user.name,
            auth_id=user.auth_id,
        )
        self.session.add(orm_user)

        if user.wallet:
            wallet = SQLAlchemyWallet(
                address=user.wallet.address,
                user=orm_user,
            )
            self.session.add(wallet)
        await self.session.flush()
        result = await self._get_user_with_filter(SQLAlchemyUser.id == orm_user.id)
        return result.to_domain()

    async def update_user(self, user: User) -> UserInDB:
        orm_user = await self._get_user_with_filter(SQLAlchemyUser.auth_id == user.auth_id)
        if not orm_user:
            raise DoesNotExistException(f'User with id {user.auth_id} does not exist')
        orm_user.name = user.name
        if orm_user.wallet and orm_user.wallet.address:
            orm_user.wallet.address = user.wallet.address
        elif not orm_user.wallet:
            wallet = SQLAlchemyWallet(address=user.wallet.address, user=orm_user)
            self.session.add(wallet)
        await self.session.flush()
        return orm_user.to_domain()
