import logging
from typing import ClassVar

import requests


class DiscordWebhookError(Exception):
    pass


class DiscordWebHookClient:
    """
    Client for sending messages to a Discord webhook.
    See docs: https://docs.discord.com/developers/resources/webhook#execute-webhook
    """

    _request_timeout_secs: ClassVar[int] = 10
    _success_status_code: ClassVar[int] = 204
    _content_min_length: ClassVar[int] = 1
    _content_max_length: ClassVar[int] = 2000

    def __init__(self, webhook_url: str) -> None:
        self._webhook_url = webhook_url
        self._logger = logging.getLogger(self.__class__.__name__)

    def send_message(self, message: str) -> None:
        if not self._is_message_valid(message):
            raise DiscordWebhookError(
                f"Message length must be between {self._content_min_length} and {self._content_max_length} characters."
            )
        try:
            payload = {"content": message}
            response = requests.post(self._webhook_url, json=payload, timeout=self._request_timeout_secs)
            response.raise_for_status()

            if response.status_code != self._success_status_code:
                raise DiscordWebhookError(f"Failed to send message. Status code: {response.status_code}")
        except requests.exceptions.HTTPError as ex:
            self._logger.exception(ex)
            raise DiscordWebhookError(f"HTTP error occurred: {ex}") from ex

    def _is_message_valid(self, message: str) -> bool:
        return self._content_min_length <= len(message) <= self._content_max_length
