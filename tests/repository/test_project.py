from datetime import datetime

import pytest
from sqlalchemy import Engine

from psitejob.configuration.configuration import DbConfiguration
from psitejob.repository.model import Project
from psitejob.repository.project import ProjectRepository


@pytest.fixture(name="project_repository")
def project_repository_fixture(data_engine: Engine, db_config: DbConfiguration) -> ProjectRepository:
    repository = ProjectRepository(db_config)
    repository.engine = data_engine

    return repository


def test_get_projects_empty(project_repository: ProjectRepository):
    projects = project_repository.get_projects()
    assert projects == []


def test_update_projects_success(project_repository: ProjectRepository):
    project_id, update_count = 0, 2

    with project_repository.get_session() as session:
        project = Project(
            id=project_id,
            title="Test project",
            description="Test description",
            url="http://github.com/dani7354/psite-job",
            is_visible=True,
            order_number=0,
        )

        session.add(project)
        session.commit()

    for _ in range(0, update_count):
        project_repository.add_update(project_id=project_id, updated_at=datetime.now())

    project_updated = project_repository.get_projects()
    assert len(project_updated[0].updates) == update_count
