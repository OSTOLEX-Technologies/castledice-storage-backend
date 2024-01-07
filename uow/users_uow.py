from abc import ABC

from repositories.users_repository import UsersRepository, SQLAlchemyUsersRepository
from .base_classes import SqlAlchemyUnitOfWork, AbstractUnitOfWork


class UsersUnitOfWork(AbstractUnitOfWork, ABC):
    users: UsersRepository


class UsersSqlAlchemyUnitOfWork(SqlAlchemyUnitOfWork, UsersUnitOfWork):
    def init_repository(self):
        self.users = SQLAlchemyUsersRepository(self.session)
