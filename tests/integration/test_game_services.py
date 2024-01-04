from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from repositories.exceptions import GameDoesNotExist
from repositories.in_db_classes import CreateGame
from services.games_services import get_game, create_game
from uow.game_uow import GameSqlAlchemyUnitOfWork
from db import Game as SQLAlchemyGame, User as SQLAlchemyUser


async def create_user_manual(session, name: str, auth_id: int):
    user = SQLAlchemyUser(name=name, auth_id=auth_id)
    session.add(user)
    await session.commit()
    result = await session.scalars(
        select(SQLAlchemyUser).filter(SQLAlchemyUser.auth_id == user.auth_id).options(joinedload(SQLAlchemyUser.wallet),
                                                                                      joinedload(SQLAlchemyUser.games),
                                                                                      joinedload(
                                                                                          SQLAlchemyUser.games_won),
                                                                                      joinedload(SQLAlchemyUser.users_assets),
                                                                                      ))
    return result.first()


async def create_game_manual(session):
    game = SQLAlchemyGame(config={"test": "test"}, game_started_time=datetime.utcnow(),
                          game_ended_time=datetime.utcnow(), users=[
            await create_user_manual(session, "test1", auth_id=1),
            await create_user_manual(session, "test2", auth_id=2)
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
    with pytest.raises(GameDoesNotExist):
        await get_game(1, uow)


@pytest.mark.asyncio
async def test_create_game_creates_game(session_factory):
    async with session_factory() as session:
        user1 = await create_user_manual(session, "test1", auth_id=1)
        user2 = await create_user_manual(session, "test2", auth_id=2)

    uow = GameSqlAlchemyUnitOfWork(session_factory)
    game = await create_game(CreateGame(config={"test": "test"}, game_started_time=datetime.utcnow(),
                                        game_ended_time=datetime.utcnow(), users=[user1.auth_id, user2.auth_id],
                                        winner=None, history=None), uow)
    assert game.id is not None
    game2 = await get_game(game.id, uow)
    assert game2 == game
