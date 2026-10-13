from argparse import Namespace, ArgumentParser
from pathlib import Path

from psitejob.api.github import GithubApiClient
from psitejob.job.project import ProjectUpdatesJob
from psitejob.log import setup_logging
from psitejob.repository.project import ProjectRepository
from psitejob.configuration.configuration_loader import load_configuration

GITHUB_API_BASE_URL = "https://api.github.com/repos/dani7354"


def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-c", "--configuration", dest="configuration", type=str, required=True)

    return parser.parse_args()


def main():
    args = parse_arguments()
    configuration = load_configuration(args.configuration)
    setup_logging(configuration, Path(__file__).stem)
    project_repository = ProjectRepository(configuration.db_configuration)
    github_api_client = GithubApiClient(GITHUB_API_BASE_URL)
    job = ProjectUpdatesJob(project_repository, github_api_client)
    job.run()


if __name__ == "__main__":
    main()
