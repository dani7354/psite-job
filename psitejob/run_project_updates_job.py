import requests
import logging
import os
from datetime import datetime
from argparse import Namespace, ArgumentParser
from psitejob.repository.project import ProjectRepository
from psitejob.configuration.configuration_loader import load_configuration


GITHUB_API_BASE_URL = "https://api.github.com/repos/dani7354"


class ApiError(Exception):
    pass


class GithubApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_latest_commits(self, project_name: str) -> list:
        url = f"{self.base_url}/{project_name}/commits"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise ApiError(f"Error while requesting {url}") from e


class ProjectUpdatesJob:
    def __init__(self, project_repository: ProjectRepository, github_api_client: GithubApiClient):
        self.project_repository = project_repository
        self.github_api_client = github_api_client

    def run(self):
        projects = self.project_repository.get_projects()
        for project in projects:
            try:
                logging.info(f"Getting commits for project {project.title}...")
                commits = self.github_api_client.get_latest_commits(project.title)
                if not commits:
                    continue

                newest_commit_date = datetime.fromisoformat(commits[0]["commit"]["author"]["date"]).replace(tzinfo=None)
                project_updates = sorted(project.updates, key=lambda x: x.updated_at, reverse=True)
                latest_existing_update = project_updates[0] if project.updates else None
                if latest_existing_update and newest_commit_date <= latest_existing_update.updated_at:
                    logging.info(f"No new commits for project {project.title}. Skipping...")
                    continue

                self.project_repository.add_update(project.id, updated_at=newest_commit_date)

            except ApiError as ex:
                logging.error(f"Error while getting update for project {project.title}: {ex}. Skipping...")


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
        level=log_level)
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
