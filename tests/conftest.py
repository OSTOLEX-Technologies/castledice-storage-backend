import asyncio
from datetime import datetime

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload
from fastapi.testclient import TestClient
from uow.base_classes import DEFAULT_SESSION_FACTORY, engine as DEFAULT_ENGINE

from db import Base, User as SQLAlchemyUser, Game as SQLAlchemyGame, Asset, UsersAssets as SQLAlchemyUsersAssets
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
    async def wrap(session_factory, name: str, auth_id: int):
        async with session_factory() as session:
            user = SQLAlchemyUser(name=name, auth_id=auth_id)
            session.add(user)
            await session.commit()
            result = await session.scalars(
                select(SQLAlchemyUser).filter(SQLAlchemyUser.auth_id == user.auth_id).options(
                    joinedload(SQLAlchemyUser.wallet),
                    joinedload(SQLAlchemyUser.games),
                    joinedload(
                        SQLAlchemyUser.games_won),
                    joinedload(SQLAlchemyUser.users_assets),
                    ))
            user = result.first()
            return user, user.to_domain()

    return wrap


@pytest.fixture
def create_game(create_user):
    async def wrap(session_factory):
        async with session_factory() as session:
            game = SQLAlchemyGame(config={"test": "test"}, game_started_time=datetime.utcnow(),
                                  game_ended_time=datetime.utcnow(), users=[
                    (await create_user(session_factory, "test1", auth_id=1))[0],
                    (await create_user(session_factory, "test2", auth_id=2))[0]
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
def general_create_asset():
    async def wrap(session_factory, ipfs_cid: str, id_: int | None = None):
        async with session_factory() as session:
            asset = Asset(ipfs_cid=ipfs_cid)
            if id_:
                asset.id = id_
            session.add(asset)
            await session.commit()
            result = await session.scalars(
                select(Asset).filter(Asset.id == asset.id)
            )
            return result.first().to_domain()
    return wrap


@pytest.fixture
def create_asset_inmemory(general_create_asset, session_factory):
    async def wrap(ipfs_cid: str, id_: int | None = None):
        return await general_create_asset(session_factory, ipfs_cid, id_)
    return wrap


@pytest.fixture
def create_users_asset():
    async def wrapper(session_factory, asset_id: int, user_id: int, nft_id: int, is_locked: bool = False):
        async with session_factory() as session:
            users_asset = SQLAlchemyUsersAssets(user_id=user_id, asset_id=asset_id, nft_id=nft_id, is_locked=is_locked)
            session.add(users_asset)
            await session.commit()
            await session.refresh(users_asset)
            users_asset = await session.scalars(
                select(SQLAlchemyUsersAssets).filter(SQLAlchemyUsersAssets.nft_id == users_asset.nft_id).options(
                    joinedload(SQLAlchemyUsersAssets.asset)
                )
            )
            return users_asset.first().to_domain()
    return wrapper


@pytest.fixture
def create_users_asset_inmemory(create_users_asset, session_factory):
    async def wrapper(user_id: int, asset_id: int, nft_id: int, is_locked: bool = False):
        return await create_users_asset(session_factory, asset_id, user_id, nft_id, is_locked)
    return wrapper


@pytest_asyncio.fixture
async def create_assets_tests_data(create_asset_inmemory, create_user, session_factory, create_users_asset_inmemory):
    await create_asset_inmemory("test_asset1", 1)
    await create_asset_inmemory("test_asset2", 2)
    await create_user(session_factory, "test_user1", 1)
    await create_user(session_factory, "test_user2", 2)
    await create_users_asset_inmemory(1, 1, 10, False)
    await create_users_asset_inmemory(2, 2, 11, False)
    await create_users_asset_inmemory(2, 2, 12, False)


@pytest.fixture
def session_factory(in_memory_db, create_db):
    return sessionmaker(bind=in_memory_db, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture
def session(session_factory):
    return session_factory()


@pytest.fixture
def client():
    return TestClient(app)
