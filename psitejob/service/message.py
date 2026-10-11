import logging
import smtplib
import ssl
from abc import ABC, abstractmethod
from email.header import Header
from email.mime.text import MIMEText
from pathlib import Path
from typing import ClassVar

from psitejob.api.discord import DiscordWebhookClient, DiscordWebhookError
from psitejob.configuration.configuration import Configuration
from psitejob.repository.model import Message


class MessageService(ABC):

    @abstractmethod
    def send_message(self, message: Message) -> None:
        pass


class EmailService(MessageService):
    _encoding: ClassVar[str] = "utf-8"

    def __init__(self, configuration: Configuration, email_template_file_path: Path) -> None:
        self._configuration = configuration
        self._mail_template_file = email_template_file_path
        self._logger = logging.getLogger(self.__class__.__name__)

    def send_message(self, message: Message) -> None:
        self._logger.info("Sending message with ID %d via email...", message.id)
        context = ssl.create_default_context()
        with smtplib.SMTP(
            host=self._configuration.mail_configuration.smtp_host,
            port=self._configuration.mail_configuration.smtp_port,
        ) as mail_server:
            mail_server.starttls(context=context)
            mail_server.login(
                self._configuration.mail_configuration.smtp_user,
                self._configuration.mail_configuration.smtp_password,
            )
            mail_server.send_message(self._create_message_str(message))

    def _create_message_str(self, message: Message) -> MIMEText:
        message_body = self._read_html_template(self._mail_template_file)
        message_body = message_body.replace("[subject]", message.subject)
        message_body = message_body.replace("[sender_email]", message.sender_email)
        message_body = message_body.replace("[sender_name]", message.sender_name)
        message_body = message_body.replace("[sender_ip]", message.sender_ip)
        message_body = message_body.replace("[body]", message.body)
        message_body = message_body.replace("[date_created]", message.date_created.strftime("%Y-%m-%d %H:%M:%S.%f"))
        mime_text_message = MIMEText(message_body, "html", self._encoding)
        subject = f"Message received: {message.subject}"
        mime_text_message["Subject"] = Header(subject, self._encoding)
        mime_text_message["From"] = self._configuration.mail_configuration.mail_sender
        mime_text_message["To"] = self._configuration.mail_configuration.mail_recipient

        return mime_text_message

    @classmethod
    def _read_html_template(cls, path: Path) -> str:
        with open(path, "r", encoding=cls._encoding) as template_file:
            return template_file.read()


class DiscordMessageService(MessageService):
    _date_format: ClassVar[str] = "%Y-%m-%d %H:%M:%S"

    def __init__(self, discord_webhook_client: DiscordWebhookClient) -> None:
        self._discord_webhook_client = discord_webhook_client
        self._logger = logging.getLogger(self.__class__.__name__)

    def send_message(self, message: Message) -> None:
        try:
            self._logger.info("Sending message with ID %d to Discord webhook...", message.id)
            message_str = self._format_message_str(message)
            self._discord_webhook_client.send_message(message_str)
        except DiscordWebhookError as ex:
            self._logger.exception(ex)
            raise RuntimeError(f"Failed to send message to Discord webhook. Exception: {ex}") from ex

    @classmethod
    def _format_message_str(cls, message: Message) -> str:
        return f"""
        ## {message.subject}
        Afsender-IP: **{message.sender_ip}**
        Afsender-navn: **{message.sender_name}**
        Afsender-email: **{message.sender_email}**
        Tidspunkt: **{message.date_created.strftime(cls._date_format)}**
        
        
        {message.body}
        """
