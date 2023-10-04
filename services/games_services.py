from repositories.in_db_classes import GameInDB
from uow.game_uow import GameUnitOfWork
from domain.game import Game


async def get_game(game_id: int, uow: GameUnitOfWork) -> Game:
    async with uow:
        game = await uow.games.get_game(game_id)
        return game


async def create_game(game: GameInDB, uow: GameUnitOfWork):
    async with uow:
        game = await uow.games.create_game(game)
        await uow.commit()
        return game
