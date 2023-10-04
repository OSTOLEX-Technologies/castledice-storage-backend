from abc import ABC

from repositories.game_repository import SQLAlchemyGameRepository, GameRepository
from .base import SqlAlchemyUnitOfWork, AbstractUnitOfWork


class GameUnitOfWork(AbstractUnitOfWork, ABC):
    games: GameRepository = None


class GameSqlAlchemyUnitOfWork(SqlAlchemyUnitOfWork, GameUnitOfWork):
    def init_repository(self):
        self.games = SQLAlchemyGameRepository(self.session)
