import abc

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .exceptions import DoesNotExistException, GameDoesNotExist, UserDoesNotExist
from db import Game as SQLAlchemyGame, User as SQLAlchemyUser
from .in_db_classes import GameInDB, CreateGame
from domain.game import Game


class GameRepository:
    @abc.abstractmethod
    def get_game(self, game_id: int) -> GameInDB:
        raise NotImplementedError

    @abc.abstractmethod
    def create_game(self, game: Game):
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
                selectinload(SQLAlchemyGame.users).subqueryload(SQLAlchemyUser.users_assets),
                selectinload(SQLAlchemyGame.winner),
            )
        )).first()
        if not game:
            raise GameDoesNotExist(game_id)
        return game.to_domain()

    async def create_game(self, game: CreateGame) -> GameInDB:
        users = (await self.session.execute(
            select(SQLAlchemyUser).filter(SQLAlchemyUser.auth_id.in_([id_ for id_ in game.users])))).scalars().all()
        if not len(users) == len(game.users):
            diff = set(game.users) - set([user.auth_id for user in users])
            for id_ in diff:
                raise UserDoesNotExist(id_)
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
        result = (await self.session.scalars(
            select(SQLAlchemyGame).filter(SQLAlchemyGame.id == game_in_db.id).options(
                selectinload(SQLAlchemyGame.users).subqueryload(SQLAlchemyUser.wallet),
                selectinload(SQLAlchemyGame.users).subqueryload(SQLAlchemyUser.users_assets),
                selectinload(SQLAlchemyGame.winner),
            ))).first()
        return result.to_domain()
