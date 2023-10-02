import abc

from sqlalchemy.ext.asyncio import AsyncSession

from db import User as SQLAlchemyUser
from repositories.in_db_classes import UserInDB


class UsersRepository(abc.ABC):
    @abc.abstractmethod
    def get_user(self, user_id: int) -> UserInDB:
        raise NotImplementedError

    @abc.abstractmethod
    def create_user(self, user: UserInDB) -> None:
        raise NotImplementedError


class SQLAlchemyUsersRepository(UsersRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: int) -> UserInDB:
        return (await self.session.get(SQLAlchemyUser, user_id)).to_domain()

    async def create_user(self, user: UserInDB) -> None:
        orm_user = SQLAlchemyUser(
            name=user.name,
        )
        self.session.add(orm_user)
