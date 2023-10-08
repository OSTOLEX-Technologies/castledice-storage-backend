from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from services.games_services import get_game, create_game
from uow.game_uow import GameSqlAlchemyUnitOfWork
from db import Game as SQLAlchemyGame, User as SQLAlchemyUser
from repositories.game_repository import GameRepository


async def create_user_manual(session, name: str):
    user = SQLAlchemyUser(name=name)
    session.add(user)
    await session.commit()
    result = await session.scalars(
        select(SQLAlchemyUser).filter(SQLAlchemyUser.id == user.id).options(joinedload(SQLAlchemyUser.wallet),
                                                                            joinedload(SQLAlchemyUser.games),
                                                                            joinedload(SQLAlchemyUser.games_won))
    )
    return result.first()


async def create_game_manual(session):
    game = SQLAlchemyGame(config={"test": "test"}, game_started_time=datetime.utcnow(),
                          game_ended_time=datetime.utcnow(), users=[
        await create_user_manual(session, "test1"),
        await create_user_manual(session, "test2")
        ], winner=None, history=None)
    session.add(game)
    await session.commit()
    return game


@pytest.mark.asyncio
async def test_get_game_returns_found_game(session_factory):
    async with session_factory() as session:
        game = await create_game_manual(session)

    uow = GameSqlAlchemyUnitOfWork(session_factory)
    game2 = await get_game(game.id, uow)
    assert game2 == game.to_domain()


@pytest.mark.asyncio
async def test_get_game_raises_exception_when_game_not_found(session_factory):
    uow = GameSqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(GameRepository.GameDoesNotExist):
        await get_game(1, uow)


@pytest.mark.asyncio
async def test_create_game_creates_game(session_factory):
    uow = GameSqlAlchemyUnitOfWork(session_factory)
    game = await create_game(SQLAlchemyGame(config={"test": "test"}, game_started_time=datetime.utcnow(),
                                            game_ended_time=datetime.utcnow(), users=[], winner=None, history=None),
                             uow)
    assert game.id is not None
    game2 = await get_game(game.id, uow)
    assert game2 == game
