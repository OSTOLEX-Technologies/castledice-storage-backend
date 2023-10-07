import abc

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from db import User as SQLAlchemyUser, Wallet as SQLAlchemyWallet
from domain.user import User
from repositories.exceptions import DoesNotExistException
from repositories.in_db_classes import UserInDB


class UsersRepository(abc.ABC):
    @abc.abstractmethod
    async def get_user(self, user_id: int) -> UserInDB:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_user(self, user: User) -> UserInDB:
        raise NotImplementedError


class SQLAlchemyUsersRepository(UsersRepository):
    class UserDoesNotExist(DoesNotExistException):
        class_name = 'User'

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: int) -> UserInDB:
        try:
            return (await self.session.execute(select(SQLAlchemyUser)
            .filter(SQLAlchemyUser.id == user_id)
            .options(
                joinedload(SQLAlchemyUser.wallet),
                joinedload(SQLAlchemyUser.games),
                joinedload(SQLAlchemyUser.games_won)
            ))).scalar().to_domain()
        except AttributeError:
            raise self.UserDoesNotExist(user_id)

    async def create_user(self, user: User) -> UserInDB:
        orm_user = SQLAlchemyUser(
            name=user.name,
        )
        self.session.add(orm_user)

        if user.wallet:
            wallet = SQLAlchemyWallet(
                address=user.wallet.address,
                user=orm_user,
            )
            self.session.add(wallet)
        await self.session.flush()
        result = await self.session.scalars(
            select(SQLAlchemyUser).options(joinedload(SQLAlchemyUser.wallet),
                                           joinedload(SQLAlchemyUser.games),
                                           joinedload(SQLAlchemyUser.games_won))
        )
        return result.first().to_domain()
