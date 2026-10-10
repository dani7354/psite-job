import pytest
from sqlalchemy import create_engine

from psitejob.configuration.configuration import DbConfiguration
from psitejob.repository.model import Base


@pytest.fixture
def data_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)


@pytest.fixture
def db_config() -> DbConfiguration:
    return DbConfiguration("", 0, "", "", "")
