from dataclasses import dataclass


@dataclass(frozen=True)
class Configuration:
    mail_configuration: 'MailConfiguration'
    db_configuration: 'DbConfiguration'
    test_mode_enabled: bool


@dataclass(frozen=True)
class MailConfiguration:
    smtp_port: int
    smtp_user: str
    smtp_host: str
    smtp_password: str
    mail_sender: str
    mail_recipient: str


@dataclass(frozen=True)
class DbConfiguration:
    host: str
    port: int
    user: str
    password: str
    name: str

