from abc import ABC
from repositories.assets_repository import AssetsRepository, SQLAlchemyAssetsRepository
from .base_classes import SqlAlchemyUnitOfWork, AbstractUnitOfWork


class AssetsUnitOfWork(AbstractUnitOfWork, ABC):
    assets: AssetsRepository


class AssetsSqlAlchemyUnitOfWork(SqlAlchemyUnitOfWork, AssetsUnitOfWork):
    def init_repository(self):
        self.assets = SQLAlchemyAssetsRepository(self.session)
