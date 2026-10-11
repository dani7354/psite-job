from argparse import Namespace, ArgumentParser
import logging
import os


from psitejob.api.github import GithubApiClient
from psitejob.job.project import ProjectUpdatesJob
from psitejob.repository.project import ProjectRepository
from psitejob.configuration.configuration_loader import load_configuration

GITHUB_API_BASE_URL = "https://api.github.com/repos/dani7354"


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
