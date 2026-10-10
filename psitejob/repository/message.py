# pylint: disable=useless-parent-delegation
from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from psitejob.configuration.configuration import DbConfiguration
from psitejob.repository.model import Message
from psitejob.repository.base import BaseRepository


class MessageRepository(BaseRepository):
    def __init__(self, db_configuration: DbConfiguration) -> None:
        super().__init__(db_configuration)

    def get_messages_to_send(self) -> list[Message]:
        with self.get_session() as session:
            statement = select(Message).where(Message.date_sent.is_(None))
            messages = session.scalars(statement).all()

        return list(messages)

    def set_messages_sent(self, messages: Sequence[Message]) -> None:
        with self.get_session() as session:
            for message in messages:
                updated_message = session.scalar(select(Message).where(Message.id == message.id))
                if updated_message is None:
                    raise LookupError(f"Message with id {message.id} was not found")
                updated_message.date_sent = datetime.now()
            session.commit()
