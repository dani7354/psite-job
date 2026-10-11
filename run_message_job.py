#!/usr/bin/env python3
import logging
from argparse import Namespace, ArgumentParser
from pathlib import Path

from psitejob.api.discord import DiscordWebHookClient
from psitejob.configuration.configuration_loader import load_configuration
from psitejob.configuration.configuration import Configuration
from psitejob.job.message import MessageJob
from psitejob.repository.message import MessageRepository
from psitejob.service.message import DiscordMessageService, EmailService

mail_template_file = Path(__file__).resolve().parent / "psitejob/mail_templates/message.html"


def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-c", "--configuration", dest="configuration", type=str, required=True)

    return parser.parse_args()


def setup_logging(configuration):
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger = logging.getLogger()
    log_level = logging.DEBUG if configuration.test_mode_enabled else logging.INFO
    logger.setLevel(log_level)
    logger.addHandler(handler)


def log_configuration_summary(configuration: Configuration):
    logging.info("Test mode enabled: %s", configuration.test_mode_enabled)
    logging.debug("Mail recipient: %s", configuration.mail_configuration.mail_recipient)
    logging.debug(
        "SMTP host: %s:%d",
        configuration.mail_configuration.smtp_host,
        configuration.mail_configuration.smtp_port,
    )
    logging.debug(
        "Database host %s:%d. Database name: %s",
        configuration.db_configuration.host,
        configuration.db_configuration.port,
        configuration.db_configuration.name,
    )


def main() -> None:
    args = parse_arguments()
    configuration = load_configuration(args.configuration)
    setup_logging(configuration)
    log_configuration_summary(configuration)

    message_repository = MessageRepository(configuration.db_configuration)
    discord_webhook_client = DiscordWebHookClient(configuration.discord_configuration.webhook_url)
    message_services = [DiscordMessageService(discord_webhook_client), EmailService(configuration, mail_template_file)]

    message_job = MessageJob(message_repository, message_services, configuration)
    message_job.run()


if __name__ == "__main__":
    main()
