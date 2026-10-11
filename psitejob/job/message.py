import logging
import smtplib
from typing import Sequence, ClassVar

from psitejob.configuration.configuration import Configuration
from psitejob.repository.message import MessageRepository
from psitejob.repository.model import Message
from psitejob.service.message import MessageService


class MessageJob:
    _encoding: ClassVar[str] = "utf-8"

    def __init__(
        self,
        message_repository: MessageRepository,
        message_services: Sequence[MessageService],
        configuration: Configuration,
    ) -> None:
        self._message_repository = message_repository

        if not message_services:
            raise ValueError("At least one message service must be provided")

        self._message_services = message_services
        self._configuration = configuration
        self._logger = logging.getLogger(__name__)

    def run(self):
        try:
            self._logger.info("Reading messages from source...")
            messages = self._get_messages()

            logging.info("Sending %d messages...", len(messages))
            messages_sent = self._send_messages(messages) if not self._configuration.test_mode_enabled else messages

            logging.info("%d messages sent successfully!", len(messages_sent))
            self._update_status_for_messages(messages_sent)
        except Exception as e:
            logging.exception(e)
            raise SystemExit(1) from e

    def _get_messages(self) -> list[Message]:
        messages = self._message_repository.get_messages_to_send()

        return messages

    def _send_messages(self, messages: Sequence[Message]) -> list[Message]:
        messages_sent = []
        for message in messages:
            try:
                for message_service in self._message_services:
                    message_service.send_message(message)
                messages_sent.append(message)
            except (ValueError, smtplib.SMTPException, RuntimeError) as e:
                logging.exception("Failed to send message with ID %d. Exception: %s", message.id, e)

        return messages_sent

    def _update_status_for_messages(self, messages_sent: Sequence[Message]) -> None:
        if not messages_sent:
            return

        self._message_repository.set_messages_sent(messages_sent)
