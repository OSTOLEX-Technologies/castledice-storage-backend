import pytest

from domain.wallet import Wallet
from repositories.users_repository import UsersRepository
from services.users_services import get_user, create_user, delete_user_by_auth_id, update_user_by_auth_id
from domain.user import User
from uow.users_uow import UsersUnitOfWork
from uow.base_classes import AbstractUnitOfWork


class FakeUsersRepository(UsersRepository):
    def __init__(self, users: dict[int, User]):
        self.users = users

    async def get_user(self, auth_id: int) -> User:
        return self.users[auth_id]

    async def get_user_by_auth_id(self, auth_id: int) -> User:
        return [user for user in self.users.values() if user.auth_id == auth_id][0]

    async def create_user(self, user: User) -> User:
        self.users[max(self.users or [0]) + 1] = user
        return user

    async def update_user(self, user: User) -> User:
        self.users[user.auth_id] = user
        return user

    async def delete_user(self, auth_id: int) -> bool:
        self.users.pop(auth_id)
        return True


class FakeUnitOfWork(UsersUnitOfWork):
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


@pytest.mark.asyncio
async def test_update_user_uses_passed_uow():
    user = User(name="test", auth_id=1, wallet=Wallet(address="test"), games=[], games_won=[])
    uow = FakeUnitOfWork()
    uow.users.users = {1: user}
    user.name = "test1"
    await update_user_by_auth_id(user, uow)
    assert uow.users.users[1].name == user.name
    assert uow.commited


@pytest.mark.asyncio
async def test_delete_user_uses_passed_uow():
    user = User(name="test", auth_id=1, wallet=Wallet(address="test"), games=[], games_won=[])
    uow = FakeUnitOfWork()
    uow.users.users = {1: user}
    await delete_user_by_auth_id(1, uow)
    assert 1 not in uow.users.users
    assert uow.commited
