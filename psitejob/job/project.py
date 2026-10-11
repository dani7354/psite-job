import logging
from datetime import datetime

from psitejob.api.github import GithubApiClient, ApiError
from psitejob.repository.project import ProjectRepository


class ProjectUpdatesJob:
    def __init__(self, project_repository: ProjectRepository, github_api_client: GithubApiClient):
        self._project_repository = project_repository
        self._github_api_client = github_api_client
        self._logger = logging.getLogger(__name__)

    def run(self):
        projects = self._project_repository.get_projects()
        for project in projects:
            try:
                self._logger.info("Getting commits for project %s...", project.title)
                commits = self._github_api_client.get_latest_commits(project.title)
                if not commits:
                    continue

                commit_date_str = commits[0]["commit"]["author"]["date"]
                # parse date from string, convert to system timezone and remove tzinfo
                newest_commit_date = datetime.fromisoformat(commit_date_str).astimezone(None).replace(tzinfo=None)

                project_updates = sorted(project.updates, key=lambda x: x.updated_at, reverse=True)
                latest_existing_update = project_updates[0] if project.updates else None
                if latest_existing_update and newest_commit_date <= latest_existing_update.updated_at:
                    self._logger.info("No new commits for project %s. Skipping...", project.title)
                    continue

                self._project_repository.add_update(project.id, updated_at=newest_commit_date)

            except ApiError as ex:
                self._logger.error(
                    "Error while getting update for project %s:. Skipping...",
                    project.title,
                )
                self._logger.exception(ex)
