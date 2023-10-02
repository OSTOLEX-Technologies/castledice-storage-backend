from repositories.users_repository import SQLAlchemyUsersRepository
from .base import SqlAlchemyUnitOfWork


class UsersSqlAlchemyUnitOfWork(SqlAlchemyUnitOfWork):
    def init_repository(self):
        self.users = SQLAlchemyUsersRepository(self.session)
