import pytest
from services.games_services import get_game
from uow.game_uow import GameSqlAlchemyUnitOfWork
from repositories.in_db_classes import GameInDB


@pytest.mark.asyncio
async def test_get_game_by_id_returns_found_game(client, create_game, default_session_factory):
    game = await create_game(default_session_factory)
    response = client.get(f"/game/{game.id}")
    assert response.status_code == 200
    assert GameInDB(**response.json()) == game


@pytest.mark.asyncio
async def test_get_game_by_id_returns_not_found(client, default_session_factory):
    response = client.get("/game/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "The Game with the given id 1 does not exist."}


@pytest.mark.asyncio
async def test_create_game_endpoint_creates_game(client, create_user, default_session_factory):
    _, user1 = await create_user(default_session_factory, "test1", auth_id=1)
    _, user2 = await create_user(default_session_factory, "test2", auth_id=2)
    response = client.post("/game", json={"config": {"test": "test"}, "game_started_time": "2021-01-01T00:00:00",
                                          "game_ended_time": None, "users": [user1.id, user2.id],
                                          "winner": None, "history": None})
    assert response.status_code == 201
    assert response.json()["status"] == "created"
    assert response.json()["game"]["config"] == {"test": "test"}

    game = await get_game(response.json()["game"]["id"], GameSqlAlchemyUnitOfWork(default_session_factory))
    assert game == GameInDB(**response.json()["game"])


@pytest.mark.asyncio
async def test_create_game_endpoint_returns_not_found_when_user_does_not_exist(client, default_session_factory):
    response = client.post("/game", json={"config": {"test": "test"}, "game_started_time": "2021-01-01T00:00:00",
                                          "game_ended_time": None, "users": [1, 2],
                                          "winner": None, "history": None})
    assert response.status_code == 404
    assert (response.json() ==
            {"detail": "The User with the given id 1 does not exist."})
