from argparse import Namespace, ArgumentParser
from typing import ClassVar
from datetime import datetime
import logging
import os

import requests

from psitejob.repository.project import ProjectRepository
from psitejob.configuration.configuration_loader import load_configuration

GITHUB_API_BASE_URL = "https://api.github.com/repos/dani7354"


class ApiError(Exception):
    pass


class GithubApiClient:
    _default_request_timeout_secs: ClassVar[int] = 10

    def __init__(self, base_url: str):
        self._base_url = base_url

    def get_latest_commits(self, project_name: str) -> list:
        url = f"{self._base_url}/{project_name}/commits"
        try:
            response = requests.get(url, timeout=self._default_request_timeout_secs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise ApiError(f"Error while requesting {url}") from e


class ProjectUpdatesJob:
    def __init__(self, project_repository: ProjectRepository, github_api_client: GithubApiClient):
        self._project_repository = project_repository
        self._github_api_client = github_api_client

    def run(self):
        projects = self._project_repository.get_projects()
        for project in projects:
            try:
                logging.info("Getting commits for project %s...", project.title)
                commits = self._github_api_client.get_latest_commits(project.title)
                if not commits:
                    continue

                commit_date_str = commits[0]["commit"]["author"]["date"]
                # parse date from string, convert to system timezone and remove tzinfo
                newest_commit_date = datetime.fromisoformat(commit_date_str).astimezone(None).replace(tzinfo=None)

                project_updates = sorted(project.updates, key=lambda x: x.updated_at, reverse=True)
                latest_existing_update = project_updates[0] if project.updates else None
                if latest_existing_update and newest_commit_date <= latest_existing_update.updated_at:
                    logging.info("No new commits for project %s. Skipping...", project.title)
                    continue

                self._project_repository.add_update(project.id, updated_at=newest_commit_date)

            except ApiError as ex:
                logging.error(
                    "Error while getting update for project %s:. Skipping...",
                    project.title,
                )
                logging.exception(ex)


def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-c", "--configuration", dest="configuration", type=str, required=True)

    return parser.parse_args()


def setup_logging(configuration):
    log_level = logging.DEBUG if configuration.test_mode_enabled else logging.INFO
    logging.basicConfig(
        filename=os.path.join(configuration.log_dir, "project_update_job.log"),
        filemode="a",
        format="%(asctime)s - %(levelname)s: %(message)s",
        level=log_level,
    )
    logging.getLogger().addHandler(logging.StreamHandler())


def main():
    args = parse_arguments()
    configuration = load_configuration(args.configuration)
    setup_logging(configuration)
    project_repository = ProjectRepository(configuration.db_configuration)
    github_api_client = GithubApiClient(GITHUB_API_BASE_URL)
    job = ProjectUpdatesJob(project_repository, github_api_client)
    job.run()


if __name__ == "__main__":
    main()
