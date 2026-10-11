#!/usr/bin/env python3
import ssl
import smtplib
import logging
import os
from argparse import Namespace, ArgumentParser
from datetime import date
from email.header import Header
from email.mime.text import MIMEText
from smtplib import SMTPException
from typing import Sequence

from psitejob.configuration.configuration_loader import load_configuration
from psitejob.configuration.configuration import Configuration
from psitejob.repository.model import Message
from psitejob.repository.message import MessageRepository

mail_template_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "psitejob/mail_templates/message.html")
today = date.today()


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


class MessageJob:
    def __init__(self, message_repository: MessageRepository, configuration: Configuration):
        self.message_repository = message_repository
        self.configuration = configuration

    def run(self):
        try:
            logging.info("Reading messages from source...")
            messages = self._get_messages()

            logging.info("Sending %d messages...", len(messages))
            messages_sent = self._send_messages(messages) if not self.configuration.test_mode_enabled else messages

            logging.info("%d messages sent successfully!", len(messages_sent))
            self._update_status_for_messages(messages_sent)
        except Exception as e:
            logging.exception(e)
            raise SystemExit(1) from e

    def _get_messages(self) -> list[Message]:
        messages = self.message_repository.get_messages_to_send()

        return messages

    def _send_messages(self, messages: Sequence[Message]) -> list[Message]:
        messages_sent = []
        for message in messages:
            try:
                message_str = self._create_message_str(message)
                self._send_message(message_str)
                messages_sent.append(message)
            except (ValueError, SMTPException) as e:
                logging.exception("Failed to send message with ID %d. Exception: %s", message.id, e)

        return messages_sent

    def _update_status_for_messages(self, messages_sent: Sequence[Message]) -> None:
        if not messages_sent:
            return

        self.message_repository.set_messages_sent(messages_sent)

    def _create_message_str(self, message: Message) -> MIMEText:
        message_body = self._read_html_template(mail_template_file)
        message_body = message_body.replace("[subject]", message.subject)
        message_body = message_body.replace("[sender_email]", message.sender_email)
        message_body = message_body.replace("[sender_name]", message.sender_name)
        message_body = message_body.replace("[sender_ip]", message.sender_ip)
        message_body = message_body.replace("[body]", message.body)
        message_body = message_body.replace("[date_created]", message.date_created.strftime("%Y-%m-%d %H:%M:%S.%f"))

        mime_text_message = MIMEText(message_body, "html", "utf-8")
        subject = f"Message received: {message.subject}"
        mime_text_message["Subject"] = Header(subject, "utf-8")
        mime_text_message["From"] = self.configuration.mail_configuration.mail_sender
        mime_text_message["To"] = self.configuration.mail_configuration.mail_recipient

        return mime_text_message

    def _send_message(self, message_str) -> None:
        context = ssl.create_default_context()
        with smtplib.SMTP(
            host=self.configuration.mail_configuration.smtp_host,
            port=self.configuration.mail_configuration.smtp_port,
        ) as mail_server:
            mail_server.starttls(context=context)
            mail_server.login(
                self.configuration.mail_configuration.smtp_user,
                self.configuration.mail_configuration.smtp_password,
            )
            mail_server.send_message(message_str)

    @staticmethod
    def _read_html_template(path) -> str:
        with open(path, "r", encoding="utf-8") as template_file:
            template = template_file.read()

            return template


def main() -> None:
    args = parse_arguments()
    configuration = load_configuration(args.configuration)
    setup_logging(configuration)
    log_configuration_summary(configuration)
    message_repository = MessageRepository(configuration.db_configuration)
    message_job = MessageJob(message_repository, configuration)
    message_job.run()


if __name__ == "__main__":
    main()
