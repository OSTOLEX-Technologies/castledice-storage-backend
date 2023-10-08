import abc

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.game import Game
from .exceptions import DoesNotExistException
from db import Game as SQLAlchemyGame, User as SQLAlchemyUser
from .in_db_classes import UserInDB


class GameInDB(Game):
    id: int
    users: list[UserInDB]
    winner: UserInDB | None


class GameRepository:
    class GameDoesNotExist(DoesNotExistException):
        class_name = 'Game'

    @abc.abstractmethod
    def get_game(self, game_id: int) -> GameInDB:
        raise NotImplementedError

    @abc.abstractmethod
    def create_game(self, game: GameInDB):
        raise NotImplementedError

    # @abc.abstractmethod
    # def update_game(self, game: GameInDB):
    #     raise NotImplementedError
    #
    # @abc.abstractmethod
    # def delete_game(self, game_id: int) -> None:
    #     raise NotImplementedError


class SQLAlchemyGameRepository(GameRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_game(self, game_id: int) -> GameInDB:
        game = (await self.session.scalars(
            select(SQLAlchemyGame).filter(SQLAlchemyGame.id == game_id).options(
                selectinload(SQLAlchemyGame.users).subqueryload(SQLAlchemyUser.wallet),
                selectinload(SQLAlchemyGame.winner),
            )
        )).first()
        if not game:
            raise self.GameDoesNotExist(game_id)
        return game.to_domain()

    async def create_game(self, game: GameInDB) -> GameInDB:
        users = (await self.session.execute(
            select(SQLAlchemyUser).filter(SQLAlchemyUser.id.in_([user.id for user in game.users])))).scalars().all()
        game_in_db = SQLAlchemyGame(
            config=game.config,
            game_started_time=game.game_started_time,
            game_ended_time=game.game_ended_time,
            winner=game.winner,
            users=users,
            history=game.history,
        )
        self.session.add(game_in_db)
        await self.session.flush()
        return game_in_db.to_domain()
