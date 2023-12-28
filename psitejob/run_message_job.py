#!/usr/bin/env python3
import ssl
import smtplib
import logging
from argparse import Namespace, ArgumentParser
from datetime import date
from email.header import Header
from email.mime.text import MIMEText
from psitejob.configuration.configuration_loader import load_configuration
from psitejob.configuration.configuration import Configuration
from psitejob.model.message import Message
from psitejob.repository.message import MessageRepository


log_file = "/var/log/psitejob/service.log"
mail_template_file = "mail_templates/message.html"
today = date.today()


def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-c", "--configuration", dest="configuration", type=str, required=True)

    return parser.parse_args()


def setup_logging(configuration):
    log_level = logging.DEBUG if configuration.test_mode_enabled else logging.INFO
    logging.basicConfig(
        filename=log_file,
        filemode="a",
        format="%(asctime)s - %(levelname)s: %(message)s",
        level=log_level)
    logging.getLogger().addHandler(logging.StreamHandler())


def log_configuration_summary(configuration: Configuration):
    logging.info(f"Test mode enabled: {configuration.test_mode_enabled}")
    logging.debug(f"Mail recipient: {configuration.mail_configuration.mail_recipient}")
    logging.debug(f"SMTP host: {configuration.mail_configuration.smtp_host}:"
                  f"{configuration.mail_configuration.smtp_port}")
    logging.debug(f"Database host {configuration.db_configuration.host}:"
                  f"{configuration.db_configuration.port}. "
                  f"Database name: {configuration.db_configuration.name}")


class MessageJob:
    def __init__(self, message_repository: MessageRepository, configuration: Configuration):
        self.message_repository = message_repository
        self.configuration = configuration

    def run(self):
        try:
            logging.info("Reading messages from source...")
            messages = self._get_messages()

            logging.info(f"Sending {len(messages)} messages...")
            messages_sent = self._send_messages(messages) if not self.configuration.test_mode_enabled else messages

            logging.info(f"{len(messages_sent)} messages sent successfully!")
            self._update_status_for_messages(messages_sent)
        except Exception as e:
            logging.error(e)

    def _get_messages(self) -> list[Message]:
        messages = self.message_repository.get_messages_to_send()

        return messages

    def _send_messages(self, messages) -> list:
        messages_sent = []
        for message in messages:
            try:
                message_str = self._create_message_str(message)
                self._send_message(message_str)
                messages_sent.append(message)
            except Exception as e:
                logging.error(f"Failed to sent message with ID {message.id}. Exception: {e}")

        return messages_sent

    def _update_status_for_messages(self, messages_sent) -> None:
        if not messages_sent:
            return
        try:
            self.message_repository.set_messages_sent(messages_sent)
        except Exception as e:
            logging.error(f"Failed to update status for messages. Exception: {e}")

    def _create_message_str(self, message) -> MIMEText:
        message_body = self._read_html_template(mail_template_file)
        message_body = message_body.replace("[subject]", message.subject)
        message_body = message_body.replace("[sender_email]", message.sender_email)
        message_body = message_body.replace("[sender_name]", message.sender_name)
        message_body = message_body.replace("[sender_ip]", message.sender_ip)
        message_body = message_body.replace("[body]", message.body)
        message_body = message_body.replace("[date_created]", message.date_created.strftime("%Y/%m/%d %H:%M:%S.%f"))

        mime_text_message = MIMEText(message_body, "html", "utf-8")
        subject = f"Message received: {message.subject}"
        mime_text_message["Subject"] = Header(subject, "utf-8")
        mime_text_message["From"] = self.configuration.mail_configuration.mail_sender
        mime_text_message["To"] = self.configuration.mail_configuration.mail_recipient

        return mime_text_message

    def _send_message(self, message_str) -> None:
        context = ssl.create_default_context()
        with smtplib.SMTP(host=self.configuration.mail_configuration.smtp_host,
                          port=self.configuration.mail_configuration.smtp_port) as mail_server:
            mail_server.starttls(context=context)
            mail_server.login(self.configuration.mail_configuration.smtp_user,
                              self.configuration.mail_configuration.smtp_password)
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
