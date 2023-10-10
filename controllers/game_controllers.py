from fastapi import APIRouter
from repositories.in_db_classes import GameInDB, CreateGame
from uow.game_uow import GameSqlAlchemyUnitOfWork
from services.games_services import get_game, create_game
from domain.game import Game


router = APIRouter()


@router.get("/game/{game_id}")
async def get_game_by_id(game_id: int) -> GameInDB:
    uow = GameSqlAlchemyUnitOfWork()
    game = await get_game(game_id, uow)
    return game


@router.post("/game", status_code=201)
async def create_game_(game: CreateGame):
    uow = GameSqlAlchemyUnitOfWork()
    game = await create_game(game, uow)
    return {"status": "created", "game": game}
