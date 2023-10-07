from repositories.in_db_classes import GameInDB
from uow.game_uow import GameUnitOfWork
from domain.game import Game


async def get_game(game_id: int, uow: GameUnitOfWork) -> GameInDB:
    async with uow:
        return await uow.games.get_game(game_id)


async def create_game(game: GameInDB, uow: GameUnitOfWork) -> GameInDB:
    async with uow:
        game = await uow.games.create_game(game)
        await uow.commit()
        return game
