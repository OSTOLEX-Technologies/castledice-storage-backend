import pytest
from services.users_services import get_user
from uow.users_uow import UsersSqlAlchemyUnitOfWork


@pytest.mark.asyncio
async def test_get_user_by_id_returns_found_user(client, create_user, default_session_factory):
    _, user = await create_user(default_session_factory, "test", auth_id=1)
    response = client.get(f"/user/{user.auth_id}")
    assert response.status_code == 200
    assert response.json() == user.model_dump()


@pytest.mark.asyncio
async def test_get_user_by_id_returns_not_found(client, default_session_factory):
    response = client.get("/user/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "The User with the given auth_id 1 does not exist."}


@pytest.mark.asyncio
async def test_create_user_endpoint_creates_user(client, default_session_factory):
    response = client.post("/user", json={"name": "test", "auth_id": 1, "wallet": {"address": "test"}})
    assert response.status_code == 201
    assert response.json()["status"] == "created"
    assert response.json()["user"]["name"] == "test"
    assert response.json()["user"]["auth_id"] == 1
    assert response.json()["user"]["wallet"]["address"] == "test"

    user = await get_user(response.json()["user"]["auth_id"], UsersSqlAlchemyUnitOfWork(default_session_factory))
    assert user.model_dump() == response.json()["user"]


@pytest.mark.asyncio
async def test_update_user_by_auth_id(client, create_user, default_session_factory):
    _, user = await create_user(default_session_factory, "test", auth_id=1)
    response = client.put("/authuser", json={"name": "test", "auth_id": 1, "wallet": {"address": "test"}})
    assert response.status_code == 200
    assert response.json()["status"] == "updated"
    assert response.json()["user"]["name"] == "test"
    assert response.json()["user"]["auth_id"] == 1
    assert response.json()["user"]["wallet"]["address"] == "test"

    user = await get_user(response.json()["user"]["auth_id"], UsersSqlAlchemyUnitOfWork(default_session_factory))
    assert user.model_dump() == response.json()["user"]


@pytest.mark.asyncio
async def test_delete_user_by_auth_id(client, create_user, default_session_factory):
    _, user = await create_user(default_session_factory, "test", auth_id=1)
    response = client.delete("/user/1")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"

    response = client.get("/user/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "The User with the given auth_id 1 does not exist."}
