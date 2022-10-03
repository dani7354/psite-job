from configuration import Configuration
import os

DEFAULT_SMTP_PORT = 587
DEFAULT_DB_PORT = 3306
DEFAULT_RUN_INTERVAL_SECONDS = 300


def load_configuration() -> Configuration:
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT", DEFAULT_SMTP_PORT)
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    db_host = os.environ.get("DB_HOST")
    db_port = os.environ.get("DB_PORT", DEFAULT_DB_PORT)
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_name = os.environ.get("DB_NAME")
    mail_recipient = os.environ.get("MAIL_RECIPIENT")
    mail_sender = os.environ.get("MAIL_SENDER")
    test_mode_enabled = bool(int(os.environ.get("TEST_MODE_ENABLED", 0)))
    run_interval_seconds = int(os.environ.get("RUN_INTERVAL_SECONDS", DEFAULT_RUN_INTERVAL_SECONDS))

    return Configuration(smtp_host,
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
                         run_interval_seconds)
