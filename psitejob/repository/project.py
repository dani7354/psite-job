from datetime import datetime

from sqlalchemy.orm import joinedload

from psitejob.configuration.configuration import DbConfiguration
from psitejob.repository.base import BaseRepository
from psitejob.repository.model import Project, ProjectUpdate


class ProjectRepository(BaseRepository):
    def __init__(self, db_configuration: DbConfiguration) -> None:
        super().__init__(db_configuration)

    def get_projects(self) -> list[Project]:
        with self.get_session() as session:
            projects = session.query(Project).options(joinedload(Project.updates)).all()

        return projects

    def add_update(self, project_id: int, updated_at: datetime) -> None:
        with self.get_session() as session:
            project_update = ProjectUpdate(project_id=project_id, updated_at=updated_at)
            session.add(project_update)
            session.commit()
