import abc

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from db import engine

DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class AbstractUnitOfWork(abc.ABC):
    async def __aenter__(self) -> 'AbstractUnitOfWork':
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    @abc.abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    @abc.abstractmethod
    def init_repository(self):
        raise NotImplementedError

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()  # type: ignore # There will be AsyncSession object
        self.init_repository()
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
