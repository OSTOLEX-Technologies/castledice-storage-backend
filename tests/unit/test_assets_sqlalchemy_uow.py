import pytest

from uow.assets_uow import AssetsSqlAlchemyUnitOfWork, AssetsUnitOfWork
from uow.base_classes import SqlAlchemyUnitOfWork
from repositories.assets_repository import AssetsRepository, SQLAlchemyAssetsRepository


@pytest.mark.asyncio
async def test_assets_uow_instantiation(default_session_factory):
    uow = AssetsSqlAlchemyUnitOfWork(default_session_factory)
    assert isinstance(uow, SqlAlchemyUnitOfWork)
    assert isinstance(uow, AssetsUnitOfWork)

    async with uow:
        assert isinstance(uow.assets, SQLAlchemyAssetsRepository)
        assert uow.session.is_active
