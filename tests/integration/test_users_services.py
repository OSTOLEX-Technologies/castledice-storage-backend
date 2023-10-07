import pytest
from services.users_services import get_user, create_user
from uow.users_uow import UsersSqlAlchemyUnitOfWork
from db import User as SQLAlchemyUser


async def create_user_manual(session):
    user = SQLAlchemyUser(name="test")
    session.add(user)
    await session.commit()
    return user


@pytest.mark.asyncio
async def test_get_user(session_factory):
    async with session_factory() as session:
        user = await create_user_manual(session)

    uow = UsersSqlAlchemyUnitOfWork(session_factory)
    user2 = await get_user(user.id, uow)
    assert user2.id == user.id


@pytest.mark.asyncio
async def test_create_user(session_factory):
    uow = UsersSqlAlchemyUnitOfWork(session_factory)
    user = await create_user(SQLAlchemyUser(name="test2"), uow)
    assert user.id is not None
