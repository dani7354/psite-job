class Configuration:
    def __init__(self,
                 smtp_host,
                 smtp_port,
                 smtp_user,
                 smtp_password,
                 db_host,
                 db_port,
                 db_user,
                 db_password,
                 db_name,
                 mail_sender,
                 mail_recipient,
                 test_mode_enabled,
                 run_interval_seconds) -> None:
        self.mail_configuration = MailConfiguration(smtp_host,
                                                    smtp_port,
                                                    smtp_user,
                                                    smtp_password,
                                                    mail_sender,
                                                    mail_recipient)

        self.db_configuration = DbConfiguration(db_host,
                                                db_port,
                                                db_user,
                                                db_password,
                                                db_name)
        self.test_mode_enabled = test_mode_enabled
        self.run_interval_seconds = run_interval_seconds


class MailConfiguration:
    def __init__(self, smtp_host, smtp_port, smtp_user, smtp_password, mail_sender, mail_recipient):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.mail_sender = mail_sender
        self.mail_recipient = mail_recipient


class DbConfiguration:
    def __init__(self, db_host, db_port, db_user, db_password, db_name):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
