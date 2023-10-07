from datetime import datetime

import pytest
from services.games_services import get_game, create_game
from uow.game_uow import GameSqlAlchemyUnitOfWork
from db import Game as SQLAlchemyGame


async def create_game_manual(session):
    game = SQLAlchemyGame(config={"test": "test"}, game_started_time=datetime.utcnow(),
                    game_ended_time=datetime.utcnow(), users=[], winner=None, history=None)
    session.add(game)
    await session.commit()
    return game


@pytest.mark.asyncio
async def test_get_game(session_factory):
    async with session_factory() as session:
        game = await create_game_manual(session)

    uow = GameSqlAlchemyUnitOfWork(session_factory)
    game2 = await get_game(game.id, uow)
    assert game2.id == game.id


@pytest.mark.asyncio
async def test_create_game(session_factory):
    uow = GameSqlAlchemyUnitOfWork(session_factory)
    game = await create_game(SQLAlchemyGame(config={"test": "test"}, game_started_time=datetime.utcnow(),
                    game_ended_time=datetime.utcnow(), users=[], winner=None, history=None), uow)
    assert game.id is not None
