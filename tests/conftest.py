import asyncio

import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from db import Base


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


@pytest.fixture
def session_factory(in_memory_db, create_db):
    return sessionmaker(bind=in_memory_db, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture
def session(session_factory):
    return session_factory()
