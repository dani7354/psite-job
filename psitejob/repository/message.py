from mysql.connector import connection
from datetime import datetime

from psitejob.configuration.configuration import DbConfiguration
from psitejob.model.message import Message


class MessageRepository:
    def __init__(self, db_configuration: DbConfiguration) -> None:
        self.db_configuration = db_configuration

    def _get_connection(self) -> connection:
        con = connection.MySQLConnection(host=self.db_configuration.host,
                                         user=self.db_configuration.user,
                                         password=self.db_configuration.password,
                                         database=self.db_configuration.name)
        return con

    def get_messages_to_send(self) -> list[Message]:
        with self._get_connection() as con:
            with con.cursor(dictionary=True) as cursor:
                query = ("SELECT Id, Subject, Body, DateCreated, SenderName, SenderEmail, SenderIp "
                         "FROM Message "
                         "WHERE DateSent IS NULL;")
                cursor.execute(query)
                messages = []
                for row in cursor:
                    message = Message(row["Id"], row["Subject"], row["Body"],
                                      row["DateCreated"], row["SenderName"],
                                      row["SenderEmail"], row["SenderIp"])
                    messages.append(message)

        return messages

    def set_messages_sent(self, messages: list[Message]) -> None:
        message_ids = tuple([m.message_id for m in messages])
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
        with self._get_connection() as con:
            with con.cursor() as cursor:
                format_strings = ",".join(["%s"] * len(message_ids))
                query = f"UPDATE Message SET DateSent = '{now}' WHERE Id IN ({format_strings})"
                cursor.execute(query, message_ids)
                con.commit()
