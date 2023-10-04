import abc

from sqlalchemy.ext.asyncio import AsyncSession

from db import User as SQLAlchemyUser, Wallet as SQLAlchemyWallet
from domain.user import User
from repositories.in_db_classes import UserInDB


class UsersRepository(abc.ABC):
    @abc.abstractmethod
    async def get_user(self, user_id: int) -> UserInDB:
        raise NotImplementedError

    @abc.abstractmethod
    async def create_user(self, user: User) -> None:
        raise NotImplementedError


class SQLAlchemyUsersRepository(UsersRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: int) -> UserInDB:
        return (await self.session.get(SQLAlchemyUser, user_id)).to_domain()

    async def create_user(self, user: User) -> None:
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
