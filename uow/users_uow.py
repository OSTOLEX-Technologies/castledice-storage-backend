from abc import ABC, abstractproperty

from repositories.users_repository import SQLAlchemyUsersRepository, UsersRepository
from .base_classes import SqlAlchemyUnitOfWork, AbstractUnitOfWork


class UsersUnitOfWork(AbstractUnitOfWork, ABC):
    users: UsersRepository = None


class UsersSqlAlchemyUnitOfWork(SqlAlchemyUnitOfWork, UsersUnitOfWork):
    def init_repository(self):
        self.users = SQLAlchemyUsersRepository(self.session)
