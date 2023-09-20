import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import Base


@pytest.fixture
def in_memory_db():
    engine = create_engine('sqlite:///:memory:')
    Base.create_all(engine)
    return engine


@pytest.fixture
def session_factory(in_memory_db):
    return sessionmaker(bind=in_memory_db)


@pytest.fixture
def session(session_factory):
    return session_factory()