from datetime import datetime
from psitejob.configuration.configuration import DbConfiguration
from psitejob.repository.model import Message
from psitejob.repository.base import BaseRepository


class MessageRepository(BaseRepository):
    def __init__(self, db_configuration: DbConfiguration) -> None:
        super().__init__(db_configuration)

    def get_messages_to_send(self) -> list[Message]:
        with self.get_session() as session:
            messages = session.query(Message).filter(Message.date_sent.is_(None)).all()

        return messages

    def set_messages_sent(self, messages: list[Message]) -> None:
        with self.get_session() as session:
            for message in messages:
                updated_message = session.query(Message).filter(Message.id == message.id).first()
                updated_message.date_sent = datetime.now()
            session.commit()
