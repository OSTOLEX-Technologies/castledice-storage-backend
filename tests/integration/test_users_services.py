import pytest
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from repositories.exceptions import UserDoesNotExist
from repositories.in_db_classes import WalletInDB
from services.users_services import get_user, create_user, update_user_by_auth_id
from uow.users_uow import UsersSqlAlchemyUnitOfWork
from db import User as SQLAlchemyUser
from domain.wallet import Wallet
from domain.user import User


async def create_user_manual(session):
    user = SQLAlchemyUser(name="test", auth_id=1)
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


@pytest.mark.asyncio
async def test_get_user_returns_found_user(session_factory):
    async with session_factory() as session:
        user = await create_user_manual(session)
        user = user.to_domain()

    uow = UsersSqlAlchemyUnitOfWork(session_factory)
    user2 = await get_user(user.auth_id, uow)
    assert user2 == user


@pytest.mark.asyncio
async def test_get_user_raises_exception_when_user_not_found(session_factory):
    uow = UsersSqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(UserDoesNotExist):
        await get_user(1, uow)


@pytest.mark.asyncio
async def test_create_user_creates_user(session_factory):
    uow = UsersSqlAlchemyUnitOfWork(session_factory)
    await create_user(User(name="test1", auth_id=1, wallet=Wallet(address="address1")),
                      uow)  # just to check that create_user() returns correct user after creation
    user = await create_user(User(name="test2", auth_id=2, wallet=Wallet(address="address2")), uow)

    assert user.auth_id is not None
    user2 = await get_user(2, uow)
    assert user2 == user


@pytest.mark.asyncio
async def test_update_user_by_auth_id_updates_user(session_factory):
    uow = UsersSqlAlchemyUnitOfWork(session_factory)
    await create_user(User(name="test2", auth_id=1, wallet=Wallet(address="address2")), uow)
    user = await update_user_by_auth_id(User(name="test3", auth_id=1, wallet=Wallet(address="address3")), uow)
    assert user.name == "test3"
    assert user.wallet.address == "address3"
    assert user.auth_id is not None
    user2 = await get_user(1, uow)
    assert user2 == user


@pytest.mark.asyncio
async def test_update_user_by_auth_id_updates_user_when_adding_wallet(session_factory):
    uow = UsersSqlAlchemyUnitOfWork(session_factory)
    await create_user(User(name="test1", auth_id=1), uow)
    assert (await get_user(1, uow)).wallet is None

    user = await update_user_by_auth_id(User(name="test1", auth_id=1, wallet=Wallet(address="address1")), uow)
    assert user.name == "test1"
    assert user.wallet.address == "address1"
    assert isinstance(user.wallet, WalletInDB)
    assert user.auth_id is not None
    user2 = await get_user(1, uow)
    assert user2 == user
