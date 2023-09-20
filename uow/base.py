import abc

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from db import engine

DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=engine
)


class AbstractUnitOfWork(abc.ABC):
    def __enter__(self) -> 'AbstractUnitOfWork':
        return self

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    @abc.abstractmethod
    def init_repository(self):
        raise NotImplementedError

    def __enter__(self):
        self.session: Session = self.session_factory()
        self.init_repository()
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()