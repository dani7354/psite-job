class Message:
    def __init__(self, message_id, subject, body, date_created, sender_name, sender_email, sender_ip) -> None:
        self.id = message_id
        self.subject = subject
        self.body = body
        self.date_created = date_created
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.sender_ip = sender_ip
