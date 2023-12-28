from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Message:
    message_id: int
    subject: str
    body: str
    date_created: datetime
    sender_name: str
    sender_email: str
    sender_ip: str
