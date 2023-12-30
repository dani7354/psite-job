from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from psitejob.configuration.configuration import DbConfiguration


class BaseRepository:
    def __init__(self, db_configuration: DbConfiguration):
        self.engine = self._get_engine(db_configuration)

    def get_session(self):
        return Session(self.engine)

    @staticmethod
    def _get_engine(db_configuration: DbConfiguration):
        return create_engine(f"mysql+mysqlconnector://{db_configuration.user}:{db_configuration.password}@"
                             f"{db_configuration.host}:{db_configuration.port}/{db_configuration.name}",
                             echo=True)