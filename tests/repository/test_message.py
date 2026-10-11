from datetime import datetime

import pytest
from sqlalchemy import Engine

from psitejob.configuration.configuration import DbConfiguration
from psitejob.repository.message import MessageRepository
from psitejob.repository.model import Message


@pytest.fixture(name="message_repository")
def message_repository_fixture(data_engine: Engine, db_config: DbConfiguration) -> MessageRepository:
    repository = MessageRepository(db_config)
    repository.engine = data_engine

    return repository


def test_get_messages_to_send_empty(message_repository: MessageRepository):
    messages = message_repository.get_messages_to_send()
    assert messages == []


def test_set_messages_sent_success(message_repository: MessageRepository):
    message = Message(
        subject="Test Subject",
        body="Test Body",
        date_created=datetime.now(),
        sender_name="Test Sender",
        sender_email="test@example.com",
        sender_ip="127.0.0.1",
    )

    with message_repository.get_session() as session:
        session.add(message)
        session.commit()

    messages = message_repository.get_messages_to_send()
    assert len(messages) == 1

    message_repository.set_messages_sent(messages)

    messages_after_update = message_repository.get_messages_to_send()
    assert len(messages_after_update) == 0
