import asyncio
import os
from datetime import datetime

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload
from fastapi.testclient import TestClient
from uow.base_classes import DEFAULT_SESSION_FACTORY, engine as DEFAULT_ENGINE

from db import Base, User as SQLAlchemyUser, Game as SQLAlchemyGame
from main import app


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def in_memory_db():
    return create_async_engine('sqlite+aiosqlite:///:memory:')


@pytest_asyncio.fixture
async def create_db(in_memory_db):
    async with in_memory_db.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with in_memory_db.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def create_default_db():
    async with DEFAULT_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with DEFAULT_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def default_session_factory(create_default_db):
    return DEFAULT_SESSION_FACTORY


@pytest.fixture
def create_user():
    async def wrap(session_factory, name: str):
        async with session_factory() as session:
            user = SQLAlchemyUser(name=name)
            session.add(user)
            await session.commit()
            result = await session.scalars(
                select(SQLAlchemyUser).filter(SQLAlchemyUser.id == user.id).options(joinedload(SQLAlchemyUser.wallet),
                                                                                    joinedload(SQLAlchemyUser.games),
                                                                                    joinedload(
                                                                                        SQLAlchemyUser.games_won))
            )
            user = result.first()
            return user, user.to_domain()

    return wrap


@pytest.fixture
def create_game(create_user):
    async def wrap(session_factory):
        async with session_factory() as session:
            game = SQLAlchemyGame(config={"test": "test"}, game_started_time=datetime.utcnow(),
                                  game_ended_time=datetime.utcnow(), users=[
                    (await create_user(session_factory, "test1"))[0],
                    (await create_user(session_factory, "test2"))[0]
                ], winner=None, history=None)
            session.add(game)
            await session.commit()
            result = await session.scalars(
                select(SQLAlchemyGame).filter(SQLAlchemyGame.id == game.id).options(joinedload(SQLAlchemyGame.users),
                                                                                    joinedload(SQLAlchemyGame.winner))
            )
            return result.first().to_domain()
    return wrap


@pytest.fixture
def session_factory(in_memory_db, create_db):
    return sessionmaker(bind=in_memory_db, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture
def session(session_factory):
    return session_factory()


@pytest.fixture
def client():
    return TestClient(app)
