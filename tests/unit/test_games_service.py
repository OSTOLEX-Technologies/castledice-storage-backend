import pytest
from datetime import datetime
from repositories.in_db_classes import GameInDB, UserInDB
from uow.game_uow import GameUnitOfWork
from uow.base_classes import AbstractUnitOfWork
from repositories.game_repository import GameRepository
from domain.game import Game
from services.games_services import get_game, create_game


class FakeGamesRepository(GameRepository):
    def __init__(self, games: dict[int, Game]):
        self.games = games

    async def get_game(self, game_id: int) -> Game:
        return self.games[game_id]
        
    async def create_game(self, game: GameInDB) -> Game:
        self.games[max(self.games or [0]) + 1] = game
        return game


class FakeUnitOfWork(AbstractUnitOfWork, GameUnitOfWork):
    def __init__(self):
        self.games = FakeGamesRepository(games={})
        self.commited = False

    async def __aenter__(self):
        await super().__aenter__()
        return self

    async def __aexit__(self, *args):
        await super().__aexit__(*args)

    async def commit(self):
        self.commited = True

    async def rollback(self):
        pass


@pytest.mark.asyncio
async def test_get_game_returns_correct_game():
    winner = UserInDB(id=2, auth_id=2, name="test2", wallet=None, games=[], games_won=[])
    game = GameInDB(id=1, config={"test": "test"}, game_started_time=datetime.utcnow(), game_ended_time=datetime.utcnow(), users=[
                UserInDB(id=1, auth_id=1, name="test", wallet=None, games=[], games_won=[]),
                winner,
    ], winner=winner, history={"test": "test"})
    uow = FakeUnitOfWork()
    uow.games.games = {1: game}
    assert (await get_game(1, uow)) == game
    assert not uow.commited


@pytest.mark.asyncio
async def test_create_game_creates_game():
    game = GameInDB(id=1, config={"test": "test"}, game_started_time=datetime.utcnow(),
                    game_ended_time=datetime.utcnow(), users=[], winner=None, history=None)
    uow = FakeUnitOfWork()
    await create_game(game, uow)
    assert uow.games.games[1] == game
    assert uow.commited
