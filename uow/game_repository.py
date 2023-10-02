from repositories.game_repository import SQLAlchemyGameRepository
from .base import SqlAlchemyUnitOfWork


class GameSqlAlchemyUnitOfWork(SqlAlchemyUnitOfWork):
    def init_repository(self):
        self.games = SQLAlchemyGameRepository(self.session)
