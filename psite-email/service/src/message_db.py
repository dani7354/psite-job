from mysql.connector import (connection)
from message import Message
from datetime import datetime


def get_connection(db_configuration) -> connection:
    con = connection.MySQLConnection(host=db_configuration.db_host,
                                     user=db_configuration.db_user,
                                     password=db_configuration.db_password,
                                     database=db_configuration.db_name)
    return con


def get_messages_to_send(db_configuration) -> list:
    with get_connection(db_configuration) as con:
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


def set_messages_sent(db_configuration, messages) -> None:
    message_ids = tuple([m.id for m in messages])
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
    with get_connection(db_configuration) as con:
        with con.cursor() as cursor:
            format_strings = ",".join(["%s"] * len(message_ids))
            query = f"UPDATE Message SET DateSent = '{now}' WHERE Id IN ({format_strings})"
            cursor.execute(query, message_ids)
            con.commit()
