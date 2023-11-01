import pytest

from domain.wallet import Wallet
from repositories.users_repository import UsersRepository
from services.users_services import get_user, create_user
from domain.user import User
from uow.users_uow import UsersUnitOfWork
from uow.base_classes import AbstractUnitOfWork


class FakeUsersRepository(UsersRepository):
    def __init__(self, users: dict[int, User]):
        self.users = users

    async def get_user(self, user_id: int) -> User:
        return self.users[user_id]

    async def create_user(self, user: User) -> User:
        self.users[max(self.users or [0]) + 1] = user
        return user


class FakeUnitOfWork(AbstractUnitOfWork, UsersUnitOfWork):
    def __init__(self):
        self.users = FakeUsersRepository(users={})
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
async def test_get_user_uses_passed_uow():
    user = User(name="test", auth_id=1, wallet=Wallet(address="test"), games=[], games_won=[])
    uow = FakeUnitOfWork()
    uow.users.users = {1: user}
    assert (await get_user(1, uow)).name == user.name
    assert not uow.commited


@pytest.mark.asyncio
async def test_create_user_uses_passed_uow():
    user = User(name="test", auth_id=1, wallet=Wallet(address="test"), games=[], games_won=[])
    uow = FakeUnitOfWork()
    await create_user(user, uow)
    assert uow.users.users[1].name == user.name
    assert uow.commited
